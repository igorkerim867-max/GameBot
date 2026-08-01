
async def handle_doctor_action(
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

    # Доктор уже сделал ход
    if actor.user_id in game.night_state.doctor_targets:
        await interaction.response.send_message(
            "❌ Вы уже сделали свой ход.",
            ephemeral=True
        )
        return

    # Сохраняем выбор именно этого доктора
    game.night_state.doctor_targets[actor.user_id] = target_id

    print(f"💉 Доктор {actor.user_id} лечит {target_id}")

    await interaction.response.send_message(
        "💉 Выбор сохранён.",
        ephemeral=True
    )

    await game.check_night_finished()