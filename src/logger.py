import logging
logger = logging.getLogger('discord')

def setup() :
  """Creates handler to log discord events"""
  logger.setLevel(logging.INFO)
  handler = logging.FileHandler(filename='history.log', encoding='utf-8', mode='w')
  handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: | %(message)s'))
  logger.addHandler(handler)

def logInfo(message: str):
  """Logs Message into log at Info level"""
  logger.info(message)

def logWarn(message: str):
  """Logs Message into log at Warn level"""
  logger.warn(message)

def logErr(message: str):
  """Logs Message into log at Error level"""
  logger.error(message)