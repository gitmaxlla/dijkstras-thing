# Dijkstra's thing
A small application built to enhance practical knowledge about graph theory.

# Simple preview
![image](https://github.com/user-attachments/assets/4c037c71-3e3f-43aa-9161-06bc0dbe0113)

# Features
* Load graph from adjacency/incidency matrix
* See the calculated path dynamically on the graph itself

# File specification (graph from the shown preview):
* Adjacency matrix:
```
0 5 1 - -
- 0 - - 2
- - 0 2 -
- - - 0 3
- - - - 0
```

* Incidency matrix:
```
 5  1  -  -  -
-5  -  2  -  -
 - -1  -  -  2
 -  -  -  3 -2
 -  - -2 -3  -
```

# Technology
**tkinter** graphics library for window, canvas, and menu rendering; **colour** library to generate path gradient colors; **indexed-priority-queue** library to implement efficient Dijkstra's algorithm.
