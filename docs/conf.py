import os
import sys
import re

sys.path.insert(0, os.path.abspath('..'))

# Read version from pyproject.toml
def get_version_from_pyproject():
    with open('../pyproject.toml', 'r') as f:
        content = f.read()
        version_match = re.search(r'version\s*=\s*"([^"]+)"', content)
        if version_match:
            return version_match.group(1)
    return "0.0.0"

version = get_version_from_pyproject()
release = version

project = 'sorterpy'
copyright = '2024, sorter.social'
author = 'zudsniper'

# Add any Sphinx extension module names here
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'myst_parser',
]

# Configuration for MyST
myst_enable_extensions = [
    "colon_fence",
    "deflist"
]

# Add any paths that contain templates here
templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# Theme configuration
html_theme = 'sphinx_rtd_theme'
html_theme_options = {
    'navigation_depth': 4,
    'titles_only': False
}

# Source suffix
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

# epub options
epub_basename = project
epub_theme = 'epub'
epub_title = project
epub_author = author
epub_publisher = 'sorter.social'
epub_copyright = copyright
epub_show_urls = 'footnote'