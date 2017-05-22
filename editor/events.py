class EventEmitter:
    def __init__(self):
        self.bindings = {}

    def on(self, event_name, method):
        bindings = self.bindings.get(event_name, [])
        bindings.append(method)
        self.bindings[event_name] = bindings

    def emit(self, event_name, *args):
        for method in self.bindings.get(event_name, []):
            method(self, *args)
