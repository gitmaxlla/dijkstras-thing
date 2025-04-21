from constants import *
from tkinter import HIDDEN, LAST, NORMAL

import math
from colour import Color


class Renderer:
    def __init__(self, canvas):
        self.nodes = {}
        self.edges = {}

        self.canvas = canvas
        self.from_label = canvas.create_text(
            0, 0, text="from", angle=0, state=HIDDEN)
        self.to_label = canvas.create_text(
            0, 0, text="to", angle=0, state=HIDDEN)
        
        self.from_label_bind = None
        self.to_label_bind = None
    
    def hide(self, obj_handle):
        self.canvas.itemconfig(obj_handle, state=HIDDEN)

    def show(self, obj_handle):
        self.canvas.itemconfig(obj_handle, state=NORMAL)

    def node_graphic_highlighted(self, node_graphic):
        return NODE_SELECTED_COLOR in \
            self.canvas.itemconfig(node_graphic.oval)['fill']

    def highlight_node_graphic(self, node_graphic):
        self.color(node_graphic.oval, NODE_SELECTED_COLOR)

    def add_node_graphic(self, node, x, y):
        self.nodes[node] = NodeGraphic(self, node, x, y)

    def add_edge_graphic(self, edge):
        self.edges[edge] = EdgeGraphic(
            self, self.get_node_graphic(edge._from),
            self.get_node_graphic(edge._to), str(edge.weight))

    def get_node_graphics(self):
        return list(self.nodes.values())

    def get_node_graphic(self, node):
        return self.nodes[node]

    def get_edge_graphic(self, edge):
        if edge in self.edges:
            return self.edges[edge]
        return None

    def remove_affected_edges_graphics(self, node):
        for edge in node.affected_edges:
            self.remove_edge_graphic(edge)

    def remove_node_graphic(self, node):
        node_graphic = self.get_node_graphic(node)
        self.nodes.pop(node)
        self.remove_affected_edges_graphics(node)
        self.canvas.delete(node_graphic.oval, 
                           node_graphic.label)

    def remove_edge_graphic(self, edge):
        edge_graphics = self.get_edge_graphic(edge)
        if edge_graphics:
            self.edges.pop(edge)
            self.canvas.delete(edge_graphics.weight_label,
                               edge_graphics.line)

    def generate_gradient_colors(color_from, color_to, steps):
        start = Color(color_from)
        return list(start.range_to(Color(color_to), steps))

    def reset_node_labels(self):
        for node_graphic in self.nodes.values():
            node_graphic.reset_label()

    def reset_node_colors(self):
        for node_graphic in self.nodes.values():
            self.reset_node_graphic_color(node_graphic)

    def get_text_centering_offset(obj):
        return (-len(str(obj))*4, -6)

    def color(self, object_handle, color):
        self.canvas.itemconfig(object_handle, fill=color)

    def reset_node_graphic_color(self, node_graphic):
        self.reset_color(node_graphic.oval)

    def move_labels_if_bound(self, node_graphic):
        self.move_from_label_if_bound(node_graphic)
        self.move_to_label_if_bound(node_graphic)

    def move_from_label_if_bound(self, node_graphic):
        if node_graphic is self.from_label_bind:
            self.canvas.moveto(
                self.from_label, 
                node_graphic.x - 12, 
                node_graphic.y - NODE_DISPLAY_DIAMETER
            )

    def move_to_label_if_bound(self, node_graphic):
        if node_graphic is self.to_label_bind:
            self.canvas.moveto(
                self.to_label,
                node_graphic.x - 4,
                node_graphic.y - NODE_DISPLAY_DIAMETER
            )

    def bind_from_label(self, node_graphic):
        self.from_label_bind = node_graphic
        self.move_from_label_if_bound(node_graphic)

    def bind_to_label(self, node_graphic):
        self.to_label_bind = node_graphic
        self.move_to_label_if_bound(node_graphic)

    def color_trace(self, from_node_graphic, to_node_graphic, trace):
        color_nodes = []
        color_nodes.append(to_node_graphic)
        trace_copy = trace[::]

        if len(trace) == 0:
            return

        while True:
            stop = trace_copy.pop()
            if stop is None: break
            color_nodes.append(self.get_node_graphics()[stop])

        if from_node_graphic not in color_nodes:
            color_nodes.append(from_node_graphic)

        colors = Renderer.generate_gradient_colors(PATH_START_COLOR, PATH_END_COLOR, len(color_nodes))
        for i, node_graphics in enumerate(color_nodes):
            self.color(node_graphics.oval, colors[i].hex_l)

    def reset_color(self, object_handle):
        self.color(object_handle, BACKGROUND_COLOR)


class NodeGraphic:
    def __init__(self, renderer, node, x, y):
        self.renderer = renderer
        self.canvas = self.renderer.canvas
        self.node = node

        self.oval = \
            self.canvas.create_oval(
                0, NODE_DISPLAY_DIAMETER, 
                NODE_DISPLAY_DIAMETER, 0, 
                fill=BACKGROUND_COLOR
            )

        self.label = \
            self.canvas.create_text(
                NODE_DISPLAY_DIAMETER / 2, 
                NODE_DISPLAY_DIAMETER / 2, 
                text=self.node.id+1
            )
        
        self.set_position(x, y)

    def set_label(self, text):
        self.canvas.itemconfig(self.label, text=text)

    def reset_label(self):
        self.canvas.itemconfig(self.label, text=self.node.id+1)

    def set_position(self, x, y):
        self.x = x
        self.y = y

        graphics_coords = (x - NODE_DISPLAY_DIAMETER / 2, y - NODE_DISPLAY_DIAMETER / 2)
        self.canvas.moveto(self.oval, *graphics_coords)

        centering_x, centering_y = Renderer.get_text_centering_offset(self.node.id)
        self.canvas.moveto(self.label, x + centering_x, y + centering_y)

        for edge in self.node.affected_edges:
            self.renderer.get_edge_graphic(edge).update_position()

    def overlaps(self, x, y):
        return self.distance_to(x, y) <= NODE_DISPLAY_DIAMETER / 2

    def distance_to(self, x, y):
        return math.dist([self.x, self.y], [x, y])

    def offset_from(self, x, y):
        return [
            self.x - x,
            self.y - y
        ]

class EdgeGraphic:
    def __init__(self, renderer, 
                 node_from_graphic, node_to_graphic,
                 weight_str):
        self.renderer = renderer
        self.canvas = self.renderer.canvas
        self.weight_str = weight_str
        self.node_from_graphic = node_from_graphic
        self.node_to_graphic = node_to_graphic

        from_x, from_y = self.get_from_coords()
        to_x, to_y = self.get_to_coords()

        self.line = self.canvas.create_line(
            from_x, from_y,
            to_x, to_y, arrow=LAST,
            tags=["edge"], width=3
        )

        self.weight_label = \
            self.canvas.create_text(0, 0, text=self.weight_str)
        
        self.move_behind()
        self.update_position()

    def get_from_coords(self):
        from_x = self.node_from_graphic.x
        from_y = self.node_from_graphic.y
        return (from_x, from_y)

    def get_to_coords(self):
        to_x = self.node_to_graphic.x
        to_y = self.node_to_graphic.y
        return (to_x, to_y)

    def move_behind(self):
        self.canvas.tag_lower("edge")

    def get_angle_between_connected_nodes(from_x, from_y, to_x, to_y):
        angle = math.pi / 2
        if to_x != from_x:
            angle = math.atan(
                (to_y - from_y) / 
                (to_x - from_x)
            )
        return angle

    def update_position(self):
        from_x, from_y = self.get_from_coords()
        to_x, to_y = self.get_to_coords()

        angle_between_nodes = \
            EdgeGraphic.get_angle_between_connected_nodes(
                from_x, from_y, to_x, to_y
            )

        x_shift = (NODE_DISPLAY_DIAMETER / 2) \
            * abs(math.cos(angle_between_nodes)) \
            * math.copysign(1, to_x - from_x)

        y_shift = (NODE_DISPLAY_DIAMETER / 2) \
            * abs(math.sin(angle_between_nodes)) \
            * math.copysign(1, to_y - from_y)

        self.canvas.coords(
            self.line,

            from_x + x_shift,
            from_y + y_shift,

            to_x + - x_shift,
            to_y + - y_shift
        )

        self.canvas.itemconfig(self.weight_label, 
                               angle=-math.degrees(angle_between_nodes))

        x_distance = to_x - from_x
        y_distance = to_y - from_y

        centering_x, centering_y = \
            Renderer.get_text_centering_offset(self.weight_str)

        shift_label_x = math.cos(angle_between_nodes + math.pi/2) \
            * LABEL_DISTANCE_FROM_EDGE + centering_x
        
        shift_label_y = math.sin(angle_between_nodes + math.pi/2) \
            * LABEL_DISTANCE_FROM_EDGE + centering_y

        self.canvas.moveto(self.weight_label, 
                      from_x + shift_label_x + x_distance / 2,
                      from_y + shift_label_y + y_distance / 2)