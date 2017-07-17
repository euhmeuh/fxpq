"""
Fxpq client
"""

import cocos
from cocos import actions

from core.application import Application
from client.services import LoggingService, NetworkingService, DimensionService, DisplayService

from core.package_manager import PackageManager
from core.serializer import Serializer


class HelloWorld(cocos.layer.Layer):
    def __init__(self):
        super().__init__()

        label = cocos.text.Label(
            'Hello world!',
            font_name='DejaVu Sans',
            font_size=32,
            anchor_x='center', anchor_y='center'
        )
        label.position = 256, 192
        label.do(actions.Repeat(actions.RotateBy(360, duration=3)))
        scale = actions.ScaleBy(3, duration=0.3)
        label.do(actions.Repeat(scale + actions.Reverse(scale)))
        self.add(label)


class KeyboardLayer(cocos.layer.Layer):
    is_event_handler = True

    def __init__(self):
        super().__init__()

        self.keys = set()

    def on_key_press(self, key, modifiers):
        self.keys.add(key)
        print(self.keys)

    def on_key_release(self, key, modifiers):
        if key in self.keys:
            self.keys.remove(key)
        print(self.keys)


class CocosClient:
    def __init__(self):
        self.current_scene = None

        self.package_manager = PackageManager("./packages")

    def run(self):
        cocos.director.director.init(width=512, height=384)

        with open("./data/Manafia/manafia.dim") as file:
            dimension = Serializer.instance().deserialize(file.read())

        self.current_scene = self._display(dimension)
        cocos.director.director.run(self.current_scene)

    def on_dimension_received(self, dimension):
        pass

    def _display(self, obj):
        main_layer = KeyboardLayer()
        main_layer.add(cocos.text.Label(obj.class_name))
        for child in obj.iter_children():
            label = cocos.text.Label(child.class_name)
            label.position = 50, 50
            main_layer.add(label)

        return cocos.scene.Scene(main_layer)


class Client(Application):
    """Master server that lists registered servers"""

    def __init__(self):
        super().__init__()

        self.services = [
            LoggingService(),
            NetworkingService("localhost", 8448),
            DisplayService()
        ]
