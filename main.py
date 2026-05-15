"""
C盘清理工具 - 入口
"""
import sys
import os

# Ensure local modules are importable regardless of working directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk
from gui import CleanerApp


def main() -> None:
    root = tk.Tk()
    CleanerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
