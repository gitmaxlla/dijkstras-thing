from graph import Graph, Edge
from constants import *
import math


class State:
    def __init__(self, renderer, weight_generator, path_found_callback):
        self.renderer = renderer
        self.weight_generator = weight_generator
        self.path_found_callback = path_found_callback

        self.graph = Graph()
        self.node_graphic_under_cursor = None
        self.position_before_dragging = None 
        self.selection_offset = [0, 0]
        self.selected_node_graphic_pair = []
        self.path_from_graphic = None
        self.path_to_graphic = None
        self.prev_trace = None

    def load_from_string(self, matrix_description, type):
        if matrix_description is None: return
        self.reset()

        step_radians = (2*math.pi)/len(matrix_description)
        radius = PLACE_LOADED_NODES_AROUND_RADIUS

        for i, line in enumerate(matrix_description):
            self.create_new_node(
                x=START_OFFSET + math.cos(i*step_radians)*radius,
                y=START_OFFSET + math.sin(i*step_radians)*radius)

        if type == TableType.INCIDENCY:
            for i, line in enumerate(matrix_description):
                matrix_description[i] = line.split()

            for i in range(len(matrix_description[0])):
                pair_for_edge = []
                weight = 0

                for j in range(self.graph.size()):
                    if matrix_description[j][i] != '-':
                        pair_for_edge.append(j)
                        weight = abs(int(matrix_description[j][i]))

                self.create_new_edge(
                    Edge(self.graph.nodes[pair_for_edge[0]],
                         self.graph.nodes[pair_for_edge[1]],
                         weight)
                )

        elif type == TableType.ADJACENCY:
            for i, line in enumerate(matrix_description):
                for j, connection in enumerate(line.split()):
                    if i == j: continue

                    if connection != '-':
                        weight = int(connection)
                        self.create_new_edge(Edge(self.graph.nodes[i],
                                                  self.graph.nodes[j],
                                                  weight))

    def get_node_graphic_under_cursor(self, x, y):
        if self.graph.size() == 0: return None

        for node_graphics in self.renderer.get_node_graphics()[::-1]:
            if node_graphics.overlaps(x, y):
                return node_graphics

        return None
    
    def above_empty_space(self):
        return not self.node_graphic_under_cursor

    def selection_not_empty(self):
        return self.selected_node_graphic_pair != []

    def reset_selection(self):
        for node_graphic in self.selected_node_graphic_pair:
            self.renderer.reset_node_graphic_color(node_graphic)
        self.selected_node_graphic_pair = []

    def on_mouse_left_pressed(self, event):        
        self.node_graphic_under_cursor = \
            self.get_node_graphic_under_cursor(event.x, event.y)

        if self.node_graphic_under_cursor:
            self.position_before_dragging = [
                self.node_graphic_under_cursor.x, self.node_graphic_under_cursor.y
            ]
            
            self.selection_offset = \
                self.node_graphic_under_cursor.offset_from(
                    event.x, event.y
            )

    def on_mouse_left_dragged(self, event):
        if self.node_graphic_under_cursor:
            self.node_graphic_under_cursor.set_position(
                event.x + self.selection_offset[0], 
                event.y + self.selection_offset[1]
            )
            self.renderer.move_labels_if_bound(
                self.node_graphic_under_cursor)
            

    def on_mouse_left_released(self, event):
        if self.above_empty_space():
            if self.selection_not_empty():
                self.reset_selection()
        else:
            if self.node_graphic_under_cursor.distance_to(
               *self.position_before_dragging) < DRAG_THRESHOLD:
                self.on_node_graphic_clicked(self.node_graphic_under_cursor)

        self.node_graphic_under_cursor = None

    def in_path_view(self):
        return self.prev_trace

    def on_mouse_right_clicked(self, event):
        self.node_graphic_under_cursor = \
            self.get_node_graphic_under_cursor(event.x, event.y)
        
        if not self.in_path_view():
            if self.above_empty_space(): self.create_new_node(event.x, event.y)
            else: self.remove_node(self.node_graphic_under_cursor.node)

    def create_new_node(self, x, y):
        node = self.graph.add_node()
        self.renderer.add_node_graphic(node, x, y)

    def create_new_edge(self, edge):
        self.graph.add_edge(edge)
        self.renderer.add_edge_graphic(edge)

    def remove_edge(self, edge):
        self.renderer.remove_edge_graphic(edge)
        self.graph.remove_edge(edge)

    def remove_node(self, node):
        self.renderer.remove_node_graphic(node)
        self.graph.remove_node(node)
        self.renderer.reset_node_labels()

    def reset(self):
        self.node_graphic_under_cursor = None
        self.position_before_dragging = None 
        self.selection_offset = [0, 0]
        self.selected_node_graphic_pair = []
        self.path_from_graphic = None
        self.clear_path_from()
        self.clear_path_to()

        node_list_copy = self.graph.nodes[::]
        for node in node_list_copy:
            self.remove_node(node)

    def set_path_from(self, node_graphic):
        self.path_from_graphic = node_graphic
        self.renderer.bind_from_label(node_graphic)
        self.renderer.show(self.renderer.from_label)
        self.renderer.move_from_label_if_bound(node_graphic)

    def set_path_to(self, node_graphic):
        self.path_to_graphic = node_graphic
        self.renderer.bind_to_label(node_graphic)
        self.renderer.show(self.renderer.to_label)
        self.renderer.move_to_label_if_bound(node_graphic)

    def clear_path_from(self):
        self.path_from_graphic = None
        self.renderer.hide(self.renderer.from_label)

    def clear_path_to(self):
        self.path_to_graphic = None
        self.renderer.hide(self.renderer.to_label)

    def exit_path_view(self):
        self.renderer.reset_node_labels()
        self.renderer.reset_node_colors()
        self.clear_path_from()
        self.clear_path_to()
        self.prev_trace = None

    def update_path(self, node):
        if self.path_from_graphic is None:
            self.set_path_from(node)
        elif node is self.path_from_graphic:
            self.clear_path_from()
            self.clear_path_to()
        elif self.path_to_graphic is None:
            self.set_path_to(node)
        else:
            self.set_path_from(node)
            self.clear_path_to()
        
    def different_selected(self):
        return self.selected_node_graphic_pair[0] \
               is not self.selected_node_graphic_pair[1]
    
    def edge_between_selected(self):
        found_edge = None
        edges_to_check = \
            self.selected_node_graphic_pair[0].node.affected_edges

        for edge in edges_to_check:
            if (edge._to == self.selected_node_graphic_pair[1].node or \
                edge._from == self.selected_node_graphic_pair[1].node):
                found_edge = edge
                break

        return found_edge

    def enter_path_view_mode(self):
        distances, trace = \
            self.graph.dijkstras(self.path_from_graphic.node.id, 
                                    self.path_to_graphic.node.id)

        self.path_found_callback(
            self.path_from_graphic.node.id, self.path_to_graphic.node.id,
            distances[self.path_to_graphic.node.id])

        for i, node_graphic in enumerate(self.renderer.get_node_graphics()):
            node_graphic.set_label(distances[i])

        self.prev_trace = trace
        self.renderer.color_trace(self.path_from_graphic, self.path_to_graphic, trace)

    def on_node_graphic_clicked(self, node_graphic):
        if self.in_path_view():
            self.exit_path_view()
            return

        if self.renderer.node_graphic_highlighted(node_graphic):
            self.update_path(node_graphic)
        else: self.renderer.highlight_node_graphic(node_graphic)

        self.selected_node_graphic_pair.append(node_graphic)

        if len(self.selected_node_graphic_pair) == 2:
            if self.different_selected():
                edge_between_selected = self.edge_between_selected()
                if edge_between_selected:
                    self.remove_edge(edge_between_selected)
                else:
                    new_weight = self.weight_generator(
                        self.selected_node_graphic_pair[0].node.id, 
                        self.selected_node_graphic_pair[1].node.id
                    )

                    if new_weight is not None:
                        self.create_new_edge(Edge(
                            self.selected_node_graphic_pair[0].node, 
                            self.selected_node_graphic_pair[1].node, 
                            int(new_weight, 10)
                        )
                    )

            self.reset_selection()

            if self.path_from_graphic and self.path_to_graphic:
                self.enter_path_view_mode()
