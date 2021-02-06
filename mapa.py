import pygame
import pygame_gui
import requests
import io

size = WIDTH, HEIGHT = 650, 450

KEYS = (pygame.K_PAGEDOWN, pygame.K_PAGEUP, pygame.K_DOWN,
        pygame.K_UP, pygame.K_LEFT, pygame.K_RIGHT)
lon_delta = 300
lat_delta = 100

url_static = "http://static-maps.yandex.ru/1.x/"


class Map:
    def __init__(self, coord, zoom, layer="map", size=size):
        self.lon, self.lat = coord
        self.z = zoom
        self.layer = layer
        self.size = size
        self.update_map()

    def update(self, event):
        if event.key == pygame.K_PAGEDOWN:
            self.z = max(0, self.z - 1)
        if event.key == pygame.K_PAGEUP:
            self.z = min(17, self.z + 1)
        if event.key == pygame.K_LEFT:
            self.lon = (self.lon + 180 - lon_delta * 2 ** -self.z) % 360 - 180
        if event.key == pygame.K_RIGHT:
            self.lon = ((self.lon + 180 + lon_delta * 2 ** -self.z) % 360 - 180)
        if event.key == pygame.K_UP:
            self.lat = min(self.lat + lat_delta * 2 ** -self.z, 85)
        if event.key == pygame.K_DOWN:
            self.lat = max(self.lat - lat_delta * 2 ** -self.z, -85)

        if event.key in KEYS:
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

coords = map(float, "55.156384, 60.151121".split(", ")[::-1])
z = 0

mapapp = Map(coords, z)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            mapapp.update(event)

    screen.blit(mapapp.map, (0, 0))
    pygame.display.flip()