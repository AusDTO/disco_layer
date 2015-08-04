# -*- coding: utf-8 -*-
#
import sys
import os
import shlex

from gitdiscribe import Gitdiscribe
gd = Gitdiscribe('../../')
if gd.tag != '':
    VERSION = gd.tag_number
    gd.write_version_file()
else:
    from version import VERSION

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.coverage',
    'sphinx.ext.viewcode',
    'sphinx.ext.graphviz',
]

templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
project = u'AusDTO Discovery Layer'
copyright = u'2015, Commonwealth of Australia'
author = u'Digital Transformation Office'
version = VERSION
release = VERSION
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
  (master_doc, 'DiscoveryLayer.tex', u'AusDTO Discovery Layer',
   u'Commonwealth of Australia, Digital Transformation Office', 'manual'),
]

texinfo_documents = [
  (master_doc, 'DiscoveryLayer', u'AusDTO Discovery Layer',
   author, 'Commonwealth of Australia, Digital Transformation Office',
   'Technical Documentation',
   'Miscellaneous'),
]
