from src.commands import start_bot
from src.logger import setup
from website import init_website

setup()
init_website()
start_bot()