class GameNotFoundError(Exception):
    pass


class GameAlreadyStartedError(Exception):
    pass


class PlayerNotInGameError(Exception):
    pass


class PlayerAlreadyJoinedError(Exception):
    pass


class GameFullError(Exception):
    pass
