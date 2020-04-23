import botsley.app
from botsley.logging import create_logger

def create_app():
    botsley.app.logger = logger = create_logger()