class PricingService:
    def __init__(self, fixed_city_ride_price: float) -> None:
        self.fixed_city_ride_price = fixed_city_ride_price

    def compute_price(self, origin_city: str, destination_city: str) -> float:
        # TODO: replace with distance/time-zone pricing logic.
        _ = (origin_city, destination_city)
        return self.fixed_city_ride_price
