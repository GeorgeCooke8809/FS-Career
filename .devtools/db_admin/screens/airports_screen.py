from db_admin import repo
from db_admin.forms.airport_form import AirportForm
from db_admin.screens.base_screen import BaseTableScreen


class AirportsScreen(BaseTableScreen):
    columns = ["ICAO", "IATA", "Name", "City", "Country"]
    referenced_by_label = "Routes"

    def fetch_rows(self, page: int):
        return repo.search_airports(self.session, self.search_text, page=page, page_size=self.page_size)

    def format_row(self, obj) -> list[str]:
        return [obj.icao, obj.iata or "", obj.name, obj.city, obj.country]

    def open_add_form(self) -> None:
        AirportForm(self, self.session, on_saved=self.refresh)

    def open_edit_form(self, obj) -> None:
        AirportForm(self, self.session, record=obj, on_saved=self.refresh)

    def do_delete(self, obj) -> None:
        repo.delete_airport(self.session, obj)

    def record_label(self, obj) -> str:
        return f"{obj.icao} — {obj.name}"
