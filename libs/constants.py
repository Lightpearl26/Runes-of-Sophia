#-*-coding:utf-8-*-

# import built-in modules
import pygame.locals as pgcts
from os.path import join

# Create constants
class SCREEN:
    size: tuple[int, int]=(32*48, 18*48)
    flags: int = pgcts.FULLSCREEN | pgcts.SCALED
    max_fps: int = 60
    
class SCENE:
    size: tuple[int, int] = (32*48, 18*48)
    flags: int = pgcts.SRCALPHA
    max_fps: int = 60

class EVENTS:
    config_path: str = join("Data", "controls.json")
    default_action: list[int] = [pgcts.K_a, pgcts.K_RETURN]
    default_cancel: list[int] = [pgcts.K_c, pgcts.K_ESCAPE]
    default_move_up: list[int] = [pgcts.K_z, pgcts.K_UP]
    default_move_down: list[int] = [pgcts.K_s, pgcts.K_DOWN]
    default_move_left: list[int] = [pgcts.K_q, pgcts.K_LEFT]
    default_move_right: list[int] = [pgcts.K_d, pgcts.K_RIGHT]
    default_events: list[str] = ["Action", "Cancel", "MoveUp", "MoveDown", "MoveLeft", "MoveRight", "Quit", "Pressed", "Release"]

class MAP:
    flags: int = pgcts.SRCALPHA
    map_folder: str = join("Data", "Maps")
    tileset_folder: str = join("Data", "Tilesets")
    tileset_graphics_folder: str = join("Assets", "Graphics", "Tilesets")
    
class TRANSITION:
    max_fps: int = 60