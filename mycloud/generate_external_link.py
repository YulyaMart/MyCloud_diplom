import random
import string


def generate_external_link_key():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(6))