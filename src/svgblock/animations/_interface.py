import difflib

from ._base import BaseAnimation
from ._presets import Drop, Fade, Pop, Pulse, Rise


class Animation:

    fade = Fade
    rise = Rise
    drop = Drop
    pop = Pop
    pulse = Pulse

    @classmethod
    def names(cls) -> list[str]:
        return [
            name
            for name, value in vars(cls).items()
            if isinstance(value, type) and issubclass(value, BaseAnimation)
        ]

    @classmethod
    def resolve(cls, animation: BaseAnimation | str | None) -> BaseAnimation | None:
        if animation is None or isinstance(animation, BaseAnimation):
            return animation
        if animation not in cls.names():
            message = f"Unknown animation {animation!r}."
            close = difflib.get_close_matches(animation, cls.names(), n=1)
            if close:
                message += f" Did you mean {close[0]!r}?"
            message += f" Available: {', '.join(cls.names())}."
            raise ValueError(message)
        return getattr(cls, animation)()
