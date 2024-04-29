from kivy.app import App
from widgets.game_stats_display import *
from app_roots.sp_game import SPGame


class SetApp(App):
    def build(self):
        self.root = SPGame()
        # return SPGame()

if __name__ == '__main__':
    SetApp().run()