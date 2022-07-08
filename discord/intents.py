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
    GUILDS = 0
    GUILD_MEMBERS = 1
    GUILD_BANS = 2
    GUILD_EMOJIS_AND_STICKERS = 3
    GUILD_INTEGRATIONS = 4
    GUILD_WEBHOOKS = 5
    GUILD_INVITES = 6
    GUILD_VOICE_STATES = 7
    GUILD_PRESENCES = 8
    GUILD_MESSAGES = 9
    GUILD_MESSAGE_REACTIONS = 10
    GUILD_MESSAGE_TYPING = 11
    DIRECT_MESSAGES = 12
    DIRECT_MESSAGE_REACTIONS = 13
    DIRECT_MESSAGE_TYPING = 14
    MESSAGE_CONTENT = 15
    GUILD_SCHEDULED_EVENTS = 16
    AUTO_MODERATION_CONFIGURATION = 20
    AUTO_MODERATION_EXECUTION = 21


def gen_number(intents: list[Intents]):
    """
    Generates the number used to tell the gateway which intents are active.

    **Parameters:**
    - intents (list[Intents]): A list of active intents

    **Returns:**
    - int: The number used as an argument for the gateway connection.
    """
    number = 1
    for i in intents:
        number << i.value
    return number
