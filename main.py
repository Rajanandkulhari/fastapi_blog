from typing import Annotated

from fastapi import FastAPI, Request, HTTPException, status,Depends
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteExceptionError
from schema import PostCreate,PostResponse, UserCreate, UserReponse, PostUpdate, UserUpdate

from sqlalchemy import select
from sqlalchemy.orm import Session

import models
from database import Base, get_db,engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/static",StaticFiles(directory = "static"), name="static")
app.mount("/media", StaticFiles(directory="media"), name="media")

templates = Jinja2Templates(directory ="templates")



#  Creating the new user

@app.post("/api/user",response_model=UserReponse,status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db:Annotated[Session, Depends(get_db)]):
        result = db.execute(
            select(models.User).where(models.User.username == user.username)
        )
        existing_username = result.scalars().first()


        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        
        result = db.execute(
            select(models.User).where(models.User.email == user.email)
        )
        existing_email = result.scalars().first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exist"
            )

        new_user = models.User(
            username = user.username,
            email = user.email
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return new_user


# updating an existing user using put

@app.put("/api/user/{user_id}",response_model=UserReponse,)
def update_user_full(user_id: int,user_data:UserCreate, db:Annotated[Session, Depends(get_db)]):
        result = db.execute(
            select(models.User).where(models.User.id == user_id)
        )
        user = result.scalars().first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No user found"
            )
        
        if user_data.username:
            result = db.execute(
                select(models.User).where(models.User.username == user_data.username, models.User.id != user_id)
            )
            existing_username = result.scalars().first()
            if existing_username:
                raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="username already exist"
            )

        if user_data.email:
            result = db.execute(select(models.User).where(models.User.email == user_data.email, models.User.id != user_id))    
            existing_email = result.scalars().first()
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already exist"
                )

        user.username = user_data.username
        user.email = user_data.email
        
       
        db.commit()
        db.refresh(user)

        return user





#  partially udating an existing user using patch

@app.patch("/api/user/{user_id}",response_model=UserReponse,)
def update_user_partial(user_id: int,user_data:UserUpdate, db:Annotated[Session, Depends(get_db)]):
        result = db.execute(
            select(models.User).where(models.User.id == user_id)
        )
        user = result.scalars().first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No user found"
            )
        
        if user_data.username:
            result = db.execute(
                select(models.User).where(models.User.username == user_data.username, models.User.id != user_id)
            )
            existing_username = result.scalars().first()
            if existing_username:
                raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="username already exist"
            )

        if user_data.email:
            result = db.execute(select(models.User).where(models.User.email == user_data.email, models.User.id != user_id))    
            existing_email = result.scalars().first()
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already exist"
                )

        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
         setattr(user,field, value)
    
        db.commit()
        db.refresh(user)

        return user


# Deleting an existing user

@app.delete("/api/user/{user_id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id:int, db:Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db.delete(user)
    db.commit()



#  Getting the existing User in api model

@app.get("/api/user/{user_id}", response_model=UserReponse)
def get_user(user_id:int, db:Annotated[Session, Depends(get_db)]):

    result = db.execute(
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

@app.get("/api/users/{user_id}/posts", response_model=list[PostResponse])
def get_user_posts(user_id:int, db:Annotated[Session, Depends(get_db)]):
    result = db.execute(
              select(models.User).where(models.User.id == user_id)  
            )
    user = result.scalars().first()
    if not user:
      raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found"
      )
    result = db.execute(select(models.Post).where(models.Post.user_id == user_id))
    posts = result.scalars().all()
    return posts



#  Home page route using database and displays all posts

@app.get("/",include_in_schema=False)   
@app.get("/posts",include_in_schema=False)    
def home(request: Request, db:Annotated[Session, Depends(get_db)]) :
    result = db.execute(select(models.Post))
    posts = result.scalars().all()
    return templates.TemplateResponse(
        request,
        "home.html",
        {"posts":posts,
          "title":"Home"})




# creating new post using api route

@app.post("/api/posts",response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def Create_Post(post: PostCreate, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.User).where(models.User.id == post.user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    new_post = models.Post(
       title = post.title,
       content = post.content,
       user_id = post.user_id
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post




 # path parameter to get the post by its id


@app.get("/post/{post_id}",include_in_schema=False)            
def post_page(request: Request,post_id: int,db:Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Post).where(models.Post.id == post_id))
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
def user_post_page(request: Request, user_id: int, db:Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Post).where(models.Post.user_id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User does not exist"
        )
    result = db.execute(select(models.Post).where(models.Post.user_id == user_id))
    posts = result.scalars().all()
    return templates.TemplateResponse(
        request,
        "user_posts.html",
        {"posts":posts,
         "user":user,
          "title":"Home"}
    )




#getting all posts by all users in api model

@app.get("/api/posts", response_model=list[PostResponse])
def get_posts(db:Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Post))
    posts = result.scalars().all()
    return posts



# path parameter to get the post by its id

@app.get("/api/post/{post_id}",response_model=PostResponse)           
def get_post(post_id: int, db:Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post


# Updating a post using put this will update full post

@app.put("/api/post/{post_id}",response_model=PostResponse)           
def update_post_full(post_id: int,post_data:PostCreate, db:Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail="Post not found")
    if post_data.user_id != post.user_id:
        result = db.execute(select(models.User).where(models.User.id == post_data.user_id))
        user= result.scalars().first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
    post.title = post_data.title
    post.content = post_data.content
    post.user_id = post_data.user_id
    
    db.commit()
    db.refresh(post)

    return post



# partially updating a post using patch 

@app.patch("/api/post/{post_id}",response_model=PostResponse)           
def update_post_partial(post_id: int,post_data:PostUpdate, db:Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    update_data = post_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(post,field, value)
    
    db.commit()
    db.refresh(post)

    return post


#  deleting post in FastAPI using delete by using post id

@app.delete("/api/post/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id:int, db:Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=" Post not found")
    db.delete(post)
    db.commit()


# Error handling using StarletteExceptionError for http errors

@app.exception_handler(StarletteExceptionError)
def  general_http_exception_handler(request: Request, exception: StarletteExceptionError):
    message = (
        exception.detail
        if exception.detail
        else "An error occured please check your request and try again "
    )

    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code = exception.status_code,
            content={"detail":message}
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
def validation_exception_handler(request: Request, exception:RequestValidationError):
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code= status.HTTP_422_UNPROCESSABLE_CONTENT,
            content= {"detail": exception.errors()}
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