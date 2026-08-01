print("SHERIFF START")
async def handle_sheriff_action(
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

    # Шериф уже сделал ход
    if actor.user_id in game.night_state.sheriff_targets:
        print("SHERIFF RESPONSE")
        print("SHERIFF CHECK NIGHT")
        await interaction.response.send_message(
            "❌ Вы уже сделали свой ход.",
            ephemeral=True
        )
        return

    # Сохраняем выбор этого шерифа
    game.night_state.sheriff_targets[actor.user_id] = target_id
    print("SHERIFF SAVED")

    await interaction.response.send_message(
        (
            "👮 **Проверка завершена**\n\n"
            f"👤 Игрок: <@{target.user_id}>\n"
            f"🎭 Роль: **{target.role.name}**"
        ),
        ephemeral=True
    )

    await game.check_night_finished()