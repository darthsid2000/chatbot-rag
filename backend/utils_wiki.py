import re
import xml.etree.ElementTree as ET
from typing import Iterable, Tuple

try:
    import mwparserfromhell as mw
except ImportError:
    mw = None

def strip_wiki(text: str) -> str:
    if not text:
        return ""
    if mw:
        text = mw.parse(text).strip_code(normalize=True, collapse=True)
    text = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]+)\]\]", r"\1", text)
    text = re.sub(r"<ref[^>]*>.*?</ref>", "", text, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+\n", "\n", text)
    return text.strip()

def normalize_title(title: str) -> str:
    return (title or "").strip().lower().replace(" ", "_")

def iter_mediawiki_pages(xml_path: str) -> Iterable[Tuple[str, str]]:
    tree = ET.parse(xml_path)
    root = tree.getroot()
    ns = ""
    if root.tag.startswith("{"):
        ns = root.tag.split("}")[0] + "}"
    for page in root.findall(f".//{ns}page"):
        t = page.findtext(f"{ns}title") or ""
        r = page.find(f"{ns}revision")
        x = r.findtext(f"{ns}text") if r is not None else ""
        yield t, x