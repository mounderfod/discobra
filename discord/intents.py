"""
    Contains constants and functions for managing the various gateway intents.

    If you do not specify an intent, the gateway will not send events related to it. Events that are not part of an
    intent are always sent. Message content, guild presences and guild members are privileged intents - you must
    enable them in the Discord developer portal.
"""
from enum import Enum, unique


@unique
class Intents(Enum):
    """
    Constants for the gateway intents, with their numerical values.

    See more at: https://discord.com/developers/docs/topics/gateway#gateway-intents
    """
    GUILDS = 1
    GUILD_MEMBERS = 2
    GUILD_BANS = 4
    GUILD_EMOJIS_AND_STICKERS = 8
    GUILD_INTEGRATIONS = 16
    GUILD_WEBHOOKS = 32
    GUILD_INVITES = 64
    GUILD_VOICE_STATES = 128
    GUILD_PRESENCES = 256
    GUILD_MESSAGES = 512
    GUILD_MESSAGE_REACTIONS = 1024
    GUILD_MESSAGE_TYPING = 2048
    DIRECT_MESSAGES = 4096
    DIRECT_MESSAGE_REACTIONS = 8192
    DIRECT_MESSAGE_TYPING = 16384
    MESSAGE_CONTENT = 32768
    GUILD_SCHEDULED_EVENTS = 65536
    AUTO_MODERATION_CONFIGURATION = 1048576
    AUTO_MODERATION_EXECUTION = 2097152


def get_number(intents: list[Intents]):
    """
    Generates the number used to tell the gateway which intents are active.

    **Parameters:**
    - intents (list[Intents]): A list of active intents

    **Returns:**
    - int: The number used as an argument for the gateway connection.
    """
    number = 1
    for i in intents:
        number += i.value
    return number


def get_intents(number: int):
    intents = []
    while number != 0:
        for i in Intents:
            if number >= i.value:
                intents.append(i)
                number -= i.value
    return intents
