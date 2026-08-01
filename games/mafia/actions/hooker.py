async def handle_hooker_action(
    self,
    interaction,
    actor,
    target_id
):
    target = self.player_service.get_player(target_id)

    if target is None or not target.alive:
        await interaction.response.send_message(
            "❌ Этот игрок уже мёртв.",
            ephemeral=True
        )
        return

    if actor.user_id == target.user_id:
        await interaction.response.send_message(
            "❌ Нельзя выбрать себя.",
            ephemeral=True
        )
        return

    # Эта проститутка уже сделала ход
    if actor.user_id in self.night_state.hooker_targets:
        await interaction.response.send_message(
            "❌ Вы уже сделали свой ход.",
            ephemeral=True
        )
        return

    # Сохраняем выбор
    self.night_state.hooker_targets[actor.user_id] = target_id
    print("HOOKER TARGETS:", self.night_state.hooker_targets)

    print(f"💋 Проститутка {actor.user_id} выбрала {target_id}")

    await interaction.response.send_message(
        "💋 Ваш выбор сохранён.",
        ephemeral=True
    )

    await self.check_night_finished()