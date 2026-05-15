"""Application entry point for C-PurgeTools."""
import tkinter as tk

from .gui import CleanerApp


def main() -> None:
    root = tk.Tk()
    CleanerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
