# Different implemented emotions of furhat
def SAD():
    return {
        "frames": [
            {
                "time": [
                    0.5
                ],
                "persist": True,
                "params": {
                    'EXPR_SAD': 1,
                }
            },
        ],
        "class": "furhatos.gestures.Gesture"
    }

def HAPPY():
    return {
        "frames": [
            {
                "time": [
                    0.5
                ],
                "persist": False,
                "params": {
                    'SMILE_CLOSED': 1,
                }
            },
        ],
        "class": "furhatos.gestures.Gesture"
    }

def reset_emotions():
    return {
        "frames": [
            {
                "time": [
                    0.1
                ],
                "persist": True,
                "params": {
                    'EXPR_SAD': 0,
                    'SMILE_CLOSED': 0,
                    'SMILE_OPEN': 0
                }
            }
        ],
        "class": "furhatos.gestures.Gesture"
    }

def SURPRISE(speed):
    return {
        "frames": [
            {
                "time": [
                    0.33 / speed
                ],
                "params": {
                    "BROW_UP_LEFT": 1,
                    'BROW_UP_RIGHT': 1,
                }
            },
            {
                "time": [
                    3 / speed
                ],
                "persist": True,
                "params": {
                    'SMILE_OPEN': 0,
                    "BROW_UP_LEFT": 0,
                    'BROW_UP_RIGHT': 0,
                }
            },
        ],
        "class": "furhatos.gestures.Gesture"
    }