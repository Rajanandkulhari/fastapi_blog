from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import models
from database import get_db
from schema import PostResponse, UserCreate, UserPublicResponse, UserUpdate, UserPrivateResponse, Token

from datetime import timedelta
from config import settings
from fastapi.security import OAuth2PasswordRequestForm
from auth import create_access_token, verify_access_token, verify_password, oauth2_scheme , hash_password

router = APIRouter()


#  Creating the new user

@router.post("",response_model=UserPrivateResponse,status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db:Annotated[AsyncSession, Depends(get_db)]):
        result = await db.execute(
            select(models.User).where(func.lower(models.User.username) == user.username.lower())
        )
        existing_username = result.scalars().first()


        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        
        result = await db.execute(
            select(models.User).where(func.lower(models.User.email) == user.email.lower())
        )
        existing_email = result.scalars().first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exist"
            )

        new_user = models.User(
            username = user.username,
            email = user.email.lower(),       # emails are case insensitive by design so we will diaplay in lower case only
            password_hash = hash_password(user.password)
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        return new_user


## login_for_access_token
@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    # Look up user by email (case-insensitive)
    # Note: OAuth2PasswordRequestForm uses "username" field, but we treat it as email
    result = await db.execute(
        select(models.User).where(
            func.lower(models.User.email) == form_data.username.lower()
        ),
    )
    user = result.scalars().first()

    # Verify user exists and password is correct
    # Don't reveal which one failed (security best practice)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token with user id as subject
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type="bearer")



@router.get("/me", response_model=UserPrivateResponse)
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get the currently authenticated user."""
    user_id = verify_access_token(token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Validate user_id is a valid integer (defense against malformed JWT)
    try:
        user_id_int = int(user_id)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await db.execute(
        select(models.User).where(models.User.id == user_id_int),
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user



# updating an existing user using put

@router.put("/{user_id}",response_model=UserPrivateResponse,)
async def update_user_full(user_id: int,user_data:UserCreate, db:Annotated[AsyncSession, Depends(get_db)]):
        result = await db.execute(
            select(models.User).where(models.User.id == user_id)
        )
        user = result.scalars().first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No user found"
            )
        
        if user_data.username:
            result = await db.execute(
                select(models.User).where(func.lower(models.User.username) == user_data.username.lower(), models.User.id != user_id)
            )
            existing_username = result.scalars().first()
            if existing_username:
                raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="username already exist"
            )

        if user_data.email:
            result = await db.execute(select(models.User).where(func.lower(models.User.email) == user_data.email.lower(), models.User.id != user_id))    
            existing_email = result.scalars().first()
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already exist"
                )

        user.username = user_data.username
        user.email = user_data.email
        
       
        await db.commit()
        await db.refresh(user)

        return user




#  partially udating an existing user using patch

@router.patch("/{user_id}",response_model=UserPrivateResponse,)
async def update_user_partial(user_id: int,user_data:UserUpdate, db:Annotated[AsyncSession, Depends(get_db)]):
        result = await db.execute(
            select(models.User).where(models.User.id == user_id)
        )
        user = result.scalars().first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No user found"
            )
        
        if user_data.username:
            result = await db.execute(
                select(models.User).where(func.lower(models.User.username) == user_data.username.lower(), models.User.id != user_id)
            )
            existing_username = result.scalars().first()
            if existing_username:
                raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="username already exist"
            )

        if user_data.email:
            result = await db.execute(select(models.User).where(func.lower(models.User.email) == user_data.email.lower(), models.User.id != user_id))    
            existing_email = result.scalars().first()
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already exist"
                )

        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
         setattr(user,field, value)
    
        await db.commit()
        await db.refresh(user)

        return user


# Deleting an existing user

@router.delete("/{user_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id:int, db:Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    await db.delete(user)
    await db.commit()



#  Getting the existing User in api model

@router.get("/{user_id}", response_model=UserPublicResponse)
async def get_user(user_id:int, db:Annotated[AsyncSession, Depends(get_db)]):

    result = await db.execute(
        select(models.User).where(models.User.id == user_id)
    )
    user = result.scalars().first()
    if user:
        return user
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found"
    )


#   Getting all the post of a specific user using its user id in api model

@router.get("/{user_id}/posts", response_model=list[PostResponse])
async def get_user_posts(user_id:int, db:Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
              select(models.User).where(models.User.id == user_id)  
            )
    user = result.scalars().first()
    if not user:
      raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found"
      )
    result = await db.execute(select(models.Post).options(selectinload(models.Post.author)).where(models.Post.user_id == user_id).order_by(models.Post.date_posted.desc()))
    posts = result.scalars().all()
    return posts