def validate_json_address(data):
    required_keys = {"name", "phoneNo", "address", "city", "state", "pinCode"}
    if not isinstance(data, dict):
        raise ValueError("additional_info must be a dictionary.")

    missing_keys = required_keys - data.keys()
    if missing_keys:
        raise ValueError(f"Missing keys in additional_info: {missing_keys}")
