from abc import ABC, abstractmethod

import discord

from core.embeds import GameEmbed


class Screen(ABC):
    """Базовый класс для всех экранов GameBot."""

    title = "GameBot"
    description = ""

    def get_embed(self) -> GameEmbed:
        return GameEmbed(
            title=self.title,
            description=self.description
        )

    @abstractmethod
    def get_view(self) -> discord.ui.View:
        """Возвращает View для данного экрана."""
        pass