from fastapi import FastAPI, Request, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

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

@app.get("/",include_in_schema=False)         
def home(request: Request) :
    return templates.TemplateResponse(request, "home.html",{"posts":posts, "title":"Home"})


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