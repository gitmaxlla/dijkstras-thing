from tkinter import *
from tkinter import messagebox

from tkinter.simpledialog import askstring
from tkinter.filedialog import askopenfilename

import math
from indexed_priority_queue import IndexedPriorityQueue
from colour import Color


nodes = [] # Можно устранить глобальные переменные, например вынести в свойства класса-состояния приложения
edges = []

def prompt_matrix():
    matrix_description = None
    file = askopenfilename()

    if file == ():
        return None

    with open(file) as f:
        matrix_description = f.readlines()

    return matrix_description

def from_incidency_matrix(): # Добавить в начало имени функции load_
    # Устранить дублирование кода в начале функций from_incidency_matrix и from_adjacency_matrix
    # (Можно создать функцию, которая содержит дублирующийся код этих двух функций и вызывает в себе одну них в зависимости от типа таблицы (аргументом передается))
    matrix_description = prompt_matrix()
    if matrix_description is None: return
    
    clear()

    RADIUS = 150 # Вынести значения в константы в одном месте, например в конфигурационном классе
    START_OFFSET = RADIUS*2

    step_radians = (2*math.pi)/len(matrix_description)

    for i, line in enumerate(matrix_description):
        nodes.append(Node(START_OFFSET + math.cos(i*step_radians)*RADIUS,
                          START_OFFSET + math.sin(i*step_radians)*RADIUS))
        matrix_description[i] = line.split()

    for i in range(len(matrix_description[0])):
        pair_for_edge = []
        weight = 0
        for j in range(len(nodes)):
            if matrix_description[j][i] != '-':
                pair_for_edge.append(j)
                weight = abs(int(matrix_description[j][i]))
        edges.append(Edge(
            nodes[pair_for_edge[0]],
            nodes[pair_for_edge[1]],
            weight)
        )

def from_adjacency_matrix(): # Добавить в начало имени функции load_
    matrix_description = prompt_matrix()
    if matrix_description is None: return
    
    clear()

    RADIUS = 150
    START_OFFSET = RADIUS*2

    step_radians = (2*math.pi)/len(matrix_description)

    for i, line in enumerate(matrix_description):
        nodes.append(Node(START_OFFSET + math.cos(i*step_radians)*RADIUS,
                          START_OFFSET + math.sin(i*step_radians)*RADIUS))
        
    for i, line in enumerate(matrix_description):
        for j, connection in enumerate(line.split()):
            if i == j: continue

            if connection != '-':
                weight = int(connection)
                edges.append(Edge(nodes[i], nodes[j], weight))

position_before_dragging = None # Эти глобал переменные тоже убрать
selection_offset = [0, 0]
node_under_cursor = None

selected_pair_edge = []
path_from = None
path_to = None

prev_trace = None

def clear(): # Все подобные функции, работающие с глобал переменными, можно сделать методами класса-состояния
    nodes_copy = nodes[::]
    for node in nodes_copy:
        remove_node(node)

def build_adj_matrix():
    result = []

    for i in range(len(nodes)):
        result.append([])

        for j in range(len(nodes)):
            if i == j: result[i].append(0)
            else: result[i].append(math.inf)

    for edge in edges:
        result[edge._from.id][edge._to.id] = edge.weight

    return result

def adj_matrix_to_a_list(matrix):
    result = []
    
    for i, line in enumerate(matrix):
        entry = []
        
        for j in range(len(line)):
            if i == j: continue
            if line[j] != float("inf"): entry.append((j, line[j]))

        result.append(entry)

    return result
                

def dijkstras(adj_matrix, start, end):
    size = len(adj_matrix)

    adj_list = adj_matrix_to_a_list(adj_matrix)
    visited = [False] * size
    distances = [0 if node == start else float("inf") for node in range(size)]

    trace = [None] * size
    
    queue = IndexedPriorityQueue()
    queue.push(start, 0)

    while queue:
        node, distance = queue.pop()
        visited[node] = True

        for destination, dest_weight in adj_list[node]:
            if visited[destination]: continue

            dist_to_node = distances[node] + dest_weight
            
            if dist_to_node < distances[destination]:
                distances[destination] = dist_to_node
                trace[destination] = node
                if destination not in queue:
                    queue.push(destination, dist_to_node)
                else:
                    queue.update(destination, dist_to_node)

        if node == end: break

    return (distances, trace)

def get_node_under_cursor(x, y):
    for node in nodes[::-1]:    
        if node.overlaps(x, y):
            return node
    
    return None

def mouse_left_pressed(event): # Можно добавить в начало названия on_..., ибо обработчик события
    global node_under_cursor, selection_offset, \
        position_before_dragging
    
    node_under_cursor = \
        get_node_under_cursor(event.x, event.y)

    if node_under_cursor:
        position_before_dragging = [
            node_under_cursor.x, node_under_cursor.y]
        
        selection_offset = \
            node_under_cursor.offset_from(
                event.x, event.y
            )

def mouse_left_dragged(event): # Можно добавить в начало названия on_..., ибо обработчик события
    if node_under_cursor:
        canvas.after(0, node_under_cursor.set_position(
            event.x + selection_offset[0], 
            event.y + selection_offset[1]))

def color(object_handle, color):
    canvas.itemconfig(object_handle, fill=color)

def set_path_from(node):
    global path_from
    path_from = node
    canvas.itemconfig(from_label, state=NORMAL)

def set_path_to(node):
    global path_to
    path_to = node
    canvas.itemconfig(to_label, state=NORMAL)

def remove_path_from():
    global path_from
    path_from = None
    canvas.itemconfig(from_label, state=HIDDEN)

def remove_path_to():
    global path_to
    path_to = None
    canvas.itemconfig(to_label, state=HIDDEN)

def color_trace(_from, _to, trace):
    color_nodes = []
    color_nodes.append(_to)
    trace_copy = trace[::]

    if len(trace) == 0:
        return

    while True:
        stop = trace_copy.pop()
        if stop is None: break
        color_nodes.append(nodes[stop])

    if _from not in color_nodes:
        color_nodes.append(_from)

    start = Color("#90F1EF") # Вынести значения в константы в одном месте, например в конфигурационном классе
    colors = list(start.range_to(Color("#F67E7D"), len(color_nodes)))

    for i, node in enumerate(color_nodes):
        color(node.oval, colors[i].hex_l)


def clicked_on_node(node): # Слишком большая функция, можно разбить на функции поменьше
    global selected_pair_edge, path_from, path_to, prev_trace

    if prev_trace is not None:
        for node in nodes:
            canvas.itemconfig(node.label, text=node.id+1)
        for node in nodes:
            color(node.oval, "white") # Вынести значения в константы в одном месте, например в конфигурационном классе
        remove_path_from()
        remove_path_to()
        prev_trace = None
        return

    if 'grey' in canvas.itemconfig(node.oval)['fill']: # Вынести значения в константы в одном месте, например в конфигурационном классе
        if path_from is None:
            set_path_from(node)
        elif node is path_from:
            remove_path_from()
            remove_path_to()
        elif path_to is None:
            set_path_to(node)
        else:
            set_path_from(node)
            remove_path_to()

        node.set_position(node.x, node.y)

    color(node.oval, "grey") # Вынести значения в константы в одном месте, например в конфигурационном классе
    selected_pair_edge.append(node)

    if len(selected_pair_edge) == 2:
        already_exists = False

        for edge in edges:
            if (edge._from == selected_pair_edge[0] or \
                edge._from == selected_pair_edge[1]) and \
               (edge._to == selected_pair_edge[0] or \
                edge._to == selected_pair_edge[1]):
                edges.remove(edge)
                canvas.delete(edge.weight_label, edge.line)
                already_exists = True
                break
                
        if not already_exists:
            if not selected_pair_edge[0] is selected_pair_edge[1]:
                prompt_result = askstring("Новая дуга", 
                    f"Введите вес дуги " + \
                        f"{selected_pair_edge[0].id+1} -> {selected_pair_edge[1].id+1}:")
                if prompt_result is not None:
                    weight = int(prompt_result, 10)
                    edges.append(Edge(*selected_pair_edge, weight))

        selected_pair_edge = reset_selection(selected_pair_edge) 

        if path_from is not None and path_to is not None:
            distances, trace = \
                dijkstras(build_adj_matrix(), path_from.id, path_to.id)

            messagebox.showinfo("Результат", 
                f"Кратчайшее расстояние от узла номер {path_from.id+1} " + \
                f"до узла номер {path_to.id+1}: {distances[path_to.id]}")

            for i, node in enumerate(nodes):
                canvas.itemconfig(node.label, text=distances[i])
            prev_trace = trace
            color_trace(path_from, path_to, trace)

def mouse_left_released(event): # Можно добавить в начало названия on_..., ибо обработчик события
    global node_under_cursor, selected_pair_edge, prev_trace
    DRAG_THRESHOLD = 5 # Вынести значения в константы в одном месте, например в конфигурационном классе

    if node_under_cursor:
        if node_under_cursor.distance_to(
            *position_before_dragging) < DRAG_THRESHOLD:
            clicked_on_node(node_under_cursor)
    elif len(selected_pair_edge) != 0:
        selected_pair_edge = reset_selection(selected_pair_edge)

    node_under_cursor = None

def remove_node(node):
    global nodes, edges
    edges_to_remove = []
    for edge in edges:
        if edge._from is node or edge._to is node:
            edges_to_remove.append(edge)
            canvas.delete(edge.line)
            canvas.delete(edge.weight_label)

    for edge in edges_to_remove:
        edges.remove(edge)
    
    canvas.delete(node.oval)
    canvas.delete(node.label)
    nodes.remove(node)

    Node._counter = 0
    for node in nodes:
        node.id = Node._counter
        Node._counter += 1
        canvas.itemconfig(node.label, text=node.id+1)

def reset_selection(selected):
    for node in selected:
        color(node.oval, "white") # Вынести значения в константы в одном месте, например в конфигурационном классе
    return []

def mouse_right_clicked(event): # Можно добавить в начало названия on_..., ибо обработчик события
    node_under_cursor = \
        get_node_under_cursor(event.x, event.y)
    
    if not prev_trace:
        if not node_under_cursor:
            create_new_node(event.x, event.y)
        else: remove_node(node_under_cursor)

def create_new_node(x, y):
    nodes.append(Node(x, y))

def open_file():
    filename = askopenfilename()
    return filename

def update_edge_positions(node):
    for edge in edges:
        if edge._from is node or edge._to is node:
           edge.update_position()

class Node: # Логика отрисовки в классах Node и Edge, что вроде как не есть хорошо (Сингл Респонсибилити Принципл), можно создать класс-рендер для работы с канвасом и вынести всё туда
    SIZE = 50 # Вынести значения в константы в одном месте, например в конфигурационном классе

    canvas = None
    _counter = 0

    def __init__(self, x, y):
        self.id = Node._counter
        Node._counter += 1
        
        self.oval = \
            canvas.create_oval(0, Node.SIZE, Node.SIZE, 0, 
                               fill="white")

        self.label = \
            canvas.create_text(Node.SIZE / 2, Node.SIZE / 2, 
                               text=Node._counter)
        
        self.set_position(x, y)

    def set_position(self, x, y):
        if self is path_from:
            canvas.moveto(from_label, self.x - 12, self.y - Node.SIZE)
        elif self is path_to:
            canvas.moveto(to_label, self.x - 4, self.y - Node.SIZE)

        self.x = x
        self.y = y
        graphics_coords = (x - Node.SIZE / 2, y - Node.SIZE / 2)
        canvas.moveto(self.oval, *graphics_coords)
        canvas.moveto(self.label, x-(len(str(self.id))*4), y-6)
        update_edge_positions(self)

    def overlaps(self, x, y):
        return self.distance_to(x, y) <= Node.SIZE / 2

    def distance_to(self, x, y):
        return math.dist([self.x, self.y], [x, y])

    def offset_from(self, x, y):
        return [
            self.x - x,
            self.y - y
        ]

class Edge:
    canvas = None

    def __init__(self, _from, _to, weight=0):
        self._from = _from
        self._to = _to
        self.line = canvas.create_line(self._from.x, self._from.y,
                           self._to.x, self._to.y, arrow=LAST,
                           tags="edge", width=3)

        self.weight = weight
        self.weight_label = canvas.create_text(0, 0, text=self.weight)
        
        canvas.tag_lower("edge")
        self.update_position()

    def update_position(self):
        angle_between_nodes = math.pi / 2

        if self._to.x != self._from.x:
            angle_between_nodes = math.atan(
                (self._to.y - self._from.y) / 
                (self._to.x - self._from.x)
            )

        x_shift = (Node.SIZE / 2) * \
            abs(math.cos(angle_between_nodes)) * \
            math.copysign(1, self._to.x - self._from.x)

        y_shift = (Node.SIZE / 2) * \
            abs(math.sin(angle_between_nodes)) * \
            math.copysign(1, self._to.y - self._from.y)

        canvas.coords(
            self.line,
            self._from.x + x_shift, self._from.y + y_shift,
            self._to.x + - x_shift, self._to.y + - y_shift
        )

        canvas.itemconfig(self.weight_label, angle=-math.degrees(angle_between_nodes))

        x_difference = self._to.x - self._from.x
        y_difference = self._to.y - self._from.y

        LABEL_DISTANCE = -30 # Вынести значения в константы в одном месте, например в конфигурационном классе

        shift_label_x = math.cos(angle_between_nodes + math.pi/2)*LABEL_DISTANCE - len(str(self.weight))*4
        shift_label_y = math.sin(angle_between_nodes + math.pi/2)*LABEL_DISTANCE - 6

        canvas.moveto(self.weight_label, 
                      self._from.x + shift_label_x + x_difference/2,
                      self._from.y + shift_label_y + y_difference/2)

def show_info():
    messagebox.showinfo("Справка", 
        "Dijkstra's thing (gitmaxlla 2025)\n\nПрограмма позволяет строить " + \
        "взвешенные однонаправленные графы и вычислять кратчайшие расстояния " + \
        "между узлами через алгоритм Дейсткры.\n\nПКМ по пустому пространству - " + \
        "создать узел.\nПКМ по узлу - удалить узел.\n\nДва клика по узлу - задать " + \
        "его как одну из конечных точек.\nКлики по двум разным узлам - задать " + \
        "новую дугу или удалить существующую.\n\nКогда обе конечные точки будут " + \
        "заданы, программа вычислит расстояние и отобразит вспомогательную информацию " + \
        "на самом графе. После ознакомления с ней для дальнейшего взаимодействия с " + \
        "программой нажмите ЛКМ на любой узел.")

def build_menu():
    load_submenu = Menu()
    load_submenu.add_command(label="Матрица смежности", command=from_adjacency_matrix)
    load_submenu.add_command(label="Матрица инцидентности", command=from_incidency_matrix)

    submenu = Menu(tearoff=0)
    submenu.add_cascade(label="Загрузить из файла", menu=load_submenu)
    submenu.add_command(label="Очистить", command=clear)

    menu = Menu()
    menu.add_cascade(label="Граф", menu=submenu)
    menu.add_command(label="Справка", command=show_info)
    return menu

root = Tk()
root.title("Dijkstra's thing")
root.geometry("1280x720")

canvas = Canvas(bg="white") # Вынести значения в константы в одном месте, например в конфигурационном классе
canvas.pack(fill="both", anchor=CENTER, expand=True)

from_label = canvas.create_text(0, 0, text="from", angle=0, state=HIDDEN)
to_label = canvas.create_text(0, 0, text="to", angle=0, state=HIDDEN)

Node.canvas = canvas
Edge.canvas = canvas

root.bind("<ButtonPress-1>", mouse_left_pressed)
root.bind("<B1-Motion>", mouse_left_dragged)
root.bind("<ButtonRelease-1>", mouse_left_released)

root.bind("<Button-3>", mouse_right_clicked)

root.config(menu=build_menu())
root.mainloop()
