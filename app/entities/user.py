from datetime import datetime

from pydantic import EmailStr

from app.core.hash_ids import HashId
from app.entities.base import BaseEntity


class UserSignUpEntity(BaseEntity):
    email: EmailStr
    password: str
    name: str


class UserSignInEntity(BaseEntity):
    email: EmailStr
    password: str


class UserEntity(BaseEntity):
    id: HashId
    email: EmailStr
    name: str
    created_at: datetime
    updated_at: datetime


class UserTokenEntity(BaseEntity):
    token: str
    user: UserEntity
