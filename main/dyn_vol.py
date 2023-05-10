import math
import numpy as np
import random
import sys
import tkinter as tk

from carbon.ffmpeg import gen_dyn_vol
from carbon.graph.graph2d import graph2d
from carbon.gui.button import Button
from carbon.gui.label import Label
from carbon.gui.slider import Slider
from carbon.noise import perlin_noise_1d


def dyn_vol(DUR):
    """`DUR`: the output duration"""

    root = tk.Tk()
    root.attributes('-fullscreen', True)

    mon_width = root.winfo_screenwidth()
    mon_height = root.winfo_screenheight()

    page = tk.Canvas(width=mon_width, height=mon_height, bg='#111', highlightthickness=0, borderwidth=0)
    page.place(x=0, y=0)

    Button.page = page
    Slider.set_page(page)
    Slider.set_page_focus([None])


    class Rt:  # runtime
        
        nchanges = 30
        vol_min = 0.65
        vol_max = 1.0
        
        ## perlin noise
        persistence = 0.65
        octaves = 3
        frequency = 5
        seed = random.randint(-10000000000, 10000000000)

        ts = None
        filter = None  # the ffmpeg dynamic-volume filter

    def redraw():
        page.delete('graph2d')

        raw = []
        for x in np.linspace(0, DUR, Rt.nchanges):
            raw.append((x, perlin_noise_1d(x, Rt.persistence, Rt.octaves, Rt.frequency, Rt.seed)))

        ## adjusting the y interval
        y_values = [y for (_, y) in raw]
        ymin_current = min(y_values)
        ymax_current = max(y_values)
        scale_factor = (Rt.vol_max - Rt.vol_min) / (ymax_current - ymin_current)
        scaled = [(x, Rt.vol_min + (y - ymin_current)*scale_factor) for (x, y) in raw]

        WIDTH = mon_width*0.6
        HEIGHT = mon_height*0.6
        graph2d(
            page,
            points=scaled,
            ymin=0,
            pos=((mon_width - WIDTH)*0.8, (mon_height - HEIGHT)/2),
            width=WIDTH,
            height=HEIGHT,
            title='Dynamic Volume',
            show_points=True,
            points_rad=5,
            x_axis_label='time',
            y_axis_label='vol',
        )

        Rt.ts = scaled  # saved for futher processing

    redraw()  # init

    X = 150
    Y = 80
    GAP = 60
    def fn(var):
        setattr(Rt, var, Slider.get_value_by_id(var))
        redraw()
    Slider(
        id='nchanges',
        min=3,
        max=max(50, int(DUR/4)),  # If the `nchanges` is too big, the command won't work.
        step=1,
        init=Rt.nchanges,
        x=X,
        y=Y,
        fn=lambda: fn('nchanges'),
        label='Number of transition',
        label_y_shift=-20
    )
    Slider(
        id='vol_min',
        min=0,
        max=1,
        step=0.01,
        init=Rt.vol_min,
        x=X,
        y=Y + GAP,
        fn=lambda: fn('vol_min'),
        label='Lowest volume',
        label_y_shift=-20
    )
    Slider(
        id='vol_max',
        min=1,
        max=1.5,  # beware of clipping
        step=0.01,
        init=Rt.vol_max,
        x=X,
        y=Y + GAP*2,
        fn=lambda: fn('vol_max'),
        label='Highest volume',
        label_y_shift=-20
    )

    Slider(
        id='persistence',
        min=0,
        max=1,
        step=0.01,
        init=Rt.persistence,
        x=X,
        y=Y + GAP*3,
        fn=lambda: fn('persistence'),
        label='Perlin noise: persistence',
        label_y_shift=-20
    )
    Slider(
        id='octaves',
        min=1,
        max=10,
        step=1,
        init=Rt.octaves,
        x=X,
        y=Y + GAP*4,
        fn=lambda: fn('octaves'),
        label='Perlin noise: octaves',
        label_y_shift=-20
    )
    Slider(
        id='frequency',
        min=2,
        max=20,
        step=1,
        init=Rt.frequency,
        x=X,
        y=Y + GAP*5,
        fn=lambda: fn('frequency'),
        label='Perlin noise: frequency',
        label_y_shift=-20
    )

    X = 150
    Y = 430
    GAP = 50

    Label(
        'seed',
        X, Y,
        f'Perlin noise seed: {Rt.seed}',
        'Consolas 10',
        anchor='center',
        bg='#111'
    )
    def new_seed():
        Rt.seed = random.randint(-10000000000, 10000000000)
        redraw()
        Label.set_text_by_id('seed', f'Perlin noise seed: {Rt.seed}',)
    Button(
        id='new_seed',
        x=X,
        y=Y + GAP/1.5,
        label='New seed',
        fn=new_seed
    )
    def pick_the_pattern():
        Rt.filter = gen_dyn_vol(Rt.ts)
        
        ## To ensure a fresh page for the next GUI, it is necessary to destroy all current GUI widgets.
        ## These must be done before `root.destroy()`
        Button.destroy_all()
        Label.destroy_all()
        Slider.destroy_all()

        root.destroy()
    Button(
        id='pick_the_pattern',
        x=X,
        y=Y + GAP*3,
        label='Pick the pattern',
        fn=pick_the_pattern,
        len=120
    )

    Button(
        id='abort',
        x=X,
        y=Y + GAP*4,
        label='Cancel (exit)',
        fn=lambda: sys.exit(1),
        len=80
    )


    def left_mouse_press(e):
        Button.press_listener()
        Slider.press_listener()
    root.bind('<ButtonPress-1>', left_mouse_press)

    def left_mouse_hold(e):
        Slider.hold_listener()
    root.bind('<B1-Motion>', left_mouse_hold)

    def left_mouse_release(e):
        Button.release_listener()
        Slider.release_listener()
    root.bind('<ButtonRelease-1>', left_mouse_release)

    def background():
        Button.hover_listener()
        Slider.hover_listener()
        root.after(50, background)
    background()

    root.bind('<Escape>', lambda e: sys.exit(1))

    root.mainloop()

    return (
        f',{Rt.filter}',
        {
            'nchanges': Rt.nchanges,
            'vol_min': Rt.vol_min,
            'vol_max': Rt.vol_max,
            'persistence': Rt.persistence,
            'octaves': Rt.octaves,
            'frequency': Rt.frequency,
            'seed': Rt.seed,
        }
    )