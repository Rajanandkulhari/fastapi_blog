from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, Request, HTTPException, status,Depends
from fastapi.exceptions import RequestValidationError

from fastapi.exception_handlers import (request_validation_exception_handler, http_exception_handler)

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteExceptionError

from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import models
from database import Base, get_db,engine

from routers import users, posts 

@asynccontextmanager
async def lifespan(_app:FastAPI):
    # startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
   #  Shutdown
    await engine.dispose()

app = FastAPI(lifespan= lifespan)

app.mount("/static",StaticFiles(directory = "static"), name="static")
app.mount("/media", StaticFiles(directory="media"), name="media")

templates = Jinja2Templates(directory ="templates")

app.include_router(users.router, prefix="/api/user", tags=["user"])
app.include_router(posts.router, prefix="/api/posts", tags=["posts"])



#  Home page route using database and displays all posts

@app.get("/",include_in_schema=False)   
@app.get("/posts",include_in_schema=False)    
async def home(request: Request, db:Annotated[AsyncSession, Depends(get_db)]) :
    result = await db.execute(select(models.Post).options(selectinload(models.Post.author)).order_by(models.Post.date_posted.desc()))
    posts = result.scalars().all()
    return templates.TemplateResponse(
        request,
        "home.html",
        {"posts":posts,
          "title":"Home"})



 # path parameter to get the post by its id


@app.get("/post/{post_id}",include_in_schema=False)            
async def post_page(request: Request,post_id: int,db:Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.Post).options(selectinload(models.Post.author)).where(models.Post.id == post_id))
    post = result.scalars().first()
     
    if post: 
          title = post.title[:50]
          return templates.TemplateResponse(
               request,
                 "post.html",
                 {"post":post, "title":title})
   
    raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail="Post not found")




#getting all post of the specific user using its user_id in html format 

@app.get("/user/{user_id}/posts", include_in_schema=False, name="user_posts")
async def user_post_page(request: Request, user_id: int, db:Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist"
        )
    result = await db.execute(select(models.Post).options(selectinload(models.Post.author)).where(models.Post.user_id == user_id).order_by(models.Post.date_posted.desc()))
    posts = result.scalars().all()
    return templates.TemplateResponse(
        request,
        "user_posts.html",
        {"posts":posts,
         "user":user,
          "title":"Home"}
    )


## login and register template_routes
@app.get("/login", include_in_schema=False)
async def login_page(request: Request):
    return templates.TemplateResponse(
        request,
        "login.html",
        {"title": "Login"},
    )


@app.get("/register", include_in_schema=False)
async def register_page(request: Request):
    return templates.TemplateResponse(
        request,
        "register.html",
        {"title": "Register"},
    )

@app.get("/account", include_in_schema=False)
async def account_page(request: Request):
    return templates.TemplateResponse(
        request,
        "account.html",
        {"title": "Account"},
    )


# Error handling using StarletteExceptionError for http errors

@app.exception_handler(StarletteExceptionError)
async def general_http_exception_handler(request: Request, exception: StarletteExceptionError):

    if request.url.path.startswith("/api"):
        return await http_exception_handler(request, exception)


    message = (
        exception.detail
        if exception.detail
        else "An error occured please check your request and try again "
    )
    
    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": exception.status_code,
            "title": exception.status_code,
            "message":message
        },
        status_code=exception.status_code,
    )


# Error handling for wrong inputs and wrong requests and it gives 422 error message

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exception:RequestValidationError):
    if request.url.path.startswith("/api"):
        return await request_validation_exception_handler(
           request,
           exception
        )
    
    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code":status.HTTP_422_UNPROCESSABLE_CONTENT,
            "title":status.HTTP_422_UNPROCESSABLE_CONTENT,
            "message":"Invalid request. Please check your request and try again"
        },
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
    )