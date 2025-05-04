"""
LDM Calculator module
Calculates Load Meter (LDM) for cargo based on vehicle type and cargo dimensions.
"""
import math


def calculate_ldm(cargo_list: list[dict], vehicle_type: str) -> float:
    """
    Calculate Load Meter (LDM) for the given cargo list and vehicle type.
    
    Args:
        cargo_list: List of cargo items with dimensions and count
        vehicle_type: Type of the vehicle ("bus", "solówka", or "naczepa")
        
    Returns:
        float: Total LDM value rounded to 2 decimal places
    """
    # Vehicle width in cm
    vehicle_width = 240
    
    total_ldm = 0
    
    for cargo in cargo_list:
        count = cargo.get("count", 0)
        width = cargo.get("width", 0)  # cm
        length = cargo.get("length", 0)  # cm
        
        # Determine the most efficient orientation (can rotate cargo)
        # We want to maximize how many pieces can fit across the width
        width_rotated = min(width, length)
        length_rotated = max(width, length)
        
        # How many pieces fit in one row across the vehicle width
        fit_by_width = max(1, int(vehicle_width / width_rotated))
        
        # Calculate number of rows needed
        rows_needed = math.ceil(count / fit_by_width)
        
        # Calculate LDM for this cargo item
        # Convert cm to meters for LDM calculation
        cargo_ldm = rows_needed * (length_rotated / 100)
        
        total_ldm += cargo_ldm
    
    # Round to 2 decimal places
    return round(total_ldm, 2)