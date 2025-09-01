import re
import random
import string
from flask import flash


def validate_email(email):
    """Validate email format"""
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password):
    """Validate password strength"""
    if not password:
        return False, "Password is required"
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    if len(password) > 10:
        return False, "Password must be no more than 10 characters long"
    return True, ""


def validate_name(name, field_name):
    """Validate name fields"""
    if not name:
        return False, f"{field_name} is required"
    if len(name.strip()) < 2:
        return False, f"{field_name} must be at least 2 characters long"
    if not name.replace(' ', '').replace('-', '').isalpha():
        return False, f"{field_name} can only contain letters, spaces, and hyphens"
    return True, ""


def validate_username(username):
    """
    Validate username format and requirements

    Rules:
    - 3-20 characters long
    - Can contain letters, numbers, underscores, and dots
    - Must start with a letter
    - Cannot end with a dot
    - Cannot have consecutive dots
    - Cannot contain spaces or special characters (except _ and .)
    """
    if not username:
        return False, "Username is required"

    # Remove whitespace
    username = username.strip()

    # Check length
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"
    if len(username) > 20:
        return False, "Username must be no more than 20 characters long"

    # Check if starts with letter
    if not username[0].isalpha():
        return False, "Username must start with a letter"

    # Check if ends with dot
    if username.endswith('.'):
        return False, "Username cannot end with a dot"

    # Check for valid characters (letters, numbers, underscore, dot)
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_.]*$', username):
        return False, "Username can only contain letters, numbers, underscores, and dots"

    # Check for consecutive dots
    if '..' in username:
        return False, "Username cannot contain consecutive dots"

    # Check for reserved usernames
    reserved_usernames = [
        'admin', 'administrator', 'root', 'user', 'test', 'guest', 'anonymous',
        'moderator', 'mod', 'support', 'help', 'info', 'contact', 'about',
        'login', 'register', 'signup', 'signin', 'logout', 'profile', 'settings',
        'api', 'www', 'mail', 'email', 'ftp', 'blog', 'news', 'forum'
    ]

    if username.lower() in reserved_usernames:
        return False, "This username is not available"

    return True, ""


def generate_username_from_name(first_name, last_name, max_attempts=10):
    """
    Generate a unique username based on first and last name

    Args:
        first_name (str): User's first name
        last_name (str): User's last name
        max_attempts (int): Maximum attempts to generate unique username

    Returns:
        str: Generated username
    """
    # Clean the names
    first_name = re.sub(r'[^a-zA-Z]', '', first_name.strip()).lower()
    last_name = re.sub(r'[^a-zA-Z]', '', last_name.strip()).lower()

    if not first_name or not last_name:
        return None

    # Generate base username variations
    base_options = [
        f"{first_name}{last_name}",  # johnsmith
        f"{first_name}.{last_name}",  # john.smith
        f"{first_name}_{last_name}",  # john_smith
        f"{first_name}{last_name[0]}",  # johns
        f"{first_name[0]}{last_name}",  # jsmith
        f"{first_name[0]}.{last_name}",  # j.smith
        f"{first_name}_{last_name[0]}",  # john_s
    ]

    # Try each base option
    for base in base_options:
        if len(base) >= 3 and len(base) <= 20:
            # Try the base username first
            is_valid, _ = validate_username(base)
            if is_valid and is_username_available(base):
                return base

            # If base is taken, try with numbers
            for i in range(1, max_attempts + 1):
                candidate = f"{base}{i}"
                if len(candidate) <= 20:
                    is_valid, _ = validate_username(candidate)
                    if is_valid and is_username_available(candidate):
                        return candidate

    # If all attempts failed, generate a random username
    return generate_random_username(first_name, last_name)


def generate_random_username(first_name="user", last_name="", length=8):
    """
    Generate a random username as fallback

    Args:
        first_name (str): Optional first name to include
        last_name (str): Optional last name to include
        length (int): Total length of username

    Returns:
        str: Random username
    """
    # Clean first name
    clean_first = re.sub(r'[^a-zA-Z]', '', first_name.strip()).lower()

    if clean_first:
        # Use first few letters of first name + random string
        base_len = min(4, len(clean_first))
        base = clean_first[:base_len]
        remaining_len = length - base_len

        if remaining_len > 0:
            random_part = ''.join(random.choices(string.digits, k=remaining_len))
            return base + random_part

    # Pure random username if no valid first name
    letters = ''.join(random.choices(string.ascii_lowercase, k=4))
    numbers = ''.join(random.choices(string.digits, k=4))
    return letters + numbers


def is_username_available(username):
    """
    Check if username is available in the database

    Args:
        username (str): Username to check

    Returns:
        bool: True if available, False if taken
    """
    from .models import User
    existing_user = User.query.filter_by(username=username).first()
    return existing_user is None


def suggest_usernames(first_name, last_name, count=5):
    """
    Generate multiple username suggestions

    Args:
        first_name (str): User's first name
        last_name (str): User's last name
        count (int): Number of suggestions to generate

    Returns:
        list: List of suggested usernames
    """
    suggestions = []

    # Clean names
    first_name = re.sub(r'[^a-zA-Z]', '', first_name.strip()).lower()
    last_name = re.sub(r'[^a-zA-Z]', '', last_name.strip()).lower()

    if not first_name or not last_name:
        return []

    # Generate different patterns
    patterns = [
        f"{first_name}{last_name}",
        f"{first_name}.{last_name}",
        f"{first_name}_{last_name}",
        f"{first_name}{last_name[0]}",
        f"{first_name[0]}{last_name}",
        f"{first_name[0]}.{last_name}",
        f"{last_name}{first_name[0]}",
        f"{first_name}_{last_name[0]}",
    ]

    for pattern in patterns:
        if len(pattern) >= 3 and len(pattern) <= 20:
            is_valid, _ = validate_username(pattern)
            if is_valid and is_username_available(pattern):
                suggestions.append(pattern)
                if len(suggestions) >= count:
                    break

    # If we don't have enough suggestions, add numbered variations
    while len(suggestions) < count and patterns:
        base = patterns[0]
        for i in range(1, 100):
            candidate = f"{base}{i}"
            if len(candidate) <= 20:
                is_valid, _ = validate_username(candidate)
                if is_valid and is_username_available(candidate):
                    suggestions.append(candidate)
                    if len(suggestions) >= count:
                        break
            if len(suggestions) >= count:
                break
        patterns.pop(0)  # Remove the pattern we just tried

    return suggestions[:count]


# Example usage:
"""
# Validate a username
is_valid, error_message = validate_username("john.smith")

# Generate username from names
username = generate_username_from_name("John", "Smith")

# Get multiple suggestions
suggestions = suggest_usernames("John", "Smith", 3)

# Check if username is available
available = is_username_available("johnsmith")
"""