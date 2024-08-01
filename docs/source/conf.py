#!/usr/bin/env python3
"""
Configuration for Sphinx.
"""

import datetime
import importlib.metadata

# pylint: disable=invalid-name

extensions = [
    "sphinx_copybutton",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinxcontrib.spelling",
    "sphinx_substitution_extensions",
]

project = "requests-mock-flask"

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# General information about the project.
year = datetime.datetime.now(tz=datetime.UTC).year
author = "Adam Dangoor"
project_copyright = f"{year}, {author}"

# Exclude the prompt from copied code with sphinx_copybutton.
# https://sphinx-copybutton.readthedocs.io/en/latest/use.html#automatic-exclusion-of-prompts-from-the-copies.
copybutton_exclude = ".linenos, .gp"

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# Use ``importlib.metadata.version`` as per
# https://setuptools-scm.readthedocs.io/en/latest/usage/#usage-from-sphinx.
version = importlib.metadata.version(distribution_name=project)
_month, _day, _year, *_ = version.split(".")
release = f"{_month}.{_day}.{_year}"

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
.. |release| replace:: {release}
.. |github-owner| replace:: adamtheturtle
.. |github-repository| replace:: requests-mock-flask
"""
