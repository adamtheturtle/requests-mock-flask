#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration for Sphinx.
"""

import datetime

from pkg_resources import get_distribution

# pylint: disable=invalid-name

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx_autodoc_typehints',
    'sphinxcontrib.spelling',
    'sphinx-prompt',
    'sphinx_substitution_extensions',
]

project = 'requests-mock-flask'

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# General information about the project.
project = 'Requests-Mock-Flask'
year = datetime.datetime.now().year
author = 'Adam Dangoor'
project_copyright = f'{year}, {author}'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# Use ``pkg_resources`` as per
# https://github.com/pypa/setuptools_scm#usage-from-sphinx.
version = get_distribution(project).version
_month, _day, _year, *_ = version.split('.')
release = f'{_month}.{_day}.{_year}'

html_theme = 'furo'
html_title = project
html_show_copyright = False
html_show_sphinx = False
html_show_sourcelink = False
html_theme_options = {
    'sidebar_hide_name': False,
}

# Output file base name for HTML help builder.
htmlhelp_basename = 'requestsmockflaskdoc'

spelling_word_list_filename = '../../spelling_private_dict.txt'

rst_prolog = f"""
.. |project| replace:: {project}
.. |release| replace:: {release}
.. |github-owner| replace:: adamtheturtle
.. |github-repository| replace:: requests-mock-flask
"""

always_document_param_types = True

set_type_checking_flag = True
# * We want to use types from packages which are not install dependencies of
#   this package.
# * To achieve that, we wrap imports in ``if typing.TYPE_CHECKING``.
# * To get those imports in sphinx-autodoc-typehints, we must use
#   ``set_type_checking_flag = True``.
# * If we use that option, we set ``typing.TYPE_CHECKING`` true in our imported
#   packages.
# * Some packages cannot be imported when we use `typing.TYPE_CHECKING``, so
#   we mock them out.
autodoc_mock_imports = ['werkzeug', 'flask']
