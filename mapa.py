import pygame
import requests
import io

size = WIDTH, HEIGHT = 650, 450

url_static = "http://static-maps.yandex.ru/1.x/"


class Map:
    def __init__(self, coord, zoom, layer="map", size=size):
        self.lon, self.lat= coord
        self.z = zoom
        self.layer = layer
        self.size = size
        self.update_map()

    def update_map(self):
        params = {"l": self.layer,
                  "ll": f"{self.lon},{self.lat}",
                  "z": self.z,
                  "size": "{},{}".format(*self.size)}

        response = requests.get(url_static, params)
        if not response:
            raise RuntimeError("Ошибка выполнения запроса")
        self.map = pygame.image.load(io.BytesIO(response.content))


pygame.init()
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()

coords = "55.156384, 60.151121".split(", ")[::-1]
z = 17

mapapp = Map(coords, z)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.blit(mapapp.map, (0, 0))
    pygame.display.flip()