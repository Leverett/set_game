from kivy.app import App
import os
import sys
import subprocess
import atexit
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from app_roots.home import HomeScreen
from app_roots.sp_game import SPGame
from app_roots.mp_game import MPGame
from game.globals import *
from game.game_objects import Rules, Identity, GameMode, Rule
import requests

class RootWidget(BoxLayout):
    pass

class SetApp(App):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.identity = Identity(default_id, default_name)
        
    def update_config(self):
        self.config.write()

    def get_config(self):
        return self.config

    def build(self):
        self.config.read(os.path.join(self.user_data_dir, CONFIG_FILE))
        self.config.setdefaults(GameMode.SINGLE_PLAYER, Rules.default_rules().to_dict())
        self.config.setdefaults(GameMode.MULTI_PLAYER, Rules.default_rules().to_dict())
        self.config.setdefaults("Identity", self.identity.to_dict())
        self.config.write()
        root = RootWidget()
        root.add_widget(HomeScreen())
        connected = False #self.send_request_to_flask()
        if not connected:
            self.start_local_host()
            self.send_request_to_flask()
        return root
    
    def start_local_host(self):
        print("Starting local host")
        python_interpreter = sys.executable
        self.host_instance = subprocess.Popen([python_interpreter, os.path.join(os.getcwd(), 'host', 'main.py')])
        # self.host_instance = subprocess.Popen([python_interpreter, os.path.join(os.getcwd(), 'host', 'local_main.py')])
        atexit.register(self.host_instance.terminate)

    def send_request_to_flask(self) -> bool:
        print("Sending ping")
        try:
            response = requests.get(get_url('ping'))
            if response.status_code == 200:
                print("Received ping")
                return True
        except requests.exceptions.ConnectionError:
            pass
        print("Failed to connect to Flask server.")
        return False
    
    def switch_root(self, new_root: Widget):
        self.root.clear_widgets()
        self.root.add_widget(new_root)

    def get_rule(self, rule, game_mode):
        return self.config[game_mode][rule].lower() in ['true', 'yes', '1']

    def set_rule(self, rule: Rule, value, game_mode: GameMode):
        self.config.set(game_mode, rule, value)
        self.config.write()

    def make_rules(self, game_mode:GameMode) -> Rules:
        return Rules(self.get_rule(Rule.PUNISH_MISSED_SETS, game_mode),
                     self.get_rule(Rule.PUNISH_MISSED_EMPTIES, game_mode),
                     self.get_rule(Rule.ENABLE_HINTS, game_mode),
                     self.get_rule(Rule.ENDLESS_MODE, game_mode))

    # TODO this seems to maintain game state after quitting
    def start_game(self, game_mode: GameMode):
        rules = self.make_rules(game_mode)
        self.switch_root(SPGame(rules))

    def go_home(self):
        self.switch_root(HomeScreen())

    def stop_host(self):
        self.host_instance.terminate()
        # requests.get('http://127.0.0.1:5000/shutdown')
        # self.host_instance.wait()

    def start_mp(self):
        self.switch_root(MPGame())


if __name__ == '__main__':
    SetApp().run()