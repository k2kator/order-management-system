import os
import sys
sys.path.insert(0, os.path.abspath('../../'))

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
]

templates_path = ['_templates']
exclude_patterns = []

language = 'ru'

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

locale_dirs = ['locale/']
gettext_compact = False