#!/usr/bin/env python3
"""
Configuration for Sphinx.
"""

import importlib.metadata
from pathlib import Path

from packaging.specifiers import SpecifierSet
from sphinx_pyproject import SphinxConfig

_pyproject_file = Path(__file__).parent.parent.parent / "pyproject.toml"
_pyproject_config = SphinxConfig(
    pyproject_file=_pyproject_file,
    config_overrides={"version": None},
)

project = _pyproject_config.name
author = _pyproject_config.author

extensions = [
    "sphinx_copybutton",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinxcontrib.spelling",
    "sphinx_substitution_extensions",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

project_copyright = f"%Y, {author}"

# Exclude the prompt from copied code with sphinx_copybutton.
# https://sphinx-copybutton.readthedocs.io/en/latest/use.html#automatic-exclusion-of-prompts-from-the-copies.
copybutton_exclude = ".linenos, .gp"

project_metadata = importlib.metadata.metadata(distribution_name=project)
requires_python = project_metadata["Requires-Python"]
specifiers = SpecifierSet(specifiers=requires_python)
(specifier,) = specifiers
if specifier.operator != ">=":
    msg = (
        f"We only support '>=' for Requires-Python, got {specifier.operator}."
    )
    raise ValueError(msg)
minimum_python_version = specifier.version

html_theme = "furo"
html_title = project
html_show_copyright = False
html_show_sphinx = False
html_show_sourcelink = False
html_theme_options = {
    "sidebar_hide_name": False,
}

# Output file base name for HTML help builder.
htmlhelp_basename = "requestsmockflaskdoc"

spelling_word_list_filename = "../../spelling_private_dict.txt"

rst_prolog = f"""
.. |project| replace:: {project}
.. |minimum-python-version| replace:: {minimum_python_version}
.. |github-owner| replace:: adamtheturtle
.. |github-repository| replace:: requests-mock-flask
"""
