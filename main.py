from kivy.app import App
import os
from widgets.game_stats_display import *
from app_roots.home import HomeScreen, SPGame

class RootWidget(BoxLayout):
    pass

class SetApp(App):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def update_config(self):
        self.config.write()

    def get_config(self):
        return self.config

    def build(self):
        self.config.read(os.path.join(self.user_data_dir, CONFIG_FILE))
        self.config.setdefaults(CONFIG_SP_RULES, Rules.default_rules().to_dict())
        self.config.setdefaults(CONFIG_MP_RULES, Rules.default_rules().to_dict())
        self.config.write()
        root = RootWidget()
        root.add_widget(HomeScreen())
        return root
    
    def switch_root(self, new_root):
        self.root.clear_widgets()
        self.root.add_widget(new_root)

    def get_rule(self, rule, game_mode):
        return self.config[game_mode][rule].lower() in ['true', 'yes', '1']

    def set_rule(self, rule, value, game_mode):
        self.config.set(game_mode, rule, value)
        self.config.write()

    def make_rules(self, game_mode):
        return Rules(self.get_rule(PUNISH_MISSED_SETS, game_mode),
                     self.get_rule(PUNISH_MISSED_EMPTIES, game_mode),
                     self.get_rule(ENABLE_HINTS, game_mode),
                     self.get_rule(ENDLESS_MODE, game_mode))

    def start_game(self, game_mode):
        rules = self.make_rules(game_mode)
        self.switch_root(SPGame(rules))

    def go_home(self):
        self.switch_root(HomeScreen())



if __name__ == '__main__':
    SetApp().run()