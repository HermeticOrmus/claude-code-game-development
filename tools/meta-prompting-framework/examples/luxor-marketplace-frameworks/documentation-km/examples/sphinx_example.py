"""
Sphinx Documentation Example
============================

Example implementation of auto-generated documentation using Sphinx
with custom extensions for the Documentation & Knowledge Management Framework.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Optional
import sphinx
from sphinx.application import Sphinx
from sphinx.util.docutils import SphinxDirective
from docutils import nodes
import ast


class EnhancedSphinxGenerator:
    """
    Enhanced Sphinx documentation generator with multi-level support.

    This class implements Level 3 (Auto-Generated Docs) of the framework,
    with hooks for higher levels like RAG integration and knowledge graphs.
    """

    def __init__(self, source_dir: str, build_dir: str = "_build"):
        """
        Initialize Sphinx generator.

        Args:
            source_dir: Directory containing source code
            build_dir: Directory for generated documentation
        """
        self.source_dir = Path(source_dir)
        self.build_dir = Path(build_dir)
        self.conf_path = self.source_dir / "conf.py"

    def setup_sphinx_project(self):
        """Setup Sphinx project with enhanced configuration."""

        # Create conf.py with custom settings
        conf_content = '''
# Sphinx configuration for Documentation Framework
import os
import sys
sys.path.insert(0, os.path.abspath('.'))

# Project information
project = 'Documentation Framework'
copyright = '2024, Framework Team'
author = 'Framework Team'

# Extensions
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.graphviz',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx_autodoc_typehints',
    'myst_parser',  # For Markdown support
]

# Custom extensions for framework
extensions.append('doc_framework_extensions')

# Napoleon settings for Google/NumPy docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True

# Autodoc settings
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}

# HTML theme
html_theme = 'sphinx_rtd_theme'
html_theme_options = {
    'navigation_depth': 4,
    'collapse_navigation': False,
    'sticky_navigation': True,
    'includehidden': True,
}

# RAG Integration settings
rag_enabled = True
rag_endpoint = "http://localhost:8000/rag"

# Knowledge Graph settings
kg_enabled = True
kg_database = "neo4j://localhost:7687"
'''

        # Create Sphinx directories
        self.source_dir.mkdir(parents=True, exist_ok=True)
        self.build_dir.mkdir(parents=True, exist_ok=True)

        # Write configuration
        with open(self.conf_path, 'w') as f:
            f.write(conf_content)

        # Create index.rst
        self._create_index_rst()

    def _create_index_rst(self):
        """Create main index.rst file."""
        index_content = '''
Documentation Framework
=======================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   introduction
   api_reference
   tutorials
   examples
   architecture

Auto-Generated API Documentation
---------------------------------

.. automodule:: main_module
   :members:
   :undoc-members:
   :show-inheritance:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
'''

        index_path = self.source_dir / "index.rst"
        with open(index_path, 'w') as f:
            f.write(index_content)

    def generate_module_docs(self, module_path: str) -> str:
        """
        Generate documentation for a Python module.

        Args:
            module_path: Path to Python module

        Returns:
            Generated RST documentation
        """
        with open(module_path, 'r') as f:
            source = f.read()

        tree = ast.parse(source)
        module_name = Path(module_path).stem

        rst = f"""
{module_name} Module
{'=' * (len(module_name) + 7)}

.. automodule:: {module_name}
   :members:
   :undoc-members:
   :show-inheritance:

Module Contents
---------------

"""

        # Extract classes and functions
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                rst += self._document_class(node, module_name)
            elif isinstance(node, ast.FunctionDef):
                rst += self._document_function(node, module_name)

        return rst

    def _document_class(self, node: ast.ClassDef, module_name: str) -> str:
        """Document a class."""
        return f"""
.. autoclass:: {module_name}.{node.name}
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

"""

    def _document_function(self, node: ast.FunctionDef, module_name: str) -> str:
        """Document a function."""
        return f"""
.. autofunction:: {module_name}.{node.name}

"""

    def build_documentation(self, format: str = "html"):
        """
        Build documentation in specified format.

        Args:
            format: Output format (html, pdf, epub, etc.)
        """
        app = Sphinx(
            srcdir=str(self.source_dir),
            confdir=str(self.source_dir),
            outdir=str(self.build_dir / format),
            doctreedir=str(self.build_dir / ".doctrees"),
            buildername=format,
        )

        app.build()

    def generate_api_reference(self, packages: List[str]) -> str:
        """
        Generate complete API reference.

        Args:
            packages: List of package names to document

        Returns:
            Generated API reference in RST format
        """
        api_ref = """
API Reference
=============

This section contains the complete API reference for all modules.

.. contents::
   :local:
   :depth: 2

"""

        for package in packages:
            api_ref += f"""
{package} Package
{'-' * (len(package) + 8)}

.. automodule:: {package}
   :members:
   :undoc-members:
   :show-inheritance:

"""

        return api_ref

    def integrate_with_rag(self):
        """
        Integrate generated documentation with RAG system.

        This method connects to Level 4 (RAG-Based Documentation).
        """
        # Parse generated HTML docs
        html_dir = self.build_dir / "html"

        documents = []
        for html_file in html_dir.rglob("*.html"):
            with open(html_file, 'r') as f:
                content = f.read()

            # Extract text content
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            text = soup.get_text()

            documents.append({
                'path': str(html_file),
                'content': text,
                'type': 'sphinx_generated',
                'metadata': {
                    'source': 'sphinx',
                    'format': 'html',
                    'module': html_file.stem
                }
            })

        # Send to RAG system
        from rag_integration import RAGConnector
        rag = RAGConnector()
        rag.index_documents(documents)

        return len(documents)

    def create_interactive_examples(self):
        """
        Create interactive documentation examples.

        This connects to Level 5 (Interactive Documentation).
        """
        # Create Jupyter notebook examples
        notebook_dir = self.source_dir / "notebooks"
        notebook_dir.mkdir(exist_ok=True)

        example_notebook = {
            "cells": [
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        "# Interactive Documentation Example\n",
                        "This notebook demonstrates the API usage interactively."
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "source": [
                        "# Import the framework\n",
                        "from doc_framework import DocumentationSystem\n",
                        "\n",
                        "# Initialize system\n",
                        "doc_sys = DocumentationSystem()\n",
                        "\n",
                        "# Generate documentation\n",
                        "result = doc_sys.generate('example.py')\n",
                        "print(result)"
                    ]
                }
            ],
            "metadata": {
                "kernelspec": {
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3"
                }
            },
            "nbformat": 4,
            "nbformat_minor": 4
        }

        import json
        notebook_path = notebook_dir / "example.ipynb"
        with open(notebook_path, 'w') as f:
            json.dump(example_notebook, f, indent=2)

        return str(notebook_path)


class CustomSphinxDirective(SphinxDirective):
    """
    Custom Sphinx directive for enhanced documentation features.

    This directive adds support for RAG queries and knowledge graph visualization
    directly in the documentation.
    """

    has_content = True
    required_arguments = 1
    optional_arguments = 0
    option_spec = {
        'type': str,
        'query': str,
        'depth': int,
    }

    def run(self):
        """Execute the directive."""
        directive_type = self.options.get('type', 'standard')

        if directive_type == 'rag_query':
            return self._handle_rag_query()
        elif directive_type == 'knowledge_graph':
            return self._handle_knowledge_graph()
        else:
            return self._handle_standard()

    def _handle_rag_query(self) -> List[nodes.Node]:
        """Handle RAG query directive."""
        query = self.options.get('query', '')

        # Create container for RAG results
        container = nodes.container()
        container += nodes.rubric(text="RAG Query Results")

        # Add query display
        query_node = nodes.literal_block(text=f"Query: {query}")
        container += query_node

        # Placeholder for dynamic RAG results
        result_node = nodes.paragraph(text="[RAG results will be populated here]")
        container += result_node

        return [container]

    def _handle_knowledge_graph(self) -> List[nodes.Node]:
        """Handle knowledge graph visualization directive."""
        depth = self.options.get('depth', 2)

        # Create container for graph
        container = nodes.container()
        container += nodes.rubric(text="Knowledge Graph")

        # Add graph placeholder
        graph_node = nodes.raw(
            text=f'<div class="knowledge-graph" data-depth="{depth}"></div>',
            format='html'
        )
        container += graph_node

        return [container]

    def _handle_standard(self) -> List[nodes.Node]:
        """Handle standard directive."""
        para = nodes.paragraph()
        para += nodes.Text(self.arguments[0])
        return [para]


def setup(app: Sphinx):
    """
    Setup function for Sphinx extension.

    Args:
        app: Sphinx application instance
    """
    app.add_directive("doc_framework", CustomSphinxDirective)

    # Add custom configuration values
    app.add_config_value('rag_enabled', False, 'env')
    app.add_config_value('rag_endpoint', '', 'env')
    app.add_config_value('kg_enabled', False, 'env')
    app.add_config_value('kg_database', '', 'env')

    # Connect event handlers
    app.connect('build-finished', on_build_finished)

    return {
        'version': '1.0',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }


def on_build_finished(app: Sphinx, exception):
    """
    Handler for build-finished event.

    Args:
        app: Sphinx application
        exception: Any exception that occurred during build
    """
    if exception is None and app.config.rag_enabled:
        # Trigger RAG indexing
        generator = EnhancedSphinxGenerator(app.srcdir, app.outdir)
        generator.integrate_with_rag()


# Example usage
if __name__ == "__main__":
    # Initialize generator
    generator = EnhancedSphinxGenerator(
        source_dir="./src",
        build_dir="./_build"
    )

    # Setup Sphinx project
    generator.setup_sphinx_project()

    # Generate documentation for specific modules
    for module in ["main.py", "utils.py", "models.py"]:
        if os.path.exists(module):
            docs = generator.generate_module_docs(module)

            # Save to RST file
            rst_path = generator.source_dir / f"{Path(module).stem}.rst"
            with open(rst_path, 'w') as f:
                f.write(docs)

    # Build HTML documentation
    generator.build_documentation("html")

    # Integrate with RAG
    generator.integrate_with_rag()

    # Create interactive examples
    notebook_path = generator.create_interactive_examples()

    print(f"Documentation generated successfully!")
    print(f"HTML docs: {generator.build_dir / 'html' / 'index.html'}")
    print(f"Interactive notebook: {notebook_path}")