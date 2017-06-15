"""
Event system that allows losely coupled communication between objects and services
"""


class EventEmitter:
    def __init__(self, *args, **kwargs):
        # to be used as a mixin, the constructor
        # allows any arguments, and pass them up to the super() chain
        super().__init__(*args, **kwargs)

        self.bindings = {}

    def on(self, event_name, method):
        bindings = self.bindings.get(event_name, [])
        bindings.append(method)
        self.bindings[event_name] = bindings

    def emit(self, event_name, *args):
        for method in self.bindings.get(event_name, []):
            method(self, *args)
