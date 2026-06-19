"""
File Name: src/__init__.py
Purpose: Marks the 'src' directory as a Python package.
Relation to Project: Allows package-level relative and absolute imports (e.g., importing src.database or src.agent) and enables Gunicorn to run the WSGI application as a module (src.app:app).
Responsibilities:
  - Establishes the 'src' directory namespace inside the Python interpreter runtime.
"""
