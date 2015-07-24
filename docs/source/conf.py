# -*- coding: utf-8 -*-
#
import sys
import os
import shlex

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.coverage',
    'sphinx.ext.viewcode',
    'sphinx.ext.graphviz',
]

templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
project = u'Discovery Layer'
copyright = u'2015, AusDTO'
author = u'AusDTO'
version = '0.1'
release = '0.1.0'
language = None
exclude_patterns = []
pygments_style = 'sphinx'
todo_include_todos = False
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
htmlhelp_basename = 'DiscoveryLayerdoc'

latex_elements = {
'papersize': 'a4paper',
}

latex_documents = [
  (master_doc, 'DiscoveryLayer.tex', u'Discovery Layer Documentation',
   u'AusDTO', 'manual'),
]

texinfo_documents = [
  (master_doc, 'DiscoveryLayer', u'Discovery Layer Documentation',
   author, 'DiscoveryLayer', 'One line description of project.',
   'Miscellaneous'),
]
