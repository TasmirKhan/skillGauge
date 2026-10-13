from .assessments import router as assessments_router
from .questions import router as questions_router
from .skills import router as skills_router

__all__ = ["assessments_router", "questions_router", "skills_router"]
