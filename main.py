import sys
import os

src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(src_path)
from src.gui import gui

if __name__ == "__main__":
    app = gui.App()    
    app.mainloop()