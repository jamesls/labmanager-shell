import logging


# python 2.7 has a NullHandler implementation,
# but to be compatible with python 2.6, we
# have to bundle our own.
class NullHandler(logging.Handler):
    def handle(self, record):
        pass

    def emit(self, record):
        pass

    def createLock(self):
        self.lock = None
