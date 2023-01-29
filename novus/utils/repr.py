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
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from typing import Any, Callable, Iterable

__all__ = ("generate_repr",)


def generate_repr(args: Iterable[str | tuple[str, str]]) -> Callable[..., str]:
    """
    Easily add a __repr__ to a class.
    """

    def wrapper(instance: Any) -> str:
        generated_args = []
        for pair in args:
            if isinstance(pair, tuple):
                kwarg_name, self_name = pair
            else:
                kwarg_name, self_name = pair, pair
            if not hasattr(instance, self_name):
                continue
            generated_args.append(f"{kwarg_name}={getattr(instance, self_name)!r}")
        return f"<{instance.__class__.__name__} {' '.join(generated_args)}>"

    return wrapper
