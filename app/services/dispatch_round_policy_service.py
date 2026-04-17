from dataclasses import dataclass

from app.config import Settings


@dataclass(slots=True)
class DispatchRoundPolicy:
    round_number: int
    radius_km: float
    timeout_seconds: int
    max_candidates: int


class DispatchRoundPolicyService:
    def __init__(self, settings: Settings) -> None:
        self.rounds = {
            1: DispatchRoundPolicy(
                round_number=1,
                radius_km=settings.dispatch_round_1_radius_km,
                timeout_seconds=settings.dispatch_round_1_timeout_seconds,
                max_candidates=settings.dispatch_round_1_max_candidates,
            ),
            2: DispatchRoundPolicy(
                round_number=2,
                radius_km=settings.dispatch_round_2_radius_km,
                timeout_seconds=settings.dispatch_round_2_timeout_seconds,
                max_candidates=settings.dispatch_round_2_max_candidates,
            ),
            3: DispatchRoundPolicy(
                round_number=3,
                radius_km=settings.dispatch_round_3_radius_km,
                timeout_seconds=settings.dispatch_round_3_timeout_seconds,
                max_candidates=settings.dispatch_round_3_max_candidates,
            ),
        }

    def get_round(self, round_number: int) -> DispatchRoundPolicy | None:
        return self.rounds.get(round_number)
