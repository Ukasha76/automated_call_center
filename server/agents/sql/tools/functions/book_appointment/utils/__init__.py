# This file makes the book_appointment directory a Python package

# Explicit imports to avoid circular dependencies
from .complete_booking import complete_booking

__all__ = [
  'complete_booking'

]
