import uvicorn
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles

from app.api import router
from app.repositories import UserRepository
from app.schemes import SUser

app = FastAPI(title="URL Shortener")
app.include_router(router)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse, tags=["Main"])
async def home(request: Request, current_user: SUser | None = Depends(UserRepository.get_current_user)):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "user": current_user
    })

@app.get("/register", response_class=HTMLResponse, tags=["Authorization"])
async def register(request: Request):
    try:
        current_user = await UserRepository.require_auth(request)
        return RedirectResponse(url="/dashboard", status_code=302)
    except HTTPException:
        return templates.TemplateResponse("register.html", {"request": request})

@app.get("/login", response_class=HTMLResponse, tags=["Authorization"])
async def login(request: Request):
    try:
        current_user = await UserRepository.require_auth(request)
        return RedirectResponse(url="/dashboard", status_code=302)
    except HTTPException:
        return templates.TemplateResponse("login.html", {"request": request})

@app.exception_handler(HTTPException)
async def auth_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 302 and "Not authenticated" in str(exc.detail):
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("error.html", {
        "request": request,
        "error": exc.detail
    }, status_code=exc.status_code)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)