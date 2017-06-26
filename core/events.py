"""
Event system that allows losely coupled communication between objects and services
"""


class EventEmitter:
    def __init__(self, *args, **kwargs):
        # to be used as a mixin, the constructor
        # allows any arguments, and pass them up to the super() chain
        super().__init__(*args, **kwargs)

        self.bindings = {}
        self.any_bindings = set()

    def on(self, event_name, method):
        """Subscribe to an event"""
        bindings = self.bindings.get(event_name, [])
        bindings.append(method)
        self.bindings[event_name] = bindings

    def on_any(self, method):
        """Subscribe to any event"""
        self.any_bindings.add(method)

    def emit(self, event_name, *args):
        """Emit an event to corresponding subscribers"""
        for method in self.bindings.get(event_name, []):
            method(self, *args)

        for method in self.any_bindings:
            method(self, event_name, *args)
