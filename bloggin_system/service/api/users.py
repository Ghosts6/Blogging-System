from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
import secrets
from django.utils import timezone

router = APIRouter()
User = get_user_model()

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class PasswordReset(BaseModel):
    username: str
    new_password: str

class PasswordResetRequest(BaseModel):
    email: str

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

@router.post("/signup/")
def create_user(user: UserCreate):
    if User.objects.filter(username=user.username).exists():
        raise HTTPException(status_code=400, detail="Username already exists")
    new_user = User.objects.create_user(username=user.username, email=user.email, password=user.password)
    return {"message": "User created successfully"}

@router.post("/login/")
def login(form_data: UserLogin):
    User = get_user_model()
    try:
        user = authenticate(username=form_data.username, password=form_data.password)
        if not user:
            raise HTTPException(status_code=400, detail="Invalid credentials")
        token, _ = Token.objects.get_or_create(user=user)
        return {"access_token": token.key, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/password_reset/")
def reset_password(data: PasswordReset):
    try:
        user = User.objects.get(username=data.username)
        user.set_password(data.new_password)
        user.save()
        return {"message": "Password updated successfully"}
    except User.DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")

@router.post("/password-reset-request/")
def password_reset_request(data: PasswordResetRequest):
    try:
        user = User.objects.get(email=data.email)
        token = secrets.token_urlsafe(32)
        user.password_reset_token = token
        user.password_reset_token_created_at = timezone.now()
        user.save()
        # In good practice, you would email the token to the user
        # For this example, we'll just return it
        return {"token": token}
    except User.DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")

@router.post("/password-reset-confirm/")
def password_reset_confirm(data: PasswordResetConfirm):
    try:
        user = User.objects.get(password_reset_token=data.token)
        if user.password_reset_token_created_at is None:
            raise HTTPException(status_code=400, detail="Invalid token")
        time_diff = timezone.now() - user.password_reset_token_created_at
        if time_diff.total_seconds() > 3600:
            raise HTTPException(status_code=400, detail="Token expired")
        user.set_password(data.new_password)
        user.password_reset_token = None
        user.password_reset_token_created_at = None
        user.save()
        return {"message": "Password updated successfully"}
    except User.DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")
