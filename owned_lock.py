__version__ = "0.1.0"
__all__ = ("Mutex",)

import sys
from dataclasses import dataclass, field, InitVar
from typing import TypeVar, Generic, Optional, ForwardRef
from threading import Lock


class OwnedLockException(Exception):
    pass


class LeakyReference(OwnedLockException):
    pass


T = TypeVar("T")


@dataclass(frozen=True)
class MutexGuard(Generic[T]):
    """An implementation of a "scoped lock" of a mutex. When this structure is dropped (falls out of scope), the lock will be unlocked.

    The data protected by the mutex can be accessed through this guard via the :attr:`value` attribute.
    """

    __hash__ = None

    value: T
    mutex: "Mutex[T]"

    def __del__(self):
        self.mutex.release()


class Mutex(Generic[T]):
    """A modern :class:`threading.Lock` variant with dynamically checked ownership rules."""

    __hash__ = None

    value: InitVar[T]

    __inner: T
    __inner_lock: Lock
    __inner_guard: Optional["MutexGuard"]

    def __init__(self, value: T, *, refcount_max: int = 5):

        if sys.getrefcount(value) > refcount_max:
            raise LeakyReference(
                f"Refusing to lock over {value=!r} because it potentially leaks! "
                "(help: destroy/weaken other refs first, use gc.getrefferents(value).)"
            )

        self.__inner = value
        self.__inner_lock = Lock()
        self.__inner_guard = None

    def __repr__(self) -> str:
        return repr(self.__inner)

    def __enter__(self) -> MutexGuard[T]:
        return self.lock()

    def __exit__(self, *_):
        pass

    @property
    def is_poisoned(self) -> bool:
        """:class:`bool` - Determines whether the mutex is poisoned."""
        raise NotImplemetedError("TODO")

    @property
    def is_locked(self) -> bool:
        with self.__inner_lock:
            return self.__inner_guard is not None

    def lock(self) -> MutexGuard[T]:
        self.__inner_lock.acquire()

        while self.__inner_guard is not None:
            self.__inner_lock.release()
            self.__inner_lock.acquire()

        assert self.__inner_lock.locked()
        self.__inner_guard = guard = MutexGuard(value=self.__inner, mutex=self)
        self.__inner_lock.release()
        return guard

    def try_lock(self) -> Optional[MutexGuard[T]]:
        with self.__inner_lock:
            if self.__inner_guard is None:
                return None
            else:
                self.__inner_guard = guard = MutexGuard(value=self.__inner, mutex=self)
                return guard

    def release(self):
        with self.__inner_lock:
            if self.__inner_guard is None:
                raise RuntimeError("Already unlocked!")
            else:
                guard = self.__inner_guard
                self.__inner_guard = None
                del guard
