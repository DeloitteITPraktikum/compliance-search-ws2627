"""Relevance keys for the compliance search evals.

A hit is the pair (family_id, article_key). Both parts ignore language and
version, so "Art. 19 Abs. 4" of the German DORA and "Article 19(1)" of the
English DORA are the same hit.

Article keys:
    EU acts          art:19   annex:III   recital:12   col:B_05.01.0090
    Pillar 3 forms   tpl:EU-OV1                      (from "Template EU OV1")
    MaRisk           AT 4.3.4   BTO 1.2   BTR 5      (the module, Tz ignored)
    BAIT, VAIT       ch:4                            (the chapter, from "Tz. 4.4")
    EBA guidelines   para:75

A corrigendum has no articles of its own. If you cite one and the label names
no article ("p. 1"), the key is `corrigendum`.

The family of a document is the `family_id` field of the document API. Pass
your own {document_id: family_id} mapping, or let `load_families` fetch it
(env DOCS_URL and KEY).

No dependencies. Copy this file into your own repo.
"""
import json
import os
import re
import urllib.request
from functools import lru_cache

CIRCULARS = {"circular", "marisk", "bait", "vait"}


def roman(number):
    """1 to 99 as a Roman numeral: ITS 2024/3172 has more than 40 annexes."""
    tens, ones = ["", "X", "XX", "XXX", "XL", "L", "LX", "LXX", "LXXX", "XC"], ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX"]
    return tens[number // 10 % 10] + ones[number % 10]


KEY = re.compile(r"(art|annex|recital|col|para|ch|tpl):\S+|(AT|BTO|BTR|BT) \d+(\.\d+)*")
TEMPLATE = re.compile(r"\bEU[ _-]?([A-Z][A-Za-z]{1,5}\d{1,2}[a-z]?|[A-Z]{3,4})\b")
COLUMN = re.compile(r"\b([A-Z])[_ ]?(\d\d\.\d\d)\.(\d{4})\b", re.IGNORECASE)
EU_PART = re.compile(
    r"\b(?P<art>art(?:icle|ikel)?s?\.?)\s*(?P<art_no>\d+[a-z]?)\b"
    r"|\b(?P<annex>annex|anhang|anh\.)\s*(?P<annex_no>[ivxl]+|\d+)\b"
    r"|\b(?P<recital>recital|erwägungsgrund|erwgr\.?|egr\.?)\s*\(?(?P<recital_no>\d+)",
    re.IGNORECASE,
)
MODULE = re.compile(r"\b(AT|BTO|BTR|BT)\s*(\d+(?:\.\d+)*)", re.IGNORECASE)
CHAPTER = re.compile(r"(\d+)(?:\.\d+)*")
PARA = re.compile(r"(?:paragraphs?|para\.?|absatz|abs\.|tz\.?|textziffer|rn\.?|rz\.?|randnummer|nr\.?|no\.?|ziffer|§)\s*(\d+)", re.IGNORECASE)


def normalize_article(doc_type_or_family, raw):
    """Map what a citation says ("Art. 19 Abs. 4", "AT 4.3.4 Tz. 2") to one key, or None."""
    raw = str(raw or "").strip()
    if KEY.fullmatch(raw):
        return raw
    kind = str(doc_type_or_family or "").lower()

    if kind in CIRCULARS:
        module = MODULE.search(raw)
        if module:
            return f"{module[1].upper()} {module[2].rstrip('.')}"
        chapter = CHAPTER.search(raw)
        return f"ch:{chapter[1]}" if chapter and kind != "marisk" else None

    if kind == "guideline" or kind.startswith("eba"):
        para = PARA.search(raw) or re.match(r"(\d+)", raw)
        return f"para:{para[1]}" if para else None

    column = COLUMN.search(raw)
    if column:
        return f"col:{column[1].upper()}_{column[2]}.{column[3]}"
    template = TEMPLATE.search(raw)
    if template:
        return f"tpl:EU-{template[1]}"
    part = EU_PART.search(raw)
    if part and part["art"]:
        return f"art:{part['art_no'].lower()}"
    if part and part["annex"]:
        number = part["annex_no"]
        return f"annex:{roman(int(number)) if number.isdigit() else number.upper()}"
    if part and part["recital"]:
        return f"recital:{part['recital_no']}"
    bare = re.match(r"(\d+[a-z]?)\b", raw)
    return f"art:{bare[1]}" if bare else None


def fetch_documents():
    """All records of the document API, tombstones included."""
    url = os.environ["DOCS_URL"].rstrip("/") + "/documents"
    request = urllib.request.Request(url, headers={"Authorization": f"Bearer {os.environ['KEY']}"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)["documents"]


@lru_cache
def load_families():
    return {doc["id"]: doc["family_id"] for doc in fetch_documents()}


def family_of(document_id, families=None):
    """Family id of a document, or None for an unknown id."""
    return (load_families() if families is None else families).get(document_id)


def key_of(document_id, article, families=None, corrigenda=()):
    """The (family_id, article_key) pair for one citation or retrieved passage.

    `corrigenda` holds the ids of the documents with `doc_type` corrigendum.
    """
    family = family_of(document_id, families)
    return family, normalize_article(family, article) or ("corrigendum" if document_id in corrigenda else None)
