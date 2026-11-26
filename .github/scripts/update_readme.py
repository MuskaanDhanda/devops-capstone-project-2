#!/usr/bin/env python3
"""Keep the two README tables in sync with the files in the repo.

1. Overview table (# | Component | Project file | Topics covered), between the
   OVERVIEW markers: every top-level file/folder gets a row. Existing rows and
   their wording are kept; new items are appended; rows whose file was deleted
   are removed; rows are renumbered.
2. Project files table, between the PROJECT-FILES markers: every file and
   folder gets a linked row. Hand-written descriptions are kept.

README.md and hidden paths such as .github/ are skipped.
"""
import os
import re
import subprocess
from urllib.parse import quote, unquote

README = "README.md"
START = "<!-- PROJECT-FILES:START -->"
END = "<!-- PROJECT-FILES:END -->"
OV_START = "<!-- OVERVIEW:START -->"
OV_END = "<!-- OVERVIEW:END -->"

IMAGE_EXT = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"}
KNOWN = {
    "dockerfile": "Instructions for building the Docker image",
    "jenkinsfile": "Jenkins pipeline configuration",
    "makefile": "Build commands",
    "license": "License",
}
EXT_DESC = {
    ".yml": "YAML configuration", ".yaml": "YAML configuration",
    ".sh": "Shell script", ".py": "Python script", ".java": "Java source file",
    ".xml": "XML configuration", ".json": "JSON configuration",
    ".tf": "Terraform configuration", ".html": "HTML page", ".txt": "Text file",
    ".pdf": "PDF document", ".md": "Documentation",
}


def tracked_files():
    out = subprocess.run(["git", "ls-files"], capture_output=True, text=True, check=True).stdout
    files = []
    for path in out.splitlines():
        if path == README or any(part.startswith(".") for part in path.split("/")):
            continue
        files.append(path)
    return files


def md_heading(path):
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                if line.startswith("#"):
                    return line.lstrip("#").strip()
    except (OSError, UnicodeDecodeError):
        pass
    return None


def auto_description(path, is_dir):
    if is_dir:
        return md_heading(os.path.join(path, "README.md")) or "Folder"
    name = os.path.basename(path)
    stem, ext = os.path.splitext(name)
    ext = ext.lower()
    if name.lower() in KNOWN:
        return KNOWN[name.lower()]
    if ext in IMAGE_EXT:
        return stem.replace("-", " ").replace("_", " ").capitalize() + " image"
    if ext == ".md":
        return md_heading(path) or "Documentation"
    return EXT_DESC.get(ext, "Project file")


def existing_descriptions(block):
    """Map link target -> description from the current table."""
    descs = {}
    for line in block.splitlines():
        m = re.match(r"\|.*?\]\(([^)]+)\)\s*\|(.*)\|\s*$", line)
        if m:
            cells = [c.strip() for c in m.group(2).split("|")]
            descs[unquote(m.group(1)).rstrip("/")] = cells[-1]
    return descs


def build_entries(files):
    entries = set()
    for f in files:
        parts = f.split("/")
        for i in range(1, len(parts)):
            entries.add(("/".join(parts[:i]), True))
        entries.add((f, False))
    # Folders before the files inside them, alphabetical (case-insensitive)
    return sorted(entries, key=lambda e: [p.lower() for p in e[0].split("/")])


def split_markers(text, start, end):
    if start not in text or end not in text:
        raise SystemExit(f"Markers {start} / {end} not found in {README}")
    head, rest = text.split(start, 1)
    block, tail = rest.split(end, 1)
    return head, block, tail


def component_name(path):
    stem = os.path.splitext(os.path.basename(path))[0]
    return stem.replace("-", " ").replace("_", " ").title() if stem.islower() else stem


def overview_table(block, entries):
    existing_paths = {p for p, _ in entries}
    top_level = [(p, d) for p, d in entries if "/" not in p]
    rows, linked = [], set()
    for line in block.splitlines():
        m = re.match(r"\|\s*\d+\s*\|(.*)\|\s*$", line)
        if not m:
            continue
        cells = [c.strip() for c in m.group(1).split("|")]
        link = re.search(r"\]\(([^)]+)\)", cells[1]) if len(cells) > 1 else None
        target = unquote(link.group(1)).rstrip("/") if link else None
        if target and target not in existing_paths:
            continue  # file was deleted
        if target:
            linked.add(target)
        rows.append(cells)
    for path, is_dir in top_level:
        if path in linked:
            continue
        name = os.path.basename(path) + ("/" if is_dir else "")
        rows.append([component_name(path), f"[{name}]({quote(path)})",
                     auto_description(path, is_dir)])
    out = ["| # | Component | Project file | Topics covered |",
           "|---|-----------|--------------|----------------|"]
    for i, cells in enumerate(rows, 1):
        out.append(f"| {i} | " + " | ".join(cells) + " |")
    return "\n".join(out)


def files_table(block, entries):
    descs = existing_descriptions(block)
    rows = ["| File / Folder | What's inside |", "|---------------|---------------|"]
    for path, is_dir in entries:
        depth = path.count("/")
        name = os.path.basename(path) + ("/" if is_dir else "")
        icon = "📁" if is_dir else ("🖼️" if os.path.splitext(path)[1].lower() in IMAGE_EXT else "📄")
        indent = "&nbsp;&nbsp;&nbsp;&nbsp;" * depth
        desc = descs.get(path) or auto_description(path, is_dir)
        rows.append(f"| {indent}{icon} [{name}]({quote(path)}) | {desc} |")
    return "\n".join(rows)


def main():
    with open(README, encoding="utf-8") as f:
        text = f.read()
    entries = build_entries(tracked_files())

    head, block, tail = split_markers(text, OV_START, OV_END)
    new_text = f"{head}{OV_START}\n{overview_table(block, entries)}\n{OV_END}{tail}"

    head, block, tail = split_markers(new_text, START, END)
    new_text = f"{head}{START}\n{files_table(block, entries)}\n{END}{tail}"

    if new_text != text:
        with open(README, "w", encoding="utf-8") as f:
            f.write(new_text)
        print("README.md updated")
    else:
        print("README.md already up to date")


if __name__ == "__main__":
    main()
