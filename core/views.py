import discord


class MainMenu(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="🎲 Игры",
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def games(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        embed = discord.Embed(
            title="🎲 Игры",
            description="Выберите игру.",
            color=0x5865F2
        )

        embed.add_field(
            name="Доступные игры",
            value=(
                "🕵️ Мафия\n"
                "☢️ Бункер\n"
                "🏦 Монополия\n"
                "🎭 Alias\n"
                "🐊 Крокодил"
            ),
            inline=False
        )

        await interaction.response.edit_message(
            embed=embed,
            view=GamesMenu()
        )


    @discord.ui.button(
        label="👤 Профиль",
        style=discord.ButtonStyle.secondary,
        row=0
    )
    async def profile(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        embed = discord.Embed(
            title="👤 Профиль",
            description=f"Игрок: {interaction.user.mention}",
            color=0x5865F2
        )

        await interaction.response.edit_message(
            embed=embed,
            view=self
        )


    @discord.ui.button(
        label="🏆 Рейтинг",
        style=discord.ButtonStyle.success,
        row=1
    )
    async def rating(
        self,
        interaction,
        button
    ):

        embed = discord.Embed(
            title="🏆 Рейтинг",
            description="Пока пусто.",
            color=0x5865F2
        )

        await interaction.response.edit_message(
            embed=embed,
            view=self
        )


    @discord.ui.button(
        label="⚙️ Настройки",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def settings(
        self,
        interaction,
        button
    ):

        embed = discord.Embed(
            title="⚙️ Настройки",
            description="Настройки появятся позже.",
            color=0x5865F2
        )

        await interaction.response.edit_message(
            embed=embed,
            view=self
        )


class GamesMenu(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="🕵️ Мафия",
        style=discord.ButtonStyle.primary
    )
    async def mafia(
        self,
        interaction,
        button
    ):

        embed = discord.Embed(
            title="🕵️ Мафия",
            description="Скоро здесь можно будет создать комнату.",
            color=0x5865F2
        )

        await interaction.response.edit_message(
            embed=embed,
            view=self
        )


    @discord.ui.button(
        label="⬅ Назад",
        style=discord.ButtonStyle.danger
    )
    async def back(
        self,
        interaction,
        button
    ):

        embed = discord.Embed(
            title="🎮 GameBot",
            description="Главное меню",
            color=0x5865F2
        )

        await interaction.response.edit_message(
            embed=embed,
            view=MainMenu()
        )