from __future__ import annotations
from typing import Tuple, overload, TypeVar, Literal
from typing_extensions import TypeVarTuple, Unpack

Ts = TypeVarTuple('Ts')
# N = TypeVar("N", bound=Literal[int])

class WrappedTuple(Tuple[Unpack[Ts]]):
    """
    Implements a wrapped tuple type, supporting infinite indexing
    """

    """
    @overload
    def __getitem__(self, index: N) -> Unpack[Ts][N]:
        pass
    """

    @overload
    def __getitem__(self, index: int):
        pass
    @overload
    def __getitem__(self, index: slice) -> WrappedTuple:
        pass

    def __getitem__(self, index):
        l = len(self)

        if isinstance(index, slice):
            st = index.start if index.start is not None else 0
            ed = index.stop if index.stop is not None else (l + 1)
            n = 1
            if index.step is not None:
                n = index.step
            elif ed < st:
                n = -1
            return WrappedTuple(self[k] for k in range(st, ed, n))
        elif isinstance(index, int):
            return super().__getitem__(((index % l) + l) % l)
        else:
            return NotImplemented

    def wrap_index(self, index: int) -> int:
        """
        Returns an index that fits within the bounds of the tuple

        :param index: Index to wrap
        :type index: int
        :return: Wrapped index
        """
        l = len(self)
        return ((index % l) + l) % l

    def count_wraps(self, index: int) -> int:
        """
        Reports how many times the index wraps around the bounds of the tuple

        :param index: Index to wrap
        :return: Repeats of list
        """
        return index // len(self)

    def as_tuple(self, rep: int = 1):
        """
        Convert into a normal tuple
        :param rep: Optional repetition parameter
        :return: Standard tuple version of the object
        """
        return tuple(self) * rep

    def forever(self, start: int = 0, step: int = 1):
        """
        Create an iterator instance that iterates forever over the tuple

        :param start: Optional starting point
        :type start: int

        :param step: Optional stepping distance
        :type step: int
        """
        if step == 0:
            raise ValueError("Step cannot be zero")

        if step == 1 and start == 0:
            while True:
                for n in self:
                    yield n
        else:
            k = start
            while True:
                yield self[k]
                k += step
