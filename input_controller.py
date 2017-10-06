import abc


class InputController:

    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self.pause = False  # type: bool
        self.quit = False  # type: bool

    @abc.abstractmethod
    def handle_input(self):
        return
