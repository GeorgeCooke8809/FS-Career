import customtkinter as ctk


class ConfirmDialog(ctk.CTkToplevel):
    def __init__(self, master, message: str, title: str = "Confirm"):
        super().__init__(master)
        self.title(title)
        self.geometry("420x160")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        self.result = False

        label = ctk.CTkLabel(self, text=message, wraplength=380, justify="left")
        label.pack(padx=20, pady=(24, 16), fill="both", expand=True)

        button_row = ctk.CTkFrame(self, fg_color="transparent")
        button_row.pack(pady=(0, 16))

        cancel_btn = ctk.CTkButton(
            button_row, text="Cancel", width=100, fg_color="gray40",
            command=self._on_cancel,
        )
        cancel_btn.pack(side="left", padx=8)

        confirm_btn = ctk.CTkButton(
            button_row, text="Delete", width=100, fg_color="#b3261e",
            hover_color="#8c1d17", command=self._on_confirm,
        )
        confirm_btn.pack(side="left", padx=8)

        self.protocol("WM_DELETE_WINDOW", self._on_cancel)

    def _on_confirm(self):
        self.result = True
        self.destroy()

    def _on_cancel(self):
        self.result = False
        self.destroy()


def confirm(master, message: str, title: str = "Confirm") -> bool:
    dialog = ConfirmDialog(master, message, title)
    master.wait_window(dialog)
    return dialog.result
