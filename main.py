from kivy.app import App
import os
from widgets.game_stats_display import *
from app_roots.home import HomeScreen

class RootWidget(BoxLayout):
    pass

class SetApp(App):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def update_config(self):
        print("update_config")
        self.config.write()

    def get_config(self):
        print("get_config")
        return self.config

    def build(self):
        self.config.read(os.path.join(self.user_data_dir, CONFIG_FILE))
        self.config.setdefaults(CONFIG_SP_RULES, Rules.default_rules().to_dict())
        self.config.setdefaults(CONFIG_MP_RULES, Rules.default_rules().to_dict())
        self.config.write()
        root = RootWidget()
        root.add_widget(HomeScreen())
        return root
    
    def switch_root(self, new_root, **kwargs):
        self.root.clear_widgets()
        self.root.add_widget(new_root)



if __name__ == '__main__':
    SetApp().run()