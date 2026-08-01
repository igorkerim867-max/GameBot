import discord

from games.mafia.roles import RoleType
from games.mafia.views import PlayerSelectView
from games.mafia.services.message_service import MessageService


async def start_night(game):

    game.night += 1

    embed = discord.Embed(
        title=f"🌙 Ночь {game.night}",
        description="Игроки совершают свои действия...",
        color=discord.Color.dark_blue()
    )

    await game.game_channel.send(embed=embed)

    for player in game.player_service.alive_players():

        role = player.role.role_type

        if role in (RoleType.MAFIA, RoleType.DON):

            await MessageService.dm(
                game.bot,
                player.user_id,
                "🔫 Выберите жертву",
                view=PlayerSelectView(
                    game,
                    player,
                    "mafia_action"
                )
            )

        elif role == RoleType.DOCTOR:

            await MessageService.dm(
                game.bot,
                player.user_id,
                "💉 Кого хотите вылечить?",
                view=PlayerSelectView(
                    game,
                    player,
                    "doctor_action"
                )
            )

        elif role == RoleType.SHERIFF:

            await MessageService.dm(
                game.bot,
                player.user_id,
                "👮 Кого хотите проверить?",
                view=PlayerSelectView(
                    game,
                    player,
                    "sheriff_action"
                )
            )

        elif role == RoleType.HOOKER:

            await MessageService.dm(
                game.bot,
                player.user_id,
                "💋 Кого хотите посетить?",
                view=PlayerSelectView(
                    game,
                    player,
                    "handle_hooker_action"
                )
            )

        elif role == RoleType.MANIAC:

            await MessageService.dm(
                game.bot,
                player.user_id,
                "🔪 Кого хотите убить?",
                view=PlayerSelectView(
                    game,
                    player,
                    "maniac_action"
                )
            )

        else:

            await MessageService.dm(
                game.bot,
                player.user_id,
                "😴 Сегодня вы спите."
            )