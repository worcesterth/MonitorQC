import tkinter as tk
import os, shutil, platform
from screens.base import BG_COLOR


def _install_font():
    """คัดลอก THSarabunNew.ttf เข้า ~/Library/Fonts/ บน macOS อัตโนมัติ"""
    if platform.system() != "Darwin":
        return
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "assets", "fonts", "THSarabunNew.ttf")
    if not os.path.exists(src):
        return
    dst = os.path.expanduser("~/Library/Fonts/THSarabunNew.ttf")
    if not os.path.exists(dst):
        shutil.copy2(src, dst)


_install_font()


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("โปรแกรมตรวจคุณภาพหน้าจอ")
        self.resizable(True, True)
        self.minsize(900, 600)
        self.configure(bg=BG_COLOR)

        # เปิดเต็มจอ
        self.after(0, self._maximize)

        # shared state
        self.session: dict = {}

        # full-window container
        self.container = tk.Frame(self, bg=BG_COLOR)
        self.container.pack(fill="both", expand=True)

        # register screens
        self.screens: dict = {}
        self._register_screens()

        self.show("home")

    def _maximize(self):
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        self.geometry(f"{ws}x{hs}+0+0")

    def _register_screens(self):
        from screens.home           import HomeScreen
        from screens.select_type    import SelectTypeScreen
        from screens.select_period  import SelectPeriodScreen
        from screens.login          import LoginScreen
        from screens.confirm        import ConfirmScreen
        from screens.instructions   import InstructionsScreen
        from screens.test_runner    import TestRunnerScreen
        from screens.results        import ResultsScreen
        from screens.after_save     import AfterSaveScreen
        from screens.criteria       import CriteriaScreen
        from screens.comparison     import ComparisonScreen
        from screens.history        import HistoryScreen
        from screens.history_result import HistoryResultScreen
        from screens.register       import RegisterScreen
        from screens.user_list      import UserListScreen

        screen_classes = {
            "home":           HomeScreen,
            "select_type":    SelectTypeScreen,
            "select_period":  SelectPeriodScreen,
            "login":          LoginScreen,
            "confirm":        ConfirmScreen,
            "instructions":   InstructionsScreen,
            "test_runner":    TestRunnerScreen,
            "results":        ResultsScreen,
            "after_save":     AfterSaveScreen,
            "criteria":       CriteriaScreen,
            "comparison":     ComparisonScreen,
            "history":        HistoryScreen,
            "history_result": HistoryResultScreen,
            "register":       RegisterScreen,
            "user_list":      UserListScreen,
        }

        for name, cls in screen_classes.items():
            frame = cls(self.container, self)
            self.screens[name] = frame

    def show(self, name: str, **kwargs):
        screen = self.screens[name]
        screen.place(relx=0, rely=0, relwidth=1, relheight=1)
        screen.lift()
        if hasattr(screen, "on_show"):
            screen.on_show(**kwargs)
        self.update_idletasks()
        for s in self.screens.values():
            if s is not screen:
                if hasattr(s, "on_hide"):
                    s.on_hide()
                s.place_forget()


if __name__ == "__main__":
    app = App()
    app.mainloop()
