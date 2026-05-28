"""
Resume Optimizer Engine

Auto-generates optimized resume based on analysis recommendations without fabrication.
"""
from .optimizer import ResumeOptimizer
from .diff_generator import DiffGenerator
from .models import OptimizedResume, Change

__all__ = [
    'ResumeOptimizer',
    'DiffGenerator',
    'OptimizedResume',
    'Change'
]
