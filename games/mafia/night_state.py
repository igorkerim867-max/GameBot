from dataclasses import dataclass, field


@dataclass
class NightState:

    # Кто кого выбрал этой ночью
    mafia_targets: dict[int, int] = field(default_factory=dict)
    doctor_targets: dict[int, int] = field(default_factory=dict)
    sheriff_targets: dict[int, int] = field(default_factory=dict)
    hooker_targets: dict[int, int] = field(default_factory=dict)

    # Маньяк пока один
    maniac_target: int | None = None

    def reset(self):
        self.mafia_targets.clear()
        self.doctor_targets.clear()
        self.sheriff_targets.clear()
        self.hooker_targets.clear()

        self.maniac_target = None