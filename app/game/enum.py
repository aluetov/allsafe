from enum import Enum


class GameStatus(str, Enum):
    WAITING = "waiting"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"
    CANCELLED = "cancelled"


class GameAccess(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"


class PlayerStatus(str, Enum):
    ACTIVE = "active"
    ELIMINATED = "eliminated"
    LEFT = "left"


class RoundStatus(str, Enum):
    DISCUSSION = "discussion"
    VOTING = "voting"
    TIEBREAK_VOTING = "tiebreak_voting"
    RESULT = "result"
    FINISHED = "finished"


class MessageType(str, Enum):
    USER = "user"
    SYSTEM = "system"
