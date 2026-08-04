import asyncio

import discord

from games.mafia.roles import RoleType, Team

async def kill_player(
    game,
    player,
    dead_players,
    reason=None
):
    if player is None or not player.alive:
        return

    player.alive = False

    if player not in dead_players:
        dead_players.append(player)

    user = await game.bot.fetch_user(player.user_id)

    text = (
        "💀 Вы были убиты этой ночью.\n"
        "Вы больше не участвуете в игре."
    )

    if reason:
        text += f"\n\nПричина: {reason}"

    await user.send(text)
async def process_mafia(
    game,
    dead_players,
    hookers,
    hooker_targets
):
    """
    Обработка всех действий мафии.
    """

    ns = game.night_state

    if not ns.mafia_targets:
        return

    # Все уникальные цели мафии
    mafia_targets = set(ns.mafia_targets.values())

    # Все игроки, которых лечили доктора
    saved_players = set(ns.doctor_targets.values())

    # Перебираем каждую уникальную цель
    for target_id in mafia_targets:

        # Доктор спас
        if target_id in saved_players:

            for doctor in game.player_service.find_alive_roles(
                RoleType.DOCTOR
            ):
                user = await game.bot.fetch_user(doctor.user_id)
                await user.send(
                    f"✅ Игрок <@{target_id}> был успешно спасён."
                )

            continue

        dead_player = game.player_service.get_player(target_id)

        if dead_player is None:
            continue

        await kill_player(
            game,
            dead_player,
            dead_players
        )

    # Всем мафиям отправляем результат
    for mafia in game.player_service.mafia_players():

        user = await game.bot.fetch_user(mafia.user_id)

        victims = "\n".join(
            f"• <@{player_id}>"
            for player_id in mafia_targets
        )

        await user.send(
            "🔫 Ваши действия обработаны.\n\n"
            f"Цели этой ночью:\n{victims}"
        )
async def process_maniac(
    game,
    dead_players,
    hookers,
    hooker_targets
):
    """
    Обрабатывает действия Маньяка.
    """

    ns = game.night_state

    if ns.maniac_target is None:
        return

    # Все спасённые игроки
    saved_players = set(ns.doctor_targets.values())

    # Доктора спасли цель Маньяка
    if ns.maniac_target in saved_players:

        for doctor in game.player_service.find_alive_roles(
            RoleType.DOCTOR
        ):
            user = await game.bot.fetch_user(doctor.user_id)
            await user.send(
                f"✅ Игрок <@{ns.maniac_target}> был успешно спасён."
            )

        maniac = game.player_service.find_alive_role(
            RoleType.MANIAC
        )

        if maniac:
            user = await game.bot.fetch_user(
                maniac.user_id
            )
            await user.send(
                "🩺 Доктор спас вашу жертву.\n"
                "❌ Убийство не удалось."
            )

        return

    dead_player = game.player_service.get_player(
        ns.maniac_target
    )

    if dead_player is None:
        return

    await kill_player(
        game,
        dead_player,
        dead_players
    )

    # Проститутка пришла к Маньяку
    for hooker in hookers:

        target = hooker_targets.get(
            hooker.user_id
        )

        if (
            hooker.alive
            and target
            and target.role.role_type == RoleType.MANIAC
        ):
            await kill_player(
                game,
                hooker,
                dead_players,
                "вы посетили Маньяка."
            )

async def process(game):

    dead_players = []
    # Сбрасываем эффект проститутки с прошлой ночи
    for player in game.players:
        player.blocked_by_hooker = False
        player.can_vote = True

    hookers = game.player_service.find_alive_roles(
        RoleType.HOOKER
    )

    hooker_targets = {}
    print("NightState hooker_targets =", game.night_state.hooker_targets)

    for hooker in hookers:

        target_id = game.night_state.hooker_targets.get(
            hooker.user_id
        )

        if target_id is None:
            continue

        target = game.player_service.get_player(target_id)

        if target:
            hooker_targets[hooker.user_id] = target

            target.can_vote = False
            target.blocked_by_hooker = True
    print("Resolved hooker_targets =", hooker_targets)

    # ==========================
    # Мафия
    # ==========================
    await process_mafia(
        game,
        dead_players,
        hookers,
        hooker_targets
    )

    # ==========================
    # Маньяк
    # ==========================

    await process_maniac(
        game,
        dead_players,
        hookers,
        hooker_targets
    )

    await finish_process(
        game,
        dead_players
    )

async def finish_process(
    game,
    dead_players
):

    game.night_state.reset()

    if dead_players:

        victims = "\n".join(
            f"💀 <@{player.user_id}> — **{player.role.name}**"
            for player in dead_players
        )

        description = (
            "☀️ Наступило утро.\n\n"
            "Сегодня ночью погибли:\n\n"
            f"{victims}"
        )

    else:

        description = (
            "☀️ Наступило утро.\n\n"
            "🩺 Сегодня ночью никто не погиб."
        )
    # ==========================
    # Живые игроки
    # ==========================

    alive_players = game.player_service.alive_players()

    alive_text = "\n".join(
        f"• <@{player.user_id}>"
        for player in alive_players
    )

    # ==========================
    # Подсчет оставшихся ролей
    # ==========================

    from collections import Counter

    role_counter = Counter(
        player.role.name
        for player in alive_players
    )

    ROLE_ICONS = {
        "Мафия": "🔫",
        "Доктор": "💉",
        "Шериф": "👮",
        "Проститутка": "💋",
        "Маньяк": "🔪",
        "Мирный": "👤"
    }

    roles_text = "\n".join(
        f"{ROLE_ICONS.get(role, '🎭')} {role} ×{count}"
        for role, count in role_counter.items()
    )

    description += (

        "\n\n━━━━━━━━━━━━━━━━━━"

        f"\n\n👥 **Живые игроки ({len(alive_players)})**\n\n"

        f"{alive_text}"

        "\n\n━━━━━━━━━━━━━━━━━━"

        "\n\n🎭 **Оставшиеся роли**\n\n"

        f"{roles_text}"
    )

    embed = discord.Embed(
        title="☀️ День",
        description=description,
        color=discord.Color.gold()
    )

    await game.game_channel.send(embed=embed)
    await asyncio.sleep(5)

    if await game.check_win():
        return

    for player in game.players:

        if player.blocked_by_hooker:
            player.can_vote = False
        else:
            player.can_vote = True

    await game.start_day()