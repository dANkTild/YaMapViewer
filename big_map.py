import os
import pygame_gui
import pygame
import requests

KEYS = (pygame.K_PAGEDOWN, pygame.K_PAGEUP, pygame.K_UP, pygame.K_DOWN,
        pygame.K_LEFT, pygame.K_RIGHT, pygame.K_h, pygame.K_m, pygame.K_s)
url_static = 'http://static-maps.yandex.ru/1.x/'
apikey_geocoder = "40d1649f-0493-4b70-98ba-98533de7710b"
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
        self.ll = None
        self.update_map()

    def update_map(self):
        if self.ll:
            params = {
                'l': self.layer,
                'll': f'{self.lon},{self.lat}',
                'z': self.z,
                'size': f'{self.w},{self.h}',
                "pt": f'{self.ll}'
            }
        else:
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
        if event.type == pygame.USEREVENT:
            self.update_map()
            return
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


def get_geoobject(address):
    geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

    geocoder_params = {
        "apikey": apikey_geocoder,
        "geocode": address,
        "format": "json"}

    response = requests.get(geocoder_api_server, params=geocoder_params)

    if not response:
        return

    json_response = response.json()
    features = json_response["response"]["GeoObjectCollection"][
        "featureMember"]
    toponym = features[0]["GeoObject"] if features else None
    return toponym


def get_coord(address):
    toponym = get_geoobject(address)
    if not toponym:
        return
    toponym_coodrinates = toponym["Point"]["pos"]
    toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")
    return toponym_longitude, toponym_lattitude


pygame.init()
screen = pygame.display.set_mode(size)
intput_box = pygame_gui
manager = pygame_gui.UIManager((w, h))
text_input = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((0,
                                                                            0), (100, 40)), manager=manager)
reset_address_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((100, 0), (200, 40)),
                                                    text='Сбросить результат поиска',
                                                    manager=manager)
coord = (60.153218, 55.156414)
mapapp = Map(coord, z)
running = True
clock = pygame.time.Clock()

while running:
    time_delta = clock.tick(60) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        elif event.type == pygame.KEYDOWN:
            mapapp.update(event)
        elif event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
                if event.ui_element == text_input:
                    toponym_to_find = text_input.get_text()
                    coord = get_coord(toponym_to_find)
                    mapapp.lon = float(coord[0])
                    mapapp.lat = float(coord[1])
                    mapapp.ll = '{},{}'.format(mapapp.lon, mapapp.lat)
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == reset_address_button:
                    mapapp.ll = None
            mapapp.update(event)
        manager.process_events(event)
    manager.update(time_delta)

    screen.blit(mapapp.map, (0, 0))
    manager.draw_ui(screen)
    pygame.display.flip()
pygame.quit()
