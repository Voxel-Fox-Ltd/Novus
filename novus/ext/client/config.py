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
import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, NoReturn

from typing_extensions import Self

import novus

if TYPE_CHECKING:
    import argparse
    import pathlib

    from .plugin import Plugin

__all__ = (
    'Config',
)


log = logging.getLogger("novus.ext.client.config")


class Config:

    token: str
    shard_ids: list[int]
    shard_count: int
    intents: novus.Intents
    plugins: list[str]

    def __init__(
            self,
            *,
            token: str = "",
            shard_ids: list[int] | None = None,
            shard_count: int = 1,
            intents: novus.Intents | None = None,
            plugins: list[str] | None = None,
            **kwargs: Any):
        self.token: str = token
        self.shard_ids: list[int] = shard_ids or []
        self.shard_count: int = shard_count
        self.intents: novus.Intents = intents or novus.Intents()
        self.plugins: list[str] = plugins or []
        for k, v in kwargs.items():
            setattr(self, k, v)
        self._extended: dict[Plugin, dict] = {}

    if TYPE_CHECKING:

        def __getattr__(self, name: str) -> str | NoReturn:
            ...

        def __setattr__(self, name: str, value: str) -> str:
            ...

    def merge_namespace(
            self,
            args: argparse.Namespace,
            unknown: list[str] | None = None) -> None:
        """
        Merge arguments from the namespace into the config.
        """

        def check(name: str) -> bool:
            return name in args and getattr(args, name) is not None

        if check("token"):
            self.token = args.token

        if check("shard_ids") and check("shard_id"):
            raise Exception("Cannot have both shard_ids and shard_id in args")
        elif check("shard_ids"):
            self.shard_ids = [int(i.strip()) for i in args.shard_ids.split(",") if i.strip()]
        elif check("shard_id"):
            self.shard_ids = [int(i.strip()) for i in args.shard_id if i.strip()]

        if check("shard_count"):
            self.shard_count = int(args.shard_count)

        if check("intents") and check("intent"):
            raise Exception("Cannot have both intents and intent in args")
        elif check("intents"):
            self.intents = novus.Intents(**{
                i.strip(): True
                for i in args.intents.split(",")
                if i.strip()
            })
        elif check("intent"):
            self.intents = novus.Intents(**{
                i.strip(): True
                for i in args.intent
                if i.strip()
            })

        if check("plugins") and check("plugin"):
            raise Exception("Cannot have both plugins and plugin in args")
        elif check("plugins"):
            self.plugins = [i.strip() for i in args.plugins.split(",") if i.strip()]
        elif check("plugin"):
            self.plugins = [i.strip() for i in args.plugin if i.strip()]

        if unknown:
            for name, value in zip(unknown[::2], unknown[1::2]):
                if not name.startswith("--"):
                    raise ValueError("Failed to parse unknown args %s" % unknown)
                setattr(self, name[2:], value)

    @classmethod
    def from_file(cls, filename: str | None) -> Self:
        if filename is None:
            try:
                filename = glob.glob("config.*")[0]
            except IndexError:
                log.warning("Missing config file from current directory")
                return cls()
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
        v = {
            "token": self.token,
            "shard_ids": self.shard_ids,
            "shard_count": self.shard_count,
            "intents": dict(self.intents.walk()),
            "plugins": self.plugins,
        }
        for ext in self._extended.values():
            v.update(ext)
        return v

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
