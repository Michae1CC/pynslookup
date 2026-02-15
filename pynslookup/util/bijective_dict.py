from __future__ import annotations

from collections.abc import Iterable, MutableMapping, Mapping
from typing import TypeVar

KT = TypeVar("KT")
VT = TypeVar("VT")


class BijectiveDict(MutableMapping[KT, VT]):

    _forward: dict[KT, VT]
    _backward: dict[VT, KT]

    def __init__(
        self,
        forward: dict[KT, VT] | None = None,
    ):

        if forward is None:
            self._forward = {}
            self._backward = {}
        else:
            self._forward = forward
            self._backward = {value: key for key, value in self._forward.items()}

    # @property
    # def inv(self) -> BijectiveDict[VT, KT]:
    #     return BijectiveDict(self._backward)
