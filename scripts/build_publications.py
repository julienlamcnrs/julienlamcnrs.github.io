#!/usr/bin/env python3
"""Convert data/publications.bib into data/publications.json for Hugo."""
import json
import re
from pathlib import Path
import bibtexparser

ROOT = Path(__file__).resolve().parents[1]
BIB_PATH = ROOT / "bibliography" / "publications.bib"
OUT_PATH = ROOT / "data" / "publications.json"

def clean(value):
    if value is None:
        return ""
    value = str(value)
    value = re.sub(r"\\\\[a-zA-Z]+", "", value)
    value = value.replace("{", "").replace("}", "")
    value = re.sub(r"\s+", " ", value).strip()
    return value

def split_authors(value):
    if not value:
        return []
    return [clean(x) for x in re.split(r"\s+and\s+", value) if clean(x)]

def main():
    if not BIB_PATH.exists():
        raise SystemExit(f"Missing BibTeX file: {BIB_PATH}")
    with BIB_PATH.open(encoding="utf-8") as f:
        db = bibtexparser.load(f)
    records = []
    for index, entry in enumerate(db.entries):
        title = clean(entry.get("title"))
        author_string = entry.get("author", "")
        authors = split_authors(author_string)
        year = clean(entry.get("year"))
        note = clean(entry.get("note"))
        doi = clean(entry.get("doi"))
        url = clean(entry.get("url"))
        if doi and not url:
            url = "https://doi.org/" + doi
        status = "Submitted" if (entry.get("ENTRYTYPE", "").lower() == "unpublished" or "submitted" in note.lower()) else ""
        # Store each original BibTeX entry for the per-paper copy button.
        raw_bib = "@" + entry.get("ENTRYTYPE", "article") + "{" + entry.get("ID", f"ref{index+1}") + ",\n"
        fields = [(k, v) for k, v in entry.items() if k not in ("ENTRYTYPE", "ID")]
        for key, value in fields:
            raw_bib += f"  {key} = {{{value}}},\n"
        raw_bib = raw_bib.rstrip(",\n") + "\n}"
        records.append({
            "key": entry.get("ID", f"ref{index+1}"),
            "title": title,
            "authors": authors,
            "authors_text": ", ".join(authors),
            "year": year,
            "journal": clean(entry.get("journal")),
            "note": note,
            "doi": doi,
            "url": url,
            "status": status,
            "bibtex": raw_bib,
            "search": " ".join([title, author_string, year, note, entry.get("journal", ""), doi]).lower()
        })
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(records)} publications to {OUT_PATH}")

if __name__ == "__main__":
    main()
