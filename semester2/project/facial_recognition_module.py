import random

def find_closest_match(login_image_data, db_images_dict):
    """
    Mock implementation of facial recognition.
    
    Args:
        login_image_data: The webcam frame (bytes or base64).
        db_images_dict: Dict mapping {uid: image_data}.
        
    Returns:
        Matched uid or None.
    """
    print("Mock find_closest_match called.")
    
    if not db_images_dict:
        print("Database images dict is empty.")
        return None
        
    # Simulate a match with some probability
    # For testing, let's just return the first user in the dict if dict is not empty
    # in a real scenario we would compare images.
    
    keys = list(db_images_dict.keys())
    if keys:
        # Simulate success (confidence <= 0.7)
        matched_uid = keys[0]
        print(f"Mock match found: {matched_uid}")
        return matched_uid
        
    return None
