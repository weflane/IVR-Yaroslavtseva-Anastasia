from fastapi import APIRouter, HTTPException, Depends
from app import models, schemas
from app.auth_utils import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=schemas.UserOut, status_code=201)
def register(body: schemas.UserRegister):
    """Register new user"""
    if models.User.objects(email=body.email).first():
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")
    user = models.User( 
        email=body.email,
        password_hash=hash_password(body.password)
    )
    user.save()
    return user


@router.post("/login", response_model=schemas.TokenResponse)
def login(body: schemas.UserLogin):
    """Login user"""
    user = models.User.objects(email=body.email).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Неверный email или пароль")

    return {"access_token": create_access_token(str(user.id))}


@router.get("/me", response_model=schemas.UserOut)
def me(current_user: models.User = Depends(get_current_user)):
    """Get current user info"""
    return current_user
