
import dearpygui.dearpygui as dpg 

import redis

# class RedisMemory:
#     def __init__(self):
#         pass


redMem = redis.Redis(host='localhost', port=6379, decode_responses=True)


class Plot:
    def __init__(self, title,  buff_size=500, timeout=50, dim=2):
        self.title = title
        self.MEMTIMEOUT = timeout
        self.buff_size = buff_size
        self.redMem = redMem
        self.dim = dim
        
        # plot memory variables
        self.x_data = f"{title}_x"
        self.y_data = f"{title}_y"
        self.z_data = f"{title}_z"
        self.plot_active_key = f"{title}_plot_active"
    
    def __get_processed_array(self, arr:list):
        return list(map(float, arr))

    def is_active(self):
        if self.redMem.exists(self.plot_active_key):
            if int(self.redMem.get(self.plot_active_key)):
                return True
            else: 
                return False
        else:
            return False

    @property
    def x(self):
        if redMem.exists(self.x_data):
            x_len = self.redMem.llen(self.x_data)
            start_index = max(0, x_len-self.buff_size)
            return self.__get_processed_array(redMem.lrange(self.x_data, start_index, -1))
        else:
            return []
        
    @property
    def y(self):
        if redMem.exists(self.y_data):
            y_len = self.redMem.llen(self.y_data)
            start_index = max(0, y_len-self.buff_size)
            return self.__get_processed_array(redMem.lrange(self.y_data, start_index, -1))
        else:
            return []


class Plot2D(Plot):
    def __init__(self, title:str="untitled", buff_size=500, timeout=50) -> None:
        super().__init__(title, buff_size, timeout, 2)
        
        self.x_name = f"{title}_x"
        self.y_name = f"{title}_y"
        self.plot_active_key = f"{title}_plot_active"

        # flags
        self.INITIALIZED = False
        # initial ops
        self.__memory_reset() # reset previous memory 
    
    def __memory_reset(self):
        """Reset Previous Data & Ensure Existance"""
        if self.redMem.exists(self.x_name):
            print(f" RESET ", self.x_name)
            self.redMem.delete(self.x_name)

        if self.redMem.exists(self.y_name):
            print(f" RESET ", self.y_name)
            self.redMem.delete(self.y_name)
        
        if self.redMem.exists(self.plot_active_key):
            self.redMem.set(self.plot_active_key, 0)

    def __get_processed_array(self, arr:list):
        return list(map(float, arr))

    @property
    def x(self):
        return self.__get_processed_array(redMem.lrange(self.x_name, 0, -1))
    
    @property
    def y(self):
        return self.__get_processed_array(redMem.lrange(self.y_name, 0, -1))
    
    
    def isNewKey(self, key_name):
        if self.redMem.exists(key_name)==1:
            return False
        else:
            return True
        
    def set_initialized(self):
        self.INITIALIZED = True
        self.redMem.set(self.plot_active_key, 1)

    def update_point(self, y=None, x=None):
        
        if not self.INITIALIZED:
            if x is None:
                if self.isNewKey(self.x_name):
                    self.redMem.rpush(self.x_name, 0)
                else:
                    last_x = self.redMem.lrange(self.x_name,-1,-1)
                    print(last_x)
                    self.redMem.rpush(self.x_name, int(last_x)+1)

            self.redMem.rpush(self.y_name, y)
            self.set_initialized()
            
            return
        
        if x is None:
            last_x = self.redMem.lrange(self.x_name,-1,-1)
            self.redMem.rpush(self.x_name, int(last_x[0])+1)
        else:
            self.redMem.rpush(self.x_name, x)
        
        self.redMem.rpush(self.y_name, y)

    def end_update(self):
        print(f" --- Ending {self.title}")
        self.redMem.set(self.plot_active_key, 0)#, ex=self.MEMTIMEOUT)
        
    

class LiveMonitor:
    def __init__(self, height=700, width=900, buff_size=500) -> None:
        self.height = height
        self.width = width

        self.plot_list:list[Plot] = []
        self.LIVE = False
        self.buff_size = buff_size

        
    def add_plot_name(self, name:str):
        self.plot_list.append(Plot(title=name, buff_size=self.buff_size))

    def reset_mem(self):
        pass
    

    def is_live_ready(self):

        # if this loop gets to the end then live is ready
        for plot in self.plot_list:
            if not plot.is_active():
                
                return False

        return True
    

    def update_plot(self, plot:Plot):
        dpg.set_value(item=plot.title, value=[plot.x,plot.y])

    def render(self):
        # reset memory 
        self.reset_mem()
        
        # start DPG window rendering process
        self.create_dpg_plot()
        dpg.create_viewport(title="Sense Monitor")#, width=800, height=800)
        dpg.setup_dearpygui()
        dpg.show_viewport()

        # dpg redering loop
        while dpg.is_dearpygui_running():
            # rendering plots
            if self.is_live_ready():
                for plot in self.plot_list:
                    self.update_plot(plot)
                
                dpg.fit_axis_data('x_axis')
                dpg.fit_axis_data('y_axis')
                

            dpg.render_dearpygui_frame()

    def create_dpg_plot(self):

        dpg.create_context()

        with dpg.window(label="LIVE Panel", 
                        height=self.height,
                        width=self.width):
            
            with dpg.plot(label="LIVE Graph", height=self.height-100, width=self.width-100, anti_aliased=True):
                dpg.add_plot_legend()
                # REQUIRED: create x and y axes
                dpg.add_plot_axis(dpg.mvXAxis, label="x", tag="x_axis")
                dpg.add_plot_axis(dpg.mvYAxis, label="y", tag="y_axis")

                for plot in self.plot_list:
                    dpg.add_line_series(plot.x, plot.y, label=plot.title, parent="y_axis", tag=plot.title)
                    
                


if __name__ == "__main__":
    import time
