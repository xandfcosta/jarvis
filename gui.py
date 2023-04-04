import dearpygui.dearpygui as dpg
import win32con, win32gui

class Window():
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.hwnd = None
        dpg.create_context()
        dpg.create_viewport(width=width, height=height, decorated=True)
        
        self.main_window()
        
    def main_window(self):
        with dpg.window(label="Jarvis", tag="primary_window", no_title_bar=True):
            values_x = [ x for x in range(1024)]
            values_y = [ 0 for _ in range(1024)]
            
            with dpg.plot(label="Jarvis voice", width=self.width, height=self.height):

                dpg.add_plot_axis(dpg.mvXAxis, label="x", tag="x_axis")
                dpg.set_axis_limits(axis="x_axis", ymin=0, ymax=1024)
                dpg.add_plot_axis(dpg.mvYAxis, label="y", tag="y_axis")
                dpg.set_axis_limits(axis="y_axis", ymin=-15000, ymax=15000)

                dpg.add_bar_series(values_x, values_y, label="audio file", parent="y_axis", tag="series_tag")

    def show(self) -> None:
        dpg.setup_dearpygui() 
        dpg.show_viewport()
        dpg.set_primary_window("primary_window", True)
        # dpg.start_dearpygui()
        while dpg.is_dearpygui_running():
            dpg.render_dearpygui_frame()
            if self.hwnd == None:
                self.hwnd = win32gui.FindWindow('Dear PyGui', None)
                win32gui.ShowWindow(self.hwnd, win32con.SW_HIDE)
            
        dpg.destroy_context()
        
    def update_plot_bars(self, data):
        values_x = [ x for x in range(1024)]
        values_y = data
        dpg.set_value('series_tag', [values_x, values_y])
        
    def bring_to_top(self):
        win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)
        win32gui.SetWindowPos(self.hwnd, win32con.HWND_TOPMOST, 0, 0, self.width, self.height, 0)
            
    def hide_window(self):
        win32gui.ShowWindow(self.hwnd, win32con.SW_HIDE)
        win32gui.SetWindowPos(self.hwnd, win32con.HWND_TOPMOST, 0, 0, self.width, self.height, 0)
