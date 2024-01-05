from __future__ import annotations

import math
from dataclasses import dataclass
from functools import cached_property
from typing import Literal, NamedTuple, Sequence

import folium

__all__ = [
    "__version__",
    "VectorIcon",
    "VectorIconHead",
    "VectorIconBody",
]

__version__ = "0.1.0"


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

    def rotate(self, x: float, y: float):
        return self.cos * x - self.sin * y, self.sin * x + self.cos * y


@dataclass(frozen=True)
class VectorIconHead:
    """Metric of head"""

    width: int | float = 8
    """Width of head"""
    length: int | float = 10
    """Width of length"""


@dataclass(frozen=True)
class VectorIconBody:
    """Metric of body"""

    width: int | float = 2
    """Width of boby"""


DEFAULT_HEAD = VectorIconHead()
DEFAULT_BODY = VectorIconBody()


class VectorIcon(folium.DivIcon):
    """Simple Vector (arrow) Icon

    Args:
        length: the length of the vector which satisfies 0 <=.
        angle: the angle of the vector in radian,
               it starts from the positive latidude axis
               and goes clockwise (Left-Handed System).
        head: the head metric,
              defraulting :obj:`VectorIconHead(width=8, length=10)`.
        body: the body metric,
              defraulting :obj:`VectorIconBody(width=2)`.
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
        ...     icon=VectorIcon(100, math.pi / 2),
        ... )

        More customized example;

        >>> folium.Marker(
        ...     (40.78322, -73.96551),
        ...     icon=VectorIcon(
        ...         100, math.pi
        ...         head=VectorIconHead(width=10, length=20),
        ...         body=VectorIconBody(width=5),
        ...         color="hsl(30deg, 100%, 50%)",
        ...         border_width=1,
        ...         border_color="red",
        ...         anchor="mid"
        ...     )
        ... )
    """

    def __init__(
        self,
        length: float,
        angle: float,
        head: VectorIconHead = DEFAULT_HEAD,
        body: VectorIconBody = DEFAULT_BODY,
        color: str = "black",
        border_width: int | float = 0,
        border_color: str = None,
        anchor: Literal["tail", "mid", "head"] = "tail",
        popup_anchor: tuple[int, int] | None = None,
        class_name: str = "empty",
    ):
        angle = angle - math.pi / 2

        handler = _MetrixHandler(
            length=length, angle=angle, margin=max(head.length, head.width, body.width)
        )

        #            5
        #            | \
        # @-----<----6  \
        # |              \
        # |               4
        # |              /
        # 1---->-----2  /
        #            | /
        #            3
        vector = (
            '<path d="M {:.7g} {:.7g} l {:.7g} {:.7g} '
            "l {:.7g} {:.7g} l {:.7g} {:.7g} "
            "l {:.7g} {:.7g} l {:.7g} {:.7g} "
            'l {:.7g} {:.7g} Z" />'
        ).format(
            # move @
            *handler.rotate(0, -body.width / 2.0),
            # to 1
            *handler.rotate(0, body.width),
            # to 2
            *handler.rotate(max(length - head.length, 0), 0),
            # to 3
            *handler.rotate(0, (head.width - body.width) / 2.0),
            # to 4
            *handler.rotate(head.length, -head.width / 2.0),
            # to 5
            *handler.rotate(-head.length, -head.width / 2.0),
            # to 6
            *handler.rotate(0, (head.width - body.width) / 2.0),
            # to @ by Z
        )

        vector = (
            '<g stroke="{line_color}" fill="{color}"'
            ' stroke-width="{line_width}">'
            "{}</g>"
            if head.length < length
            else '<g stroke="{line_color}" fill="{color}"'
            ' stroke-width="{line_width}" transform="scale({scale})">'
            "{}</g>"
        ).format(vector)

        html = (
            "<svg"
            ' xmlns="http://www.w3.org/2000/svg"'
            ' version="1.1"'
            ' viewBox="{bbox.x0} {bbox.y0} {bbox.x} {bbox.y}">'
            "{vector}"
            "</svg>"
        )

        html = html.format(
            angle=angle,
            vector=vector,
            #
            bbox=handler.bbox,
            scale=length / head.length,
            #
            color=color,
            line_width=border_width,
            line_color=border_color if border_color is not None else color,
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
        head: VectorIconHead = DEFAULT_HEAD,
        body: VectorIconBody = DEFAULT_BODY,
        color: str = "black",
        border_width: int | float = 0,
        border_color: str = None,
        anchor: Literal["tail", "mid", "head"] = "tail",
        popup_anchor: tuple[int, int] | None = None,
        class_name: str = "empty",
    ):
        """Makes a :class:`VectorIcon` from components of latitude and longitude direction

        Args:
            components: the components vector, latitude and longitude direction.
            head: the head metric,
                  defraulting :obj:`VectorIconHead(width=8, length=10)`.
            body: the body metric,
                  defraulting :obj:`VectorIconBody(width=2)`.
            color: the color of the vector, supporting any CSS color propery.
            border_width: the border width.
            border_color: the border color.
            anchor: the anchor of the vector.
            popup_anchor: it passes to the :class:`folium.DivIcon` constructor.
            class_name: it passes to the :class:`folium.DivIcon` constructor.

        Returns:
             a :class:`VectorIcon` obj

        Examples:
            A marker with a vector icon
            of which latitude compnent is 100 px and longitude is 50px.

            >>> folium.Marker(
            ...     (40.78322, -73.96551),
            ...     icon=VectorIcon.from_comp((100, 50)),
            ... )

            More customized example;

            >>> folium.Marker(
            ...     (40.78322, -73.96551),
            ...     icon=VectorIcon.from_comp(
            ...         (100, 50)
            ...         head=VectorIconHead(width=10, length=20),
            ...         body=VectorIconBody(width=5),
            ...         color="hsl(30deg, 100%, 50%)",
            ...         border_width=1,
            ...         border_color="red",
            ...         anchor="mid"
            ...     ),
            ... )
        """
        intensity = math.hypot(components[1], components[0])
        angle = math.atan2(components[1], components[0])

        return cls(
            length=intensity,
            angle=angle,
            head=head,
            body=body,
            color=color,
            border_width=border_width,
            border_color=border_color,
            popup_anchor=popup_anchor,
            class_name=class_name,
            anchor=anchor,
        )
