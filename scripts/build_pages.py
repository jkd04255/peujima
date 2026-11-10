#!/usr/bin/env python3
"""Build PRZIMA's static GitHub Pages output with its PUBLIC, domain-restricted Kakao JS key.

Only use this during an explicitly approved release or a local test.
Never commit dist/, print key material, or upload it as a general QA artifact.
REST/Admin keys are NOT supported.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
KEY_NAME = "PJM012_KAKAO_JS_KEY"
ANCHOR = '<script src="./pjm012-nearby.js"></script>'
KEY_PATTERN = re.compile(r"^[A-Za-z0-9]{20,64}$")
ASSETS = ("pjm012-nearby.js", "pjm012-nearby.css", "pjm013-navigation.js", "pjm013-navigation.css", "pjm019-insurance.js", "pjm019-insurance.css")


def build_site(output_dir: Path, kakao_js_key: str) -> None:
    if not KEY_PATTERN.fullmatch(kakao_js_key):
        raise ValueError("Kakao JavaScript key must be alphanumeric, length 20-64")
    output_dir = output_dir.resolve()
    if output_dir == ROOT or ROOT == output_dir.parent:
        # "dist" is allowed under ROOT, but overwriting the repo root is not.
        if output_dir == ROOT:
            raise ValueError("Output must not overwrite repository root")
    original = (ROOT / "index.html").read_text(encoding="utf-8")
    if original.count(ANCHOR) != 1:
        raise ValueError("Could not find exactly one PJM-012 JS script anchor")
    if "PRZIMA_KAKAO_JS_KEY =" in original:
        raise ValueError("A key assignment is already embedded in the committed page")
    js_value = json.dumps(kakao_js_key, ensure_ascii=True)
    config = (
        "<script id=\"przima-kakao-public-config\">"
        f"window.PRZIMA_KAKAO_JS_KEY = {js_value};"
        "</script>"
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "index.html").write_text(
        original.replace(ANCHOR, config + ANCHOR), encoding="utf-8"
    )
    for filename in ASSETS:
        shutil.copyfile(ROOT / filename, output_dir / filename)
    (output_dir / ".nojekyll").write_text("", encoding="utf-8")
    # Do NOT print actual key or rendered markup.
    print("PJM-012 static Pages build complete (public origin-restricted JS key injected)")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    args = parser.parse_args()
    key = os.environ.get(KEY_NAME, "").strip()
    if not key:
        parser.error(f"{KEY_NAME} is required; refusing to build an unusable release")
    build_site(args.output, key)


if __name__ == "__main__":
    main()
