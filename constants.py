from enum import Enum


class TableType(Enum):
    ADJACENCY = 0
    INCIDENCY = 1


DRAG_THRESHOLD = 5
LABEL_DISTANCE_FROM_EDGE = -30

PLACE_LOADED_NODES_AROUND_RADIUS = 150
START_OFFSET = PLACE_LOADED_NODES_AROUND_RADIUS*2

BACKGROUND_COLOR = "white"
NODE_SELECTED_COLOR = "grey"

PATH_START_COLOR = "#90F1EF"
PATH_END_COLOR = "#F67E7D"

PROGRAM_ABOUT = "Dijkstra's thing (gitmaxlla 2025)\n\nПрограмма позволяет строить " + \
                "взвешенные однонаправленные графы и вычислять кратчайшие расстояния " + \
                "между узлами через алгоритм Дейсткры.\n\nПКМ по пустому пространству - " + \
                "создать узел.\nПКМ по узлу - удалить узел.\n\nДва клика по узлу - задать " + \
                "его как одну из конечных точек.\nКлики по двум разным узлам - задать " + \
                "новую дугу или удалить существующую.\n\nКогда обе конечные точки будут " + \
                "заданы, программа вычислит расстояние и отобразит вспомогательную информацию " + \
                "на самом графе. После ознакомления с ней для дальнейшего взаимодействия с " + \
                "программой нажмите ЛКМ на любой узел."

NODE_DISPLAY_DIAMETER = 50
