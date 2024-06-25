"""Simple arrow (vector/quiver) icon for folium."""

from __future__ import annotations

import math
from dataclasses import dataclass
from functools import cached_property
from typing import Final, Literal, NamedTuple, Sequence

import folium

__all__ = [
    "ArrowIcon",
    "ArrowIconHead",
    "ArrowIconBody",
]

__version__: Final = "0.1.0"


class _BBox(NamedTuple):
    x0: int
    y0: int
    x: int
    y: int


@dataclass(frozen=True)
class _MetrixHandler:
    length: float
    angle: float
    margin: int

    @property
    def degree(self):
        return math.degrees(self.angle)

    @cached_property
    def cos(self):
        return math.cos(self.angle)

    @cached_property
    def sin(self):
        return math.sin(self.angle)

    @cached_property
    def x(self):
        return self.length * self.cos

    @cached_property
    def y(self):
        return self.length * self.sin

    @cached_property
    def bbox(self):
        if 0 <= self.x:
            x = math.ceil(self.x)
            x0 = -self.margin
        else:
            x = math.floor(self.x)
            x0 = x - self.margin

        if 0 <= self.y:
            y = math.ceil(self.y)
            y0 = -self.margin
        else:
            y = math.floor(self.y)
            y0 = y - self.margin

        return _BBox(x0, y0, abs(x) + 2 * self.margin, abs(y) + 2 * self.margin)

    def size(self):
        return abs(self.bbox.x), abs(self.bbox.y)

    def anchor(self, anchor: Literal["tail", "mid", "head"]):
        if anchor == "head":
            return abs(self.bbox.x0) + self.x, abs(self.bbox.y0) + self.y
        elif anchor == "mid":
            return abs(self.bbox.x0) + self.x / 2.0, abs(self.bbox.y0) + self.y / 2.0
        return abs(self.bbox.x0), abs(self.bbox.y0)


@dataclass(frozen=True)
class ArrowIconHead:
    """Metric of head."""

    def __post_init__(self):  # noqa: D105
        if self.width < 0:
            raise ValueError(f"width must be 0 <=, we got {self.width}")
        if self.width < 0:
            raise ValueError(f"length must be 0 <=, we got {self.length}")

    width: int | float = 8
    """Width of head"""
    length: int | float = 10
    """Width of length"""


@dataclass(frozen=True)
class ArrowIconBody:
    """Metric of body."""

    def __post_init__(self):  # noqa: D105
        if self.width < 0:
            raise ValueError(f"width must be 0 <=, we got {self.width}")

    width: int | float = 2
    """Width of boby"""


DEFAULT_HEAD = ArrowIconHead()
DEFAULT_BODY = ArrowIconBody()


class ArrowIcon(folium.DivIcon):
    """Simple arrow (vector/quiver) Icon.

    Args:
        length: the length of the vector which satisfies 0 <=.
        angle: the angle of the vector in radian,
               it starts from the positive latidude axis
               and goes clockwise (Left-Handed System).
        head: the head metric,
              defraulting :obj:`ArrowIconHead(width=8, length=10)`.
        body: the body metric,
              defraulting :obj:`ArrowIconBody(width=2)`.
        color: the color of the vector, supporting any CSS color propery.
        border_width: the border width.
        border_color: the border color.
        anchor: the anchor of the vector.
        popup_anchor: it passes to the :class:`folium.DivIcon` constructor.
        class_name: it passes to the :class:`folium.DivIcon` constructor.

    Examples:
        A marker with a vector icon
        of which length is 100px and directing positive longitude.

        >>> folium.Marker(
        ...     (40.78322, -73.96551),
        ...     icon=ArrowIcon(100, math.pi / 2),
        ... )

        More customized example;

        >>> folium.Marker(
        ...     (40.78322, -73.96551),
        ...     icon=ArrowIcon(
        ...         100, math.pi
        ...         head=ArrowIconHead(width=10, length=20),
        ...         body=ArrowIconBody(width=5),
        ...         color="hsl(30deg, 100%, 50%)",
        ...         border_width=1,
        ...         border_color="red",
        ...         anchor="mid"
        ...     )
        ... )
    """

    def __init__(
        self,
        length: int | float,
        angle: int | float,
        head: ArrowIconHead = DEFAULT_HEAD,
        body: ArrowIconBody = DEFAULT_BODY,
        color: str = "black",
        border_width: int | float = 0,
        border_color: str = None,
        anchor: Literal["tail", "mid", "head"] = "tail",
        popup_anchor: tuple[int, int] | None = None,
        class_name: str = "empty",
    ):
        if length < 0:
            raise ValueError(f"length must be 0 <=, we got {length}")

        handler = _MetrixHandler(
            length=length,
            angle=angle - math.pi / 2,
            margin=max(head.length, head.width, body.width),
        )

        #
        #    |          5
        #    |          | \
        #    @-----<----6  \
        #    |              \
        # ---+---------------4---
        #    |              /
        #    1---->-----2  /
        #    |          | /
        #    |          3
        #
        path = (
            '<path d="M {:.7g} {:.7g} l {:.7g} {:.7g} '
            "l {:.7g} {:.7g} l {:.7g} {:.7g} "
            "l {:.7g} {:.7g} l {:.7g} {:.7g} "
            'l {:.7g} {:.7g} Z" />'
        ).format(
            # move @
            0,
            -body.width / 2.0,
            # to 1
            0,
            body.width,
            # to 2
            max(length - head.length, 0),
            0,
            # to 3
            0,
            (head.width - body.width) / 2.0,
            # to 4
            head.length,
            -head.width / 2.0,
            # to 5
            -head.length,
            -head.width / 2.0,
            # to 6
            0,
            (head.width - body.width) / 2.0,
            # to @ by Z
        )

        g = (
            "<g "
            'stroke="{line_color}" '
            'fill="{color}" '
            'stroke-width="{line_width}" '
            'transform="rotate({angle} 0 0)">'
            "{path}"
            "</g>"
            if head.length < length
            else "<g "
            'stroke="{line_color}" '
            'fill="{color}" '
            'stroke-width="{line_width}" '
            'transform="scale({scale})rotate({angle} 0 0)">'
            "{path}"
            "</g>"
        )

        html = (
            "<svg "
            'xmlns="http://www.w3.org/2000/svg" '
            'version="1.1" '
            'viewBox="{bbox.x0} {bbox.y0} {bbox.x} {bbox.y}">'
            "{g}"
            "</svg>"
        )

        html = html.format(
            bbox=handler.bbox,
            g=g.format(
                path=path,
                angle=handler.degree,
                scale=length / head.length,
                color=color,
                line_width=border_width,
                line_color=border_color if border_color is not None else color,
            ),
        )

        super().__init__(
            html=html,
            icon_size=handler.size(),
            icon_anchor=handler.anchor(anchor=anchor),
            popup_anchor=popup_anchor,
            class_name=class_name,
        )

    @classmethod
    def from_comp(
        cls,
        components: Sequence[int | float],
        head: ArrowIconHead = DEFAULT_HEAD,
        body: ArrowIconBody = DEFAULT_BODY,
        color: str = "black",
        border_width: int | float = 0,
        border_color: str = None,
        anchor: Literal["tail", "mid", "head"] = "tail",
        popup_anchor: tuple[int, int] | None = None,
        class_name: str = "empty",
    ):
        """Makes a :class:`ArrowIcon` from components of latitude and longitude direction.

        Args:
            components: the components vector, latitude and longitude direction.
            head: the head metric,
                  defraulting :obj:`ArrowIconHead(width=8, length=10)`.
            body: the body metric,
                  defraulting :obj:`ArrowIconBody(width=2)`.
            color: the color of the vector, supporting any CSS color propery.
            border_width: the border width.
            border_color: the border color.
            anchor: the anchor of the vector.
            popup_anchor: it passes to the :class:`folium.DivIcon` constructor.
            class_name: it passes to the :class:`folium.DivIcon` constructor.

        Returns:
             a :class:`ArrowIcon` obj

        Examples:
            A marker with a vector icon
            of which latitude compnent is 100 px and longitude is 50px.

            >>> folium.Marker(
            ...     (40.78322, -73.96551),
            ...     icon=ArrowIcon.from_comp((100, 50)),
            ... )

            More customized example;

            >>> folium.Marker(
            ...     (40.78322, -73.96551),
            ...     icon=ArrowIcon.from_comp(
            ...         (100, 50)
            ...         head=ArrowIconHead(width=10, length=20),
            ...         body=ArrowrIconBody(width=5),
            ...         color="hsl(30deg, 100%, 50%)",
            ...         border_width=1,
            ...         border_color="red",
            ...         anchor="mid"
            ...     ),
            ... )
        """
        if len(components) != 2:
            raise ValueError(f"length of components must be 2, we got {components}")

        return cls(
            length=math.hypot(components[1], components[0]),
            angle=math.atan2(components[1], components[0]),
            head=head,
            body=body,
            color=color,
            border_width=border_width,
            border_color=border_color,
            popup_anchor=popup_anchor,
            class_name=class_name,
            anchor=anchor,
        )
