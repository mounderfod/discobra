class User:
    __slots__ = (
        "id",
        "username",
        "discriminator",
        "avatar",
        "avatar_decoration"
        "bot",
        "system",
        "mfa_enabled",
        "banner",
        "banner_color",
        "accent_color",
        "bio",
        "pronouns",
        "locale",
        "verified",
        "email",
        "flags",
        "premium_type",
        "public_flags"
    )

    def __init__(self, data: dict):
        for k in data:
            setattr(self, k, data[k])
