from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .types.components import (
        Component as ComponentPayload,
    )


def _component_factory(data: ComponentPayload):
    from .ui import (
        BaseComponent,  # Fallback
        ActionRow,  # 1
        Button,  # 2
        SelectMenu,  # 3
        # Modal is 4 but that'll never appear on a message, and shouldn't be sent to a bot
        UserSelectMenu,  # 5
        RoleSelectMenu,  # 6
        MentionableSelectMenu,  # 7
        ChannelSelectMenu,  # 8
    )
    component_type = data['type']
    if component_type == 1:
        return ActionRow.from_dict(data)
    elif component_type == 2:
        return Button.from_dict(data)
    elif component_type == 3:
        return SelectMenu.from_dict(data)
    elif component_type == 5:
        return UserSelectMenu.from_dict(data)
    elif component_type == 6:
        return RoleSelectMenu.from_dict(data)
    elif component_type == 7:
        return MentionableSelectMenu.from_dict(data)
    elif component_type == 8:
        return ChannelSelectMenu.from_dict(data)
    else:
        v = BaseComponent()
        v.data = data
        v.custom_id = data.get("custom_id")
        return v
