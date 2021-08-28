from enum import Enum

class Browser(Enum):
    NONE = 0
    CHROME = 1
    FIREFOX = 2
    OPERA = 3
    EDGE = 4
    CHROMIUM = 5

class Action(Enum):
    NEW_DRAFT = 0
    NEWDRAFT = 0

    UPDATE_DRAFT = 1
    UPDATEDRAFT = 1
    # ! TODO: haven't built any of the other functionality
    NEW_CHAPTER = 2
    NEWCHAPTER = 2

    UPDATE_CHAPTER = 3
    UPDATECHAPTER = 3