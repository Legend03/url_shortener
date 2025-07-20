import sys
import os

from fastapi.middleware.cors import CORSMiddleware

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import uvicorn
from fastapi import FastAPI

from app.api.linksAPI import router as router_link
from app.api.userAPI import router as router_user
app = FastAPI(title="URL Shortener")

app.include_router(router_link)
app.include_router(router_user)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)