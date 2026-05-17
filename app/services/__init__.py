"""Application service layer.

Services keep file/database/cache access out of Flask route handlers so the
HTTP layer can stay thin and the core behavior can be tested independently.
"""
