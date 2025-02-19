#! usr/bin/env python3
#-*- coding: utf-8 -*-

# Import external modules
from typing import Self, Dict, Tuple, Optional, Union
from PIL import Image, ImageTk
from tkinter.messagebox import askyesno
from tkinter.filedialog import askopenfilename, asksaveasfilename
from os.path import basename
import pygame as pg
import tkinter as tk
import json

# import game components
from libs.Map import Map, Tile, Tileset

# Create constants
WIDTH: int = 48*20
HEIGHT: int = 48*11
SCROLL_SPEED: int = 5

# Initialize interfaces
pg.init()
root = tk.Tk()
root.withdraw()


# === Create main object === #
class MapEditor:
    """
    """
    def __init__(self: Self) -> None:
        # Initialize display
        self.screen: pg.Surface = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption("Map Editor")

        # Initialize scrolling
        self.scroll_x: int = 0
        self.scroll_y: int = 0
        self.dragging: Dict[str, Union[bool, Tuple[int, int]]] = {"active": False, "start_pos": (0, 0)}
        self.mouse_held: Dict[str, bool] = {"placing": False, "removing": False}

        # Initialize Map
        self.current_map: Optional[Map] = None
        self.current_layer: int = 0
        
        # Initialize tile picker
        self.current_tile: Optional[Tile] = None
        self.tiles_per_row: int = 4
        self.tiles_images: list = []

        self.tile_picker: tk.Toplevel = tk.Toplevel()
        self.tile_picker.title("Tile picker")

        # Create tile picker widgets
        self.canvas: tk.Canvas = tk.Canvas(self.tile_picker)
        self.scroll_bar: tk.Scrollbar = tk.Scrollbar(self.tile_picker, orient=tk.VERTICAL)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH)
        self.scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)

        # Initialize loop
        self.alive: bool = True

        # Render both displays

        self.render_editor()
        self.render_tile_picker()

    # rendering methods
    def render_editor(self: Self) -> None:
        if self.current_map:
            layers: Dict[int, pg.Surface] = self.current_map.render_layers((0, 0))

            for layer_id, surface in layers.items():
                if layer_id < self.current_layer:
                    filtered_surface: pg.Surface = pg.Surface(surface.get_size(), pg.SRCALPHA)
                    filtered_surface.fill((0, 0, 0, 128))
                    surface.blit(filtered_surface, (0, 0))
                    
                elif layer_id > self.current_layer:
                    surface.set_alpha(128)
                
                self.screen.blit(surface, (-self.scroll_x, -self.scroll_y))

            font: pg.font.Font = pg.font.Font(None, 24)
            text: pg.Surface = font.render(f"Current layer: {self.current_layer}", True, (255, 255, 255))
            self.screen.blit(text, (10, 10))

    def render_tile_picker(self: Self) -> None:
        if self.current_map:
            tile_num: int = len(self.current_map.tileset.tiles)
            tile_size: int = self.current_map.tileset.tiles[0].size
            width: int = self.tiles_per_row * tile_size

            self.tiles_images.clear()

            self.canvas.delete("all")
            self.canvas.config(width=width, height=HEIGHT, scrollregion=(0, 0, width, (tile_num//self.tiles_per_row+1)*tile_size))
            self.scroll_bar.config(command=self.canvas.yview)
            self.canvas.config(yscrollcommand=self.scroll_bar.set)

            for i, tile in enumerate(self.current_map.tileset.tiles):
                # create image
                pg_surface = tile.get_tile([0]*8)
                if self.current_tile and i == self.current_tile.tile_id:
                    surf = pg.Surface((tile_size, tile_size), pg.SRCALPHA)
                    surf.fill((0, 255, 0, 128))
                    pg_surface.blit(surf, (0, 0))
                else:
                    surf = pg.Surface((tile_size, tile_size), pg.SRCALPHA)
                    surf.fill((255, 255, 255, 10))
                    pg_surface.blit(surf, (0, 0))
                array = pg.surfarray.array3d(pg_surface)
                image = Image.fromarray(array.swapaxes(0, 1))
                tk_image = ImageTk.PhotoImage(image)
                self.tiles_images.append(tk_image)

                # calculate image coordinates
                x = (i%self.tiles_per_row)*tile_size
                y = (i//self.tiles_per_row)*tile_size

                # blit image on canvas and create bindings
                img_id = self.canvas.create_image(x, y, anchor="nw", image=tk_image)
                self.canvas.tag_bind(img_id, "<Button-1>", lambda event, t=tile, o=self: o.__setattr__("current_tile", t))
            self.canvas.update()

    # Event handler methods
    def get_tile_pos(self: Self, mouse_pos: Tuple[int, int]) -> Tuple[int, int]:
        if self.current_map:
            tile_size = self.current_map.tileset.tile_size
            return (mouse_pos[0]+self.scroll_x)//tile_size, (mouse_pos[1]+self.scroll_y)//tile_size
        return (0, 0)

    def handle_tile_placement(self: Self, mouse_pos: Tuple[int, int], is_removal: bool=False) -> None:
        if self.current_map:
            x, y = self.get_tile_pos(mouse_pos)
            if 0 <= x < self.current_map.size[0] and 0 <= y < self.current_map.size[1]:
                if is_removal:
                    self.current_map.tilemap[self.current_layer][y][x] = None
                else:
                    self.current_map.tilemap[self.current_layer][y][x] = self.current_tile

    def handle_mouse_drag(self: Self) -> None:
        if self.mouse_held["placing"]:
            self.handle_tile_placement(pg.mouse.get_pos())
        elif self.mouse_held["removing"]:
            self.handle_tile_placement(pg.mouse.get_pos(), is_removal=True)

    def handle_drag(self: Self, event: pg.event.Event) -> None:
        if self.current_map:
            tile_size = self.current_map.tileset.tile_size
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 2:
                self.dragging["active"] = True
                self.dragging["start_pos"] = event.pos
            elif event.type == pg.MOUSEBUTTONUP and event.button == 2:
                self.dragging["active"] = False
            elif event.type == pg.MOUSEMOTION and self.dragging["active"]:
                dx, dy = event.pos[0]-self.dragging["start_pos"][0], event.pos[1]-self.dragging["start_pos"][1] # type: ignore
                self.scroll_x = max(0, min(self.current_map.size[0]*tile_size-WIDTH, self.scroll_x-dx))
                self.scroll_y = max(0, min(self.current_map.size[1]*tile_size-HEIGHT, self.scroll_y-dy))
                self.dragging["start_pos"] = event.pos

    # Map managing methods
    def create_new_map(self: Self) -> None:
        pass

    def save_map(self: Self) -> None:
        if self.current_map:
            file_path = asksaveasfilename(defaultextension=".json", filetypes=[("Map Files", "*.json")])
        
            if file_path:
                map_data = {
                    "name": self.current_map.name,
                    "size": self.current_map.size,
                    "bgm": "",
                    "bgs": "",
                    "layer_id_range": self.current_map.layer_id_range,
                    "tileset": self.current_map.tileset.name,
                    "layers": []
                }
                
                for layer_id, tiles in self.current_map.tilemap.items():
                    layer_data = {
                        "id": layer_id,
                        "tiles": [[tile.tile_id if tile else -1 for tile in row] for row in tiles]
                    }
                    map_data["layers"].append(layer_data)

                with open(file_path, 'w') as file:
                    json.dump(map_data, file)

    def load_map(self: Self) -> None:
        file_path = askopenfilename(defaultextension=".json", filetypes=[("Map Files", "*.json")])
    
        if file_path:
            self.current_map = Map(basename(file_path)[:-5])

    # Main loop
    def run(self: Self) -> None:
        while self.alive:
            self.screen.fill((255, 255, 255))
            self.render_editor()
            self.render_tile_picker()

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.alive = False

                elif event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.mouse_held["placing"] = True
                        self.handle_tile_placement(event.pos)
                    elif event.button == 3:
                        self.mouse_held["removing"] = True
                        self.handle_tile_placement(event.pos, is_removal=True)

                elif event.type == pg.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.mouse_held["placing"] = False
                    elif event.button == 3:
                        self.mouse_held["removing"] = False

                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_UP:
                        if self.current_map:
                            if self.current_layer < self.current_map.layer_id_range[-1]-1:
                                self.current_layer += 1
                            else:
                                answer = askyesno("New Layer", f"Do you want to create a new layer above layer {self.current_layer} ?")
                                if answer:
                                    self.current_layer += 1
                                    self.current_map.layer_id_range[-1] += 1
                                    self.current_map.tilemap[self.current_layer] = [[None for _ in range(self.current_map.size[0])] for _ in range(self.current_map.size[1])]

                    elif event.key == pg.K_DOWN:
                        if self.current_map:
                            if self.current_layer > self.current_map.layer_id_range[0]:
                                self.current_layer -= 1
                            else:
                                answer = askyesno("New Layer", f"Do you want to create a new layer under layer {self.current_layer} ?")
                                if answer:
                                    self.current_layer -= 1
                                    self.current_map.layer_id_range[0] -= 1
                                    self.current_map.tilemap[self.current_layer] = [[None for _ in range(self.current_map.size[0])] for _ in range(self.current_map.size[1])]

                    elif event.key == pg.K_o:
                        self.load_map()

                    elif event.key == pg.K_s:
                        self.save_map()

                    elif event.key == pg.K_n:
                        self.create_new_map()

                self.handle_drag(event)

            self.handle_mouse_drag()

            pg.display.flip()
            self.tile_picker.update()

# Launch the script
if __name__ == "__main__":
    editor = MapEditor()
    editor.run()
    pg.quit()
