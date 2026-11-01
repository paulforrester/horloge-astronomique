"""Gear-ratio engineering tools for the 1:8 Strasbourg clock replica (Phase 1)."""
from .core import Evaluation, Stage, Train, evaluate, format_period, max_teeth_for_diameter
from .search import Result, search_coaxial, search_compound, search_differential

__all__ = ["Evaluation", "Stage", "Train", "evaluate", "format_period", "max_teeth_for_diameter",
           "Result", "search_compound", "search_coaxial", "search_differential"]
