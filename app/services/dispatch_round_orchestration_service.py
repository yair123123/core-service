from decimal import Decimal

from app.domain.enums.ride_status import RideStatus
from app.domain.schemas.dispatch import (
    DispatchRidePreview,
    DispatchRoundResultRequest,
    DispatchRoundResultStatus,
    DispatchRoundResultResponse,
    StartDispatchRoundRequest,
)
from app.repositories.ride_event_repository import RideEventRepository
from app.repositories.ride_repository import RideRepository
from app.services.dispatch_round_policy_service import DispatchRoundPolicyService
from app.services.dispatch_socket_client import DispatchSocketClient


TERMINAL_STATUSES = {RideStatus.COMPLETED, RideStatus.CANCELED, RideStatus.FAILED}


class DispatchRoundOrchestrationService:
    def __init__(
        self,
        ride_repository: RideRepository,
        ride_event_repository: RideEventRepository,
        policy_service: DispatchRoundPolicyService,
        dispatch_socket_client: DispatchSocketClient,
    ) -> None:
        self.ride_repository = ride_repository
        self.ride_event_repository = ride_event_repository
        self.policy_service = policy_service
        self.dispatch_socket_client = dispatch_socket_client

    def on_ride_created(self, ride_id: int) -> None:
        ride = self.ride_repository.get_by_id(ride_id)
        if not ride or ride.status != RideStatus.SEARCHING_DRIVER:
            return
        if ride.dispatch_round_number >= 1:
            return
        self._start_round(ride_id=ride.id, round_number=1)

    def handle_round_result(self, payload: DispatchRoundResultRequest) -> DispatchRoundResultResponse:
        ride = self.ride_repository.get_by_id(payload.ride_id)
        if not ride:
            return DispatchRoundResultResponse(success=False, action="ride_not_found")

        if ride.last_dispatch_result_round_id == payload.round_id and ride.last_dispatch_result_status == payload.status.value:
            return DispatchRoundResultResponse(success=True, action="duplicate_ignored")

        if ride.status in TERMINAL_STATUSES:
            self._mark_round_processed(payload)
            return DispatchRoundResultResponse(success=True, action="terminal_ride_ignored")

        if payload.round_number < ride.dispatch_round_number:
            self._mark_round_processed(payload)
            return DispatchRoundResultResponse(success=True, action="stale_round_ignored")

        if payload.status == DispatchRoundResultStatus.WINNER_SELECTED:
            if payload.winner_driver_id is None:
                self._mark_round_processed(payload)
                return DispatchRoundResultResponse(success=False, action="winner_missing_driver")
            if ride.status != RideStatus.SEARCHING_DRIVER:
                self._mark_round_processed(payload)
                return DispatchRoundResultResponse(success=True, action="state_incompatible_ignored")

            self.ride_repository.assign_driver(ride, payload.winner_driver_id)
            self._mark_round_processed(payload)
            self.ride_event_repository.add_event(
                ride.id,
                "DISPATCH_ROUND_WINNER_SELECTED",
                {
                    "roundId": payload.round_id,
                    "roundNumber": payload.round_number,
                    "winnerDriverId": payload.winner_driver_id,
                },
            )
            return DispatchRoundResultResponse(success=True, action="driver_assigned")

        self._mark_round_processed(payload)
        self.ride_event_repository.add_event(
            ride.id,
            "DISPATCH_ROUND_FINISHED",
            {
                "roundId": payload.round_id,
                "roundNumber": payload.round_number,
                "status": payload.status.value,
            },
        )

        if payload.status == DispatchRoundResultStatus.DISPATCH_FAILED:
            self.ride_repository.update_status(ride, RideStatus.FAILED)
            self.ride_event_repository.add_event(ride.id, "DISPATCH_FAILED", {"reason": "dispatch_socket_failed"})
            return DispatchRoundResultResponse(success=True, action="dispatch_failed")

        next_round_number = payload.round_number + 1
        next_round = self.policy_service.get_round(next_round_number)
        if next_round is None:
            self.ride_repository.update_status(ride, RideStatus.FAILED)
            self.ride_event_repository.add_event(
                ride.id,
                "DISPATCH_FAILED",
                {"reason": "max_rounds_exhausted", "lastRoundNumber": payload.round_number},
            )
            return DispatchRoundResultResponse(success=True, action="dispatch_failed")

        self._start_round(ride_id=ride.id, round_number=next_round_number)
        return DispatchRoundResultResponse(success=True, action="next_round_started")

    def _start_round(self, ride_id: int, round_number: int) -> None:
        ride = self.ride_repository.get_by_id(ride_id)
        if not ride:
            return

        policy = self.policy_service.get_round(round_number)
        if policy is None:
            self.ride_repository.update_status(ride, RideStatus.FAILED)
            self.ride_event_repository.add_event(ride.id, "DISPATCH_FAILED", {"reason": "missing_policy"})
            return

        round_id = f"ride_{ride.id}_round_{round_number}"
        self.ride_repository.set_dispatch_round(ride, round_number=round_number, round_id=round_id)
        self.ride_event_repository.add_event(
            ride.id,
            "DISPATCH_ROUND_STARTED",
            {
                "roundId": round_id,
                "roundNumber": round_number,
                "radiusKm": policy.radius_km,
                "timeoutSeconds": policy.timeout_seconds,
                "maxCandidates": policy.max_candidates,
            },
        )

        preview = DispatchRidePreview(
            origin_text=ride.origin_text,
            destination_text=ride.destination_text,
            price=float(ride.price_amount) if isinstance(ride.price_amount, Decimal) else ride.price_amount,
            note=ride.notes_text,
        )
        payload = StartDispatchRoundRequest(
            ride_id=ride.id,
            round_id=round_id,
            round_number=round_number,
            station_id=ride.station_id,
            origin_lat=None,
            origin_lon=None,
            radius_km=policy.radius_km,
            timeout_seconds=policy.timeout_seconds,
            max_candidates=policy.max_candidates,
            ride_preview=preview,
        )

        try:
            self.dispatch_socket_client.start_round(payload)
        except Exception:
            self.ride_event_repository.add_event(
                ride.id,
                "DISPATCH_ROUND_START_FAILED",
                {"reason": "start_round_http_error", "roundNumber": round_number},
            )

    def _mark_round_processed(self, payload: DispatchRoundResultRequest) -> None:
        ride = self.ride_repository.get_by_id(payload.ride_id)
        if not ride:
            return
        self.ride_repository.set_dispatch_result(
            ride,
            round_id=payload.round_id,
            status=payload.status.value,
        )
