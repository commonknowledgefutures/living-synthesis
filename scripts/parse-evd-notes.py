#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
roam_to_obsidian.py
CLI to convert Roam page markdown exports into Obsidian-friendly markdown.

Usage (from repo root):
  python3 scripts/roam_to_obsidian.py \
      --in_dir content/NodeInbox \
      --out_dir content/NodesToConvert \
      --flatten heuristic

Flatten modes: none | unwrap | bullets | heuristic
"""

from __future__ import annotations
import argparse
import re
from pathlib import Path
from typing import Dict, List, Tuple

# HEADER_RE = re.compile(r'^(#{1,6})\s+(.+?)\s*$')
HEADER_RE = re.compile(r'^(#{1,6})\s+(.+?)(?:\s+\[.*)?$')
PROP_LINE_RE = re.compile(r'^\s*([A-Za-z0-9 _\-/]+?)::\s*(.+?)\s*$')
BLOCK_REF_RE = re.compile(r'\(\([^)]+\)\)')
LIST_LINE_RE = re.compile(r'^(\s*)([-*+])\s+(.*)$')

KEEP_TITLES = {"description", "methods context"}


# ---------- preprocessing helpers ----------

def preprocess_line(line: str) -> str:
    """Strip leading bullets/emoji so headings/properties are detectable."""
    clean = re.sub(r"^\s*[-*+]\s+", "", line)
    clean = clean.lstrip("🏷️ ").strip()
    return clean


def preprocess_lines(lines: List[str]) -> List[str]:
    return [preprocess_line(l) for l in lines]


# ---------- properties parsing ----------

def parse_properties_block(lines: List[str]) -> Tuple[Dict[str, str], int]:
    props = {}
    consumed = 0
    in_props = False
    for i, raw in enumerate(lines):
        line = raw.strip()
        if line.lower().startswith("#.properties"):
            in_props = True
            continue
        if in_props:
            if HEADER_RE.match(line):
                break
            m = PROP_LINE_RE.match(line)
            if m:
                props[m.group(1).strip()] = m.group(2).strip()
                consumed = i+1
            elif line == "":
                continue
            else:
                break
    return props, consumed

def yaml_escape(value: str) -> str:
    v = value.strip()
    if v.startswith("[[") and v.endswith("]]"):
        return v
    if any(ch in v for ch in [":", "{", "}", "[", "]", ",", "#", "&", "*", "!", "|", ">", "'", '"', "%", "@", "`"]):
        v = v.replace('"', '\\"')
        return f'"{v}"'
    return v


def build_yaml(props: Dict[str, str]) -> str:
    if not props:
        return ""
    lines = ["---"]
    for k, v in props.items():
        key = str(k).strip().replace(" ", "_")
        lines.append(f"{key}: {yaml_escape(v)}")
    lines.append("---")
    return "\n".join(lines) + "\n\n"


# ---------- section extraction & cleanup ----------

def extract_kept_sections(lines: List[str]) -> List[str]:
    kept: List[str] = []
    in_keep = False
    keep_level = None
    for line in lines:
        h = HEADER_RE.match(line)
        if h:
            level = len(h.group(1))
            title = h.group(2).split("[")[0].strip().lower()
            if title in KEEP_TITLES:
                in_keep = True
                keep_level = level
                kept.append(f"{'#'*level} {title.title()}")
                continue
            # only exit if this is a heading of same or higher level
            if in_keep and level <= keep_level:
                in_keep = False
                keep_level = None
        if in_keep:
            line = BLOCK_REF_RE.sub("", line)
            kept.append(line)
    return kept



# ---------- flatten modes ----------

def flatten_none(lines: List[str]) -> List[str]:
    return lines

def flatten_unwrap(lines: List[str]) -> List[str]:
    out: List[str] = []
    for line in lines:
        m = LIST_LINE_RE.match(line)
        if m:
            content = m.group(3)
            out.append(content)
        else:
            out.append(line)
    return out

def flatten_bullets(lines: List[str]) -> List[str]:
    out: List[str] = []
    for line in lines:
        m = LIST_LINE_RE.match(line)
        if m:
            content = m.group(3)
            out.append(f"- {content}")
        else:
            out.append(line)
    return out

def flatten_heuristic(lines: List[str]) -> List[str]:
    tmp = []
    for line in lines:
        # keep blockquotes as-is
        if line.lstrip().startswith(">"):
            tmp.append(line.strip())
            continue
        m = LIST_LINE_RE.match(line)
        if m:
            content = m.group(3).strip()
            tmp.append(f"- {content}")
        else:
            tmp.append(line.strip())
    # squeeze blank runs
    out = []
    blank = False
    for l in tmp:
        if l.strip():
            out.append(l)
            blank = False
        else:
            if not blank:
                out.append("")
            blank = True
    return out


def flatten(lines: List[str], mode: str) -> List[str]:
    if mode == "none":
        return flatten_none(lines)
    if mode == "unwrap":
        return flatten_unwrap(lines)
    if mode == "bullets":
        return flatten_bullets(lines)
    return flatten_heuristic(lines)


# ---------- conversion ----------

def convert_markdown(md: str, flatten_mode: str, orig_rel_for_backlink: str) -> str:
    lines = preprocess_lines(md.splitlines())
    props, consumed = parse_properties_block(lines)
    remainder = lines[consumed:]
    kept = extract_kept_sections(remainder)
    body_lines = flatten(kept, flatten_mode) if kept else []
    out = []
    yaml = build_yaml(props)
    if yaml:
        out.append(yaml.rstrip("\n"))
        out.append("")
    out.append(f"> backlink: [[{orig_rel_for_backlink}]]")
    out.append("")
    out.extend(body_lines)
    return "\n".join(out).rstrip() + "\n"


def process_file(src: Path, out_root: Path, repo_root: Path, flatten_mode: str) -> Path:
    text = src.read_text(encoding="utf-8", errors="replace")
    backlink_target = src.stem
    converted = convert_markdown(text, flatten_mode, backlink_target)
    out_path = out_root / src.name
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(converted, encoding="utf-8")
    return out_path


def find_markdown_files(in_dir: Path) -> List[Path]:
    return sorted([p for p in in_dir.rglob("*.md") if p.is_file()])


def main():
    parser = argparse.ArgumentParser(description="Convert Roam markdown exports to Obsidian-friendly markdown.")
    parser.add_argument("--in_dir", default="content/NodeInbox", type=str)
    parser.add_argument("--out_dir", default="content/NodesToConvert", type=str)
    parser.add_argument("--flatten", default="heuristic", choices=["none", "unwrap", "bullets", "heuristic"])
    args = parser.parse_args()

    repo_root = Path(".").resolve()
    in_dir = (repo_root / args.in_dir).resolve()
    out_dir = (repo_root / args.out_dir).resolve()
    if not in_dir.exists():
        raise SystemExit(f"input dir not found: {in_dir}")
    md_files = find_markdown_files(in_dir)
    if not md_files:
        print("no markdown files found.")
        return
    out_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    for src in md_files:
        out_path = process_file(src, out_dir, repo_root, args.flatten)
        count += 1
        print(f"wrote: {out_path.relative_to(repo_root)}")
    print(f"\nconverted {count} files → {out_dir.relative_to(repo_root)} (flatten={args.flatten})")


if __name__ == "__main__":
    main()
