class CometChatException(Exception):
    pass


class CometChatUIDAlreadyExistsException(CometChatException):
    pass


class CometChatUIDNotFoundException(CometChatException):
    pass


class CometChatAuthTokenNotFoundException(CometChatException):
    pass
