from enum import Enum
class FilmStatus(str, Enum):
    NOT_YET_AIRED = "not_yet_aired"
    AIRING = "airing"
    FINISHED_AIRING = "finished_airing"
    
class Role(str, Enum):
    USER = "user"
    ADMIN = "admin"
    
class UserFilmStatus(str, Enum):
    PLAN_TO_WATCH = "plan_to_watch"
    WATCHING = "watching"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"
    DROPPED = "dropped"
    
class ReactionType(str, Enum):
    LIKE = "like"
    DISLIKE = "dislike"