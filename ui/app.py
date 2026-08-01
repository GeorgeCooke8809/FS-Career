import customtkinter
from ui.active_day_schedule import ActiveDaySchedule

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.geometry("500x750")
        self.minsize(500, 750)
        self.title("Random Schedule Generator")

        # TODO: Add all of the controlling widgets at the top

        self.content = ActiveDaySchedule(self, schedule=[])

        self.mainloop()

    # TODO: Add Generate schedule functionality