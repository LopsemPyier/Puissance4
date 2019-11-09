from _P4.puissance4 import *
from _P4.tkinter_puissance4 import *

if __name__ == "__main__":
    root = Tk.Tk()
    game = Game(getDefaultGrid(), 1)
    clientGui = ClientGui(root, game)
    root.mainloop()