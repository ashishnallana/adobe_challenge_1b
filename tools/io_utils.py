import json

def save_json_output(data, output_path):
    try:
        # Read existing content
        with open(output_path, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # If file doesn't exist or is empty, start with an empty list
        existing_data = []

    # Ensure existing_data is a list
    if not isinstance(existing_data, list):
        existing_data = [existing_data]

    # Append new data
    existing_data.append(data)

    # Write updated content back to the file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, indent=4, ensure_ascii=False)