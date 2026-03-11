import secrets
import string

def generate_credentials(length: int = 6) -> str:
    """
    Kriptografik jihatdan xavfsiz, 6 xonali tasodifiy 
    harf va raqamlardan iborat kombinatsiya yaratadi.
    
    Misol: '7K2P9X', 'A1B8N4'
    """
    # Katta harflar va raqamlar to'plami (chalkashlik bo'lmasligi uchun 'I', 'l', '0', 'O' kabilarni olib tashlash ham mumkin)
    characters = string.ascii_uppercase + string.digits
    
    # secrets kutubxonasi randomga qaraganda xavfsizroq hisoblanadi
    code = ''.join(secrets.choice(characters) for _ in range(length))
    return code

def generate_auth_pair():
    """
    Bir vaqtning o'zida ham login, ham parol yaratib beradi.
    """
    login = generate_credentials(6)
    password = generate_credentials(6)
    return login, password