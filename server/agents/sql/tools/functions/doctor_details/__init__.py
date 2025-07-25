# This file makes the doctor_details directory a Python package

# Explicit imports to avoid circular dependencies

from .get_doctor_name import get_doctor_name
from .extract_doctor_details import extract_doctor_details
    
__all__ = ['get_doctor_name', 'extract_doctor_details']

