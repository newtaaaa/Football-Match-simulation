import math
import heapq

class Graph:
    def __init__(self):
        self.graph = {}

    def set_graphe(self, liste):
        for joueur in liste:
            if joueur not in self.graph:
                self.graph[joueur] = []

    def add_edge(self, u, v, weight):
        if (v, weight) not in self.graph[u]:
            self.graph[u].append((v, weight))
        if (u, weight) not in self.graph[v]:
            self.graph[v].append((u, weight))

    def a_star(self, start, goal):
        open_set = []
        heapq.heappush(open_set, (0, start))  # Ajouter le point de départ avec une priorité de 0
        came_from = {}
        g_score = {vertex: float('infinity') for vertex in self.graph}
        g_score[start] = 0
        f_score = {vertex: float('infinity') for vertex in self.graph}
        f_score[start] = self.heuristic(start, goal)

        while open_set:
            current = heapq.heappop(open_set)[1]

            if current == goal:
                path = self.reconstruct_path(came_from, start, goal)
                return path

            for neighbor, weight in self.graph[current]:
                tentative_g_score = g_score[current] + weight

                if tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self.heuristic(neighbor, goal)

                    # Remplacez l'ajout dans open_set par le module heapq
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

        return None

    def heuristic(self, playa1, playa2):
        # Heuristique basée sur la distance euclidienne
        x1, y1 = playa1.coord
        x2, y2 = playa2.coord
        return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

    def reconstruct_path(self, came_from, start, goal):
        current = goal
        path = [current]

        while current != start:
            current = came_from[current]
            path.insert(0, current)

        return path


def distance(point1, point2):
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)
