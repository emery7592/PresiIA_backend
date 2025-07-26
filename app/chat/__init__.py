"""
Expose les éléments clés du module.
Permet : `from chat import chat` ou `from chat import router`.
"""
from .services import chat  # noqa: F401
from .router import router  # noqa: F401
