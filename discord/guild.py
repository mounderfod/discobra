from discord.user import User

class GuildMember:
    """
        Represents a member of a `Guild`.
    """
    _user: User
    _nick: str
    _avatar: str
    _roles: list
    _joined_at: str
    _premium_since: str
    _deaf: bool
    _mute: bool
    _pending: bool
    _permissions: str
    _communication_disabled_until: str

    # TODO: Add datetime formatting
    def __init__(self, data: dict):
        for key, value in data.items():
            match (key):
                case 'user':
                    self._user = User(value)
                case _:
                    setattr(self, f"_{key}", value)

    def __repr__(self) -> str:
        return f"<GuildMember user={self._user}>"

    @property
    def user(self) -> User:
        return self._user

class GuildRole:
    _id: str
    _name: str
    _color: int
    _hoist: bool
    _icon: str
    _unicode_emoji: str
    _position: int
    _permissions: str
    _managed: bool
    _mentionable: bool
    _tags: dict

    def __init__(self, data: dict):
        for key, value in data.items():
            match (key):
                case 'color':
                    self._color = value
                case _:
                    setattr(self, f"_{key}", value)

    def __repr__(self) -> str:
        return f"<GuildRole id={self._id} name={self._name}>"
    

class GuildEmoji:
    _id: str
    _name: str
    _roles: list
    _user: User
    _require_colons: bool
    _managed: bool
    _animated: bool
    _available: bool

    def __init__(self, data: dict):
        for key, value in data.items():
            match (key):
                case 'user':
                    self._user = User(value)
                case _:
                    setattr(self, f"_{key}", value)

    def __repr__(self) -> str:
        return f"<GuildEmoji id={self._id} name={self._name}>"

class Guild:
    _id: str
    _name: str
    _icon: str
    _icon_hash: str
    _splash: str
    _discovery_splash: str
    _owner_id: str
    _joined_at: str
    _large: bool
    _unavailable: bool
    _member_count: int
    _region: str
    _voice_states: list
    _members: list[GuildMember]
    _channels: list
    _threads: list
    _afk_channel_id: str
    _afk_timeout: int
    _widget_enabled: bool
    _widget_channel_id: str
    _verification_level: int
    _default_message_notifications: str
    _explicit_content_filter: str
    _roles: list[GuildRole]
    _emojis: list
    _features: list
    _mfa_level: int
    _application_id: str
    _system_channel_id: str
    _system_channel_flags: int
    _rules_channel_id: str
    _max_presences: int | None
    _max_members: int
    _vanity_url_code: str
    _description: str
    _banner: str
    _premium_tier: int
    _presences: list
    _guild_scheduled_events: list
    _premium_subscription_count: int
    _preferred_locale: str
    _public_updates_channel_id: str
    _max_video_channel_users: int
    _approximate_member_count: int
    _approximate_presence_count: int
    _welcome_screen: dict
    _nsfw_level: int
    _stickers: list
    _stage_instances: list
    _premium_progress_bar_enabled: bool

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name
    
    @property
    def members(self) -> list[GuildMember]:
        return self._members
    
    @property
    def roles(self) -> list[GuildRole]:
        return self._roles

    @property
    def channels(self) -> list:
        return self._channels
    
    @property
    def emojis(self) -> list[GuildEmoji]:
        return self._emojis
    
    @property
    def stickers(self) -> list:
        return self._stickers

    def __init__(self, data: dict):
        for key, value in data.items():
            match (key):
                case 'roles':
                    self._roles = [GuildRole(role) for role in value]
                case 'emojis':
                    self._emojis = [GuildEmoji(emoji) for emoji in value]
                case 'members':
                    self._members = [GuildMember(member) for member in value]
                case 'welcome_screen':
                    self._welcome_screen = value
                case 'stickers':
                    self._stickers = value
                case _:
                    setattr(self, f"_{key}", value)

    def __repr__(self) -> str:
        return f"<Guild id={self._id} name={self._name}>"