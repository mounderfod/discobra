from enum import Enum, unique


@unique
class PremiumType(Enum):
    NONE = 0,
    NITRO_CLASSIC = 1,
    NITRO = 2