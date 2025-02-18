"""Contains generic base classes for file IO."""

from abc import ABCMeta
from typing import (
    Optional,
    cast,
    Iterable,
    Union,
    TextIO,
    BinaryIO,
    Type,
    ContextManager,
)
from typing_extensions import Literal
from types import TracebackType

import can
import can.typechecking


class BaseIOHandler(ContextManager, metaclass=ABCMeta):
    """A generic file handler that can be used for reading and writing.

    Can be used as a context manager.

    :attr file:
        the file-like object that is kept internally, or `None` if none
        was opened
    """

    file: Optional[can.typechecking.FileLike]

    def __init__(self, file: can.typechecking.AcceptedIOType, mode: str = "rt") -> None:
        """
        :param file: a path-like object to open a file, a file-like object
                     to be used as a file or `None` to not use a file at all
        :param mode: the mode that should be used to open the file, see
                     :func:`open`, ignored if *file* is `None`
        """
        if file is None or (hasattr(file, "read") and hasattr(file, "write")):
            # file is None or some file-like object
            self.file = cast(Optional[can.typechecking.FileLike], file)
        else:
            # file is some path-like object
            self.file = open(cast(can.typechecking.StringPathLike, file), mode)

        # for multiple inheritance
        super().__init__()

    def __enter__(self) -> "BaseIOHandler":
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> Literal[False]:
        self.stop()
        return False

    def stop(self) -> None:
        """Closes the underlying file-like object and flushes it, if it was opened in write mode."""
        if self.file is not None:
            # this also implies a flush()
            self.file.close()


# pylint: disable=abstract-method,too-few-public-methods
class MessageWriter(BaseIOHandler, can.Listener, metaclass=ABCMeta):
    """The base class for all writers."""


# pylint: disable=abstract-method,too-few-public-methods
class FileIOMessageWriter(MessageWriter, metaclass=ABCMeta):
    """A specialized base class for all writers with file descriptors."""

    file: Union[TextIO, BinaryIO]


# pylint: disable=too-few-public-methods
class MessageReader(BaseIOHandler, Iterable, metaclass=ABCMeta):
    """The base class for all readers."""
