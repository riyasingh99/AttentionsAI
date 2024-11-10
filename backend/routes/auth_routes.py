from fastapi import APIRouter, HTTPException, status
from models.user_models import UserCreate, UserLogin
from database.db_setup import users_collection
from utils.hashing import hash_password, verify_password
import re

router = APIRouter()

# Enhanced user registration route with additional constraints
@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate):
    # Check if user already exists
    if users_collection.find_one({"username": user.username}):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")
    
    if users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    # Validate email format to ensure it ends with '@gmail.com'
    if not user.email.endswith("@gmail.com"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email must be a valid address ending with '@gmail.com'"
        )

    # Validate password length (6 to 10 characters) and complexity
    if (len(user.password) < 6 or len(user.password) > 10 or
        not re.search(r"[A-Z]", user.password) or    # At least one uppercase letter
        not re.search(r"[a-z]", user.password) or    # At least one lowercase letter
        not re.search(r"\d", user.password) or       # At least one digit
        not re.search(r"[!@#$%^&*(),.?\":{}|<>]", user.password)):  # At least one special character
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be 6-10 characters long and include at least one uppercase letter, "
                   "one lowercase letter, one number, and one special character"
        )

    # Hash the password and store the user
    hashed_password = hash_password(user.password)
    users_collection.insert_one({
        "username": user.username,
        "email": user.email,
        "password": hashed_password
    })
    return {"message": "User registered successfully"}

# Enhanced user login route
@router.post("/login")
async def login_user(user: UserLogin):
    db_user = users_collection.find_one({"username": user.username})

    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not verify_password(user.password, db_user['password']):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    return {"message": "Login successful"}

