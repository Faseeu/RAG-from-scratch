class MemoryError_(Exception):
    """Base class for this module's errors (named to avoid shadowing builtin)."""


class HistoryCorruptedError(MemoryError_):
    """Raised when a history file exists but can't be parsed safely."""


class SessionNotFoundError(MemoryError_):
    """Raised when a referenced session_id doesn't exist in the index."""
