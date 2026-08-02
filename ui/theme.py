import customtkinter

class Colours:
    ROUTE_CARD_COMPLETED_SIDE = "#b9b9b9"
    ROUTE_CARD_CURRENT_SIDE = "#21c73d"
    ROUTE_CARD_FUTURE_SIDE = "#3769d6"

    ROUTE_CARD_ON_TIME_FONT = "#21c73d"

class Fonts:
    _route_card_airport_icao = None
    _route_card_subheader = None

    @classmethod
    def route_card_airport_icao(cls):
        if cls._route_card_airport_icao is None:
            cls._route_card_airport_icao = customtkinter.CTkFont(family="Segoe UI", size=25, weight="bold")
        return cls._route_card_airport_icao

    @classmethod
    def route_card_subheader(cls):
        if cls._route_card_subheader is None:
            cls._route_card_subheader = customtkinter.CTkFont(family="Segoe UI", size=12)
        return cls._route_card_subheader