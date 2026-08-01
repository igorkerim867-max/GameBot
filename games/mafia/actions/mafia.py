async def handle_mafia_action(
    game,
    interaction,
    actor,
    target_id
):
    target = game.player_service.get_player(target_id)

    if target is None or not target.alive:
        await interaction.response.send_message(
            "❌ Этот игрок уже мёртв.",
            ephemeral=True
        )
        return

    # Уже сделал выбор
    if actor.user_id in game.night_state.mafia_targets:
        await interaction.response.send_message(
            "❌ Вы уже сделали свой ход.",
            ephemeral=True
        )
        return

    # Сохраняем выбор этой мафии
    game.night_state.mafia_targets[actor.user_id] = target_id

    print(
        f"🔫 Мафия {actor.user_id} выбрала {target_id}"
    )

    await interaction.response.send_message(
        "🔫 Выбор сохранён.",
        ephemeral=True
    )

    await game.check_night_finished()