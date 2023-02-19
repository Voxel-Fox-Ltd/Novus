"""
Copyright (c) Kae Bartlett

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

from __future__ import annotations

import glob
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from typing_extensions import Self

import novus

if TYPE_CHECKING:
    import pathlib

__all__ = (
    'Config',
)


@dataclass
class Config:
    token: str = ""
    shard_ids: list[int] = field(default_factory=list)
    shard_count: int = 1
    intents: novus.Intents = field(default_factory=novus.Intents.none)

    @classmethod
    def from_file(cls, filename: str | None) -> Self:
        if filename is None:
            try:
                filename = glob.glob("config.*")[0]
            except IndexError:
                raise Exception("Missing config file from current directory")
        try:
            if filename.endswith(".yaml") or filename.endswith(".yml"):
                return cls.from_yaml(filename)
            elif filename.endswith(".toml"):
                return cls.from_toml(filename)
            elif filename.endswith(".json"):
                return cls.from_json(filename)
        except FileNotFoundError:
            raise Exception("File %s does not exist" % filename)
        raise Exception("File %s could not be parsed (invalid file type)" % filename)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        intent_dict = data.pop("intents")
        intents = novus.Intents(**intent_dict)
        return cls(**data, intents=intents)

    def to_dict(self) -> dict[str, Any]:
        return {
            "token": self.token,
            "shard_ids": self.shard_ids,
            "shard_count": self.shard_count,
            "intents": dict(self.intents.walk()),
        }

    @classmethod
    def from_yaml(cls, filename: str | pathlib.Path) -> Self:
        try:
            import yaml
        except ImportError:
            raise Exception("Missing YAML module.")
        with open(filename) as a:
            return cls.from_dict(yaml.load(a, Loader=yaml.Loader))

    def to_yaml(self) -> str:
        try:
            import yaml
        except ImportError:
            raise Exception("Missing YAML module.")
        return yaml.dump(self.to_dict(), default_flow_style=False)

    @classmethod
    def from_toml(cls, filename: str | pathlib.Path) -> Self:
        try:
            import toml
        except ImportError:
            raise Exception("Missing TOML module.")
        with open(filename) as a:
            return cls.from_dict(toml.load(a))

    def to_toml(self) -> str:
        try:
            import toml
        except ImportError:
            raise Exception("Missing TOML module.")
        return toml.dumps(self.to_dict())

    @classmethod
    def from_json(cls, filename: str | pathlib.Path) -> Self:
        import json
        with open(filename) as a:
            return cls.from_dict(json.load(a))

    def to_json(self) -> str:
        import json
        return json.dumps(self.to_dict(), indent=4)
