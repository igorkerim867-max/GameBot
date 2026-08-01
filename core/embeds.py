import discord

COLOR = 0x5865F2
VERSION = "0.1.0"


class GameEmbed(discord.Embed):
    def __init__(self, title: str, description: str = ""):
        super().__init__(
            title=title,
            description=description,
            color=COLOR
        )

        self.set_footer(
            text=f"GameBot • v{VERSION}"
        )