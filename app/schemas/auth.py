from pydantic import BaseModel, Field


class UserLogin(BaseModel):
    username: str = Field(min_length=1, max_length=30, pattern=r"^[a-zA-Z0-9_]+$")
    password: str = Field(min_length=8, max_length=64)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
