import contextlib
from typing import Sequence, Tuple, Union

from IPython.display import display

from .turtle import DimPoint, Turtle

_turtle = None

# The simplified API.


def _check_turtle():
    global _turtle
    if _turtle is None:
        _turtle = Turtle()
        _turtle.stats = {
            "moves": 0,
            "jumps": 0,
            "strokes": 0,
            "turns": 0,
            "words": [],
            "_last_down": 0,
        }
        display(_turtle)
    return _turtle


def clear():
    """Clear the canvas."""
    tu = _check_turtle()
    _turtle.stats = {
        "moves": 0,
        "jumps": 0,
        "strokes": 0,
        "turns": 0,
        "words": [],
        "_last_down": 0,
    }
    tu.clear()


def move(distance: float):
    """Move the turtle by distance pixels."""
    tu = _check_turtle()
    tu.stats["moves"] += 1
    tu.move(distance)


def turn(degrees: float):
    """Turn the pen by degrees. Positive numbers turn left, negative numbers
    turn right."""
    tu = _check_turtle()
    tu.stats["turns"] += 1
    tu.turn(degrees)


def pen_up():
    """Pick the pen up. Movements won't make lines."""
    tu = _check_turtle()
    if tu.stats["moves"] > tu.stats["_last_down"]:
        tu.stats["strokes"] += 1
    tu.pen_up()


def pen_down():
    """Put the pen down. Movements will make lines."""
    tu = _check_turtle()
    tu.stats["_last_down"] = tu.stats["moves"]
    tu.pen_down()


def show_turtle():
    """Show the turtle in the scene."""
    tu = _check_turtle()
    tu.show()


def hide_turtle():
    """Hide the turtle in the scene."""
    tu = _check_turtle()
    tu.hide()


def write(
    text: str, font: str = "24px sans-serif", text_align: str = "center"
):
    """Write text.

    Arguments:

        text: The text to write
        font: The HTML font specification
        text_align: The alignment of the text relative to the turtle
    """
    tu = _check_turtle()
    tu.stats["words"].append(text)
    tu.write(text, font, text_align)


def goto(*place: Union[Tuple[int, int], Sequence[int], DimPoint]):
    """Jump to a point"""
    tu = _check_turtle()
    tu.stats["moves"] += 1
    tu.stats["jumps"] += 1
    tu.pos = place


def set_background(filename: str):
    """Set the background image"""
    tu = _check_turtle()
    tu.background(filename)


def set_heading(heading: float):
    """Set the pen to face heading in degrees."""
    tu = _check_turtle()
    tu.stats["turns"] += 1
    tu.heading = heading


def set_color(color: Union[str, int]):
    """Set the pen color using HTML color notation."""
    tu = _check_turtle()
    tu.color = color


def set_width(width: int):
    """Set the line thickness."""
    tu = _check_turtle()
    tu.width = width


def set_size(width: int, height: int):
    """Set the size of the arena."""
    tu = _check_turtle()
    tu.size = (width, height)


@contextlib.contextmanager
def polygon(
    *,
    color: str | None = None,
    width: int | None = None,
    fill: str | None = None,
):
    """
    Draw a polygon by connecting moves together.

    Example:

    with tu.polygon():
        tu.move(30)
        tu.turn(45)
        tu.move(30)
        tu.turn(45)
        tu.move(30)
    """
    tu = _check_turtle()
    old_color = tu.color
    old_width = tu.width
    old_fill = tu.fill
    try:
        if color is not None:
            tu.color = color
        if fill is not None:
            tu.fill = fill
        if width is not None:
            tu.width = width

        with tu.polygon():
            yield

    finally:
        tu.color = old_color
        tu.fill = old_fill
        tu.width = old_width


def pre_run_cell(info):
    """
    Callback before a cell is run.
    """
    global _turtle
    _turtle = None


def post_run_cell(result):
    """
    Callback after a cell has run.
    """
    global _turtle
    result.turtle = _turtle
    if _turtle is not None:
        if _turtle.stats["moves"] > _turtle.stats["_last_down"]:
            _turtle.stats["strokes"] += 1


def load_ipython_extension(ipython):
    ipython.events.register("pre_run_cell", pre_run_cell)
    ipython.events.register("post_run_cell", post_run_cell)
