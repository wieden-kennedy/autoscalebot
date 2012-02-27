RESPONSE_BUCKET_CHOICES = [
    ("low", "Too low"),
    ("right", "Just right"),
    ("high", "Too high"),
]

SCALE_ACTION_CHOICES = [
    ("up", "Up"),
    ("down", "Down"),
]

TOO_LOW = "low"
JUST_RIGHT = "right"
TOO_HIGH = "high"

class MissingParameter(Exception):
    pass
