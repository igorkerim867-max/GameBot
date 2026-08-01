import discord


class MessageService:

    @staticmethod
    async def dm(bot, user_id: int, message: str, **kwargs):
        """
        Безопасная отправка сообщения в ЛС.
        """

        try:
            user = await bot.fetch_user(user_id)
            await user.send(message, **kwargs)
            return True

        except discord.Forbidden:
            print(f"[DM] Пользователь {user_id} закрыл ЛС.")
            return False

        except Exception as e:
            print(f"[DM ERROR] {user_id}: {e}")
            return False

    @staticmethod
    async def ephemeral(interaction, message: str):
        """
        Эфемерное сообщение.
        """

        await interaction.response.send_message(
            message,
            ephemeral=True
        )

    @staticmethod
    async def edit_game_message(game, title, description, color):

        if game.game_message is None:
            return

        embed = discord.Embed(
            title=title,
            description=description,
            color=color
        )

        await game.game_message.edit(
            embed=embed
        )