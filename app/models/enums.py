from enum import Enum

class VehicleType(str, Enum):
    CAR = "car"
    MOTORCYCLE = "motorcycle"
    TRUCK = "truck"

class SpotType(str, Enum):
    COMMON = "common"
    ELDERLY = "elderly"
    PCD = "pcd"
    MOTORCYCLE = "motorcycle"
