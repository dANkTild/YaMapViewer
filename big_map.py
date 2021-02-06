from io import BytesIO
import os
import pygame
import pygame_gui
import requests
from PIL import Image

KEYS = (pygame.KEYDOWN, pygame.K_PAGEUP, pygame.K_UP, pygame.K_DOWN,
        pygame.K_LEFT, pygame.K_RIGHT, pygame.K_h, pygame.K_m, pygame.K_s)
url_static = 'http://static-maps.yandex.ru/1.x/'
w, h = size = 650, 450
lon_delta = 320
lat_delta = 108
z = 10


class Map:
    def __init__(self, coord, zoom, layer='map', size=(650, 450)):
        self.lon, self.lat = coord
        self.z = zoom
        self.layer = layer
        self.w, self.h = size
        self.update_map()

    def update_map(self):
        params = {
            'l': self.layer,
            'll': f'{self.lon},{self.lat}',
            'z': self.z,
            'size': f'{self.w},{self.h}'
        }
        response = requests.get(url_static, params)
        if not response:
            raise RuntimeError('Ошибка выполнения запроса\n'
                               f'{response.url}')
        filename = 'temp_img.png'
        with open(filename, 'wb') as file:
            file.write(response.content)
        self.map = pygame.image.load(filename)
        os.remove(filename)

    def update(self, event):
        if event.key == pygame.K_PAGEDOWN:
            self.z = max(0, self.z - 1)
        elif event.key == pygame.K_PAGEUP:
            self.z = min(20, self.z + 1)
        elif event.key == pygame.K_LEFT:
            self.lon = (self.lon + 180 - lon_delta * (2 ** -self.z)) % 360 - 180
        elif event.key == pygame.K_RIGHT:
            self.lon = (self.lon + 180 + lon_delta * (2 ** -self.z)) % 360 - 180
        elif event.key == pygame.K_UP:
            self.lat = min(self.lat + lat_delta * (2 ** -self.z), 85)
        elif event.key == pygame.K_DOWN:
            self.lat = max(self.lat - lat_delta * (2 ** -self.z), -85)
        elif event.key == pygame.K_m:
            self.layer = 'map'
        elif event.key == pygame.K_s:
            self.layer = 'sat'
        elif event.key == pygame.K_h:
            self.layer = 'sat,skl'
        if event.key in KEYS:
            self.update_map()


pygame.init()
screen = pygame.display.set_mode(size)
coord = (60.153218, 55.156414)
mapapp = Map(coord, z)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            mapapp.update(event)

    screen.blit(mapapp.map, (0, 0))
    pygame.display.flip()
pygame.quit()
