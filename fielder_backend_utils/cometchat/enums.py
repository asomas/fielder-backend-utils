from enum import Enum, auto


class CometChatErrorCodes(Enum):
    ERR_UID_ALREADY_EXISTS = auto()
    ERR_UID_NOT_FOUND = auto()
    ERR_AUTH_TOKEN_NOT_FOUND = auto()
    ERR_ON_BEHALF_OF_UID_NOT_FOUND = auto()
    ERR_BAD_REQUEST = auto()
