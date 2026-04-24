from utils.constants import (
    GUID_START_BLOCK_LEN, GUID_REMAINING_LEN, GUID_DASH_POSITIONS,
    GUID_POSSIBLE_CHARS, GUID_SUCCESS_OFFSET, GUID_REPLACEMENT,
    AUTH0_ID_MAX_LEN, AUTH0_ID_POSSIBLE_CHARS, AUTH0_ID_REPLACEMENT,
    AUTH0_HEAD, AUTH0_VERTICAL_BAR_CODE,
)


def clean_message(message: str) -> str:
  # Implement any message cleaning logic here, e.g. removing variable parts of the message
  # For simplicity, we'll just return the original message for now
  idx = 0
  while idx < len(message):
    # Clean GUID
    c = message[idx]
    try:
      if c == "-":
        possible_guid = message[idx-GUID_START_BLOCK_LEN:idx+GUID_REMAINING_LEN]
        print(possible_guid)
        if all(ch in GUID_POSSIBLE_CHARS for ch in possible_guid.lower()) and all(possible_guid[pos] == "-" for pos in GUID_DASH_POSITIONS):
          message = message.replace(possible_guid, GUID_REPLACEMENT)
          idx = idx - GUID_SUCCESS_OFFSET
    except IndexError:
      pass
    
    try:
      start = 0
      if message[idx:idx+len(AUTH0_HEAD)] == AUTH0_HEAD:
        if message[idx+len(AUTH0_HEAD)] == "|":
          start = idx + len(AUTH0_HEAD) + 1
        elif message[idx+len(AUTH0_HEAD):idx+len(AUTH0_HEAD)+len(AUTH0_VERTICAL_BAR_CODE)] == AUTH0_VERTICAL_BAR_CODE:
          start = idx + len(AUTH0_HEAD) + len(AUTH0_VERTICAL_BAR_CODE)

      if start != 0:
        possible_id = message[start:start+AUTH0_ID_MAX_LEN]
        print(possible_id)
        if all(ch in AUTH0_ID_POSSIBLE_CHARS for ch in possible_id.lower()):
          message = message.replace(AUTH0_HEAD + ("|" if start == idx + len(AUTH0_HEAD) + 1 else AUTH0_VERTICAL_BAR_CODE) + possible_id, AUTH0_ID_REPLACEMENT)
          idx = idx + len(AUTH0_ID_REPLACEMENT) - 1

    except IndexError:
      pass

    idx += 1

  return message
