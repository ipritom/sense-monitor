# Sense Monitor
Lightning fast LIVE graph visualisation tool based on Redis and DPG. At this moment, it supports only 2D line plots. Multiple graphs can be visualised in a single window. This tool works in a pub-sub manner to facilitate graph visualisation of dynamic scripts in a non-blocking way. 

# How to use
You need to install [Redis](https://redis.io/docs/latest/operate/oss_and_stack/install/install-redis/). Default redis client can be modified.

### `Class Plot2D`

This class helps to initialize the plot context. Data points are stored in the Redis.

Here we are initiating plot variable. We can give them a title which will be shown as legend.

```python
from senseview.monitor import Plot2D

t1 = Plot2D("C")
t2 = Plot2D("D")
```
How to update data points is shown bellow.

```python
for i in range(0,100000):
    t1.update_point(math.sin(2*math.pi*0.002*i))
    t2.update_point(math.cos(2*math.pi*0.002*i))
```

We must ensure the end.

```python
t1.end_update()
t2.end_update()
```

### `Class LiveMonitor`
This class helps to visualise plots created in a seperated program. 


```python
from senseview.monitor import LiveMonitor

lv = LiveMonitor(buff_size=1000)
lv.add_plot_name("C")
lv.add_plot_name("D")
lv.render()

```
`buff_size` : limit of data points we want to visualise at a time in a single graph window.

### Change default redis clients 
```python
import redis
from senseview.monitor import LiveMonitor

redis_client = ... # your redis client
lv = LiveMonitor(buff_size=1000)
lv.redMem = redis_client

```
