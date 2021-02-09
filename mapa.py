import pygame
import pygame_gui
import requests
import io

size = WIDTH, HEIGHT = 650, 450

KEYS = (pygame.K_PAGEDOWN, pygame.K_PAGEUP, pygame.K_DOWN,
        pygame.K_UP, pygame.K_LEFT, pygame.K_RIGHT,
        pygame.K_m, pygame.K_s, pygame.K_h,
        pygame.K_RETURN)
lon_delta = 300
lat_delta = 100

url_static = "http://static-maps.yandex.ru/1.x/"
geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
geocoder_api_key = "40d1649f-0493-4b70-98ba-98533de7710b"


def get_geoobject(address):
    geocoder_params = {
        "apikey": geocoder_api_key,
        "geocode": address,
        "format": "json"}

    response = requests.get(geocoder_api_server, params=geocoder_params)

    if not response:
        return

    json_response = response.json()
    # Получаем первый топоним из ответа геокодера.
    features = json_response["response"]["GeoObjectCollection"]["featureMember"]
    toponym = features[0]["GeoObject"] if features else None
    return toponym


def get_coord(address):
    toponym = get_geoobject(address)
    toponym_coodrinates = toponym["Point"]["pos"]
    toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")
    return tuple(map(float, (toponym_longitude, toponym_lattitude)))


class Map:
    def __init__(self, coord, zoom, layer="map", size=size):
        self.lon, self.lat = coord
        self.z = zoom
        self.layer = layer
        self.size = size
        self.point = None
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

        if not place.is_focused:
            if event.key == pygame.K_m:
                self.layer = "map"
            if event.key == pygame.K_s:
                self.layer = "sat"
            if event.key == pygame.K_h:
                self.layer = "sat,skl"

        if event.key == pygame.K_RETURN:
            self.search()

        if event.key in KEYS:
            self.update_map()

    def search(self):
        self.point = self.lon, self.lat = get_coord(place.get_text())

    def update_map(self):
        params = {"l": self.layer,
                  "ll": f"{self.lon},{self.lat}",
                  "z": self.z,
                  "size": "{},{}".format(*self.size)}
        if self.point:
            params["pt"] = f"{self.point[0]},{self.point[1]},pm2rdm"

        response = requests.get(url_static, params)
        if not response:
            raise RuntimeError("Ошибка выполнения запроса")
        filename = "temp.img"
        with open(filename, "wb") as file:
            file.write(response.content)
        self.map = pygame.image.load(filename)


pygame.init()
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()

manager = pygame_gui.UIManager(size)

place = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((0, 0), (200, 20)),
                                            manager=manager)

coords = map(float, "55.156384, 60.151121".split(", ")[::-1])
z = 15

mapapp = Map(coords, z)

clock = pygame.time.Clock()
running = True
while running:
    time_delta = clock.tick() / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            mapapp.update(event)


        manager.process_events(event)

    manager.update(time_delta)

    screen.blit(mapapp.map, (0, 0))
    manager.draw_ui(screen)

    pygame.display.flip()