from senseview.monitor import LiveMonitor

lv = LiveMonitor(buff_size=100000)
lv.add_plot_name("C")
lv.add_plot_name("D")
lv.render()