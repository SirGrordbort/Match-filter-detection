"""
A work in progress intended to show the animation of the events along side where they are plotted on a graph of
cumulative detections

:author: Toby Messerli
:date: 13/2/2020
"""

from matplotlib import pyplot as plt
from matplotlib import animation

fig = plt.figure()
ax = plt.axes()
points = ax.scatter([], [])


def init():
    points.x = []
    points.y = []
    return points


def animate(i):
    x = []
    y = []
    for n in range(0, i):
        x.append(n)
        y.append(n)
    points.x = x
    points.y = y
    return points


anim = animation.FuncAnimation(fig, animate, init_func=init,
                               frames=200, interval=20, blit=False)
plt.show()
