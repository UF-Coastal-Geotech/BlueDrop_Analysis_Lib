# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'BlueDropAnalysis'
copyright = '2024, WaveHello'
author = 'WaveHello'
release = '0.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration
import os
import sys

# Function to add all subdirectories to sys.path
def add_subdirectories_to_path(directory):
    for root, dirs, files in os.walk(directory):
        sys.path.insert(0, root)

# Add the 'lib' directory and all its subdirectories to the Python path
add_subdirectories_to_path(os.path.abspath('..'))
# sys.path.insert(0, os.path.abspath('../lib'))
print("Current working dir:", os.getcwd())
print("system path: \n", sys.path)

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',  # For Google and NumPy style docstrings
    'sphinx.ext.autosectionlabel', # For automatically generate section labels and references
]

# Document all members (methods and attributes) of each class
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
}

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
