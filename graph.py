from indexed_priority_queue import IndexedPriorityQueue
import math


class Graph:
    def __init__(self):
        self.nodes = []
        self.edges = []

    def size(self):
        return len(self.nodes)
    
    def get_adj_matrix(self):
        result = []

        for i in range(self.size()):
            result.append([])

            for j in range(self.size()):
                if i == j: result[i].append(0)
                else: result[i].append(math.inf)

        for edge in self.edges:
            result[edge._from.id][edge._to.id] = edge.weight

        return result
    
    def add_node(self):
        node = Node(id=self.size())
        self.nodes.append(node)
        return node
    
    def add_edge(self, edge):
        edge._from.add_affected_edge(edge)
        edge._to.add_affected_edge(edge)
        self.edges.append(edge)

    def remove_edge(self, edge):
        edge._to.remove_affected_edge(edge)
        edge._from.remove_affected_edge(edge)
        self.edges.remove(edge)

    def reset_ids(self):
        for i, node in enumerate(self.nodes):
            node.id = i
    
    def remove_node(self, node):
        self.nodes.remove(node)
        
        for edge in node.affected_edges:
            if edge in self.edges:
                self.remove_edge(edge)

        self.reset_ids()

    def get_nodes(self):
        return self.nodes

    def get_edges(self):
        return self.edges

    def adj_list(self):
        result = []
        
        for i, line in enumerate(self.get_adj_matrix()):
            entry = []
            
            for j in range(len(line)):
                if i == j: continue
                if line[j] != float("inf"): entry.append((j, line[j]))

            result.append(entry)

        return result
                

    def dijkstras(self, start, end):
        adj_list = self.adj_list()

        visited = [False] * self.size()
        trace = [None] * self.size()
        distances = [0 if node == start else float("inf") for node in range(self.size())]
        
        queue = IndexedPriorityQueue()
        queue.push(start, 0)

        while queue:
            node, _ = queue.pop()
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


class Node:
    def __init__(self, id):
        self.id = id
        self.affected_edges = []

    def add_affected_edge(self, edge):
        self.affected_edges.append(edge)

    def remove_affected_edge(self, edge):
        self.affected_edges.remove(edge)


class Edge:
    def __init__(self, _from, _to, weight):
        self._from = _from
        self._to = _to
        self.weight = weight
