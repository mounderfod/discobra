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
    """Events relating to the creation, removal and modification of guilds (servers)."""
    GUILD_MEMBERS = 2
    """
    Events relating to the joining, leaving and modification of a guild's members.
    Events from this intent relating to the client are sent regardless of whether the intent is enabled.
    This is a privileged intent that must be enabled in the Discord developer portal.
    """
    GUILD_BANS = 4
    """Events relating to the creation and removal of a guild's bans."""
    GUILD_EMOJIS_AND_STICKERS = 8
    """Events relating to the modification of a guild's emojis and stickers."""
    GUILD_INTEGRATIONS = 16
    """Events relating to the creation, removal and modification of a guild's integrations."""
    GUILD_WEBHOOKS = 32
    """Events relating to the modification of a guild's webhooks."""
    GUILD_INVITES = 64
    """Events relating to the creation and removal of a guild's invites."""
    GUILD_VOICE_STATES = 128
    """Events relating to the modification of a guild's voice states."""
    GUILD_PRESENCES = 256
    """
    Events relating to the modification of a guild's members' presences.
    This is a privileged intent that must be enabled in the Discord developer portal.
    """
    GUILD_MESSAGES = 512
    """Events relating to the sending, editing and deleting of messages in a guild's channels."""
    GUILD_MESSAGE_REACTIONS = 1024
    """Events relating to the addition and removal of reactions to messages in a guild's channels."""
    GUILD_MESSAGE_TYPING = 2048
    """Events relating to when members start typing in a guild's channels."""
    DIRECT_MESSAGES = 4096
    """Events relating to the sending, editing and deleting of messages in a DM channel."""
    DIRECT_MESSAGE_REACTIONS = 8192
    """Events relating to the addition and removal of reactions to messages in a DM channel."""
    DIRECT_MESSAGE_TYPING = 16384
    """Events relating to when users start typing in a DM channel."""
    MESSAGE_CONTENT = 32768
    """
    The data relating to the content of messages from message events.
    As of August 2022, this will be a privileged intent that must be enabled in the Discord developer portal.
    """
    GUILD_SCHEDULED_EVENTS = 65536
    """Events relating to the scheduling, modification and cancelling of a guild's events."""
    AUTO_MODERATION_CONFIGURATION = 1048576
    """Events relating to Automod rules."""
    AUTO_MODERATION_EXECUTION = 2097152
    """Events relating to Automod actions."""


def get_number(intents: list[Intents]):
    """
    Generates the number used to tell the gateway which intents are active.

    **Parameters:**
    - intents: A list of active intents

    **Returns:**
    - int: The number used as an argument for the gateway connection.
    """
    number = 1
    for i in intents:
        number += i.value
    return number


def get_intents(number: int):
    """
    Generates a list of intents from the number used to tell the gateway which are active.

    **Parameters:**
    - number: The number which represents the intents.

    **Returns:**
    - list[`discord.intents.Intents`]: The list of intents which the number represents.
    """
    intents = []
    while number != 0:
        for i in Intents:
            if number >= i.value:
                intents.append(i)
                number -= i.value
    return intents
