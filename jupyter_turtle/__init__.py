"""
"""

from IPython.display import display

from . import drawing

from typing import Dict, List, Sequence, Tuple, Union

_t = None 

def _turtle():
    global _t
    if _t is None:
        _t = drawing.Turtle()
    return _t 

def clear():
    _turtle().clear()

def draw(distance: float):
    _turtle().draw(distance)

def turn(degrees: float):
    _turtle().turn(degrees)

def goto(*place: Union[Tuple[int,int], Sequence[int], drawing.Turtle.DimPoint]):
    _turtle().goto(*place)

def heading(heading: float):
    _turtle().heading(heading)

def up():
    _turtle().up()

def down():
    _turtle().down()

def color(color: str):
    _turtle().color(color)

def width(width: int):
    _turtle().width(width)

def show():
    _turtle().show()

def hide():
    _turtle().hide()

def background(filename: str):
    _turtle().background(filename)

def find_faces() -> List[Dict[str, Union[Tuple[int, int], Sequence[Tuple[int, int]]]]]:
    _turtle().find_faces()

def polygon(points: Sequence[Tuple[int, int]]):
    _turtle().polygon(points)

def write(text: str, font: str="24px sans-serif", text_align: str="center", line_color: str=None, fill_color: str=None):
    _turtle().write(text, font, text_align, line_color, fill_color)

def pre_run_cell(info):
    global _t
    _t = None

def post_run_cell(result):
    global _t
    if _t is not None:
        display(_t)

def load_ipython_extension(ipython):
    ipython.events.register('pre_run_cell', pre_run_cell)
    ipython.events.register('post_run_cell', post_run_cell)

def unload_ipython_extension(ipython):
    ipython.events.unregister('pre_run_cell', pre_run_cell)
    ipython.events.unregister('post_run_cell', post_run_cell)

