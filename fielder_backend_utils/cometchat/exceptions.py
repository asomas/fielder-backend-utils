class CometChatException(Exception):
    pass


class CometChatUIDAlreadyExistsException(CometChatException):
    pass


class CometChatUIDNotFoundException(CometChatException):
    pass


class CometChatAuthTokenNotFoundException(CometChatException):
    pass


class CometChatOnBehalfOfUIDNotFoundException(CometChatException):
    pass


class CometChatBadRequestException(CometChatException):
    pass
