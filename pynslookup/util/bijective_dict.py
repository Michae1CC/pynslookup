from __future__ import annotations

from collections.abc import Iterable, MutableMapping, Mapping
from typing import Iterator
from typing import TypeVar
from typing import cast

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

    def _raise_non_invertible(self, key1: KT, key2: KT, value: VT) -> None:
        raise ValueError(f"non-invertible: {key1}, {key2} both map to: {value}")

    @property
    def inv(self) -> BijectiveDict[VT, KT]:
        return BijectiveDict(self._backward)

    def __getitem__(self, item: KT) -> VT:
        return self._forward[item]

    def __setitem__(self, key: KT, value: VT) -> None:
        missing = object()
        old_key = self._backward.get(value, missing)
        if old_key is not missing and old_key != key:
            self._raise_non_invertible(cast(KT, old_key), key, value)

        old_value = self._forward.get(key, missing)
        if old_value is not missing:
            del self._backward[cast(VT, old_value)]

        self._forward[key] = value
        self._backward[value] = key

    def __delitem__(self, key: KT) -> None:
        value = self._forward[key]
        del self._forward[key]
        del self._backward[value]

    def __iter__(self) -> Iterator[KT]:
        return iter(self._forward)

    def __len__(self) -> int:
        return len(self._forward)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._forward!r})"

    def clear(self) -> None:
        self._forward.clear()
        self._backward.clear()
