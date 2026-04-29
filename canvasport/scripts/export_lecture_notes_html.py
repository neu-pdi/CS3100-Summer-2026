#!/usr/bin/env python3
"""
Stage 1 exporter for lecture notes.

Reads lecture IDs from course.config.json, converts lecture markdown files to HTML,
exports lecture slide decks to PDF,
and copies linked assets into:
  canvasport/build/files/<lecture-note-name>/img
  canvasport/build/files/<lecture-note-name>/code

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
from typing import Dict, List, Optional, Set, Tuple

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
    parser = argparse.ArgumentParser(description="Export lecture markdown to HTML for Canvas staging.")
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
    parser.add_argument("--clean", action="store_true", help="Delete output directory before generation")
    parser.add_argument("--skip-slide-pdfs", action="store_true", help="Skip slide PDF export")
    parser.add_argument("--verbose", action="store_true", help="Print per-file progress while exporting")
    return parser.parse_args()


def strip_front_matter(text: str) -> tuple:
    """Return (body_without_frontmatter, title_or_None)."""
    if not text.startswith("---\n"):
        return text, None
    closing = text.find("\n---\n", 4)
    if closing == -1:
        return text, None
    front = text[4:closing]
    body = text[closing + 5 :]
    title = None
    for line in front.splitlines():
        m = re.match(r'^title:\s*(.+)$', line)
        if m:
            title = m.group(1).strip().strip('"\'')
            break
    return body, title


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
    return (
        body_object.encode(formatter='html').decode()
        .replace('│', '&#x2502;')
        .replace('┼', '&#x253c;')
        .replace('└', '&boxur;')
        .replace('┴', '&boxhu;')
        .replace('┘', '&boxul;')
    )


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
    clean: bool,
    skip_slide_pdfs: bool,
    verbose: bool,
) -> int:
    if clean and output_dir.exists():
        shutil.rmtree(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)
    lecture_ids = load_lecture_ids(config_path)

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

        markdown_text = lecture_path.read_text(encoding="utf-8")
        markdown_text, fm_title = strip_front_matter(markdown_text)
        if fm_title:
            markdown_text = f"# {fm_title}\n\n" + markdown_text
        markdown_text = strip_mdx_only_lines(markdown_text)

        markdown_text = inline_mermaid_svgs(
            markdown_text=markdown_text,
            lecture_id=lecture_id,
            warnings=warnings,
            mermaid_cache=mermaid_cache,
        )

        markdown_text, asset_warnings = copy_and_rewrite_assets(repo_root, output_dir, lecture_id, markdown_text)
        warnings.extend(asset_warnings)

        html = markdown_to_html(markdown_text)
        output_html_path.write_text(html, encoding="utf-8")
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

    manifest = {
        "exportedLectureCount": exported_html,
        "requestedLectureCount": len(lecture_ids),
        "lectures": lecture_ids,
        "slidePdfExportedCount": exported_slide_pdfs,
        "slidePdfRequestedCount": len(lecture_ids),
        "warnings": warnings,
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"Exported {exported_html}/{len(lecture_ids)} lecture notes to HTML in {output_dir}")
    if skip_slide_pdfs:
        print("Skipped slide PDF export (--skip-slide-pdfs)")
    else:
        print(f"Exported {exported_slide_pdfs}/{len(lecture_ids)} slide decks to PDF in {output_dir}")
    if warnings:
        print(f"Warnings: {len(warnings)} (see {output_dir / 'manifest.json'})")

    return 0


def export_pages(
    repo_root: Path,
    pages_dir: Path,
    output_dir: Path,
    verbose: bool,
) -> int:
    """Convert all .md files in pages_dir to HTML and write them to output_dir."""
    md_files = sorted(pages_dir.glob("*.md"))
    if not md_files:
        print("No markdown pages found to export")
        return 0

    output_dir.mkdir(parents=True, exist_ok=True)
    warnings: List[str] = []
    mermaid_cache: Dict[str, Optional[str]] = {}
    exported = 0

    for index, md_path in enumerate(md_files, start=1):
        page_id = md_path.stem
        output_html_path = output_dir / f"{page_id}.html"

        if verbose:
            print(f"[{index}/{len(md_files)}] Creating {output_html_path} from {md_path}")

        markdown_text = md_path.read_text(encoding="utf-8")
        markdown_text, fm_title = strip_front_matter(markdown_text)
        if fm_title:
            markdown_text = f"# {fm_title}\n\n" + markdown_text
        markdown_text = strip_mdx_only_lines(markdown_text)

        markdown_text = inline_mermaid_svgs(
            markdown_text=markdown_text,
            lecture_id=page_id,
            warnings=warnings,
            mermaid_cache=mermaid_cache,
        )

        markdown_text, asset_warnings = copy_and_rewrite_assets(repo_root, output_dir, page_id, markdown_text)
        warnings.extend(asset_warnings)

        html = markdown_to_html(markdown_text)
        output_html_path.write_text(html, encoding="utf-8")
        exported += 1

        if verbose:
            print(f"[{index}/{len(md_files)}] Done creating {output_html_path}; moving to next page")

    print(f"Exported {exported}/{len(md_files)} pages to HTML in {output_dir}")
    if warnings:
        print(f"Page export warnings: {len(warnings)}")
        for w in warnings:
            print(f"  {w}")
    return 0


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    config_path = (repo_root / args.config).resolve()
    lectures_dir = (repo_root / args.lectures_dir).resolve()
    slides_dir = (repo_root / args.slides_dir).resolve()
    slides_build_dir = (repo_root / args.slides_build_dir).resolve()
    output_dir = (repo_root / args.output_dir).resolve()
    pages_dir = (repo_root / args.pages_dir).resolve()

    rc = export_lectures(
        repo_root=repo_root,
        config_path=config_path,
        lectures_dir=lectures_dir,
        slides_dir=slides_dir,
        slides_build_dir=slides_build_dir,
        output_dir=output_dir,
        clean=args.clean,
        skip_slide_pdfs=args.skip_slide_pdfs,
        verbose=args.verbose,
    )
    if rc != 0:
        return rc

    return export_pages(
        repo_root=repo_root,
        pages_dir=pages_dir,
        output_dir=output_dir,
        verbose=args.verbose,
    )


if __name__ == "__main__":
    raise SystemExit(main())
