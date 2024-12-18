#-*-coding:utf-8-*-

# Import built-in modules
from typing import Self
from pygame.mixer_music import load, play, get_busy, set_volume
from pygame.mixer import Sound

# Create the Sound Manager
class SoundManager:
    """
    This object handle any music or soundeffect of our game
    """
    def __init__(self: Self) -> None:
        self.current_music: dict[str, str] | None = None
        self.next_music: dict[str, str] | None = None
        self.music_phase: str | None = None
        self.ask_music_end: bool = False
        self.sfx: dict[str, Sound] = {}

    def play_music(self: Self, music: dict[str, str]) -> None:
        self.next_music = music
        self.ask_music_end = True

    def switch_to_next_music(self: Self) -> None:
        if self.next_music:
            self.current_music = self.next_music
            self.next_music = None
            self.play_header()

    def play_header(self: Self) -> None:
        if self.current_music["header"]:
            load(self.current_music["header"])
            play()
            self.music_phase = "header"
        else:
            self.play_loop()

    def play_loop(self: Self) -> None:
        load(self.current_music["loop"])
        play()
        self.music_phase = "loop"

    def play_queue(self: Self) -> None:
        if self.current_music["queue"]:
            load(self.current_music["queue"])
            play(fade_ms=1000)
            self.music_phase = "queue"
        else:
            self.switch_to_next_music()

    def update(self: Self) -> None:
        if not get_busy():
            if self.current_music:
                if self.music_phase == "header":
                    self.play_loop()
                elif self.music_phase == "loop":
                    if self.ask_music_end:
                        self.play_queue()
                        self.ask_music_end = False
                    else:
                        self.play_loop()
                elif self.music_phase == "queue":
                    self.switch_to_next_music()
            else:
                self.switch_to_next_music()

    def load_sfx(self: Self, name: str, file_path: str) -> None:
        self.sfx[name] = Sound(file_path)

    def play_sfx(self: Self, name: str) -> None:
        if name in self.sfx:
            self.sfx[name].play()

    def set_music_volume(self: Self, volume: int) -> None:
        set_volume(volume)

    def set_sfx_volume(self: Self, volume: int) -> None:
        for name in self.sfx.keys():
            self.sfx[name].set_volume(volume)

    def stop_music(self: Self) -> None:
        self.ask_music_end = True
