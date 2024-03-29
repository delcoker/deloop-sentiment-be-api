from typing import List, Optional
from core.schemas import group_categories_dto
from pydantic import BaseModel


class SocialAccountBase(BaseModel):
    name: str
    oauth_token: str
    oauth_token_secret: str


class SocialAccountCreate(SocialAccountBase):
    pass


class SocialAccount(SocialAccountBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str


class User(UserBase):
    id: int

    # is_active: bool
    # is_deleted: bool

    class Config:
        orm_mode = True


class UserCreate(User):
    password: str

    # social_accounts: List[SocialAccount] = []

    # used to provide configurations to Pydantic
    # read the data even if it is not a dict
    class Config:
        orm_mode = True


class LoggedInUser(User):
    token: str
    token_type: str

    class Config:
        orm_mode = True


class SocialUser(User):
    social_accounts: List[SocialAccount] = []

    # used to provide configurations to Pydantic
    # read the data even if it is not a dict
    class Config:
        orm_mode = True


class UserGroupCategories(User):
    group_categories: List['group_categories_dto.GroupCategory'] = []

    # used to provide configurations to Pydantic
    # read the data even if it is not a dict

    class Config:
        orm_mode = True


class Url(BaseModel):
    url: str
