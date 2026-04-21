from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import models
from database import get_db

from auth import CurrentUser

router = APIRouter()

#getting saved posts of a user

@router.get("")
async def get_user_saved_posts(current_user:CurrentUser, db:Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.Post)
                              .join(models.SavedPost)
                              .where(models.SavedPost.user_id == current_user.id)
                              .order_by(models.SavedPost.date_saved.desc()))
    posts = result.scalars().all()
    return posts


#saving post in saved posts using api route

@router.put("/{post_id}")
async def save_new_post(post_id: int,current_user:CurrentUser,db:Annotated[AsyncSession, Depends(get_db)]):
    
    result =await  db.execute(select(models.Post).where(models.Post.id== post_id))
    post = result.scalars().first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="post not found"
        )
    result = await db.execute(select(models.SavedPost)
                              .where((models.SavedPost.user_id==current_user.id) 
                                     & (models.SavedPost.post_id==post_id)))
    existing_post = result.scalars().first()
    
    if existing_post:
        raise HTTPException(
            status_code= status.HTTP_409_CONFLICT,
            detail="post already saved"
        )
    saved_post = models.SavedPost(
        user_id= current_user.id,
        post_id = post_id
    )
    db.add(saved_post)
    await db.commit()
    await db.refresh(saved_post)
    return saved_post

# deleting a saved post folder

@router.delete("/{post_id}")
async def delete_saved_post(post_id:int,current_user:CurrentUser,db:Annotated[AsyncSession, Depends(get_db)]):
    result =await  db.execute(select(models.SavedPost).where((models.SavedPost.post_id== post_id)& models.SavedPost.user_id ==current_user.id))
    post = result.scalars().first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="post not found"
        )
    await db.delete(post)
    await db.commit()