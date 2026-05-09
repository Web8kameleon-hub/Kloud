"""
Kloud Identity Loader
========================
Një file i vetëm për identitetin e platformës.
Të gjitha modulet e lexojnë këtë - asnjë hardcode.
"""

from pathlib import Path

# Path te dokumenti
DOCS_DIR = Path(__file__).parent / "documents"
IDENTITY_FILE = DOCS_DIR / "company_info.md"

_identity_cache = None


def load_identity() -> dict:
    """Lexon identitetin nga company_info.md"""
    global _identity_cache

    if _identity_cache:
        return _identity_cache

    identity = {
        "platforma": "Kloud Cloud",
        "ai": "Ocean",
        "krijues": "Ledjan Ahmati",
        "ceo": "Ledjan Ahmati",
        "firma": "ABA GmbH",
        "website": "kloud.cloud"
    }

    try:
        if IDENTITY_FILE.exists():
            content = IDENTITY_FILE.read_text(encoding="utf-8")
            for line in content.split("\n"):
                if "**Platforma:**" in line:
                    identity["platforma"] = line.split(":**")[1].strip()
                elif "**AI:**" in line:
                    identity["ai"] = line.split(":**")[1].strip()
                elif "**Krijues" in line:
                    identity["krijues"] = line.split(":**")[1].strip()
                elif "**CEO:**" in line:
                    identity["ceo"] = line.split(":**")[1].strip()
                elif "**Firma:**" in line:
                    identity["firma"] = line.split(":**")[1].strip()
    except Exception as e:
        print(f"[IDENTITY] Error loading: {e}")

    _identity_cache = identity
    return identity


def get_identity_text() -> str:
    """Kthen identitetin si tekst të thjeshtë"""
    i = load_identity()
    return f"""Platforma: {i['platforma']}
AI: {i['ai']}
Krijues: {i['krijues']}
CEO: {i['ceo']}
Firma: {i['firma']}
Website: {i['website']}"""


def get_identity_short() -> str:
    """Versioni KONCIZ për system prompt — vetëm 2 rreshta, pa vonesa"""
    i = load_identity()
    return (
        f"You are {i['ai']}, AI of {i['platforma']}, "
        f"created by {i['krijues']} ({i['firma']}). "
        f"Website: {i['website']}"
    )


def get_ceo() -> str:
    return load_identity()["ceo"]


def get_company() -> str:
    return load_identity()["firma"]


def get_krijues() -> str:
    return load_identity()["krijues"]

