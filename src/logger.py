import logging
logger = logging.getLogger('discord')

def setup() :
  logger.setLevel(logging.DEBUG)
  handler = logging.FileHandler(filename='history.log', encoding='utf-8', mode='w')
  handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: | %(message)s'))
  logger.addHandler(handler)