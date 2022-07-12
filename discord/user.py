from discord.flags import get_flags, Flags
from discord.premium_type import PremiumType


class User:
    _id: str
    _username: str
    _discriminator: str
    _avatar: str
    _bot: bool
    _system: bool
    _mfa_enabled: bool
    _banner: str
    _accent_color: int
    _locale: str
    _verified: bool
    _email: str
    _pronouns: str
    _bio: str
    _flags: list[Flags]
    _premium_type: PremiumType
    _public_flags: list[Flags]

    @property
    def id(self):
        """The user's ID."""
        return self._id

    @property
    def username(self):
        """The user's username. This is not unique."""
        return self._username

    @property
    def discriminator(self):
        """The user's 4-digit tag."""
        return self._discriminator

    @property
    def avatar(self):
        """The user's avatar hash."""
        return self._avatar

    @property
    def bot(self):
        """Whether the user is a bot."""
        return self._bot

    @property
    def pronouns(self):
        """The user's pronouns (not yet implemented into Discord frontend)."""
        return self._pronouns

    @property
    def bio(self):
        """The contents of the user's About Me section."""
        return self._bio

    @property
    def system(self):
        """Whether the user is an Official Discord System user (for urgent messages)."""
        return self._system

    @property
    def mfa_enabled(self):
        """Whether the user has 2FA set up."""
        return self._mfa_enabled

    @property
    def banner(self):
        """The user's banner hash."""
        return self._banner

    @property
    def accent_color(self):
        """The user's banner color."""
        return self._accent_color

    @property
    def locale(self):
        """The user's chosen language."""
        return self._locale

    @property
    def verified(self):
        """Whether the email on the user's account is verified."""
        return self._verified

    @property
    def email(self):
        """The user's email."""
        return self._email

    @property
    def flags(self):
        """The flags on the user's account."""
        return self._flags

    @property
    def premium_type(self):
        """The type of Nitro subscription on a user's account."""
        return self._premium_type

    @property
    def public_flags(self):
        """The public flags on a user's account."""
        return self._public_flags

    def __init__(self, data: dict):
        for k in data:
            if k == "flags" or k == "public_flags":
                setattr(self, f"_{k}", get_flags(data[k]))
            elif k == "premium_type":
                setattr(self, f"_{k}", PremiumType(data[k]))
            else:
                setattr(self, f"_{k}", data[k])

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username} discriminator={self.discriminator}>"
