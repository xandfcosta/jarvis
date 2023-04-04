import threading
from jarvis import Jarvis
from gui import Window

def main():
    win = Window(1280, 720)
    jarvis = Jarvis(win.update_plot_bars, win.bring_to_top, win.hide_window)
    
    gui_thread = threading.Thread(target=win.show, args=())
    jarvis_thread = threading.Thread(target=jarvis.start, args=())
    
    gui_thread.start()
    jarvis_thread.start()
    
    gui_thread.join()
    jarvis_thread.join()

if __name__ == "__main__":
    main()