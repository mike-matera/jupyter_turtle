"""
A simple implementation of turtle graphics for teaching algorithms. 

Author: Mike Matera
"""

import math 
import pathlib
import numpy 
import PIL 
import contextlib
import face_recognition

from collections import namedtuple
from ipycanvas import Canvas, MultiCanvas, hold_canvas

from IPython.display import display

from typing import Dict, List, Sequence, Tuple, Union


class Turtle:

    DimPoint = namedtuple('DimPoint', ['x', 'y'])

    def __init__(self, size=(600, 300), **kwargs):
        """Create a Turtle drawing canvas.
        
        Arguments:
            image: Load the image into the canvas. 
            size: Set the size of the canvas.
        """
        # Load the Turtle image
        turtle = numpy.array(PIL.Image.open(pathlib.Path(__file__).parent / "turtle.png"))
        self._turtle = Canvas(width=turtle.shape[0], height=turtle.shape[1])
        self._turtle.put_image_data(turtle)

        # Create a new Canvas
        self._size = Turtle.DimPoint(size[0], size[1])
        self._canvas = MultiCanvas(n_canvases=3, width=self._size.x, height=self._size.y, **kwargs) 

        # Initialize properties
        self._current = self._to_native(Turtle.DimPoint(0,0))
        self._cur_heading = (3 * math.pi) / 2 # in Canvas Y is negative.
        self._pendown = True 
        self._show = True
        self._fill = None
        self._image = None

        # Render the turtle
        with self._do_draw():
            self._canvas.clear()

    @contextlib.contextmanager
    def _do_draw(self):
        """Context manager that combines all drawing operations and re-renders the turtle."""
        with hold_canvas(self._canvas):
            yield 
            self._canvas[2].clear()
            if self._show:
                self._canvas[2].save()
                self._canvas[2].translate(self._current.x, self._current.y)
                self._canvas[2].rotate(self._cur_heading + math.pi / 2)
                self._canvas[2].draw_image(self._turtle, 
                    x=-15, y=-15, 
                    width=30, height=30)
                self._canvas[2].restore()

    def _to_native(self, point: Tuple[int, int]) -> DimPoint:
        """Convert Turtle coordinates to native ones."""
        return Turtle.DimPoint(x=self._size.x//2 + point[0], y=self._size.y//2 - point[1])

    def _to_turtle(self, point: DimPoint) -> Tuple[int, int]:
        """Convert Turtle coordinates to native ones."""
        return (point[0] - self._size.x//2, self._size.y//2 - point[1])
        
    def _ipython_display_(self):
        display(self._canvas)
    
    def new(self, size=(600, 300), **kwargs):
        # Render into the notebook
        self.__init__(size, **kwargs)
        display(self._canvas)

    def move(self, distance: float):
        """Move the pen by distance."""
        with self._do_draw():
            start = self._current
            self._current = Turtle.DimPoint(x = self._current.x + math.cos(self._cur_heading) * distance,
                            y = self._current.y + math.sin(self._cur_heading) * distance)                        
            if self._pendown:
                self._canvas[1].begin_path()
                self._canvas[1].move_to(*start)
                self._canvas[1].line_to(*self._current)
                self._canvas[1].stroke()

    def turn(self, degrees: float):
        """Turn the pen by degrees."""
        with self._do_draw():
            self._cur_heading = (self._cur_heading - math.radians(degrees)) % (math.pi * 2)

    def pen_up(self):
        """Pick the pen up. Movements won't make lines."""
        self._pendown = False

    def pen_down(self):
        """Put the pen down. Movements will make lines."""
        self._pendown = True

    def show(self):
        """Show the turtle in the scene.""" 
        with self._do_draw():
            self._show = True 
    
    def hide(self):
        """Hide the turtle in the scene.""" 
        with self._do_draw():
            self._show = False 
    
    def background(self, filename: str):
        """Set the background image"""
        self._image = numpy.array(PIL.Image.open(filename))
        self.size = (self._image.shape[1], self._image.shape[0])
        self._canvas[0].put_image_data(self._image)

    def find_faces(self) -> List[Dict[str, Union[Tuple[int, int], Sequence[Tuple[int, int]]]]]:
        """
        Find the faces in the background image. Returns list of dictionaries, one for each 
        face that's found. Face dictionaries have landmark names as keys and points as 
        values. 

        The face dictionary has two types of values. Single-point values and path values. 
        The single point values are: 

            "top_right", "top_left", "bottom_right", "bottom_left" 

        The points in these keys are the box where the face was found. The other values 
        are paths that form the contour of a facial feature. They are: 

            "bottom_lip", "top_lip", "left_eye", "right_eye", "left_eyebrow", "right_eyebrow", 
            "nose_tip", "nose_bridge", "chin" 
        
        Returns:

            A list of face dictionaries. 
        """
        if self._image is None:
            return []
        
        faces = face_recognition.face_locations(self._image, model='hog')
        features = face_recognition.face_landmarks(self._image, face_locations=faces)
        rval = []        
        for i in range(len(faces)):
            face = {}
            face.update({
                'top_right':    self._to_turtle(Turtle.DimPoint(x=faces[i][1], y=faces[i][0])),
                'top_left':     self._to_turtle(Turtle.DimPoint(x=faces[i][3], y=faces[i][0])),
                'bottom_left':  self._to_turtle(Turtle.DimPoint(x=faces[i][3], y=faces[i][2])),
                'bottom_right': self._to_turtle(Turtle.DimPoint(x=faces[i][1], y=faces[i][2])),                
            })
            for feature in features[i]:
                face[feature] = list(map(self._to_turtle, features[i][feature]))
            rval.append(face)
        return rval

    def polygon(self, points: Sequence[Tuple[int, int]], fill=True):
        """Draw a filled polygon.
        
        Arguments:

            points: A list of 2D tuples of (x,y)

        """
        with self._do_draw():
            self._canvas[1].begin_path()
            self._canvas[1].move_to(*self._to_native(points[0]))
            for point in points[1:]:
                self._canvas[1].line_to(*self._to_native(point))
            self._canvas[1].close_path()
            self._canvas[1].stroke()
            if self._fill is not None:
                self._canvas[1].fill()

    def write(self, text: str, font: str="24px sans-serif", text_align: str="center", line_color: str=None, fill_color: str=None):
        """Write text.
        
        Arguments:

            text: The text to write 
            font: The HTML font specification 
            text_align: The alignment of the text relative to the turtle 
            line_color: The color of the outline of the text (defaults to the pen color)
            fill_color: The color of the fill of the text (defaults to the pen color)
        """
        with self._do_draw():
            old_stroke = self._canvas[1].stroke_style
            old_fill = self._canvas[1].fill_style
            if line_color is not None:
                self._canvas[1].stroke_style = line_color
            if fill_color is not None:
                self._canvas[1].fill_style = fill_color
            self._canvas[1].translate(self._current.x, self._current.y)
            self._canvas[1].rotate(self._cur_heading + math.pi/2)
            self._canvas[1].font = font
            self._canvas[1].text_align = text_align
            self._canvas[1].fill_text(text, 0, 0)
            self._canvas[1].stroke_text(text, 0, 0)
            self._canvas[1].reset_transform()
            self._canvas[1].stroke_style = old_stroke
            self._canvas[1].fill_style = old_fill

    @property
    def size(self) -> Tuple[int,int]:
        """Get the size of the canvas' color buffer (not layout size)."""
        return (self._size.x, self._size.y)

    @size.setter
    def size(self, newsize: Tuple[int,int]):
        """Resize the canvas element and adjust they layout size."""
        self._size = Turtle.DimPoint(x=newsize[0], y=newsize[1])
        with self._do_draw():            
            self._canvas.width = self._size.x
            self._canvas.height = self._size.y
            
            # Move the turtle to the center
            self._current = self._to_native(Turtle.DimPoint(0,0))
            self._cur_heading = (3 * math.pi) / 2 # in Canvas Y is negative.

            if self._size.x >= 800:
                self._canvas.layout.width = "90%"
                self._canvas.layout.max_width = f"{self._size.x}px"
                self._canvas.layout.min_width = "800px"
            else:
                self._canvas.layout.width = "auto"
                self._canvas.layout.max_width = "auto"
                self._canvas.layout.min_width = "auto"

    @property
    def pos(self) -> Tuple[int,int]:
        """Get the current location of the Turtle."""
        return self._to_turtle(self._current)
    
    @pos.setter
    def pos(self, *place: Union[Tuple[int,int], Sequence[int], DimPoint]):
        """Goto a point in the coordinate space."""
        if len(place) == 0:
            raise ValueError("Goto where?")
        elif isinstance(place[0], Turtle.DimPoint):
            p = place[0]
        elif isinstance(place[0], tuple):
            p = Turtle.DimPoint._make(*place)
        else:
            p = Turtle.DimPoint._make(place)

        with self._do_draw():
            start = self._current
            self._current = self._to_native(p)
            if self._pendown:
                self._canvas[1].begin_path()
                self._canvas[1].move_to(*start)
                self._canvas[1].line_to(*self._current)
                self._canvas[1].stroke()

    @property
    def heading(self) -> float:
        """Get the current heading."""
        return -math.degrees(self._cur_heading + math.pi/2) % 360

    @heading.setter
    def heading(self, heading: float):
        """Set the pen to face heading in degrees."""
        with self._do_draw():
            self._cur_heading = math.radians(-heading - 90) % (math.pi * 2)

    @property
    def color(self) -> str:
        """Set the pen color using HTML color notation."""
        return self._canvas[1].stroke_style

    @color.setter
    def color(self, color: str):
        """Set the pen color using HTML color notation."""
        self._canvas[1].stroke_style = color

    @property
    def fill(self) -> str:
        """Set the pen color using HTML color notation."""
        return self._fill

    @fill.setter
    def fill(self, color: str):
        """Set the pen color using HTML color notation."""
        self._fill = color
        if color is not None:
            self._canvas[1].fill_style = color

    @property
    def width(self) -> int:
        return self._canvas[1].line_width

    @width.setter
    def width(self, width: int):
        """Set the line thickness."""
        self._canvas[1].line_width = width 

    