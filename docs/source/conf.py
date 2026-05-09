# Configuration file for the Sphinx documentation builder.

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

project = "API Pools"
copyright = "2026, Juan Manuel Mejia Botero"
author = "Juan Manuel Mejia Botero"
release = "0.2.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

templates_path = ["_templates"]
exclude_patterns: list[str] = []

html_theme = "furo"
html_title = "API Pools"
html_static_path = ["_static"]
language = "en"

html_theme_options = {
    "sidebar_hide_name": False,
    "footer_icons": [],
}

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

nitpick_ignore = [
    ("py:class", "Protocol"),
    ("py:class", "typing.Protocol"),
]
