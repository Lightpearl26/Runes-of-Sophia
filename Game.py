#-*-coding:utf-8-*-

# ---------------------------- #
# - Author : Franck Lafiteau - #
# ---------------------------- #

# Import built-in modules
from typing import Self
import pygame as pg

# Initialize Pygame environment
pg.init()
pg.display.init()
pg.mixer.init()

# Import Game Engines
from libs import constants as cts
from libs import Scene
from libs import Event
from libs import Sound

# Create Scenes dictionnary and initialize all scenes
SCENES: dict[str, Scene.BaseScene] = {
    "TitleScreen": Scene.TitleScreen(),
    "Options": Scene.Options(),
    "NewGame": Scene.NewGame(),
    "LoadGame": Scene.LoadGame(),
}

# Create Main GameEngine object
class GameEngine:
    """
    Instance of the main game engine
    """
    def __init__(self: Self) -> None:
        self.screen: pg.Surface = pg.display.set_mode(cts.SCREEN.size, cts.SCREEN.flags)
        self.clock: pg.time.Clock = pg.time.Clock()
        self.scene: str | None = None
        self.event_manager: Event.EventManager = Event.EventManager()
        self.sound_manager: Sound.SoundManager = Sound.SoundManager()
        self.alive: bool = True
        
    def quit(self: Self) -> None:
        self.alive = False
        
    def change_scene(self: Self, new_scene: str | None=None, reinit: bool=True) -> None:
        # First we kill all timer events we created for previous scene
        self.event_manager.kill_timers()
        
        # If no scene is parsed we quit the game
        if not new_scene:
            self.quit()
            return
        
        # If there is a new scene, we initialize it
        self.scene = new_scene
        SCENES[self.scene].game_engine = self
        if reinit:
            SCENES[self.scene].reinit()
            
        # Then we render it one time full
        SCENES[self.scene].update()
        SCENES[self.scene].render()
        pg.display.flip()

    def run(self: Self) -> None:
        while self.alive:
            # We handle the events of pygame
            self.event_manager.handle_events()
            
            # We update our current scene with changes
            updated_rects = SCENES[self.scene].update()
            
            # We update our sound engine
            self.sound_manager.update()
            
            # We render our scene on the screen
            SCENES[self.scene].render()
            
            # We update screen only on modified rects
            pg.display.update(updated_rects)
            
            # We tick our clock
            self.clock.tick(cts.SCREEN.max_fps)
        
        # If we exit our loop then the game has been exited
        pg.quit()
        exit()
        
# Launching the game
if __name__ == "__main__":
    game = GameEngine()
    game.change_scene(new_scene="TitleScreen")
    game.run()