async def handle_maniac_action(
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

    # Маньяк уже сделал ход
    if game.night_state.maniac_target is not None:
        await interaction.response.send_message(
            "❌ Вы уже сделали свой ход.",
            ephemeral=True
        )
        return

    game.night_state.maniac_target = target_id

    print(f"🔪 Маньяк {actor.user_id} выбрал {target_id}")

    await interaction.response.send_message(
        "🔪 Ваш выбор сохранён.",
        ephemeral=True
    )

    await game.check_night_finished()