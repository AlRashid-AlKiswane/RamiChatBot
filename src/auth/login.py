import logging
import os
import sys
import jwt
from datetime import datetime, timedelta
from sqlite3 import connect, Error as SQLError

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jwt import PyJWTError

try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    if not os.path.exists(MAIN_DIR):
        raise FileNotFoundError(f"Project directory not found at: {MAIN_DIR}")

    # Add to Python path only if it's not already there
    if MAIN_DIR not in sys.path:
        sys.path.append(MAIN_DIR)

    from src.helpers import get_settings, Settings
    from src.logs import log_info, log_warning, log_error
except ModuleNotFoundError as e:
    logging.error("Module not found: %s", e, exc_info=True)
except ImportError as e:
    logging.error("Import error: %s", e, exc_info=True)
except Exception as e:
    logging.critical("Unexpected setup error: %s", e, exc_info=True)
    raise


# === Configuration === #
MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
DB_PATH = os.path.join(MAIN_DIR, "database/user.db")

app_settings: Settings = get_settings()
SECRET_KEY = app_settings.SECRET_KEY

if not SECRET_KEY or len(SECRET_KEY) < 32:
    raise ValueError("SECRET_KEY must be at least 32 characters long")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# === Password hashing context === #
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

# === Database Setup === #
try:
    conn = connect(DB_PATH, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT NOT NULL UNIQUE,
            hashed_password TEXT NOT NULL
        );
    """)
    conn.commit()
    log_info("[AUTH] User table ensured in database.")
except SQLError as e:
    log_error(f"[AUTH] SQLite error while initializing DB: {e}")
    raise RuntimeError("Failed to initialize user database.")

# === Helper Functions === #
def init_default_user(username: str = "admin", password: str = "admin") -> None:
    try:
        cursor.execute("SELECT * FROM users WHERE user = ?", (username,))
        if not cursor.fetchone():
            hashed = pwd_context.hash(password)
            cursor.execute("INSERT INTO users (user, hashed_password) VALUES (?, ?)", (username, hashed))
            conn.commit()
            log_info(f"[AUTH] Default user created: {username}")
        else:
            log_info("[AUTH] Default user already exists.")
    except SQLError as e:
        log_error(f"[AUTH] Error initializing default user: {e}")
    except Exception as e:
        log_error(f"[AUTH] Unexpected error in init_default_user: {e}")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        result = pwd_context.verify(plain_password, hashed_password)
        log_info("[AUTH] Password verification successful.")
        return result
    except Exception as e:
        log_error(f"[AUTH] Password verification failed: {e}")
        return False

def get_user(username: str) -> dict | None:
    try:
        cursor.execute("SELECT user, hashed_password FROM users WHERE user = ?", (username,))
        row = cursor.fetchone()
        if row:
            log_info(f"[AUTH] User found: {username}")
            return {"username": row[0], "hashed_password": row[1]}
        else:
            log_warning(f"[AUTH] User not found: {username}")
            return None
    except SQLError as e:
        log_error(f"[AUTH] Database error fetching user '{username}': {e}")
        return None
    except Exception as e:
        log_error(f"[AUTH] Unexpected error fetching user '{username}': {e}")
        return None

def authenticate_user(username: str, password: str) -> dict | bool:
    user = get_user(username)
    if not user:
        log_warning(f"[AUTH] Authentication failed: user '{username}' not found.")
        return False
    if not verify_password(password, user["hashed_password"]):
        log_warning(f"[AUTH] Authentication failed: invalid password for '{username}'.")
        return False
    log_info(f"[AUTH] Authentication successful: {username}")
    return user

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    try:
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire})

        encoded_jwt = jwt.encode(
            to_encode,
            SECRET_KEY,
            algorithm=ALGORITHM
        )
        log_info(f"[AUTH] Token created for user: {to_encode.get('sub')}")
        return encoded_jwt
    except Exception as e:
        log_error(f"[AUTH] Failed to create JWT: {e}")
        raise RuntimeError("Token creation failed")

async def get_current_user(request: Request, token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token:
        # Try from cookies if token is not in header
        token = request.cookies.get("access_token")
        if token:
            if token.startswith("Bearer "):
                token = token[len("Bearer "):]
            else:
                log_warning("Token doesn't start with Bearer prefix.")
                raise credentials_exception
        else:
            log_warning("No token found in request headers or cookies.")
            raise credentials_exception
    
    try:
        # Decoding the JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            log_warning("JWT token missing 'sub' field.")
            raise credentials_exception
        user = get_user(username)
        if user is None:
            log_warning(f"User {username} not found in DB.")
            raise credentials_exception
        log_info(f"User {username} authenticated successfully.")
        return user
    except PyJWTError as e:
        log_error(f"JWT decoding error: {e}")
        raise credentials_exception
