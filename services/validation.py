"""
Validation module
Validates cargo dimensions and provides appropriate messages based on business rules.
"""

def validate(data: dict, ldm: float) -> list[str]:
    """
    Validate the cargo data and LDM against business rules.
    
    Args:
        data: Dictionary containing cargo and transport data
        ldm: Calculated Load Meter value
        
    Returns:
        list[str]: List of validation messages
    """
    messages = []
    
    # Maximum LDM values for different vehicle types
    max_ldm = {
        "bus": 4.5,
        "solówka": 7.3,
        "naczepa": 13.6
    }
    
    vehicle_type = data.get("vehicle_type", "")
    
    # Validate LDM against vehicle type
    if vehicle_type in max_ldm:
        vehicle_max_ldm = max_ldm[vehicle_type]
        
        # Check if LDM exceeds maximum for the vehicle
        if ldm > vehicle_max_ldm:
            messages.append("Gabaryt za duży na wybrany typ pojazdu – zmień pojazd.")
        
        # Check if LDM is less than 80% of the maximum
        elif ldm < 0.8 * vehicle_max_ldm:
            messages.append("Wybranie konkretnego pojazdu oznacza wynajem jego całości – rozważ wybór 'dowolny'.")
    
    # Validate cargo dimensions
    for cargo in data.get("cargo", []):
        height = cargo.get("height", 0)
        width = cargo.get("width", 0)
        length = cargo.get("length", 0)
        
        # Check if cargo is too high
        if height > 260:
            messages.append("Ładunek jest za wysoki.")
        
        # Check if cargo might be oversized
        if width > 240 or length > 1360:
            messages.append("Ładunek może być ponadgabarytowy.")
    
    # Add urgent message if the delivery is marked as urgent
    if data.get("is_urgent", False):
        messages.append("Zlecenie jest pilne – spedytor skontaktuje się dziś telefonicznie.")
    
    return messages