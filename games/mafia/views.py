import discord


class PlayerSelect(discord.ui.Select):

    def __init__(self, game, actor, callback_name):

        self.game = game
        self.actor = actor
        self.callback_name = callback_name

        options = []

        for player in game.player_service.alive_players():

            if player.user_id == actor.user_id:
                continue
            # Мафия не может выбирать мафию
            if callback_name == "mafia_action":
                if player.role.team == actor.role.team:
                    continue

            user = game.bot.get_user(player.user_id)

            if user is None:
                label = str(player.user_id)
            else:
                label = user.display_name

            options.append(
                discord.SelectOption(
                    label=label,
                    value=str(player.user_id)
                )
            )

        super().__init__(
            placeholder="Выберите игрока...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        self.disabled = True

        for item in self.view.children:
            item.disabled = True

        await interaction.message.edit(view=self.view)

        target_id = int(self.values[0])

        await getattr(
            self.game,
            self.callback_name
        )(
            interaction,
            self.actor,
            target_id
        )

class PlayerSelectView(discord.ui.View):

    def __init__(self, game, actor, callback_name):

        super().__init__(timeout=None)

        self.add_item(
            PlayerSelect(
                game,
                actor,
                callback_name
            )
        )