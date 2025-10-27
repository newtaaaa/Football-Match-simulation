import math
import matplotlib.pyplot as plt

def distance(point1, point2):
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)


def plus_proche(points, point_choisi):
    closest_point = None
    min_distance = float('inf')

    for point in points:
        d = distance(point, point_choisi)
        if d < min_distance:
            min_distance = d
            closest_point = point

    return closest_point

# Affichage du nuage de points
'''
x, y = zip(*points)
plt.scatter(x, y, label='Points', color='blue')
plt.scatter(*given_point, label='Point choisi', color='red')
plt.scatter(*closest_point, label='Point le plus proche', color='green')
plt.legend()
plt.xlabel('X-axis')
plt.ylabel('Y-axis')
plt.title('Nuage de points avec le point le plus proche')
plt.show()'''
