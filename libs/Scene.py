#-*-coding:utf-8-*-

# Import built-in modules
from typing import Self, Any
from pygame import Rect, Surface
from pygame.font import SysFont as font

# Import game components
from .constants import SCENE as cts
from . import Map
from .Transition import FadeIn, FadeOut


# Create base object for all Scenes
class BaseScene:
    """
    Base instance of all scenes of the game
    """
    def __init__(self: Self, game_engine: Any) -> None:
        self.game_engine: Any = game_engine
        self.surface: Surface = Surface(cts.size, cts.flags)
        
    def reinit(self: Self) -> None:
        raise NotImplementedError
    
    def update(self: Self) -> list[Rect] | None:
        if self.game_engine.event_manager.get_event("Quit"):
            self.game_engine.quit()
    
    def render(self: Self) -> None:
        self.game_engine.screen.fill((255, 255, 255))
        self.game_engine.screen.blit(self.surface, (0, 0))
 
   
# Create TitleScreen
class TitleScreen(BaseScene):
    """
    TitleScreen of the game
    """
    def __init__(self: Self, game_engine: Any) -> None:
        # Here we initialize all unchanged attributes
        BaseScene.__init__(self, game_engine)
        self.choices: list[str] = ["Nouvelle Partie", "Continuer", "Options", "Quitter"]
        self.scenes: list[str | None] = ["NewGame", "LoadGame", "Options", None]
        self.title_font = font(None, 48)
        self.text_font = font(None, 32)
        
        # Now we initialize changing attributes
        self.current_choice: int = 0
        self.lock_cursor: bool = False
        
    def reinit(self: Self) -> None:
        self.current_choice = 0
        self.lock_cursor = False
    
    def update(self: Self) -> list[Rect]:
        BaseScene.update(self)
        # get events and make updates of it
        if self.game_engine.event_manager.get_event("Release"):
            self.lock_cursor = False
            self.game_engine.event_manager.kill_timer("UnlockCursor")
            
        if self.game_engine.event_manager.get_event("Pressed") and not self.lock_cursor:
            self.game_engine.event_manager.add_timer("UnlockCursor", 250, repeat=True)
            
        if self.game_engine.event_manager.get_event("UnlockCursor"):
            self.lock_cursor = False
            
        if self.game_engine.event_manager.get_event("MoveUp") and not self.lock_cursor:
            self.lock_cursor = True
            self.current_choice = (self.current_choice - 1) % 4
            
        if self.game_engine.event_manager.get_event("MoveDown") and not self.lock_cursor:
            self.lock_cursor = True
            self.current_choice = (self.current_choice + 1) % 4
        
        if self.game_engine.event_manager.get_event("Action") and not self.lock_cursor:
            if not self.current_choice == 3:
                transition = FadeOut(1000)
                transition.play(self)
            self.game_engine.change_scene(self.scenes[self.current_choice], enter_transition=FadeIn(1000))
            return [Rect(0, 0, *cts.size)]
            
        # make changes to the surface and storing updated rects
        modified_rects: list[Rect] = []
        blits: list[tuple[Surface, Rect]] = []
        title: Surface = self.title_font.render("Runes of Sophia", True, (0, 0, 0))
        title_rect: Rect = title.get_rect(center=(cts.size[0]//2, cts.size[1]//4))
        modified_rects.append(title_rect)
        blits.append((title, title_rect))

        for i, choice in enumerate(self.choices):
            if self.current_choice == i:
                surf: Surface = Surface((cts.size[0]//2, 48), cts.flags)
                surf.fill((155, 255, 55))
                surf_rect: Rect = Rect(cts.size[0]//4, cts.size[1]//2 + i*48, cts.size[0]//2, 48)
                blits.append((surf, surf_rect))
            txt: Surface = self.text_font.render(choice, True, (0, 0, 0))
            txt_rect: Rect = txt.get_rect(center=(cts.size[0]//2, cts.size[1]//2 + 24 + i*48))
            blits.append((txt, txt_rect))

        modified_rects.append(Rect(cts.size[0]//4, cts.size[1]//2, cts.size[0]//2, 128))

        # rendering the surface
        self.surface.fill((255, 255, 255))
        for blit, blit_rect in blits:
            self.surface.blit(blit, blit_rect)

        return modified_rects


# Create Options scene
class Options(BaseScene):
    """
    Instance of Option scene
    
    This scene shows the options of the game
    and give ability to user to change them
    """
    def __init__(self: Self, game_engine: Any) -> None:
        BaseScene.__init__(self, game_engine)

    def reinit(self: Self) -> None:
        pass

    def update(self: Self) -> list[Rect]:
        BaseScene.update(self)
        if self.game_engine.event_manager.get_event("Cancel"):
            self.game_engine.change_scene("TitleScreen", reinit=False)
        self.surface.fill((0, 255, 255))
        return [Rect(0, 0, *cts.size)]


# Create NewGame scene
class NewGame(BaseScene):
    """
    Instance of NewGame scene
    
    This scene trigger when the user wants to create a new save
    """
    def __init__(self: Self, game_engine: Any) -> None:
        BaseScene.__init__(self, game_engine)

    def reinit(self: Self) -> None:
        pass

    def update(self: Self) -> list[Rect]:
        BaseScene.update(self)
        if self.game_engine.event_manager.get_event("Cancel"):
            self.game_engine.change_scene("TitleScreen", reinit=False)
        self.surface.fill((255, 0, 255))
        return [Rect(0, 0, *cts.size)]


# Create LoadGame Scene
class LoadGame(BaseScene):
    """
    Instance of LoadGame scene
    
    This scene gives user possibility to choose a existing save
    if no existing save is found, it create a new save
    """
    def __init__(self: Self, game_engine: Any) -> None:
        BaseScene.__init__(self, game_engine)

    def reinit(self: Self) -> None:
        pass

    def update(self: Self) -> list[Rect]:
        BaseScene.update(self)
        if self.game_engine.event_manager.get_event("Cancel"):
            self.game_engine.change_scene("TitleScreen", reinit=False)
        self.surface.fill((255, 255, 0))
        return [Rect(0, 0, *cts.size)]


# Create OverWorld Scene
class OverWorld(BaseScene):
    """
    Instance of Overworld Scene
    
    Overworld is the scene where the player can walk
    on map and interact with various entities
    """
    def __init__(self: Self, game_engine: Any) -> None:
        BaseScene.__init__(self, game_engine)
        self.map = Map.Map("tests")
        self.frame = 0
        
    def reinit(self: Self) -> None:
        pass
    
    def update(self: Self) -> list[Rect]:
        BaseScene.update(self)
        self.surface.fill((0, 0, 0, 0))
        
        layers = self.map.render_layers(self.frame, (0, 0))
        
        for layer_id in range(*self.map.layer_id_range):
            self.surface.blit(layers[layer_id], (0, 0))
        
        self.frame += 1
        
        return [Rect(0, 0, *cts.size)]
