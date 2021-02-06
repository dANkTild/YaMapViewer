import pygame
import requests
from io import BytesIO

url_static = 'https://static-maps.yandex.ru/1.x/'


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
            raise RuntimeError('Ошибка запроса')
        self.map = pygame.image.load(BytesIO(response.content))


# if __name__ == '__main__':
pygame.init()
w, h = size = (650, 450)
screen = pygame.display.set_mode(size)

coord = '60.153218,55.156414'.split(',')
z = 17
mapapp = Map(coord, z)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.blit(mapapp.map, (0, 0))
    pygame.display.flip()

pygame.quit()
