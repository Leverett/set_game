from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from game.globals import *
from kivy.app import App
from kivy.properties import StringProperty
from functools import partial
from kivy.clock import Clock
from game.game_objects import Rule

class LabeledCheckBox(RelativeLayout):
    text = StringProperty("")
    rule = StringProperty("")

    disabled_color = [0.5, 0.5, 0.5, 1]
    enabled_color = [1, 1, 1, 1]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def checkbox(self):
        return self.ids.checkbox
    
    def disable(self, is_disabled):
        self.checkbox().disabled = is_disabled
        self.ids.label.color = self.disabled_color if is_disabled else self.enabled_color

class GameSettings(BoxLayout):
    game_mode = StringProperty("")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        Clock.schedule_once(self._on_widget_ready)

    def _on_widget_ready(self, dt):
        self.opts = [opt for opt in self.children if isinstance(opt, LabeledCheckBox)]
        self.set_opts()
        self.bound_funcs = {}
        self.bind_opts(True)

    def opts(self):
        return 

    def on_opt_selected(self, rule, checkbox, value):
        self.set_rule(rule, value)
        if self.is_enable_hints_disabled():
            self.set_rule(Rule.ENABLE_HINTS, False)
        self.update_opts()

    def update_opts(self):
        self.bind_opts(False)
        self.set_opts()
        self.bind_opts(True)

    def set_opts(self):
        for opt in self.opts:
            opt.checkbox().active = self.get_rule(opt.rule)
            if opt.rule == Rule.ENABLE_HINTS:
                opt.disable(self.is_enable_hints_disabled())

    def is_enable_hints_disabled(self):
        return self.get_rule(Rule.PUNISH_MISSED_SETS) or self.get_rule(Rule.PUNISH_MISSED_EMPTIES)

    def bind_opts(self, activate):
        for opt in self.opts:
            if activate:
                func = partial(self.on_opt_selected, opt.rule)
                opt.checkbox().bind(active=func)
                self.bound_funcs[opt.rule] = func
            else:
                opt.checkbox().unbind(active=self.bound_funcs[opt.rule])

    def get_rule(self, rule):
        return self.app.get_rule(rule, self.game_mode)

    def set_rule(self, rule, value):
        self.app.set_rule(rule, value, self.game_mode)
