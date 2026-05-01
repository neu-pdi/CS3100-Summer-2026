#!/usr/bin/env python3
"""
Stage 1 exporter for Canvas course content.

Reads configured lecture, assignment, and lab content from course.config.json,
converts markdown files to HTML, exports lecture slide decks to PDF, exports
top-level pages from src/pages, and copies linked assets into:
    canvasport/build/files/<content-slug>/img
    canvasport/build/files/<content-slug>/code

Only writes under canvasport/build.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
import os
import contextlib
import functools
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import urlsplit, urlunsplit

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

import markdown
from bs4 import BeautifulSoup

from markdownextensions import (
    AsciiArtExtension,
    ExerciseExtension,
    IncerciseExtension,
    MarginNotesExtension,
    TodoExtension,
)

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".bmp", ".ico", ".avif", ".tif", ".tiff"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export Canvas course markdown content to HTML for staging.")
    script_path = Path(__file__).resolve()
    repo_root_default = script_path.parents[2]

    parser.add_argument("--repo-root", default=str(repo_root_default), help="Repository root path")
    parser.add_argument("--config", default="course.config.json", help="Path to course config JSON, relative to repo root")
    parser.add_argument("--lectures-dir", default="lecture-notes", help="Lecture notes directory, relative to repo root")
    parser.add_argument("--slides-dir", default="lecture-slides", help="Slides source directory, relative to repo root")
    parser.add_argument(
        "--slides-build-dir",
        default="build/lecture-slides",
        help="Built slides directory containing <lectureId>/index.html, relative to repo root",
    )
    parser.add_argument("--output-dir", default="canvasport/build", help="Output directory, relative to repo root")
    parser.add_argument("--pages-dir", default="src/pages", help="Pages directory containing extra markdown files (e.g. syllabus.md), relative to repo root")
    parser.add_argument("--clean", action="store_true", help="Delete output directory and exit (no rebuild)")
    parser.add_argument("--skip-slide-pdfs", action="store_true", help="Skip slide PDF export")
    parser.add_argument("--verbose", action="store_true", help="Print per-file progress while exporting")
    return parser.parse_args()


def _extract_front_matter_value(front_matter: str, key: str) -> Optional[str]:
    pattern = re.compile(rf"^{re.escape(key)}:\s*(.+)$", flags=re.MULTILINE)
    match = pattern.search(front_matter)
    if not match:
        return None

    value = match.group(1).strip().strip('"\'')
    return value or None


def strip_front_matter(text: str) -> tuple:
    """Return (body_without_frontmatter, title_or_None, description_or_None)."""
    if not text.startswith("---\n"):
        return text, None, None
    closing = text.find("\n---\n", 4)
    if closing == -1:
        return text, None, None

    front = text[4:closing]
    body = text[closing + 5 :]
    title = _extract_front_matter_value(front, "title")
    description = _extract_front_matter_value(front, "description")
    return body, title, description


def strip_mdx_only_lines(text: str) -> str:
    cleaned_lines: List[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("import "):
            continue
        if stripped.startswith("export "):
            continue
        if re.match(r"^<\w[\w\d]*(\s[^>]*)?\s*/>$", stripped):
            continue
        cleaned_lines.append(line)
    return "\n".join(cleaned_lines) + "\n"


def slug_from_url(url: str) -> str:
    path = url.split("#", 1)[0].split("?", 1)[0]
    return path


def is_external_url(url: str) -> bool:
    lowered = url.lower()
    return lowered.startswith("http://") or lowered.startswith("https://") or lowered.startswith("mailto:") or lowered.startswith("tel:")


def classify_asset(url: str) -> str:
    """
    Returns one of: img, code, skip.
    """
    slug = slug_from_url(url)
    if is_external_url(slug):
        return "skip"
    if slug.startswith("/"):
        extension = Path(slug).suffix.lower()
        if slug.startswith("/img/") or extension in IMAGE_EXTENSIONS:
            return "img"
        if slug.startswith("/code/"):
            return "code"
        if extension:
            return "code"
    return "skip"


def find_markdown_links(markdown_text: str) -> List[Tuple[str, str]]:
    """
    Returns tuples of (full_match_url_part, url).
    Supports markdown links/images and basic HTML src/href attributes.
    """
    links: List[Tuple[str, str]] = []

    md_pattern = re.compile(r"!?(?:\[[^\]]*\])\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
    for match in md_pattern.finditer(markdown_text):
        url = match.group(1).strip()
        links.append((url, url))

    html_pattern = re.compile(r"(?:src|href)=\"([^\"]+)\"")
    for match in html_pattern.finditer(markdown_text):
        url = match.group(1).strip()
        links.append((url, url))

    return links


def resolve_repo_source(repo_root: Path, url: str) -> Path:
    slug = slug_from_url(url)
    relative = slug.lstrip("/")
    static_candidate = repo_root / "static" / relative
    if static_candidate.exists():
        return static_candidate
    direct_candidate = repo_root / relative
    if direct_candidate.exists():
        return direct_candidate
    return static_candidate


def build_target_relative(asset_type: str, lecture_id: str, source_path: Path, source_url: str) -> Path:
    slug = slug_from_url(source_url)

    if slug.startswith("/img/"):
        relative_inside_group = Path(slug[len("/img/") :])
    elif slug.startswith("/code/"):
        relative_inside_group = Path(slug[len("/code/") :])
    else:
        relative_inside_group = Path(source_path.name)

    return Path("files") / lecture_id / asset_type / relative_inside_group


def copy_and_rewrite_assets(
    repo_root: Path,
    output_dir: Path,
    lecture_id: str,
    markdown_text: str,
) -> Tuple[str, List[str]]:
    warnings: List[str] = []
    rewritten = markdown_text
    replacements: Dict[str, str] = {}
    seen_urls: Set[str] = set()

    for _full, url in find_markdown_links(markdown_text):
        if url in seen_urls:
            continue
        seen_urls.add(url)

        asset_type = classify_asset(url)
        if asset_type == "skip":
            continue

        source_path = resolve_repo_source(repo_root, url)
        if not source_path.exists() or not source_path.is_file():
            warnings.append(f"[{lecture_id}] missing asset: {url}")
            continue

        target_relative = build_target_relative(asset_type, lecture_id, source_path, url)
        target_path = output_dir / target_relative
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, target_path)

        suffix = ""
        if "#" in url:
            suffix += "#" + url.split("#", 1)[1].split("?", 1)[0]
        if "?" in url:
            suffix += "?" + url.split("?", 1)[1]

        replacements[url] = str(target_relative).replace("\\", "/") + suffix

    for old, new in replacements.items():
        rewritten = rewritten.replace(f"({old})", f"({new})")
        rewritten = rewritten.replace(f"({old} ", f"({new} ")
        rewritten = rewritten.replace(f"({old}\t", f"({new}\t")
        rewritten = rewritten.replace(f'="{old}"', f'="{new}"')

    return rewritten, warnings


def render_mermaid_to_svg(mermaid_code: str, timeout_seconds: int = 30) -> Tuple[Optional[str], Optional[str]]:
    """
    Render Mermaid source to SVG. Returns (svg_text, error_message).
    """
    commands = [
        ["mmdc"],
        ["npx", "-y", "@mermaid-js/mermaid-cli@10.9.1"],
    ]

    with tempfile.TemporaryDirectory(prefix="canvasport_mermaid_") as temp_dir:
        temp_path = Path(temp_dir)
        input_file = temp_path / "diagram.mmd"
        output_file = temp_path / "diagram.svg"
        input_file.write_text(mermaid_code, encoding="utf-8")

        errors: List[str] = []
        for base_cmd in commands:
            cmd = base_cmd + ["-i", str(input_file), "-o", str(output_file), "-b", "transparent"]
            try:
                completed = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=timeout_seconds,
                    check=False,
                )
            except FileNotFoundError:
                errors.append(f"command not found: {' '.join(base_cmd)}")
                continue
            except subprocess.TimeoutExpired:
                errors.append(f"timeout running: {' '.join(base_cmd)}")
                continue

            if completed.returncode == 0 and output_file.exists():
                return output_file.read_text(encoding="utf-8"), None

            stderr = (completed.stderr or "").strip()
            stdout = (completed.stdout or "").strip()
            message = stderr or stdout or f"exit code {completed.returncode}"
            errors.append(f"{' '.join(base_cmd)}: {message}")

    return None, "; ".join(errors)


def inline_mermaid_svgs(
    markdown_text: str,
    lecture_id: str,
    warnings: List[str],
    mermaid_cache: Dict[str, Optional[str]],
) -> str:
    pattern = re.compile(r"```mermaid[^\n]*\n(.*?)\n```", flags=re.DOTALL)
    diagram_counter = 0

    def replace_match(match: re.Match) -> str:
        nonlocal diagram_counter
        diagram_counter += 1
        mermaid_code = match.group(1).strip()

        if not mermaid_code:
            warnings.append(f"[{lecture_id}] empty mermaid block at index {diagram_counter}")
            return match.group(0)

        cache_key = hashlib.sha256(mermaid_code.encode("utf-8")).hexdigest()
        if cache_key in mermaid_cache:
            svg_text = mermaid_cache[cache_key]
        else:
            svg_text, error = render_mermaid_to_svg(mermaid_code)
            mermaid_cache[cache_key] = svg_text
            if error and svg_text is None:
                warnings.append(f"[{lecture_id}] mermaid render failed at index {diagram_counter}: {error}")

        if not mermaid_cache.get(cache_key):
            return match.group(0)

        svg = mermaid_cache[cache_key] or ""
        return (
            "\n<div class=\"mermaid-diagram\">\n"
            f"{svg}\n"
            "</div>\n"
        )

    return pattern.sub(replace_match, markdown_text)


def resize_images(soup: BeautifulSoup, max_width: str = "90%") -> None:
    """Add max-width style to all img tags to prevent oversized images."""
    for img in soup.find_all("img"):
        existing_style = img.get("style", "")
        if "max-width" not in existing_style:
            if existing_style:
                img["style"] = f"{existing_style}; max-width: {max_width}; height: auto;"
            else:
                img["style"] = f"max-width: {max_width}; height: auto;"


def collect_initial_document_sources(
    repo_root: Path,
    config_path: Path,
    lectures_dir: Path,
    pages_dir: Path,
) -> Dict[str, Path]:
    documents: Dict[str, Path] = {}

    for lecture_id in load_lecture_ids(config_path):
        try:
            documents.setdefault(lecture_id, read_markdown_file(lectures_dir, lecture_id))
        except FileNotFoundError:
            continue

    for page_path in pages_dir.glob("*.md"):
        documents.setdefault(page_path.stem, page_path)

    for section_name in ["assignments", "labs"]:
        for url in load_material_urls(config_path, section_name):
            source_path = resolve_markdown_from_url(repo_root, url)
            stem = output_stem_from_url(url)
            if source_path and stem:
                documents.setdefault(stem, source_path)

    return documents


def build_export_targets(
    known_html: Set[str],
    known_pdf: Set[str],
) -> Tuple[Set[str], Set[str]]:
    return set(known_html), set(known_pdf)


def resolve_linked_markdown_source(repo_root: Path, current_source: Path, url: str) -> Optional[Path]:
    lowered = url.lower().strip()
    if (
        not lowered
        or lowered.startswith("http://")
        or lowered.startswith("https://")
        or lowered.startswith("mailto:")
        or lowered.startswith("tel:")
        or lowered.startswith("#")
    ):
        return None

    if classify_asset(url) != "skip":
        return None

    split = urlsplit(url)
    path = split.path.strip()
    if not path:
        return None

    candidates: List[Path] = []
    if path.startswith("/"):
        candidates.append(repo_root / path.lstrip("/"))
    else:
        candidates.append((current_source.parent / path).resolve())

    for candidate in candidates:
        if candidate.suffix.lower() in {".md", ".mdx"} and candidate.exists() and candidate.is_file():
            return candidate
        if not candidate.suffix:
            for extension in [".md", ".mdx"]:
                candidate_with_extension = candidate.with_suffix(extension)
                if candidate_with_extension.exists() and candidate_with_extension.is_file():
                    return candidate_with_extension

    return None


def expand_linked_document_sources(
    repo_root: Path,
    initial_documents: Dict[str, Path],
) -> Dict[str, Path]:
    expanded = dict(initial_documents)
    seen_paths: Set[Path] = {path.resolve() for path in expanded.values()}
    queue: List[Path] = list(expanded.values())

    while queue:
        current_source = queue.pop(0)
        markdown_text = current_source.read_text(encoding="utf-8")
        for _full, url in find_markdown_links(markdown_text):
            linked_source = resolve_linked_markdown_source(repo_root, current_source, url)
            if not linked_source:
                continue

            resolved_linked_source = linked_source.resolve()
            if resolved_linked_source in seen_paths:
                continue

            seen_paths.add(resolved_linked_source)
            expanded.setdefault(linked_source.stem, linked_source)
            queue.append(linked_source)

    return expanded


def rewrite_internal_document_links(
    html_text: str,
    known_html: Set[str],
    known_pdf: Set[str],
) -> str:
    soup = BeautifulSoup(html_text, "html.parser")

    for anchor in soup.find_all("a", href=True):
        href = anchor["href"].strip()
        if not href:
            continue

        lowered = href.lower()
        if (
            lowered.startswith("http://")
            or lowered.startswith("https://")
            or lowered.startswith("mailto:")
            or lowered.startswith("tel:")
            or lowered.startswith("#")
        ):
            continue

        split = urlsplit(href)
        path = split.path or ""
        if not path or path.startswith("files/"):
            continue

        normalized_path = path.replace("\\", "/")
        path_obj = Path(normalized_path)
        suffix = path_obj.suffix.lower()
        stem = path_obj.stem if suffix else path_obj.name

        replacement_path: Optional[str] = None

        if normalized_path.startswith("/lecture-slides/") and stem in known_pdf:
            replacement_path = f"{stem}.pdf"
        elif suffix in {".md", ".mdx", ".html"} and stem in known_html:
            replacement_path = f"{stem}.html"
        elif normalized_path.startswith(("/lecture-notes/", "/assignments/", "/labs/", "/overview", "/doc/")):
            if stem in known_html:
                replacement_path = f"{stem}.html"
            elif stem in known_pdf and normalized_path.startswith("/lecture-slides/"):
                replacement_path = f"{stem}.pdf"
        elif not suffix and stem in known_html:
            replacement_path = f"{stem}.html"
        elif not suffix and normalized_path.startswith("/lecture-slides/") and stem in known_pdf:
            replacement_path = f"{stem}.pdf"

        if replacement_path is None:
            continue

        anchor["href"] = urlunsplit(("", "", replacement_path, split.query, split.fragment))

    return str(soup)


def markdown_to_html(markdown_text: str) -> str:
    def convert_math(text: str) -> str:
        odd = True
        result = ''
        for index, char in enumerate(text):
            if char == '$':
                previous = text[index - 1] if index > 0 else ''
                if previous != '\\':
                    result += '<MATH>' if odd else '</MATH>'
                    odd = not odd
                else:
                    result = result[:-1]
                    result += char
            else:
                result += char
        return result

    html_body = markdown.markdown(
        markdown_text,
        extensions=[
            TodoExtension(),
            MarginNotesExtension(),
            IncerciseExtension(),
            ExerciseExtension(),
            AsciiArtExtension(),
            "codehilite",
            "fenced_code",
            "toc",
            "tables",
            "sane_lists",
        ],
        extension_configs={
            "codehilite": {"noclasses": True, "pygments_style": "a11y-light"},
            "toc": {"baselevel": 3},
        },
    )

    html_body = convert_math(html_body)
    body_object = BeautifulSoup(html_body, 'html.parser')
    resize_images(body_object)
    return (
        body_object.encode(formatter='html').decode()
        .replace('│', '&#x2502;')
        .replace('┼', '&#x253c;')
        .replace('└', '&boxur;')
        .replace('┴', '&boxhu;')
        .replace('┘', '&boxul;')
    )


def export_markdown_document(
    repo_root: Path,
    output_dir: Path,
    document_id: str,
    source_path: Path,
    known_html: Set[str],
    known_pdf: Set[str],
    warnings: List[str],
    mermaid_cache: Dict[str, Optional[str]],
) -> Path:
    markdown_text = source_path.read_text(encoding="utf-8")
    markdown_text, fm_title, fm_description = strip_front_matter(markdown_text)

    front_matter_headings: List[str] = []
    if fm_title:
        front_matter_headings.append(f"# {fm_title}")
    if fm_description:
        front_matter_headings.append(f"## {fm_description}")
    if front_matter_headings:
        markdown_text = "\n\n".join(front_matter_headings) + "\n\n" + markdown_text

    markdown_text = strip_mdx_only_lines(markdown_text)

    markdown_text = inline_mermaid_svgs(
        markdown_text=markdown_text,
        lecture_id=document_id,
        warnings=warnings,
        mermaid_cache=mermaid_cache,
    )

    markdown_text, asset_warnings = copy_and_rewrite_assets(repo_root, output_dir, document_id, markdown_text)
    warnings.extend(asset_warnings)

    html = markdown_to_html(markdown_text)
    html = rewrite_internal_document_links(html, known_html=known_html, known_pdf=known_pdf)
    output_html_path = output_dir / f"{document_id}.html"
    output_html_path.write_text(html, encoding="utf-8")
    return output_html_path


def load_lecture_ids(config_path: Path) -> List[str]:
    with config_path.open("r", encoding="utf-8") as f:
        config = json.load(f)

    lectures = config.get("lectures", [])
    ids: List[str] = []
    for lecture in lectures:
        lecture_id = lecture.get("lectureId")
        if lecture_id:
            ids.append(lecture_id)
    return ids


def load_material_urls(config_path: Path, section_name: str) -> List[str]:
    with config_path.open("r", encoding="utf-8") as f:
        config = json.load(f)

    entries = config.get(section_name, [])
    urls: List[str] = []
    for entry in entries:
        url = entry.get("url")
        if isinstance(url, str) and url.strip():
            urls.append(url.strip())
    return urls


def resolve_markdown_from_url(repo_root: Path, url: str) -> Optional[Path]:
    slug = slug_from_url(url).strip("/")
    if not slug:
        return None

    md_path = repo_root / f"{slug}.md"
    mdx_path = repo_root / f"{slug}.mdx"

    if md_path.exists():
        return md_path
    if mdx_path.exists():
        return mdx_path
    return None


def output_stem_from_url(url: str) -> Optional[str]:
    slug = slug_from_url(url).strip("/")
    if not slug:
        return None
    return Path(slug).name


def read_markdown_file(lectures_dir: Path, lecture_id: str) -> Path:
    md_path = lectures_dir / f"{lecture_id}.md"
    mdx_path = lectures_dir / f"{lecture_id}.mdx"

    if md_path.exists():
        return md_path
    if mdx_path.exists():
        return mdx_path

    raise FileNotFoundError(f"Lecture file not found for lectureId '{lecture_id}'")


def _select_slide_slug(
    lecture_id: str,
    slides_by_slug: Dict[str, Path],
) -> Tuple[Optional[str], Optional[str]]:
    if lecture_id in slides_by_slug:
        return lecture_id, None

    return None, f"[{lecture_id}] slide source not found in lecture-slides"


class _QuietHTTPRequestHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None:
        return


@contextlib.contextmanager
def serve_build_for_slides(repo_root: Path, build_root: Path):
    repo_name = repo_root.name
    with tempfile.TemporaryDirectory(prefix="canvasport_slides_server_") as temp_dir:
        temp_path = Path(temp_dir)
        alias_path = temp_path / repo_name
        os.symlink(build_root, alias_path, target_is_directory=True)

        handler = functools.partial(_QuietHTTPRequestHandler, directory=str(temp_path))
        server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()

        try:
            base_url = f"http://127.0.0.1:{server.server_port}/{repo_name}"
            yield base_url
        finally:
            server.shutdown()
            thread.join(timeout=2)
            server.server_close()


def render_slide_pdf_with_playwright(
    repo_root: Path,
    slide_url: str,
    output_pdf_path: Path,
    timeout_seconds: int = 240,
) -> Optional[str]:
    renderer_script = repo_root / "canvasport/scripts/render_slides_pdf_playwright.mjs"
    if not renderer_script.exists():
        return f"missing renderer script: {renderer_script}"

    cmd = ["node", str(renderer_script), slide_url, str(output_pdf_path)]
    completed = subprocess.run(
        cmd,
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=timeout_seconds,
        check=False,
    )

    if completed.returncode != 0:
        stderr = (completed.stderr or "").strip()
        stdout = (completed.stdout or "").strip()
        details = stderr or stdout or f"exit code {completed.returncode}"
        return f"playwright render failed: {details}"

    if not output_pdf_path.exists() or output_pdf_path.stat().st_size == 0:
        return "playwright completed but PDF is missing or empty"
    return None


def export_slide_pdfs(
    repo_root: Path,
    lecture_ids: List[str],
    slides_dir: Path,
    slides_build_dir: Path,
    output_dir: Path,
    warnings: List[str],
) -> int:
    if not slides_build_dir.exists() or not slides_build_dir.is_dir():
        warnings.append(f"[slides] built slides directory not found: {slides_build_dir}")
        return 0

    slide_sources = sorted(slides_dir.glob("*.mdx"))
    slides_by_slug: Dict[str, Path] = {p.stem: p for p in slide_sources}

    exported = 0
    build_root = slides_build_dir.parent
    with serve_build_for_slides(repo_root=repo_root, build_root=build_root) as slides_base_url:
        for lecture_id in lecture_ids:
            selected_slide_slug, warning = _select_slide_slug(
                lecture_id=lecture_id,
                slides_by_slug=slides_by_slug,
            )
            if warning:
                warnings.append(warning)
            if not selected_slide_slug:
                continue

            slide_html = slides_build_dir / selected_slide_slug / "index.html"
            if not slide_html.exists():
                warnings.append(f"[{lecture_id}] built slide page not found: {slide_html}")
                continue

            output_pdf = output_dir / f"{lecture_id}.pdf"
            # Use print view and suppress notes to keep only visible slide content.
            slide_url = f"{slides_base_url}/lecture-slides/{selected_slide_slug}/?print-pdf&showNotes=false"
            pdf_error = render_slide_pdf_with_playwright(
                repo_root=repo_root,
                slide_url=slide_url,
                output_pdf_path=output_pdf,
            )
            if pdf_error:
                warnings.append(f"[{lecture_id}] {pdf_error}")
                continue

            exported += 1

    return exported


def export_lectures(
    repo_root: Path,
    config_path: Path,
    lectures_dir: Path,
    slides_dir: Path,
    slides_build_dir: Path,
    output_dir: Path,
    known_html: Set[str],
    known_pdf: Set[str],
    skip_slide_pdfs: bool,
    verbose: bool,
) -> Dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    lecture_ids = load_lecture_ids(config_path)
    known_html, known_pdf = build_export_targets(known_html=known_html, known_pdf=known_pdf)

    warnings: List[str] = []
    mermaid_cache: Dict[str, Optional[str]] = {}
    exported_html = 0

    for index, lecture_id in enumerate(lecture_ids, start=1):
        output_html_path = output_dir / f"{lecture_id}.html"
        try:
            lecture_path = read_markdown_file(lectures_dir, lecture_id)
        except FileNotFoundError as err:
            warnings.append(str(err))
            if verbose:
                print(f"[{index}/{len(lecture_ids)}] Skipping {lecture_id}: source file not found")
            continue

        if verbose:
            print(f"[{index}/{len(lecture_ids)}] Creating {output_html_path} from {lecture_path}")

        export_markdown_document(
            repo_root=repo_root,
            output_dir=output_dir,
            document_id=lecture_id,
            source_path=lecture_path,
            known_html=known_html,
            known_pdf=known_pdf,
            warnings=warnings,
            mermaid_cache=mermaid_cache,
        )
        if verbose:
            print(f"[{index}/{len(lecture_ids)}] Done creating {output_html_path}; moving to next lecture")
        exported_html += 1

    exported_slide_pdfs = 0
    if not skip_slide_pdfs:
        exported_slide_pdfs = export_slide_pdfs(
            repo_root=repo_root,
            lecture_ids=lecture_ids,
            slides_dir=slides_dir,
            slides_build_dir=slides_build_dir,
            output_dir=output_dir,
            warnings=warnings,
        )

    print(f"Exported {exported_html}/{len(lecture_ids)} lecture notes to HTML in {output_dir}")
    if skip_slide_pdfs:
        print("Skipped slide PDF export (--skip-slide-pdfs)")
    else:
        print(f"Exported {exported_slide_pdfs}/{len(lecture_ids)} slide decks to PDF in {output_dir}")
    return {
        "exportedHtmlCount": exported_html,
        "requestedCount": len(lecture_ids),
        "lectureIds": lecture_ids,
        "slidePdfExportedCount": exported_slide_pdfs,
        "slidePdfRequestedCount": len(lecture_ids),
        "warnings": warnings,
    }


def export_pages(
    repo_root: Path,
    pages_dir: Path,
    output_dir: Path,
    known_html: Set[str],
    known_pdf: Set[str],
    verbose: bool,
) -> Dict[str, Any]:
    """Convert all .md files in pages_dir to HTML and write them to output_dir."""
    md_files = sorted(pages_dir.glob("*.md"))
    if not md_files:
        print("No markdown pages found to export")
        return {"exportedCount": 0, "requestedCount": 0, "pageIds": [], "warnings": []}

    output_dir.mkdir(parents=True, exist_ok=True)
    known_html, known_pdf = build_export_targets(known_html=known_html, known_pdf=known_pdf)
    warnings: List[str] = []
    mermaid_cache: Dict[str, Optional[str]] = {}
    exported = 0

    for index, md_path in enumerate(md_files, start=1):
        page_id = md_path.stem
        output_html_path = output_dir / f"{page_id}.html"

        if verbose:
            print(f"[{index}/{len(md_files)}] Creating {output_html_path} from {md_path}")

        export_markdown_document(
            repo_root=repo_root,
            output_dir=output_dir,
            document_id=page_id,
            source_path=md_path,
            known_html=known_html,
            known_pdf=known_pdf,
            warnings=warnings,
            mermaid_cache=mermaid_cache,
        )
        exported += 1

        if verbose:
            print(f"[{index}/{len(md_files)}] Done creating {output_html_path}; moving to next page")

    print(f"Exported {exported}/{len(md_files)} pages to HTML in {output_dir}")
    if warnings:
        print(f"Page export warnings: {len(warnings)}")
        for w in warnings:
            print(f"  {w}")
    return {
        "exportedCount": exported,
        "requestedCount": len(md_files),
        "pageIds": [md_path.stem for md_path in md_files],
        "warnings": warnings,
    }


def export_config_materials(
    repo_root: Path,
    config_path: Path,
    output_dir: Path,
    known_html: Set[str],
    known_pdf: Set[str],
    verbose: bool,
) -> Dict[str, Any]:
    material_items: List[Tuple[str, str]] = []
    known_html, known_pdf = build_export_targets(known_html=known_html, known_pdf=known_pdf)
    seen_urls: Set[str] = set()

    for section_name in ["assignments", "labs"]:
        for url in load_material_urls(config_path, section_name):
            if url in seen_urls:
                continue
            seen_urls.add(url)
            material_items.append((section_name, url))

    if not material_items:
        print("No assignments or labs found in course config to export")
        return {"exportedCount": 0, "requestedCount": 0, "items": [], "warnings": []}

    output_dir.mkdir(parents=True, exist_ok=True)
    warnings: List[str] = []
    mermaid_cache: Dict[str, Optional[str]] = {}
    exported = 0

    for index, (section_name, url) in enumerate(material_items, start=1):
        source_path = resolve_markdown_from_url(repo_root, url)
        stem = output_stem_from_url(url)

        if not source_path or not stem:
            warnings.append(f"[{section_name}] source markdown not found for {url}")
            if verbose:
                print(f"[{index}/{len(material_items)}] Skipping {url}: source markdown not found")
            continue

        output_html_path = output_dir / f"{stem}.html"
        if verbose:
            print(f"[{index}/{len(material_items)}] Creating {output_html_path} from {source_path}")

        export_markdown_document(
            repo_root=repo_root,
            output_dir=output_dir,
            document_id=stem,
            source_path=source_path,
            known_html=known_html,
            known_pdf=known_pdf,
            warnings=warnings,
            mermaid_cache=mermaid_cache,
        )
        exported += 1

        if verbose:
            print(f"[{index}/{len(material_items)}] Done creating {output_html_path}; moving to next material")

    print(f"Exported {exported}/{len(material_items)} assignments/labs to HTML in {output_dir}")
    if warnings:
        print(f"Material export warnings: {len(warnings)}")
        for warning in warnings:
            print(f"  {warning}")
    return {
        "exportedCount": exported,
        "requestedCount": len(material_items),
        "items": [
            {"section": section_name, "url": url, "stem": output_stem_from_url(url)}
            for section_name, url in material_items
        ],
        "warnings": warnings,
    }


def export_additional_linked_documents(
    repo_root: Path,
    output_dir: Path,
    additional_documents: Dict[str, Path],
    known_html: Set[str],
    known_pdf: Set[str],
    verbose: bool,
) -> Dict[str, Any]:
    if not additional_documents:
        return {"exportedCount": 0, "requestedCount": 0, "documentIds": [], "warnings": []}

    output_dir.mkdir(parents=True, exist_ok=True)
    warnings: List[str] = []
    mermaid_cache: Dict[str, Optional[str]] = {}
    exported = 0

    for index, (document_id, source_path) in enumerate(sorted(additional_documents.items()), start=1):
        output_html_path = output_dir / f"{document_id}.html"
        if verbose:
            print(f"[{index}/{len(additional_documents)}] Creating linked document {output_html_path} from {source_path}")

        export_markdown_document(
            repo_root=repo_root,
            output_dir=output_dir,
            document_id=document_id,
            source_path=source_path,
            known_html=known_html,
            known_pdf=known_pdf,
            warnings=warnings,
            mermaid_cache=mermaid_cache,
        )
        exported += 1

        if verbose:
            print(f"[{index}/{len(additional_documents)}] Done creating linked document {output_html_path}")

    print(f"Exported {exported}/{len(additional_documents)} linked supporting documents to HTML in {output_dir}")
    return {
        "exportedCount": exported,
        "requestedCount": len(additional_documents),
        "documentIds": sorted(additional_documents.keys()),
        "warnings": warnings,
    }


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    config_path = (repo_root / args.config).resolve()
    lectures_dir = (repo_root / args.lectures_dir).resolve()
    slides_dir = (repo_root / args.slides_dir).resolve()
    slides_build_dir = (repo_root / args.slides_build_dir).resolve()
    output_dir = (repo_root / args.output_dir).resolve()
    pages_dir = (repo_root / args.pages_dir).resolve()

    initial_documents = collect_initial_document_sources(
        repo_root=repo_root,
        config_path=config_path,
        lectures_dir=lectures_dir,
        pages_dir=pages_dir,
    )
    expanded_documents = expand_linked_document_sources(repo_root=repo_root, initial_documents=initial_documents)
    known_html = set(expanded_documents.keys())
    known_pdf = set(load_lecture_ids(config_path))

    if args.clean:
        if output_dir.exists():
            shutil.rmtree(output_dir)
            print(f"Cleaned build output directory: {output_dir}")
        else:
            print(f"Nothing to clean at: {output_dir}")
        return 0

    lecture_summary = export_lectures(
        repo_root=repo_root,
        config_path=config_path,
        lectures_dir=lectures_dir,
        slides_dir=slides_dir,
        slides_build_dir=slides_build_dir,
        output_dir=output_dir,
        known_html=known_html,
        known_pdf=known_pdf,
        skip_slide_pdfs=args.skip_slide_pdfs,
        verbose=args.verbose,
    )
    page_summary = export_pages(
        repo_root=repo_root,
        pages_dir=pages_dir,
        output_dir=output_dir,
        known_html=known_html,
        known_pdf=known_pdf,
        verbose=args.verbose,
    )
    material_summary = export_config_materials(
        repo_root=repo_root,
        config_path=config_path,
        output_dir=output_dir,
        known_html=known_html,
        known_pdf=known_pdf,
        verbose=args.verbose,
    )
    additional_documents = {
        document_id: source_path
        for document_id, source_path in expanded_documents.items()
        if document_id not in initial_documents
    }
    linked_document_summary = export_additional_linked_documents(
        repo_root=repo_root,
        output_dir=output_dir,
        additional_documents=additional_documents,
        known_html=known_html,
        known_pdf=known_pdf,
        verbose=args.verbose,
    )

    manifest = {
        "exportedLectureCount": lecture_summary["exportedHtmlCount"],
        "requestedLectureCount": lecture_summary["requestedCount"],
        "lectures": lecture_summary["lectureIds"],
        "slidePdfExportedCount": lecture_summary["slidePdfExportedCount"],
        "slidePdfRequestedCount": lecture_summary["slidePdfRequestedCount"],
        "pages": page_summary,
        "materials": material_summary,
        "linkedDocuments": linked_document_summary,
        "warnings": lecture_summary["warnings"] + page_summary["warnings"] + material_summary["warnings"] + linked_document_summary["warnings"],
    }
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    total_warnings = len(manifest["warnings"])
    if total_warnings:
        print(f"Warnings: {total_warnings} (see {manifest_path})")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
