from tkinter import *
from tkinter import messagebox

from tkinter.simpledialog import askstring
from tkinter.filedialog import askopenfilename

from constants import BACKGROUND_COLOR, PROGRAM_ABOUT, TableType
from state import State
from graphics import Renderer


def prompt_matrix_from_file():
    matrix_description = None

    file = askopenfilename()
    if file == ():
        return None

    with open(file) as f:
        matrix_description = f.readlines()

    return matrix_description

def prompt_edge_weight(from_id, to_id):
    result = askstring(
        "Новая дуга", 
        f"Введите вес дуги " + \
        f"{from_id+1} -> {to_id+1}:"
    )

    return result

def path_found_callback(from_id, to_id, distance):
    messagebox.showinfo("Результат", 
    f"Кратчайшее расстояние от узла номер {from_id+1} " + \
    f"до узла номер {to_id+1}: {distance}")

def show_program_info():
    messagebox.showinfo("Справка", PROGRAM_ABOUT)

def build_menu():
    load_submenu = Menu()
    load_submenu.add_command(label="Матрица смежности", 
                             command=lambda: state.load_from_string(
                                prompt_matrix_from_file(), 
                                TableType.ADJACENCY))
    
    load_submenu.add_command(label="Матрица инцидентности", 
                             command=lambda: state.load_from_string(
                                prompt_matrix_from_file(), 
                                TableType.INCIDENCY))

    submenu = Menu(tearoff=0)
    submenu.add_cascade(label="Загрузить из файла", menu=load_submenu)
    submenu.add_command(label="Очистить", command=lambda: state.reset())

    menu = Menu()
    menu.add_cascade(label="Граф", menu=submenu)
    menu.add_command(label="Справка", command=show_program_info)
    return menu

def set_handlers():
    root.bind("<ButtonPress-1>", state.on_mouse_left_pressed)
    root.bind("<B1-Motion>", state.on_mouse_left_dragged)
    root.bind("<ButtonRelease-1>", state.on_mouse_left_released)

    root.bind("<Button-3>", state.on_mouse_right_clicked)

root = Tk()
root.title("Dijkstra's thing")
root.geometry("1280x720")

canvas = Canvas(bg=BACKGROUND_COLOR)
canvas.pack(fill="both", anchor=CENTER, expand=True)

state = State(renderer=Renderer(canvas),
              weight_generator=prompt_edge_weight,
              path_found_callback=path_found_callback)

set_handlers()
root.config(menu=build_menu())
root.mainloop()
