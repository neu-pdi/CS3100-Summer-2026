#!/usr/bin/env python3
"""
Upload generated artifacts from canvasport/build to Canvas and publish content.

This script:
- uploads all files from canvasport/build to Canvas course files
- creates/updates Canvas pages from lecture HTML files
- updates Canvas syllabus from syllabus HTML

It preserves relative folder structure on Canvas using parent_folder_path.
"""

from __future__ import annotations

import argparse
from datetime import datetime
from html import escape
import json
import mimetypes
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import quote, urlsplit

import markdown
import pytz
import requests

# ============================================================================
# REQUIRED CONFIGURATION (PASTE VALUES HERE BEFORE RUNNING)
# ============================================================================
CANVAS_BASE_URL = "https://northeastern.instructure.com"
COURSE_ID = "252474"
API_ACCESS_TOKEN = "14523~JMvnhAPLWu7LFUPFTEAPuFy8AZJ9FWMKHx3TMZxyhmkW9cEMGfPeLrmtKX9aVXLN"
# ============================================================================

DEFAULT_BUILD_DIR = "canvasport/build"
DEFAULT_TARGET_ROOT_FOLDER = "canvasport"
DEFAULT_COURSE_CONFIG = "course.config.json"


class CanvasUploadError(RuntimeError):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Upload canvasport/build artifacts to Canvas course files.")
    script_path = Path(__file__).resolve()
    repo_root_default = script_path.parents[2]

    parser.add_argument("--repo-root", default=str(repo_root_default), help="Repository root path")
    parser.add_argument("--build-dir", default=DEFAULT_BUILD_DIR, help="Build folder relative to repo root")
    parser.add_argument("--config", default=DEFAULT_COURSE_CONFIG, help="Course config path relative to repo root")
    parser.add_argument(
        "--target-root-folder",
        default=DEFAULT_TARGET_ROOT_FOLDER,
        help="Top-level folder path to create/use in Canvas course files",
    )
    parser.add_argument("--dry-run", action="store_true", help="Show what would upload without uploading")
    parser.add_argument("--verbose", action="store_true", help="Print per-file progress while uploading")
    parser.add_argument("--timeout", type=int, default=60, help="HTTP timeout seconds")
    return parser.parse_args()


def require_config() -> Tuple[str, str, str]:
    base = CANVAS_BASE_URL.strip().rstrip("/")
    course_id = str(COURSE_ID).strip()
    token = API_ACCESS_TOKEN.strip()

    if not base:
        raise CanvasUploadError("CANVAS_BASE_URL is empty.")
    if not course_id:
        raise CanvasUploadError("COURSE_ID is empty.")
    if not token:
        raise CanvasUploadError("API_ACCESS_TOKEN is empty.")

    return base, course_id, token


def ensure_api_base(base_url: str) -> str:
    if base_url.endswith("/api/v1"):
        return base_url
    return f"{base_url}/api/v1"


def gather_files(build_dir: Path) -> List[Path]:
    if not build_dir.exists() or not build_dir.is_dir():
        raise CanvasUploadError(f"Build directory not found: {build_dir}")

    files = sorted([p for p in build_dir.rglob("*") if p.is_file()])
    if not files:
        raise CanvasUploadError(f"No files found under build directory: {build_dir}")
    return files


def load_lecture_metadata(config_path: Path) -> List[Dict[str, str]]:
    if not config_path.exists():
        raise CanvasUploadError(f"Course config not found: {config_path}")

    raw = json.loads(config_path.read_text(encoding="utf-8"))
    lectures = raw.get("lectures", [])
    metadata: List[Dict[str, str]] = []
    for lecture in lectures:
        lecture_id = str(lecture.get("lectureId", "")).strip()
        if not lecture_id:
            continue
        topics = lecture.get("topics") or []
        lecture_name = lecture_id
        if isinstance(topics, list) and topics:
            first_topic = str(topics[0]).strip()
            if first_topic:
                lecture_name = first_topic
        metadata.append({"lectureId": lecture_id, "lectureName": lecture_name})
    return metadata


def ensure_syllabus_html(repo_root: Path, build_dir: Path) -> Optional[Path]:
    syllabus_md = repo_root / "src/pages/syllabus.md"
    syllabus_html = build_dir / "syllabus.html"

    if not syllabus_md.exists():
        return None

    source = syllabus_md.read_text(encoding="utf-8")
    body = markdown.markdown(
        source,
        extensions=["fenced_code", "codehilite", "tables", "toc", "sane_lists"],
        extension_configs={
            "codehilite": {"noclasses": True, "pygments_style": "a11y-light"},
            "toc": {"baselevel": 2},
        },
    )

    html = (
        "<!DOCTYPE html>\n"
        "<html lang=\"en\">\n"
        "<head>\n"
        "  <meta charset=\"UTF-8\">\n"
        "  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n"
        "  <title>Syllabus</title>\n"
        "</head>\n"
        "<body>\n"
        f"{body}\n"
        "</body>\n"
        "</html>\n"
    )

    syllabus_html.write_text(html, encoding="utf-8")
    return syllabus_html


def relative_canvas_folder(target_root_folder: str, rel_path: Path) -> str:
    parent = rel_path.parent.as_posix().strip(".")
    if parent in ("", "."):
        return target_root_folder.strip("/")
    return f"{target_root_folder.strip('/')}/{parent.strip('/')}"


def content_type_for(path: Path) -> str:
    guessed, _ = mimetypes.guess_type(str(path))
    return guessed or "application/octet-stream"


def canvas_request(
    method: str,
    url: str,
    token: str,
    timeout: int,
    **kwargs,
) -> requests.Response:
    headers = kwargs.pop("headers", {})
    headers["Authorization"] = f"Bearer {token}"
    response = requests.request(method, url, headers=headers, timeout=timeout, **kwargs)
    return response


def initialize_file_upload(
    api_base: str,
    token: str,
    course_id: str,
    canvas_folder: str,
    file_path: Path,
    timeout: int,
) -> Dict:
    url = f"{api_base}/courses/{course_id}/files"
    payload = {
        "name": file_path.name,
        "size": file_path.stat().st_size,
        "content_type": content_type_for(file_path),
        "parent_folder_path": canvas_folder,
        "on_duplicate": "overwrite",
    }

    response = canvas_request("POST", url, token, timeout, data=payload)
    if response.status_code >= 400:
        raise CanvasUploadError(
            f"Failed to initialize upload for {file_path}: {response.status_code} {response.text}"
        )

    data = response.json()
    if "upload_url" not in data or "upload_params" not in data:
        raise CanvasUploadError(f"Upload init response missing upload_url/upload_params for {file_path}")
    return data


def finalize_upload(upload_url: str, upload_params: Dict, file_path: Path, timeout: int) -> Dict:
    with file_path.open("rb") as f:
        files = {"file": (file_path.name, f, content_type_for(file_path))}
        response = requests.post(upload_url, data=upload_params, files=files, timeout=timeout, allow_redirects=True)

    if response.status_code >= 400:
        raise CanvasUploadError(
            f"Failed to upload {file_path.name}: {response.status_code} {response.text}"
        )

    # Canvas may return JSON directly or redirect to a file object endpoint.
    try:
        return response.json()
    except ValueError:
        # Some Canvas deployments return non-JSON on final step; treat as success if 2xx.
        return {"status": "uploaded"}


def upload_file(
    api_base: str,
    token: str,
    course_id: str,
    canvas_folder: str,
    file_path: Path,
    timeout: int,
) -> Dict:
    init_data = initialize_file_upload(api_base, token, course_id, canvas_folder, file_path, timeout)
    return finalize_upload(init_data["upload_url"], init_data["upload_params"], file_path, timeout)


def build_uploaded_file_url_map(uploaded_records: List[Dict]) -> Dict[str, str]:
    mapping: Dict[str, str] = {}
    for record in uploaded_records:
        rel = record.get("relativePath")
        result = record.get("result", {})
        url = result.get("url")
        if rel and url:
            mapping[rel] = url
    return mapping


def rewrite_file_links_for_canvas(html_text: str, file_url_map: Dict[str, str]) -> str:
    rewritten = html_text

    # Replace links like src="files/..." or href="files/..."
    pattern = re.compile(r'(src|href)="(files/[^"]+)"')

    def replace_attr(match: re.Match) -> str:
        attr = match.group(1)
        rel = match.group(2)
        url = file_url_map.get(rel)
        if not url:
            return match.group(0)
        return f'{attr}="{url}"'

    rewritten = pattern.sub(replace_attr, rewritten)
    return rewritten


def is_external_or_special_href(href: str) -> bool:
    lowered = href.lower().strip()
    return (
        lowered.startswith("http://")
        or lowered.startswith("https://")
        or lowered.startswith("mailto:")
        or lowered.startswith("tel:")
        or lowered.startswith("#")
        or lowered.startswith("javascript:")
    )


def _normalize_internal_path(path: str) -> str:
    normalized = path.strip()
    if not normalized:
        return normalized
    normalized = normalized.replace("\\", "/")
    if not normalized.startswith("/"):
        normalized = "/" + normalized
    if normalized.endswith("/") and normalized != "/":
        normalized = normalized.rstrip("/")
    return normalized


def _strip_known_doc_extensions(path: str) -> str:
    lowered = path.lower()
    if lowered.endswith(".md") or lowered.endswith(".mdx") or lowered.endswith(".html"):
        return path.rsplit(".", 1)[0]
    return path


def _slug_from_path(path: str) -> str:
    return path.rstrip("/").split("/")[-1]


def rewrite_internal_links_for_canvas(
    html_text: str,
    route_url_map: Dict[str, str],
    slug_url_map: Dict[str, str],
    unresolved_links: Optional[List[Dict[str, str]]],
    source_slug: str,
) -> str:
    pattern = re.compile(r'href="([^"]+)"')

    def replace_attr(match: re.Match) -> str:
        href = match.group(1)
        if is_external_or_special_href(href):
            return match.group(0)

        split = urlsplit(href)
        raw_path = split.path or ""
        if not raw_path:
            return match.group(0)

        # Uploaded file assets are handled in rewrite_file_links_for_canvas.
        if raw_path.startswith("files/"):
            return match.group(0)

        candidates: List[str] = []

        normalized = _normalize_internal_path(raw_path)
        if normalized:
            candidates.append(normalized)
            stripped = _strip_known_doc_extensions(normalized)
            if stripped != normalized:
                candidates.append(stripped)

        for candidate in candidates:
            replacement_base = route_url_map.get(candidate)
            if replacement_base:
                rewritten = replacement_base
                if split.query:
                    rewritten += f"?{split.query}"
                if split.fragment:
                    rewritten += f"#{split.fragment}"
                return f'href="{rewritten}"'

        # Fallback: map by slug for relative links like ./l17-creation-patterns.md.
        slug_candidates = [_slug_from_path(c) for c in candidates if c and c != "/"]
        for slug in slug_candidates:
            replacement_base = slug_url_map.get(slug)
            if replacement_base:
                rewritten = replacement_base
                if split.query:
                    rewritten += f"?{split.query}"
                if split.fragment:
                    rewritten += f"#{split.fragment}"
                return f'href="{rewritten}"'

        if unresolved_links is not None:
            unresolved_links.append({"source": source_slug, "href": href})
        return match.group(0)

    return pattern.sub(replace_attr, html_text)


def rewrite_math_for_canvas(html_text: str, canvas_base_url: str) -> str:
    """Convert <math>...</math> tags to Canvas equation image markup."""

    base = canvas_base_url.strip().rstrip("/")
    pattern = re.compile(r"<math>(.*?)</math>", flags=re.IGNORECASE | re.DOTALL)

    def replace_math(match: re.Match) -> str:
        latex = match.group(1).strip()
        if not latex:
            return ""

        # Canvas expects the equation path segment to be URL-encoded twice.
        encoded_once = quote(latex, safe="")
        encoded_twice = quote(encoded_once, safe="")
        escaped_latex = escape(latex, quote=True)
        return (
            f'<img class="equation_image" '
            f'title="{escaped_latex}" '
            f'src="{base}/equation_images/{encoded_twice}" '
            f'alt="LaTeX: {escaped_latex}" '
            f'data-equation-content="{escaped_latex}" />'
        )

    return pattern.sub(replace_math, html_text)


def lecture_title_from_html(html_text: str, fallback: str) -> str:
    match = re.search(r"<h[1-6][^>]*>(.*?)</h[1-6]>", html_text, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return fallback
    stripped = re.sub(r"<[^>]+>", "", match.group(1)).strip()
    return stripped or fallback


def find_canvas_page_url_by_title(
    api_base: str,
    token: str,
    course_id: str,
    page_title: str,
    timeout: int,
) -> Optional[str]:
    """Return Canvas page URL slug for an exact title match, or None."""
    list_url = f"{api_base}/courses/{course_id}/pages"
    response = canvas_request(
        "GET",
        list_url,
        token,
        timeout,
        params={"search_term": page_title, "per_page": 100},
    )
    if response.status_code >= 400:
        raise CanvasUploadError(
            f"Failed page search for title '{page_title}': {response.status_code} {response.text}"
        )

    pages = response.json()
    wanted = page_title.strip().casefold()
    for page in pages:
        title = str(page.get("title", "")).strip().casefold()
        page_url = page.get("url")
        if title == wanted and page_url:
            return str(page_url)
    return None


def upsert_canvas_page(
    api_base: str,
    token: str,
    course_id: str,
    page_slug: str,
    page_title: str,
    page_body: str,
    timeout: int,
) -> Dict[str, str]:
    get_url = f"{api_base}/courses/{course_id}/pages/{page_slug}"
    get_response = canvas_request("GET", get_url, token, timeout)

    payload = {
        "wiki_page[title]": page_title,
        "wiki_page[body]": page_body,
        "wiki_page[published]": "true",
    }

    if get_response.status_code == 200:
        put_response = canvas_request("PUT", get_url, token, timeout, data=payload)
        if put_response.status_code >= 400:
            raise CanvasUploadError(
                f"Failed to update page {page_slug}: {put_response.status_code} {put_response.text}"
            )
        page_url = str(put_response.json().get("url") or page_slug)
        return {"status": "updated", "pageUrl": page_url}

    if get_response.status_code not in (404,):
        raise CanvasUploadError(
            f"Failed page lookup for {page_slug}: {get_response.status_code} {get_response.text}"
        )

    # If slug lookup misses, update an existing page with the same title
    # to avoid creating duplicate pages.
    existing_url = find_canvas_page_url_by_title(
        api_base=api_base,
        token=token,
        course_id=course_id,
        page_title=page_title,
        timeout=timeout,
    )
    if existing_url:
        put_by_title_url = f"{api_base}/courses/{course_id}/pages/{existing_url}"
        put_response = canvas_request("PUT", put_by_title_url, token, timeout, data=payload)
        if put_response.status_code >= 400:
            raise CanvasUploadError(
                f"Failed to update page '{page_title}' at {existing_url}: "
                f"{put_response.status_code} {put_response.text}"
            )
        page_url = str(put_response.json().get("url") or existing_url)
        return {"status": "updated", "pageUrl": page_url}

    post_url = f"{api_base}/courses/{course_id}/pages"
    create_response = canvas_request("POST", post_url, token, timeout, data=payload)
    if create_response.status_code >= 400:
        raise CanvasUploadError(
            f"Failed to create page {page_slug}: {create_response.status_code} {create_response.text}"
        )
    page_url = str(create_response.json().get("url") or page_slug)
    return {"status": "created", "pageUrl": page_url}


def publish_lecture_pages(
    api_base: str,
    token: str,
    course_id: str,
    build_dir: Path,
    file_url_map: Dict[str, str],
    route_url_map: Dict[str, str],
    slug_url_map: Dict[str, str],
    unresolved_links: Optional[List[Dict[str, str]]],
    timeout: int,
    dry_run: bool,
) -> Dict[str, Any]:
    created = 0
    updated = 0
    skipped = 0
    lecture_pages: Dict[str, Dict[str, str]] = {}

    lecture_html_files = sorted(
        p for p in build_dir.glob("*.html") if p.name not in {"syllabus.html"}
    )

    for html_file in lecture_html_files:
        slug = html_file.stem
        html_text = html_file.read_text(encoding="utf-8")
        html_text = rewrite_file_links_for_canvas(html_text, file_url_map)
        html_text = rewrite_internal_links_for_canvas(
            html_text=html_text,
            route_url_map=route_url_map,
            slug_url_map=slug_url_map,
            unresolved_links=unresolved_links,
            source_slug=slug,
        )
        html_text = rewrite_math_for_canvas(html_text, canvas_base_url=CANVAS_BASE_URL)
        title = lecture_title_from_html(html_text, fallback=slug)
        lecture_pages[slug] = {"title": title, "pageUrl": slug}

        if dry_run:
            print(f"[DRY RUN] Page {slug} ({title})")
            skipped += 1
            continue

        result = upsert_canvas_page(
            api_base=api_base,
            token=token,
            course_id=course_id,
            page_slug=slug,
            page_title=title,
            page_body=html_text,
            timeout=timeout,
        )
        lecture_pages[slug]["pageUrl"] = result["pageUrl"]
        if result["status"] == "created":
            created += 1
            print(f"Page created: {slug}")
        else:
            updated += 1
            print(f"Page updated: {slug}")

    return {
        "created": created,
        "updated": updated,
        "dryRunSkipped": skipped,
        "lecturePages": lecture_pages,
    }


def rewrite_lecture_pages_after_mapping(
    api_base: str,
    token: str,
    course_id: str,
    build_dir: Path,
    file_url_map: Dict[str, str],
    route_url_map: Dict[str, str],
    slug_url_map: Dict[str, str],
    unresolved_links: Optional[List[Dict[str, str]]],
    timeout: int,
    dry_run: bool,
) -> Dict[str, int]:
    updated = 0
    skipped = 0

    lecture_html_files = sorted(
        p for p in build_dir.glob("*.html") if p.name not in {"syllabus.html"}
    )

    for html_file in lecture_html_files:
        slug = html_file.stem
        html_text = html_file.read_text(encoding="utf-8")
        html_text = rewrite_file_links_for_canvas(html_text, file_url_map)
        html_text = rewrite_internal_links_for_canvas(
            html_text=html_text,
            route_url_map=route_url_map,
            slug_url_map=slug_url_map,
            unresolved_links=unresolved_links,
            source_slug=slug,
        )
        html_text = rewrite_math_for_canvas(html_text, canvas_base_url=CANVAS_BASE_URL)
        title = lecture_title_from_html(html_text, fallback=slug)

        if dry_run:
            print(f"[DRY RUN] Rewrite links in page {slug}")
            skipped += 1
            continue

        result = upsert_canvas_page(
            api_base=api_base,
            token=token,
            course_id=course_id,
            page_slug=slug,
            page_title=title,
            page_body=html_text,
            timeout=timeout,
        )
        if result["status"] in {"updated", "created"}:
            updated += 1

    return {"updated": updated, "dryRunSkipped": skipped}


def list_canvas_modules(
    api_base: str,
    token: str,
    course_id: str,
    timeout: int,
) -> List[Dict[str, Any]]:
    url = f"{api_base}/courses/{course_id}/modules"
    response = canvas_request("GET", url, token, timeout, params={"per_page": 100})
    if response.status_code >= 400:
        raise CanvasUploadError(f"Failed to list modules: {response.status_code} {response.text}")
    return response.json()


def delete_canvas_module(
    api_base: str,
    token: str,
    course_id: str,
    module_id: int,
    timeout: int,
) -> None:
    url = f"{api_base}/courses/{course_id}/modules/{module_id}"
    response = canvas_request("DELETE", url, token, timeout)
    if response.status_code >= 400:
        raise CanvasUploadError(
            f"Failed to delete module {module_id}: {response.status_code} {response.text}"
        )


def create_canvas_module(
    api_base: str,
    token: str,
    course_id: str,
    module_name: str,
    timeout: int,
) -> Dict[str, Any]:
    url = f"{api_base}/courses/{course_id}/modules"
    payload = {
        "module[name]": module_name,
        "module[published]": "true",
    }
    response = canvas_request("POST", url, token, timeout, data=payload)
    if response.status_code >= 400:
        raise CanvasUploadError(
            f"Failed to create module '{module_name}': {response.status_code} {response.text}"
        )

    module = response.json()
    module_id = module.get("id")
    if not module_id:
        return module

    # Canvas appears to ignore module[published] on create for some deployments,
    # so publish explicitly after the module exists.
    publish_url = f"{api_base}/courses/{course_id}/modules/{module_id}"
    publish_response = canvas_request(
        "PUT",
        publish_url,
        token,
        timeout,
        data={"module[published]": "true"},
    )
    if publish_response.status_code >= 400:
        raise CanvasUploadError(
            f"Failed to publish module '{module_name}' ({module_id}): "
            f"{publish_response.status_code} {publish_response.text}"
        )
    return publish_response.json()


def list_canvas_module_items(
    api_base: str,
    token: str,
    course_id: str,
    module_id: int,
    timeout: int,
) -> List[Dict[str, Any]]:
    url = f"{api_base}/courses/{course_id}/modules/{module_id}/items"
    response = canvas_request("GET", url, token, timeout, params={"per_page": 100})
    if response.status_code >= 400:
        raise CanvasUploadError(
            f"Failed to list module items for module {module_id}: {response.status_code} {response.text}"
        )
    return response.json()


def create_canvas_module_item(
    api_base: str,
    token: str,
    course_id: str,
    module_id: int,
    payload: Dict[str, str],
    timeout: int,
) -> Dict[str, Any]:
    url = f"{api_base}/courses/{course_id}/modules/{module_id}/items"
    response = canvas_request("POST", url, token, timeout, data=payload)
    if response.status_code >= 400:
        raise CanvasUploadError(
            f"Failed to create module item in module {module_id}: {response.status_code} {response.text}"
        )
    return response.json()


def publish_lecture_modules(
    api_base: str,
    token: str,
    course_id: str,
    lecture_metadata: List[Dict[str, str]],
    lecture_pages: Dict[str, Dict[str, str]],
    file_url_map: Dict[str, str],
    timeout: int,
    dry_run: bool,
) -> Dict[str, int]:
    modules_created = 0
    modules_reused = 0
    items_created = 0
    dry_run_skipped = 0

    existing_modules = list_canvas_modules(api_base=api_base, token=token, course_id=course_id, timeout=timeout)
    if dry_run:
        for m in existing_modules:
            print(f"[DRY RUN] Would delete module: {m.get('name')} (id={m.get('id')})")
    else:
        for m in existing_modules:
            delete_canvas_module(
                api_base=api_base,
                token=token,
                course_id=course_id,
                module_id=int(m["id"]),
                timeout=timeout,
            )
            print(f"Module deleted: {m.get('name')} (id={m.get('id')})")

    if dry_run:
        for lecture in lecture_metadata:
            lecture_id = lecture["lectureId"]
            module_name = lecture_pages.get(lecture_id, {}).get("title") or lecture["lectureName"]
            print(f"[DRY RUN] Module {module_name} for {lecture_id}")
            dry_run_skipped += 1

            if lecture_id in lecture_pages:
                print(f"[DRY RUN] Module item (Page): {lecture_id}")
                dry_run_skipped += 1

            slides_url = file_url_map.get(f"{lecture_id}.pdf")
            if slides_url:
                print(f"[DRY RUN] Module item (Slides): {lecture_id}.pdf")
                dry_run_skipped += 1

        return {
            "modulesCreated": modules_created,
            "modulesReused": modules_reused,
            "itemsCreated": items_created,
            "dryRunSkipped": dry_run_skipped,
        }

    module_by_name: Dict[str, Dict[str, Any]] = {}

    for lecture in lecture_metadata:
        lecture_id = lecture["lectureId"]
        module_name = lecture_pages.get(lecture_id, {}).get("title") or lecture["lectureName"]
        module_key = module_name.strip().casefold()

        module = module_by_name.get(module_key)
        if module is None:
            module = create_canvas_module(
                api_base=api_base,
                token=token,
                course_id=course_id,
                module_name=module_name,
                timeout=timeout,
            )
            module_by_name[module_key] = module
            modules_created += 1
            print(f"Module created: {module_name}")
        else:
            modules_reused += 1

        module_id = int(module["id"])
        module_items = list_canvas_module_items(
            api_base=api_base,
            token=token,
            course_id=course_id,
            module_id=module_id,
            timeout=timeout,
        )

        page_info = lecture_pages.get(lecture_id)
        if page_info:
            page_url = page_info["pageUrl"]
            page_item_exists = any(
                str(item.get("type", "")) == "Page" and str(item.get("page_url", "")) == page_url
                for item in module_items
            )
            if not page_item_exists:
                create_canvas_module_item(
                    api_base=api_base,
                    token=token,
                    course_id=course_id,
                    module_id=module_id,
                    timeout=timeout,
                    payload={
                        "module_item[type]": "Page",
                        "module_item[title]": "Lecture Notes",
                        "module_item[page_url]": page_url,
                        "module_item[published]": "true",
                    },
                )
                items_created += 1
                print(f"Module item created (Page): {module_name} -> {page_url}")

        slides_url = file_url_map.get(f"{lecture_id}.pdf")
        if slides_url:
            slide_item_exists = any(
                str(item.get("type", "")) == "ExternalUrl"
                and str(item.get("external_url", "")) == slides_url
                for item in module_items
            )
            if not slide_item_exists:
                create_canvas_module_item(
                    api_base=api_base,
                    token=token,
                    course_id=course_id,
                    module_id=module_id,
                    timeout=timeout,
                    payload={
                        "module_item[type]": "ExternalUrl",
                        "module_item[title]": "Slides",
                        "module_item[external_url]": slides_url,
                        "module_item[new_tab]": "true",
                        "module_item[published]": "true",
                    },
                )
                items_created += 1
                print(f"Module item created (Slides): {module_name} -> {lecture_id}.pdf")

    return {
        "modulesCreated": modules_created,
        "modulesReused": modules_reused,
        "itemsCreated": items_created,
        "dryRunSkipped": dry_run_skipped,
    }


def publish_syllabus(
    api_base: str,
    token: str,
    course_id: str,
    build_dir: Path,
    file_url_map: Dict[str, str],
    route_url_map: Dict[str, str],
    slug_url_map: Dict[str, str],
    unresolved_links: Optional[List[Dict[str, str]]],
    timeout: int,
    dry_run: bool,
) -> str:
    syllabus_html = build_dir / "syllabus.html"
    if not syllabus_html.exists():
        return "missing"

    html_text = syllabus_html.read_text(encoding="utf-8")
    html_text = rewrite_file_links_for_canvas(html_text, file_url_map)
    html_text = rewrite_internal_links_for_canvas(
        html_text=html_text,
        route_url_map=route_url_map,
        slug_url_map=slug_url_map,
        unresolved_links=unresolved_links,
        source_slug="syllabus",
    )
    html_text = rewrite_math_for_canvas(html_text, canvas_base_url=CANVAS_BASE_URL)

    if dry_run:
        print("[DRY RUN] Syllabus update")
        return "dry-run"

    url = f"{api_base}/courses/{course_id}"
    payload = {
        "course[syllabus_body]": html_text,
        "course[syllabus_course_summary]": "true",
    }
    response = canvas_request("PUT", url, token, timeout, data=payload)
    if response.status_code >= 400:
        raise CanvasUploadError(
            f"Failed to update syllabus: {response.status_code} {response.text}"
        )
    print("Syllabus updated")
    return "updated"


def parse_datetime_for_canvas(date_str: str, time_str: Optional[str], tz_name: str) -> str:
    """Convert date and optional time to ISO 8601 datetime string in UTC."""
    if time_str:
        dt_str = f"{date_str}T{time_str}:00"
    else:
        dt_str = f"{date_str}T00:00:00"
    
    tz = pytz.timezone(tz_name)
    local_dt = datetime.fromisoformat(dt_str)
    local_dt = tz.localize(local_dt)
    utc_dt = local_dt.astimezone(pytz.UTC)
    return utc_dt.isoformat()


def resolve_assigned_time(entry: Dict[str, Any]) -> str:
    """Return configured assignedTime or default release time of 18:00."""
    assigned_time = str(entry.get("assignedTime", "")).strip()
    return assigned_time or "18:00"


def load_assignments_and_labs(
    config_path: Path,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], str]:
    """Load assignments and labs from config, return both lists and course timezone."""
    if not config_path.exists():
        return [], [], "America/New_York"
    
    config = json.loads(config_path.read_text(encoding="utf-8"))
    assignments = config.get("assignments", [])
    labs = config.get("labs", [])
    timezone = config.get("timezone", "America/New_York")
    
    return assignments, labs, timezone


def list_canvas_assignments(
    api_base: str,
    token: str,
    course_id: str,
    timeout: int,
) -> Dict[str, Dict[str, Any]]:
    """List all assignments on Canvas course."""
    url = f"{api_base}/courses/{course_id}/assignments"
    response = canvas_request("GET", url, token, timeout, params={"per_page": 100})
    if response.status_code >= 400:
        raise CanvasUploadError(
            f"Failed to list assignments: {response.status_code} {response.text}"
        )
    
    assignments = response.json()
    result: Dict[str, Dict[str, Any]] = {}
    for assignment in assignments:
        title = str(assignment.get("name", "")).strip().casefold()
        if not title:
            continue
        existing = result.get(title)
        if existing is None:
            result[title] = assignment
            continue

        # Keep the newest assignment when duplicate titles already exist.
        existing_updated = str(existing.get("updated_at", ""))
        candidate_updated = str(assignment.get("updated_at", ""))
        if candidate_updated > existing_updated:
            result[title] = assignment
    return result


def create_or_update_assignment(
    api_base: str,
    token: str,
    course_id: str,
    assignment_id: str,
    title: str,
    points: int,
    release_at: str,
    due_at: str,
    published: bool,
    description: str = "",
    existing_canvas_assignment_id: Optional[str] = None,
    timeout: int = 60,
) -> Dict[str, Any]:
    """Create or update assignment on Canvas."""
    if existing_canvas_assignment_id:
        url = f"{api_base}/courses/{course_id}/assignments/{existing_canvas_assignment_id}"
        method = "PUT"
    else:
        url = f"{api_base}/courses/{course_id}/assignments"
        method = "POST"
    
    payload = {
        "assignment[name]": title,
        "assignment[points_possible]": points,
        "assignment[unlock_at]": release_at,
        "assignment[due_at]": due_at,
        "assignment[description]": description,
        "assignment[published]": "true" if published else "false",
    }
    
    response = canvas_request(method, url, token, timeout, data=payload)
    if response.status_code >= 400:
        action = "update" if existing_canvas_assignment_id else "create"
        raise CanvasUploadError(
            f"Failed to {action} assignment '{title}': {response.status_code} {response.text}"
        )
    return response.json()


def load_description_html(build_dir: Path, url: str) -> str:
    """Load exported HTML body for an assignment/lab from build_dir, given its config url."""
    stem = url.rstrip("/").split("/")[-1]
    html_path = build_dir / f"{stem}.html"
    if not html_path.exists():
        return ""
    return html_path.read_text(encoding="utf-8")


def canvas_course_page_url(course_base_url: str, course_id: str, page_url: str) -> str:
    return f"{course_base_url}/courses/{course_id}/pages/{page_url}".replace("//courses", "/courses")


def canvas_assignment_url(course_base_url: str, course_id: str, assignment_id: str) -> str:
    return f"{course_base_url}/courses/{course_id}/assignments/{assignment_id}".replace("//courses", "/courses")


def build_internal_link_maps(
    course_base_url: str,
    course_id: str,
    lecture_pages: Dict[str, Dict[str, str]],
    assignments_list: List[Dict[str, Any]],
    labs_list: List[Dict[str, Any]],
    file_url_map: Dict[str, str],
) -> Tuple[Dict[str, str], Dict[str, str]]:
    route_url_map: Dict[str, str] = {}
    slug_url_map: Dict[str, str] = {}

    for slug, info in lecture_pages.items():
        page_url = str(info.get("pageUrl") or slug).strip()
        if not page_url:
            continue
        target = canvas_course_page_url(course_base_url, course_id, page_url)
        route_url_map[f"/lecture-notes/{slug}"] = target
        route_url_map[f"/{slug}"] = target
        slug_url_map[slug] = target

    for assignment in assignments_list:
        assignment_id = str(assignment.get("id", "")).strip()
        route = str(assignment.get("url", "")).strip().rstrip("/")
        if not assignment_id or not route:
            continue
        target = canvas_assignment_url(course_base_url, course_id, assignment_id)
        route_url_map[route] = target
        slug_url_map[_slug_from_path(route)] = target

    for lab in labs_list:
        lab_id = str(lab.get("id", "")).strip()
        route = str(lab.get("url", "")).strip().rstrip("/")
        if not lab_id or not route:
            continue
        target = canvas_assignment_url(course_base_url, course_id, lab_id)
        route_url_map[route] = target
        slug_url_map[_slug_from_path(route)] = target

    for rel, file_url in file_url_map.items():
        if not rel.lower().endswith(".pdf"):
            continue
        slide_slug = Path(rel).stem
        route_url_map[f"/lecture-slides/{slide_slug}"] = file_url
        route_url_map[f"/lecture-slides/{slide_slug}.pdf"] = file_url

    return route_url_map, slug_url_map


def publish_assignments_and_labs(
    api_base: str,
    token: str,
    course_id: str,
    config_path: Path,
    build_dir: Path,
    file_url_map: Dict[str, str],
    route_url_map: Dict[str, str],
    slug_url_map: Dict[str, str],
    unresolved_links: Optional[List[Dict[str, str]]],
    timeout: int,
    dry_run: bool,
) -> Dict[str, Any]:
    """Publish assignments and labs to Canvas."""
    assignments_list, labs_list, timezone = load_assignments_and_labs(config_path)
    
    if not assignments_list and not labs_list:
        return {"created": 0, "updated": 0, "dryRunSkipped": 0, "failed": []}
    
    created = 0
    updated = 0
    skipped = 0
    failed = []

    existing_by_title: Dict[str, Dict[str, Any]] = {}
    if not dry_run:
        existing_by_title = list_canvas_assignments(
            api_base=api_base,
            token=token,
            course_id=course_id,
            timeout=timeout,
        )
    
    # Process assignments
    for assignment in assignments_list:
        assignment_id = assignment.get("id")
        title = assignment.get("title", "")
        points = assignment.get("points", 0)
        assigned_date = assignment.get("assignedDate")
        assigned_time = resolve_assigned_time(assignment)
        due_date = assignment.get("dueDate")
        due_time = assignment.get("dueTime", "23:59")
        status = assignment.get("status", "draft")
        is_published = status == "published"
        url = assignment.get("url", "")
        description = load_description_html(build_dir, url) if url else ""
        if description:
            description = rewrite_internal_links_for_canvas(
                html_text=description,
                route_url_map=route_url_map,
                slug_url_map=slug_url_map,
                unresolved_links=unresolved_links,
                source_slug=f"assignment:{assignment_id or 'unknown'}",
            )
            description = rewrite_file_links_for_canvas(description, file_url_map)
            description = rewrite_math_for_canvas(description, canvas_base_url=CANVAS_BASE_URL)
        
        if not assignment_id or not title or not assigned_date or not due_date:
            failed.append({"id": assignment_id, "title": title, "error": "missing required fields"})
            continue
        
        try:
            release_at = parse_datetime_for_canvas(assigned_date, assigned_time, timezone)
            due_at = parse_datetime_for_canvas(due_date, due_time, timezone)
            title_key = title.strip().casefold()
            existing = existing_by_title.get(title_key)
            existing_id = str(existing.get("id", "")).strip() if existing else None
            
            if dry_run:
                has_desc = "with description" if description else "no description"
                print(
                    f"[DRY RUN] Assignment: {title} "
                    f"(release: {assigned_date} {assigned_time}, due: {due_date} {due_time}, "
                    f"points: {points}, published: {is_published}, {has_desc})"
                )
                skipped += 1
            else:
                result = create_or_update_assignment(
                    api_base=api_base,
                    token=token,
                    course_id=course_id,
                    assignment_id=assignment_id,
                    title=title,
                    points=points,
                    release_at=release_at,
                    due_at=due_at,
                    published=is_published,
                    description=description,
                    existing_canvas_assignment_id=existing_id,
                    timeout=timeout,
                )
                if existing_id:
                    print(f"Assignment updated: {title}")
                    updated += 1
                else:
                    print(f"Assignment created: {title}")
                    created += 1
                existing_by_title[title_key] = result
        except Exception as exc:
            failed.append({"id": assignment_id, "title": title, "error": str(exc)})
            print(f"FAILED: Assignment {title}: {exc}")
    
    # Process labs
    for lab in labs_list:
        lab_id = lab.get("id")
        title = lab.get("title", "")
        dates = lab.get("dates", [])
        assigned_time = resolve_assigned_time(lab)
        status = lab.get("status", "draft")
        is_published = status == "published"
        points = 0
        url = lab.get("url", "")
        description = load_description_html(build_dir, url) if url else ""
        if description:
            description = rewrite_internal_links_for_canvas(
                html_text=description,
                route_url_map=route_url_map,
                slug_url_map=slug_url_map,
                unresolved_links=unresolved_links,
                source_slug=f"lab:{lab_id or 'unknown'}",
            )
            description = rewrite_file_links_for_canvas(description, file_url_map)
            description = rewrite_math_for_canvas(description, canvas_base_url=CANVAS_BASE_URL)
        
        if not lab_id or not title or not dates:
            failed.append({"id": lab_id, "title": title, "error": "missing required fields"})
            continue
        
        try:
            lab_date = dates[0]
            release_at = parse_datetime_for_canvas(lab_date, assigned_time, timezone)
            due_at = parse_datetime_for_canvas(lab_date, "23:59", timezone)
            title_key = title.strip().casefold()
            existing = existing_by_title.get(title_key)
            existing_id = str(existing.get("id", "")).strip() if existing else None
            
            if dry_run:
                has_desc = "with description" if description else "no description"
                print(
                    f"[DRY RUN] Lab: {title} "
                    f"(release: {lab_date} {assigned_time}, due: {lab_date} 23:59, "
                    f"published: {is_published}, {has_desc})"
                )
                skipped += 1
            else:
                result = create_or_update_assignment(
                    api_base=api_base,
                    token=token,
                    course_id=course_id,
                    assignment_id=lab_id,
                    title=title,
                    points=points,
                    release_at=release_at,
                    due_at=due_at,
                    published=is_published,
                    description=description,
                    existing_canvas_assignment_id=existing_id,
                    timeout=timeout,
                )
                if existing_id:
                    print(f"Lab updated: {title}")
                    updated += 1
                else:
                    print(f"Lab created: {title}")
                    created += 1
                existing_by_title[title_key] = result
        except Exception as exc:
            failed.append({"id": lab_id, "title": title, "error": str(exc)})
            print(f"FAILED: Lab {title}: {exc}")
    
    return {"created": created, "updated": updated, "dryRunSkipped": skipped, "failed": failed}


def main() -> int:
    args = parse_args()

    repo_root = Path(args.repo_root).resolve()
    build_dir = (repo_root / args.build_dir).resolve()
    config_path = (repo_root / args.config).resolve()

    lecture_metadata = load_lecture_metadata(config_path)

    ensure_syllabus_html(repo_root, build_dir)

    files_to_upload = gather_files(build_dir)

    if args.dry_run:
        base_url = CANVAS_BASE_URL.strip().rstrip("/") or "https://example.instructure.com"
        course_id = str(COURSE_ID).strip() or "DRY_RUN"
        token = API_ACCESS_TOKEN.strip() or "DRY_RUN"
    else:
        base_url, course_id, token = require_config()

    api_base = ensure_api_base(base_url)

    summary = {
        "courseId": course_id,
        "canvasBaseUrl": base_url,
        "buildDir": str(build_dir),
        "targetRootFolder": args.target_root_folder,
        "dryRun": bool(args.dry_run),
        "fileCount": len(files_to_upload),
        "uploaded": [],
        "failed": [],
        "pages": {"created": 0, "updated": 0, "dryRunSkipped": 0},
        "modules": {"modulesCreated": 0, "modulesReused": 0, "itemsCreated": 0, "dryRunSkipped": 0},
        "syllabus": "not-run",
        "assignmentsAndLabs": {"created": 0, "updated": 0, "dryRunSkipped": 0, "failed": []},
    }

    print(f"Preparing to process {len(files_to_upload)} file(s) from {build_dir}")
    if args.dry_run:
        print("Dry-run mode: no upload requests will be sent.")

    for index, file_path in enumerate(files_to_upload, start=1):
        rel_path = file_path.relative_to(build_dir)
        canvas_folder = relative_canvas_folder(args.target_root_folder, rel_path)
        rel_display = rel_path.as_posix()

        if args.verbose:
            print(f"[{index}/{len(files_to_upload)}] Uploading {rel_display} to folder {canvas_folder}")

        if args.dry_run:
            print(f"[DRY RUN] {rel_display} -> folder: {canvas_folder}")
            if args.verbose:
                print(f"[{index}/{len(files_to_upload)}] Done with {rel_display}; moving to next file")
            continue

        try:
            result = upload_file(
                api_base=api_base,
                token=token,
                course_id=course_id,
                canvas_folder=canvas_folder,
                file_path=file_path,
                timeout=args.timeout,
            )
            summary["uploaded"].append(
                {
                    "relativePath": rel_display,
                    "canvasFolder": canvas_folder,
                    "result": result,
                }
            )
            print(f"Uploaded: {rel_display} -> {canvas_folder}")
            if args.verbose:
                print(f"[{index}/{len(files_to_upload)}] Done with {rel_display}; moving to next file")
        except Exception as exc:
            summary["failed"].append(
                {
                    "relativePath": rel_display,
                    "canvasFolder": canvas_folder,
                    "error": str(exc),
                }
            )
            print(f"FAILED: {rel_display} -> {canvas_folder}: {exc}")
            if args.verbose:
                print(f"[{index}/{len(files_to_upload)}] Done with {rel_display}; moving to next file")

    file_url_map = build_uploaded_file_url_map(summary["uploaded"])
    lecture_pages: Dict[str, Dict[str, str]] = {}
    unresolved_internal_links: List[Dict[str, str]] = []

    assignments_list, labs_list, _timezone = load_assignments_and_labs(config_path)
    route_url_map: Dict[str, str] = {}
    slug_url_map: Dict[str, str] = {}

    try:
        page_results = publish_lecture_pages(
            api_base=api_base,
            token=token,
            course_id=course_id,
            build_dir=build_dir,
            file_url_map=file_url_map,
            route_url_map=route_url_map,
            slug_url_map=slug_url_map,
            unresolved_links=unresolved_internal_links,
            timeout=args.timeout,
            dry_run=args.dry_run,
        )
        lecture_pages = page_results.pop("lecturePages", {})
        summary["pages"] = page_results
    except Exception as exc:
        summary["failed"].append(
            {
                "relativePath": "[pages]",
                "canvasFolder": "n/a",
                "error": str(exc),
            }
        )
        print(f"FAILED: page publishing: {exc}")

    route_url_map, slug_url_map = build_internal_link_maps(
        course_base_url=base_url,
        course_id=course_id,
        lecture_pages=lecture_pages,
        assignments_list=assignments_list,
        labs_list=labs_list,
        file_url_map=file_url_map,
    )

    try:
        link_rewrite_result = rewrite_lecture_pages_after_mapping(
            api_base=api_base,
            token=token,
            course_id=course_id,
            build_dir=build_dir,
            file_url_map=file_url_map,
            route_url_map=route_url_map,
            slug_url_map=slug_url_map,
            unresolved_links=unresolved_internal_links,
            timeout=args.timeout,
            dry_run=args.dry_run,
        )
        summary["internalLinkRewrite"] = link_rewrite_result
    except Exception as exc:
        summary["failed"].append(
            {
                "relativePath": "[internalLinkRewrite]",
                "canvasFolder": "n/a",
                "error": str(exc),
            }
        )
        print(f"FAILED: internal link rewrite pass: {exc}")

    try:
        module_results = publish_lecture_modules(
            api_base=api_base,
            token=token,
            course_id=course_id,
            lecture_metadata=lecture_metadata,
            lecture_pages=lecture_pages,
            file_url_map=file_url_map,
            timeout=args.timeout,
            dry_run=args.dry_run,
        )
        summary["modules"] = module_results
    except Exception as exc:
        summary["failed"].append(
            {
                "relativePath": "[modules]",
                "canvasFolder": "n/a",
                "error": str(exc),
            }
        )
        print(f"FAILED: module publishing: {exc}")

    try:
        summary["syllabus"] = publish_syllabus(
            api_base=api_base,
            token=token,
            course_id=course_id,
            build_dir=build_dir,
            file_url_map=file_url_map,
            route_url_map=route_url_map,
            slug_url_map=slug_url_map,
            unresolved_links=unresolved_internal_links,
            timeout=args.timeout,
            dry_run=args.dry_run,
        )
    except Exception as exc:
        summary["failed"].append(
            {
                "relativePath": "[syllabus]",
                "canvasFolder": "n/a",
                "error": str(exc),
            }
        )
        print(f"FAILED: syllabus publishing: {exc}")

    try:
        assignments_labs_results = publish_assignments_and_labs(
            api_base=api_base,
            token=token,
            course_id=course_id,
            config_path=config_path,
            build_dir=build_dir,
            file_url_map=file_url_map,
            route_url_map=route_url_map,
            slug_url_map=slug_url_map,
            unresolved_links=unresolved_internal_links,
            timeout=args.timeout,
            dry_run=args.dry_run,
        )
        summary["assignmentsAndLabs"] = assignments_labs_results
    except Exception as exc:
        summary["failed"].append(
            {
                "relativePath": "[assignmentsAndLabs]",
                "canvasFolder": "n/a",
                "error": str(exc),
            }
        )
        print(f"FAILED: assignments/labs publishing: {exc}")

    manifest_path = build_dir / "canvas_upload_manifest.json"
    summary["unresolvedInternalLinks"] = unresolved_internal_links
    manifest_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("Upload process complete.")
    print(f"Manifest: {manifest_path}")
    print(f"Uploaded: {len(summary['uploaded'])}, Failed: {len(summary['failed'])}")
    print(
        f"Pages: {summary['pages']['created']} created, {summary['pages']['updated']} updated, "
        f"{summary['pages']['dryRunSkipped']} dry-run skipped"
    )
    print(
        f"Modules: {summary['modules']['modulesCreated']} created, "
        f"{summary['modules']['modulesReused']} reused, "
        f"{summary['modules']['itemsCreated']} items created, "
        f"{summary['modules']['dryRunSkipped']} dry-run skipped"
    )
    print(f"Syllabus: {summary['syllabus']}")
    print(
        f"Assignments/Labs: {summary['assignmentsAndLabs']['created']} created, "
        f"{summary['assignmentsAndLabs']['dryRunSkipped']} dry-run skipped"
    )
    internal = summary.get("internalLinkRewrite", {"updated": 0, "dryRunSkipped": 0})
    print(
        f"Internal link rewrite: {internal.get('updated', 0)} pages updated, "
        f"{internal.get('dryRunSkipped', 0)} dry-run skipped"
    )
    print(f"Unresolved internal links: {len(unresolved_internal_links)}")

    return 1 if summary["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
