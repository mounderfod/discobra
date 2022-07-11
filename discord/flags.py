from enum import Enum, unique


@unique
class Flags(Enum):
    STAFF = 1
    PARTNER = 2
    HYPESQUAD = 4
    BUG_HUNTER_LEVEL_1 = 8
    HYPESQUAD_ONLINE_HOUSE_1 = 64
    HYPESQUAD_ONLINE_HOUSE_2 = 128
    HYPESQUAD_ONLINE_HOUSE_3 = 256
    TEAM_PSUEDO_USER = 1024
    BUG_HUNTER_LEVEL_2 = 16384
    VERIFIED_BOT = 65536
    VERIFIED_DEVELOPER = 131072
    CERTIFIED_MODERATOR = 262144
    BOT_HTTP_INTERACTIONS = 524288


def get_number(flags: list[Flags]):
    number = 1
    for i in flags:
        number += i.value
    return number


def get_flags(number: int):
    flags = []
    while number != 0:
        for i in Flags:
            if number >= i.value:
                flags.append(i)
                number -= i.value
    return flags
