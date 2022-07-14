from __future__ import annotations
from enum import IntEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from discord.guild import Guild

class ChannelType(IntEnum):
    GUILD_TEXT = 0
    DM = 1
    GUILD_VOICE = 2
    GROUP_DM = 3
    GUILD_CATEGORY = 4
    GUILD_NEWS = 5
    GUILD_NEWS_THREAD = 10
    GUILD_PUBLIC_THREAD = 11
    GUILD_PRIVATE_THREAD = 12
    GUILD_STAGE_VOICE = 13
    GUILD_DIRECTORY = 14

class GuildChannel:
    _id: str
    _guild: Guild
    _name: str
    _type: ChannelType
    _position: int
    _nsfw: bool
    _permission_overwrites: list
    _parent_id: str | None
    _flags: int

    def __init__(self, data: dict, guild: Guild):
        self._guild = guild
        for key, value in data.items():
            setattr(self, f"_{key}", value)

    def __repr__(self) -> str:
        return f"<GuildChannel id={self._id} name={self._name}>"

    @property
    def id(self) -> str:
        return self._id
    
    @property
    def guild(self) -> Guild:
        return self._guild
    
    @property
    def name(self) -> str:
        return self._name

    @property
    def type(self) -> ChannelType:
        return self._type.name

    @property
    def position(self) -> int:
        return self._position

    @property
    def nsfw(self) -> bool:
        return self._nsfw

    @property
    def permission_overwrites(self) -> list:
        return self._permission_overwrites

    @property
    def parent_id(self) -> str:
        return self._parent_id

    @property
    def flags(self) -> int:
        return self._flags

class CategoryChannel(GuildChannel):
    
    def __init__(self, data: dict, guild: Guild):
        super().__init__(data, guild)

    def __repr__(self) -> str:
        return f"<CategoryChannel id={self._id} name={self._name}>"
    

class TextChannel(GuildChannel):
    _rate_limit_per_user: int
    _topic: str
    _last_message_id: str
    _default_auto_archive_duration: int

    @property
    def rate_limit_per_user(self) -> int:
        return self._rate_limit_per_user

    @property
    def topic(self) -> str:
        return self._topic

    @property
    def last_message_id(self) -> str:
        return self._last_message_id

    @property
    def default_auto_archive_duration(self) -> int:
        return self._default_auto_archive_duration

    def __init__(self, data: dict, guild: Guild):
        super().__init__(data, guild)
        for key, value in data.items():
            setattr(self, f"_{key}", value)

    def __repr__(self) -> str:
        return f"<TextChannel id={self._id} name={self._name}>"

class VoiceChannel(GuildChannel):
    _bitrate: int
    _user_limit: int
    _rtc_region: str
    
    @property
    def bitrate(self) -> int:
        return self._bitrate

    @property
    def user_limit(self) -> int:
        return self._user_limit

    @property
    def rtc_region(self) -> str:
        return self._rtc_region

    def __init__(self, data: dict, guild: Guild):
        super().__init__(data, guild)
        for key, value in data.items():
            setattr(self, f"_{key}", value)

    def __repr__(self) -> str:
        return f"<VoiceChannel id={self._id} name={self._name}>"


class StageChannel(GuildChannel):
    pass

class AnnouncementChannel(GuildChannel):
    _topic: str
    _last_message_id: str
    _default_auto_archive_duration: int

    @property
    def topic(self) -> str:
        return self._topic

    @property
    def last_message_id(self) -> str:
        return self._last_message_id

    @property
    def default_auto_archive_duration(self) -> int:
        return self._default_auto_archive_duration

    def __init__(self, data: dict, guild: Guild):
        super().__init__(data, guild)
        for key, value in data.items():
            setattr(self, f"_{key}", value)

    def __repr__(self) -> str:
        return f"<AnnouncementChannel id={self._id} name={self._name}>"