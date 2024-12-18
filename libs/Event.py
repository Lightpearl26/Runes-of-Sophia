#-*-coding:utf-8-*-

# Import built-in modules
from typing import Self
from pygame.locals import QUIT, KEYDOWN, KEYUP, K_F4, KMOD_ALT
from pygame.event import get as getevents
from pygame.time import get_ticks
from os.path import exists
from json import load, dump

# Import game components
from .constants import EVENTS as cts

# Create the Event Manager
class EventManager:
    """
    This object handle all pygame events and translate them to something
    our game can understand
    """
    def __init__(self: Self) -> None:
        self.event_map: dict[str, list[int]] = {}
        self.events: dict[str, bool] = {event:False for event in cts.default_events}
        self.timers: dict[str, list[int | bool]] = {}
        self.load_controls()
        
    def load_controls(self: Self) -> None:
        if exists(cts.config_path):
            # We have a custom config stored
            with open(cts.config_path, 'r') as file:
                self.event_map = load(file)
        else:
            # No custom config stored, create a new one
            self.event_map = {
                "Action": cts.default_action,
                "Cancel": cts.default_cancel,
                "MoveUp": cts.default_move_up,
                "MoveDown": cts.default_move_down,
                "MoveLeft": cts.default_move_left,
                "MoveRight": cts.default_move_right,
            }
            self.save_controls()
            
    def save_controls(self: Self) -> None:
        with open(cts.config_path, "w") as file:
            dump(self.event_map, file, indent=4, sort_keys=True)
            
    def add_event(self: Self, name: str) -> None:
        self.events[name] = False
        
    def remove_event(self: Self, name: str) -> None:
        self.events.pop(name, None)
        
    def add_timer(self: Self, name: str, duration: int, repeat: bool=False) -> None:
        self.add_event(name)
        self.timers[name] = [get_ticks(), duration, repeat]
        
    def kill_timer(self: Self, name: str) -> None:
        self.remove_event(name)
        self.timers.pop(name, None)
        
    def kill_timers(self: Self) -> None:
        for timer_name in list(self.timers.keys()):
            self.kill_timer(timer_name)
            
    def update_event(self: Self, event_name: str, keys: list[int]) -> None:
        self.event_map[event_name] = keys
        self.save_controls()
        
    def get_event(self: Self, name: str) -> bool:
        return self.events.get(name, False)
    
    def handle_events(self: Self) -> None:
        # We reset all events except keyboard events
        for event in set(self.events) - set(self.event_map):
            self.events[event] = False
            
        # We handle pygame events
        for event in getevents():
            if event.type == QUIT:
                self.events["Quit"] = True
            elif event.type == KEYDOWN and event.key == K_F4 and event.mod == KMOD_ALT:
                self.events["Quit"] = True
            elif event.type == KEYDOWN:
                self.events["Pressed"] = True
                for name, keys in self.event_map.items():
                    if event.key in keys:
                        self.events[name] = True
            elif event.type == KEYUP:
                self.events["Release"] = True
                for name, keys in self.event_map.items():
                    if event.key in keys:
                        self.events[name] = False
            else:
                pass
            
        # We handle custom timer events
        current_time: int = get_ticks()
        for name in list(self.timers.keys()):
            if current_time - self.timers[name][0] >= self.timers[name][1]:
                self.events[name] = True
                if self.timers[name][2]:
                    self.timers[name][0] = current_time
                else:
                    self.kill_timer(name)
