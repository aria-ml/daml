# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

project = "DAML"
copyright = "2023, ARiA"
author = "ARiA"

site_url = "https://jatic.pages.jatic.net/aria/daml/"
repo_url = "https://gitlab.jatic.net/jatic/aria/daml"
repo_name = "DAML"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.graphviz",
    "sphinx_rtd_size",
    "myst_nb",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

autosummary_generate = False
sphinx_rtd_size_width = "80%"
nb_execution_timeout = -1

# html_static_path = ['_static']
html_theme = "sphinx_rtd_theme"
html_show_sourcelink = False
html_theme_options = {
    "navigation_depth": 4,
}


# because we expose private modules in public namespaces
# and rename some classes, documentation recognizes these
# public classes as aliases, which we don't want
def normalize_module(mod_names):
    import importlib

    for mod_name in mod_names:
        mod = importlib.import_module(mod_name)
        for cls_name in mod.__all__:
            cls = getattr(mod, cls_name)
            cls.__name__ = cls_name
            cls.__module__ = mod_name


def setup(app):
    normalize_module(
        [
            "daml.metrics.ber",
            "daml.metrics.divergence",
            "daml.metrics.outlier_detection",
        ]
    )
