#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration for Sphinx.
"""

from pkg_resources import get_distribution

# pylint: disable=invalid-name

# -- General configuration ------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinxcontrib.spelling',
    'sphinx_substitution_extensions',
]

project = 'requests-mock-flask'

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# General information about the project.
project = 'Requests-Mock-Flask'
copyright = '2020, Adam Dangoor'  # pylint: disable=redefined-builtin
author = 'Adam Dangoor'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# Use ``pkg_resources`` as per
# https://github.com/pypa/setuptools_scm#usage-from-sphinx.
version = get_distribution(project).version
_month, _day, _year, *_ = version.split('.')
release = f'{_month}.{_day}.{_year}'

substitutions = [
    ('|release|', release),
    ('|github-owner|', 'adamtheturtle'),
    ('|github-repository|', 'requests-mock-flask'),
]

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = False

# -- Options for HTML output ----------------------------------------------

# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
html_show_sphinx = False

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
html_show_copyright = False

# Output file base name for HTML help builder.
htmlhelp_basename = 'requestsmockflaskdoc'

spelling_word_list_filename = '../../spelling_private_dict.txt'

rst_prolog = f"""
.. |project| replace:: {project}
"""

always_document_param_types = True
