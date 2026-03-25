from dataclasses import dataclass


@dataclass(slots=True)
class ProcessedOrderSpeech:
    origin_text: str
    destination_text: str
    notes_text: str
    origin_city: str
    origin_street: str
    origin_house_number: str
    destination_city: str
    destination_street: str
    destination_house_number: str


class SpeechProcessingAdapter:
    """Development stub. Replace with real STT/NLU integration later."""

    def process_order_recordings(
        self, origin_recording_url: str, destination_recording_url: str, notes_recording_url: str
    ) -> ProcessedOrderSpeech:
        return ProcessedOrderSpeech(
            origin_text=f"origin from {origin_recording_url}",
            destination_text=f"destination from {destination_recording_url}",
            notes_text=f"notes from {notes_recording_url}",
            origin_city="Tel Aviv",
            origin_street="Herzl",
            origin_house_number="10",
            destination_city="Tel Aviv",
            destination_street="Allenby",
            destination_house_number="5",
        )
