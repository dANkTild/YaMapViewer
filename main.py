import pygame
import requests
from io import BytesIO

url_static = 'https://static-maps.yandex.ru/1.x/'
KEYS = (pygame.K_PAGEDOWN, pygame.K_PAGEUP, pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT)
# lon_d = 0.001
lon_d = 320
lat_d = 100


class Map:
    def __init__(self, coord, zoom, layer='map', size=(650, 450)):
        self.lon, self.lat = coord
        self.z = zoom
        self.layer = layer
        self.map = None
        self.size = size
        self.update_map()

    def update_map(self):
        params = {'l': self.layer,
                  'll': f'{self.lon},{self.lat}',
                  'z': self.z,
                  'size': '{},{}'.format(*self.size)}

        response = requests.get(url_static, params)
        if not response:
            raise RuntimeError('Ошибка запроса:\n' + response.url)
        self.map = pygame.image.load(BytesIO(response.content))

    def update(self, event):
        if event.key == pygame.K_PAGEDOWN:
            self.z = max(0, self.z - 1)
        elif event.key == pygame.K_PAGEUP:
            self.z = min(20, self.z + 1)

        elif event.key == pygame.K_LEFT:
            self.lon = ((self.lon + 180 - lon_d * 2 ** -(self.z)) % 360 - 180)
        elif event.key == pygame.K_RIGHT:
            self.lon = ((self.lon + 180 + lon_d * 2 ** -(self.z)) % 360 - 180)

        elif event.key == pygame.K_UP:
            self.lat = min(self.lat + lat_d * 2 ** -(self.z), 85)
        elif event.key == pygame.K_DOWN:
            self.lat = max(self.lat - lat_d * 2 ** -(self.z), -85)

        if event.key in KEYS:
            self.update_map()


# if __name__ == '__main__':
pygame.init()
w, h = size = (650, 450)
screen = pygame.display.set_mode(size)

coord = (60.153218, 55.156414)
z = 0
mapapp = Map(coord, z)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            mapapp.update(event)
    screen.blit(mapapp.map, (0, 0))
    pygame.display.flip()

pygame.quit()
