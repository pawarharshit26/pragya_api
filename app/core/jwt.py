import json
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union

import jwt

from app.core.config import settings
from app.core.exceptions import BaseException


class JWTService:
    class JWTException(BaseException):
        pass

    class JWTTokenExpiredException(JWTException):
        pass

    class JWTInvalidTokenException(JWTException):
        pass

    def __init__(self):
        self.algorithm = settings.JWT_ALGORITHM
        self.secret_key = settings.JWT_SECRET
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES

    def encode(
        self,
        subject: Union[dict, Any],
        expires_delta: Optional[timedelta] = None,
        **kwargs,
    ) -> str:
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=self.access_token_expire_minutes
            )

        if isinstance(subject, dict):
            subject = json.dumps(subject)

        to_encode = {"exp": expire, "iat": datetime.utcnow(), "sub": subject, **kwargs}

        return jwt.encode(
            payload=to_encode, key=self.secret_key, algorithm=self.algorithm
        )

    def decode(
        self, token: str, options: Optional[Dict[str, bool]] = None
    ) -> Dict[str, Any]:
        if options is None:
            options = {"verify_signature": True, "verify_exp": True}

        try:
            payload = jwt.decode(
                jwt=token,
                key=self.secret_key,
                algorithms=[self.algorithm],
                options=options,
            )

            if "sub" in payload and isinstance(payload["sub"], str):
                try:
                    payload["sub"] = json.loads(payload["sub"])
                except json.JSONDecodeError:
                    pass

            return payload

        except jwt.ExpiredSignatureError:
            raise self.JWTTokenExpiredException(message="Token has expired") from None
        except jwt.InvalidTokenError as e:
            raise self.JWTInvalidTokenException(message=f"Invalid token: {e!s}") from e

    def get_payload(self, token: str) -> dict[str, Any]:
        return self.decode(token=token, options={"verify_signature": False})

    def get_subject(self, payload: dict[str, Any]) -> str:
        return payload.get("sub")

    def is_token_expired(self, token: str) -> bool:
        try:
            self.decode(token=token)
            return False
        except Exception:
            return True


def get_jwt_service():
    return JWTService()
