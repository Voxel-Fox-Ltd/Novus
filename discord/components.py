from __future__ import annotations

from typing import Any, ClassVar, Dict, List, Optional, TYPE_CHECKING, Tuple, Type, TypeVar, Union
from .enums import try_enum, ComponentType, ButtonStyle
from .utils import get_slots, MISSING
from .partial_emoji import PartialEmoji, _EmojiTag

if TYPE_CHECKING:
    from .types.components import (
        Component as ComponentPayload,
    )


def _component_factory(data: ComponentPayload):
    from .ui import BaseComponent, ActionRow, Button, SelectMenu
    component_type = data['type']
    if component_type == 1:
        return ActionRow.from_dict(data)
    elif component_type == 2:
        return Button.from_dict(data)
    elif component_type == 3:
        return SelectMenu.from_dict(data)
    else:
        v = BaseComponent()
        v.data = data
        v.custom_id = v.get("custom_id")
