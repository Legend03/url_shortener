import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles

from app.api import router

app = FastAPI(title="URL Shortener")
app.include_router(router)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse, tags=["Main"])
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/register", response_class=HTMLResponse, tags=["Main"])
async def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/login", response_class=HTMLResponse, tags=["Main"])
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)