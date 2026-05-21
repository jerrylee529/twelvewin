# -*- coding: utf-8 -*-

"""Base job runner — delegates to compute.runner (no Flask dependency)."""

from compute.runner import JobRunner, Step  # noqa: F401

__all__ = ['JobRunner', 'Step']
