from senseview.monitor import Plot2D
import time
import math


t1 = Plot2D("C")
t2 = Plot2D("D")

for i in range(0,100000):
    t1.update_point(math.sin(2*math.pi*0.002*i))
    t2.update_point(math.cos(2*math.pi*0.002*i))

t1.end_update()
t2.end_update()