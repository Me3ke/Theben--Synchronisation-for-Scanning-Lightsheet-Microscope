"""
    Event class. Creates a callable object that directs
    an event to all handlers in its list. These handlers
    are object methods that will be executed.
"""


class Event(object):

    def __init__(self):
        self.event_handlers = []

    def __iadd__(self, handler):
        self.event_handlers.append(handler)
        return self

    def __isub__(self, handler):
        self.event_handlers.remove(handler)
        return self

    def __call__(self, *args, **kwargs):
        for event_handler in self.event_handlers:
            event_handler(*args, **kwargs)
