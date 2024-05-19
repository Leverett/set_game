from game.globals import *
from kivy.uix.image import Image
from kivy.graphics import RoundedRectangle
from kivy.graphics import Color as KivyColor
from kivy.clock import Clock


class HighlightedImage(Image):
    def __init__(self, **kwargs):
        super(HighlightedImage, self).__init__(**kwargs)
        self.flashing = False

    def flash_hint(self):
        for i in range(HINT_FLASHES):
            Clock.schedule_once(self.flash_switch, FLASH_INTERVAL * (2 * i))
            Clock.schedule_once(self.flash_switch, FLASH_INTERVAL * (2 * i + 1))

    def flash_switch(self, dt=None):
        self.flashing = not self.flashing
        color = FLASH_COLOR if self.flashing else HIGHLIGHT_COLOR
        self.canvas.before.clear()
        with self.canvas.before:
            KivyColor(*color)
            RoundedRectangle(pos=self.highlight_pos(), size=self.highlight_size())

    def on_size(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            KivyColor(*HIGHLIGHT_COLOR)
            RoundedRectangle(pos=self.highlight_pos(), size=self.highlight_size())
    
    def highlight_size(self):
        return (self.norm_image_size[0]*1.1, self.norm_image_size[1]*1.1)
    
    def highlight_pos(self):
        size = self.highlight_size()
        return (self.center_x - size[0]/2, self.center_y - size[1]/2)