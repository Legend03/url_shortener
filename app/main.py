from fastapi import FastAPI

app = FastAPI(title="URL Shortener")

@app.get('/healthcheck')
def health_check():
    return {'status': 'ok'}