from pydantic import BaseModel

class SLink(BaseModel):
    id: int
    original_url: str
    short_code: str
    clicks_count: int

    class Config:
        from_attributes = True

class SLinkCreate(BaseModel):
    original_url: str

    class Config:
        from_attributes = True