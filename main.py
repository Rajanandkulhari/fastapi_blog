from fastapi import FastAPI, Request, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteExceptionError
from schema import PostCreate,PostResponse

app = FastAPI()

app.mount("/static",StaticFiles(directory = "static"), name="static")

templates = Jinja2Templates(directory ="templates")

posts: list[dict] = [
    {
        "id": 1,
        "author": "Corey Schafer",
        "title": "FastAPI is Awesome",
        "content": "This framework is really easy to use and super fast.",
        "date_posted": "April 20, 2025",
    },
    {
        "id": 2,
        "author": "Jane Doe",
        "title": "Python is Great for Web Development",
        "content": "Python is a great language for web development, and FastAPI makes it even better.",
        "date_posted": "April 21, 2025",
    },
]

@app.get("/",response_model=list[PostResponse])         
def home(request: Request) :
    return templates.TemplateResponse(
        request,
        "home.html",
        {"posts":posts,
          "title":"Home"})


@app.post("/api/posts",response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def Create_Post(post: PostCreate):
    new_id = max(p["id"] for p in posts)+ 1 if posts else 1
    new_post = {
        "id":new_id,
        "author":post.author,
        "title":post.title,
        "content":post.content,
        "date_posted":"23 Mar 2026"
    }
    posts.append(new_post)
    return new_post


@app.get("/post/{post_id}", response_model=PostResponse)             # path parameter to get the post by its id
def post_page(request: Request,post_id: int):
    for post in posts:
        if post.get("id") == post_id:
           title = post["title"][:50]
           return templates.TemplateResponse(
               request,
                 "post.html",
                 {"post":post, "title":title})
    raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail="Post not found")


@app.get("/homepage")
def homepage():
    return{"message":"This is home page"}

@app.get("/api/posts")
def get_posts():
    return posts


@app.get("/api/post/{post_id}")             # path parameter to get the post by its id
def get_posts(post_id: int):
    for post in posts:
        if post.get("id") == post_id:
           return post
    raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail="Post not found")





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