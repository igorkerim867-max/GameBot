import discord

from core.embeds import GameEmbed


class GamesMenu(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="🕵️ Мафия",
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def mafia(self, interaction: discord.Interaction, button: discord.ui.Button):
        print("1. Нажали кнопку")

        try:
            from ui.mafia_menu import MafiaMenu
            print("2. Импорт прошёл")
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(e)
            raise

        embed = GameEmbed(
            title="🕵️ Мафия",
            description=(
                "Добро пожаловать в игру Мафия!\n\n"
                "Вы можете создать комнату или присоединиться к существующей."
            )
        )

        print("3. Создаём MafiaMenu")
        view = MafiaMenu()
        print("4. MafiaMenu создано")

        await interaction.response.edit_message(
            embed=embed,
            view=view
        )

        print("5. Сообщение изменено")

    @discord.ui.button(
        label="☢️ Бункер",
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def bunker(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "☢️ Бункер скоро появится!",
            ephemeral=True
        )

    @discord.ui.button(
        label="🏦 Монополия",
        style=discord.ButtonStyle.primary,
        row=1
    )
    async def monopoly(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "🏦 Монополия скоро появится!",
            ephemeral=True
        )

    @discord.ui.button(
        label="⬅️ Назад",
        style=discord.ButtonStyle.danger,
        row=2
    )
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        from ui.main_menu import MainMenu

        embed = GameEmbed(
            "🎮 GameBot",
            "Добро пожаловать в игровой центр!\n\nВыберите нужный раздел."
        )

        await interaction.response.edit_message(
            embed=embed,
            view=MainMenu()
        )