#-*-coding: utf-8-*-

# Import built-in modules
from typing import Self
from pygame.display import flip
from pygame.time import get_ticks
from pygame import Surface, SRCALPHA, quit

# Import game components
from .constants import TRANSITION as cts


# Create Base objects for all transitions
class Transition:
    """
    This object is the base objects of all transitions
    
    It does nothing as transition its only a structure object
    """
    def __init__(self: Self) -> None:
        pass
    
    def play(self, scene) -> None:
        pass
    

# Create Fade-out transition
class FadeOut(Transition):
    """
    FadeOut transition
    """
    def __init__(self: Self, duration: int) -> None:
        Transition.__init__(self)
        self.duration: int = duration
        
    def play(self, scene) -> None:
        clock = scene.game_engine.clock
        start_time = get_ticks()
        alpha = 0
        
        while alpha < 255:
            scene.game_engine.event_manager.handle_events()
            if scene.game_engine.event_manager.get_event("Quit"):
                quit()
                exit()

            elapsed = get_ticks() - start_time
            alpha = int(min(255, (elapsed / self.duration) * 255))

            scene.render()
            fade_surface = Surface(scene.game_engine.screen.get_size(), SRCALPHA)
            fade_surface.fill((0, 0, 0, alpha))
            scene.game_engine.screen.blit(fade_surface, (0, 0))
            flip()
            clock.tick(cts.max_fps)


# Create Fade-in transition
class FadeIn(Transition):
    """
    FadeIn transition
    """
    def __init__(self: Self, duration: int) -> None:
        Transition.__init__(self)
        self.duration: int = duration
        
    def play(self, scene) -> None:
        clock = scene.game_engine.clock
        start_time = get_ticks()
        alpha = 255
        
        while alpha > 0:
            scene.game_engine.event_manager.handle_events()
            if scene.game_engine.event_manager.get_event("Quit"):
                quit()
                exit()
            
            elapsed = get_ticks() - start_time
            alpha = int(max(0, (1 - elapsed / self.duration) * 255))

            scene.render()
            fade_surface = Surface(scene.game_engine.screen.get_size(), SRCALPHA)
            fade_surface.fill((0, 0, 0, alpha))
            scene.game_engine.screen.blit(fade_surface, (0, 0))
            flip()
            clock.tick(cts.max_fps)