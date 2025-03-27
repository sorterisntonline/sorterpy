import os
import sys
sys.path.insert(0, os.path.abspath('..'))

project = 'sorterpy'
copyright = '2024, sorter.social'
author = 'zudsniper'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'myst_parser',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
html_theme = 'sphinx_rtd_theme'
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}