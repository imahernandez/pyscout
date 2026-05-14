"""
utils/i18n.py — Sistema de traducción simple para PyScout.

USO EN CUALQUIER ARCHIVO:
    from utils.i18n import _
    btn = QPushButton(_("Guardar"))

    # Con variables:
    state.toast_requested.emit(_('"{}" guardado').format(name))

PARA INICIALIZAR (en main.py, ANTES de crear cualquier widget):
    from utils.i18n import detect_and_load
    detect_and_load()

PARA CAMBIAR IDIOMA EN RUNTIME:
    from utils.i18n import save_language
    save_language("en")
"""

from __future__ import annotations
import importlib

_strings: dict[str, str] = {}
_current_lang: str = "es"


def set_language(lang: str) -> None:
    global _strings, _current_lang
    _current_lang = lang
    try:
        mod = importlib.import_module(f"translations.{lang}")
        _strings = getattr(mod, "STRINGS", {})
    except (ImportError, AttributeError):
        _strings = {}


def detect_and_load() -> str:
    """
    Detectar el idioma del sistema y cargarlo.
    Prioridad: 1) QSettings  2) Locale del SO  3) Español fallback
    """
    from PySide6.QtCore import QSettings, QLocale

    settings = QSettings("ScoutApp", "prefs")
    saved = settings.value("language", "")
    if saved and _lang_available(saved):
        set_language(saved)
        return saved

    locale = QLocale.system().name()
    lang = locale.split("_")[0]

    if _lang_available(lang):
        set_language(lang)
    else:
        set_language("es")

    return _current_lang


def save_language(lang: str) -> None:
    from PySide6.QtCore import QSettings
    QSettings("ScoutApp", "prefs").setValue("language", lang)
    set_language(lang)


def available_languages() -> list[str]:
    return ["es", "en"]


def current_language() -> str:
    return _current_lang


def _lang_available(lang: str) -> bool:
    return lang in available_languages()


def _(text: str) -> str:
    """Traducir un string. Si no hay traducción, devuelve el original."""
    return _strings.get(text, text)
