"""
Hash generation library.
"""

from string import ascii_letters, ascii_uppercase, digits
from random import choice

def generic_id_generator(size, chars):
    """
    Generate a random hash.
    """
    return ''.join(choice(chars) for _ in range(size))

def file_id_generator(size=6, chars=ascii_letters+digits):
    """
    Generate a random hash for the temp files.
    """
    return generic_id_generator(size, chars)

def title_id_generator(size=6, chars=ascii_uppercase+digits):
    """
    Generate a random hash for GitHub titles.
    """
    return generic_id_generator(size, chars)
