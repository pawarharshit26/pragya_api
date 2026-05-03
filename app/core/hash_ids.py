from typing import Any

from hashids import Hashids
from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema

from app.core.config import settings
from app.core.exceptions import BaseException

hashids = Hashids(
    salt=settings.SECRET_KEY,
    min_length=16,
)


class HashIdException(BaseException):
    message = "Hash Id Exception"


class HashIdInvalidException(HashIdException):
    message = "Invalid Hash Id"


def encode(id: int) -> str:
    return hashids.encode(id)


def decode(hash_id: str) -> int:
    decoded = hashids.decode(hash_id)
    if not decoded:
        raise HashIdInvalidException()
    return decoded[0]


class HashId(int):
    """
    Internal type: int
    External (API): hash string
    """

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:

        def validate(value: Any) -> int:
            if isinstance(value, str):
                return decode(hash_id=value)

            if isinstance(value, int):
                return value

            raise ValueError("HashId must be int or str")

        def serialize(value: int) -> str:
            return encode(value)

        return core_schema.no_info_after_validator_function(
            validate,
            core_schema.int_schema(),
            serialization=core_schema.plain_serializer_function_ser_schema(
                function=serialize
            ),
        )

    @classmethod
    def __get_pydantic_serializer__(cls):
        def serialize(value: int) -> str:
            return encode(value)

        return serialize
