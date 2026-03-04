from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class LanguageEntry:
    lang_id: str
    bcp47: str
    native_name: str
    english_name: str
    flag: str


_LANG_ID_RE = re.compile(r"^[A-Za-z]{2,3}$")
_BCP47_MULTI_RE = re.compile(r"^[A-Za-z]{2,3}(?:-[A-Za-z0-9]{2,8})+$")
_BCP47_REGION_RE = re.compile(r"^[A-Za-z]{2,3}-[A-Za-z]{2}$")

_ENTRY_BY_LANG: dict[str, LanguageEntry] = {
    "en": LanguageEntry("en", "en-US", "English", "English", "🇺🇸"),
    "ja": LanguageEntry("ja", "ja-JP", "日本語", "Japanese", "🇯🇵"),
    "fr": LanguageEntry("fr", "fr-FR", "Français", "French", "🇫🇷"),
    "de": LanguageEntry("de", "de-DE", "Deutsch", "German", "🇩🇪"),
    "es": LanguageEntry("es", "es-ES", "Español", "Spanish", "🇪🇸"),
    "it": LanguageEntry("it", "it-IT", "Italiano", "Italian", "🇮🇹"),
    "pt": LanguageEntry("pt", "pt-PT", "Português", "Portuguese", "🇵🇹"),
    "ko": LanguageEntry("ko", "ko-KR", "한국어", "Korean", "🇰🇷"),
    "zh": LanguageEntry("zh", "zh-CN", "中文", "Chinese", "🇨🇳"),
    "zh-cn": LanguageEntry("zh-cn", "zh-CN", "简体中文", "Chinese (Simplified)", "🇨🇳"),
    "zh-tw": LanguageEntry("zh-tw", "zh-TW", "繁體中文", "Chinese (Traditional)", "🇹🇼"),
}


def _normalize_key(value: str) -> str:
    return (value or "").strip().replace("_", "-").lower()


def get_language_entry(value: str) -> LanguageEntry | None:
    key = _normalize_key(value)
    if not key:
        return None
    entry = _ENTRY_BY_LANG.get(key)
    if entry is not None:
        return entry
    base = key.split("-", 1)[0]
    return _ENTRY_BY_LANG.get(base)


def format_language_label(value: str) -> str:
    entry = get_language_entry(value)
    if entry is None:
        return value
    return f"{entry.flag} {entry.native_name} ({value})"


def to_bcp47_lang_tag(value: str) -> str:
    raw = (value or "").strip().replace("_", "-")
    if not raw:
        return raw

    if _BCP47_MULTI_RE.fullmatch(raw):
        if _BCP47_REGION_RE.fullmatch(raw):
            base, region = raw.split("-", 1)
            return f"{base.lower()}-{region.upper()}"
        return raw

    entry = get_language_entry(raw)
    if entry is not None:
        return entry.bcp47

    if _LANG_ID_RE.fullmatch(raw):
        base = raw.lower()
        return f"{base}-{base.upper()}"

    return raw
