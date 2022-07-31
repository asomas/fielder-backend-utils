from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class CometChatUser:
    uid: str
    name: str
    link: Optional[str] = None
    avatar: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    rawMetadata: Optional[str] = None
    status: Optional[str] = None
    role: Optional[str] = None
    createdAt: Optional[int] = None
    updatedAt: Optional[int] = None
    lastActiveAt: Optional[int] = None
    tags: Optional[list[str]] = None
    authToken: Optional[str] = None


@dataclass
class CometChatAuthToken:
    uid: str
    authToken: str
    createdAt: int
