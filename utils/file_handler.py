def append_to_file(filename, text):
    with open(filename, 'a') as file:
        file.write(text + '\n')

def remove_line_from_file(filename, text_to_remove):
    if not isinstance(filename, str):
        raise ValueError("Filename must be a string.")
    if not isinstance(text_to_remove, str):
        raise ValueError("Text to remove must be a string.")
    
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
        
        lines = [line for line in lines if line.strip() != text_to_remove]
        
        with open(filename, 'w') as file:
            file.writelines(lines)
    
    except IOError as e:
        print(f"An error occurred while accessing the file: {e}")

def exclude_entries(blocked_websites, file_path):
    try:
        with open(file_path, "r") as file:
            domains_to_remove = {line.strip() for line in file if line.strip()}
        updated_blocked_websites = [domain for domain in blocked_websites if domain not in domains_to_remove]
        return updated_blocked_websites
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return blocked_websites
    
def add_blocked_websites(blocked_websites, file_path):
    try:
        with open(file_path, "r") as file:
            new_domains = {line.strip() for line in file if line.strip()}
        updated_blocked_websites = blocked_websites + [domain for domain in new_domains if domain not in blocked_websites]
        return updated_blocked_websites
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return blocked_websites