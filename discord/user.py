class User:
    __slots__ = (
        "id",
        "username",
        "discriminator",
        "avatar",
        "bot",
        "system",
        "mfa_enabled",
        "banner",
        "accent_color",
        "locale",
        "verified",
        "email",
        "flags",
        "premium_type",
        "public_flags"
    )

    def __init__(self, data: dict):
        for k, v in data:
            setattr(self, k, v)
