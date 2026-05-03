from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from app.core.exceptions import BaseException

InputT = TypeVar("InputT")
OutputT = TypeVar("OutputT")


class BaseInteractor(ABC, Generic[InputT, OutputT]):
    class InteractorException(BaseException):
        message = "Interactor error"

    @abstractmethod
    async def execute(self, input: InputT) -> OutputT: ...
