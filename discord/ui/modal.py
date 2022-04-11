"""
The MIT License (MIT)

Copyright (c) 2021-present Kae Bartlett

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from __future__ import annotations

import typing
import uuid

from .models import ComponentHolder
from ..components import _component_factory
from ..types.components import (
    Modal as ModalPayload,
)

if typing.TYPE_CHECKING:
    from .models import BaseComponent


__all__ = (
    "Modal",
)


class Modal(ComponentHolder):
    """
    The component holder class for modal responses.

    .. versionadded:: 0.0.5
    """

    def __init__(self, *, title: str, custom_id: str = None, components: typing.List[BaseComponent] = None):
        self.title = title
        self.custom_id = custom_id or str(uuid.uuid1())
        self.components = components or []

    def __repr__(self) -> str:
        attrs = (
            ('title', self.title),
            ('custom_id', self.custom_id),
            ('components', self.components),
        )
        inner = ' '.join('%s=%r' % t for t in attrs)
        return f'{self.__class__.__name__}({inner})'

    def to_dict(self) -> ModalPayload:
        return {
            "title": self.title,
            "custom_id": self.custom_id,
            "components": [i.to_dict() for i in self.components],
        }  # type: ignore

    @classmethod
    def from_dict(cls, data: ModalPayload):
        new_components = []
        for i in data['components']:
            v = _component_factory(i)
            new_components.append(v)
        return cls(title=data['title'], custom_id=data['custom_id'], components=new_components)
