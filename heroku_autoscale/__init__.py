RESPONSE_BUCKET_CHOICES = [
    ("low", "Too low"),
    ("right", "Just right"),
    ("high", "Too high"),
]

SCALE_ACTION_CHOICES = [
    ("up", "Up"),
    ("down", "Down"),
]


class MissingParameter(Exception):
    pass
