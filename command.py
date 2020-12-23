from api_service import get_erbs_root

def command(message):
  if message.startswith("%status"):
    return "Aya is in the chat!"

  if message.startswith("%isERBSup"):
    return get_erbs_root()
  
  return ""