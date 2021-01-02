from src.bot import start_bot
from src.logger import setup
from website.server import init_website

setup()
init_website()
start_bot()