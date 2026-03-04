# core/security.py — PASSWORD HASHING & JWT TOKENS

# This File handles two things :
#   1. Hashing Password ( so we never store plain text)
#   2. Creating / Verifying JWT tokens (for authentication)

# JWT = JSON Web Token
# Its like signed "ID card" the user gets after login
# They send this card with every request to prove who they are.

from datetime import dattime, timedelta
from typing import Optional

# jose = Javascript Object Signing and Encrypyion
# we use it to create and decode JWT tokens
from jose import JWTError, jwt

# passlib handles password hashing securely 
# bcrypt is the hashing algorithm - industry sttandard 
from passlib.context import CryptContext

# Security Configuration
# SECRET_KEY : A random secret string used to sign tokens
# In production , store this in environmet varieble
# Never hardcode this in real apps
# ALGORITHM: the algoritm used to sign the JWT
# ACCESS_TOKEN_EXPIRE_MINUTES: how long tokens are valid 

SECRET_KEY = "you-super-secret-key"
ALGORITHM ="HS256" # HMAC with SHA-256
ACCESS_TOKEN_EXPIRE_MINUTES = 30

#PASSWORD CONTEXT
# THIS object knows how to hash and verify passwords,
# "bcrypt" is the hashing scheme = It's slow by design
# # (make brute-force attacks harder ) 
# deprecated= "auto" will auto-upgrade old hashes

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Takes a plain text password like "mysecret123"
    and returns a hashed version like "$2466$ab"
    We store the HASH in the database, never the plain text.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Checks if a plain text password matches the stored hash.
    Returns True if yes else False
    Example: verify_password("my_secret","$6257Svd")
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) ->str:
    """
    Creates JWT token containing the given data.
    The Token encodes:
        - The data (e.g user's email/id)
        - An expiry time (so tokens don't last forever)
    Examples: 
        {"sub":"user@exmple.com", "exp" : 1700000}

    The token looks like: "eyJhbGci...abc.def.ghi"
    It's a long string made of 3 parts separated by dots.
    """
    to_encode = data.copy() # copy the data so we dont modify the original

    # add expiry to the token payload
    if expires_delta:
        expire = datatime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutess=15) # default= 15 minutes

    # Add expiry to the token payload
    to_encode.update({"exp": expire})

    # Encode and sign the token using our secret key
    # The signature ensures nobody can tamper with the token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional(str):
    """
    Decodes a JWT token and extracts the user identifier (subject).
    Returns None if the token is invalid or expired.

    "sub" (sbuject)  is standard JWT field - we store the user's email there.
    """
    try:
        # Decode and VERIFY the token signature
        payload = jwt.decode(token, SECRET_KEY, algorithm=[ALGORITHM])

        #extract the "sub" (subject) field - we stored the email here
        email: str = payload.get("sub")

        if email is None:
            return None # Token doesn't have a subject

        return email
    except JWTError:
        #To ken is expired , tampered with or malformed
        return None