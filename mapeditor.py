import pygame
from pygame.locals import * # type: ignore
import tkinter as tk
from tkinter import Canvas, filedialog
from tkinter.messagebox import askyesno
from PIL import Image, ImageTk
from libs.Map import Map, Tile
from typing import Optional
import json

# === Initialize Pygame and Tkinter ===
pygame.init()
root = tk.Tk()
root.withdraw()  # Hide the root Tkinter window (for file dialogs)

# === Pygame Screen Setup ===
WIDTH, HEIGHT = 48*21, 48*17
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Map Editor")

# === Load Initial Map ===
my_map: Map = Map("blank")

# === Editor Variables ===
scroll_offset = 0  # Scroll offset for tile selection
scroll_x, scroll_y = 0, 0  # Map scrolling
scroll_speed = 5
viewport_width = WIDTH
viewport_height = HEIGHT
current_layer_id = 0  # Start on the first valid layer
selected_tile: Optional[Tile] = my_map.tileset.get_tile(0) if my_map else None
dragging = {"active": False, "start_pos": (0, 0)}

# === Tkinter Tile Picker Window ===
tile_images = []
tile_size = my_map.tileset.tile_size
tiles_per_row = 5  # Number of tiles per row in picker

picker_width = tiles_per_row * tile_size
picker_height = ((len(my_map.tileset.tiles) // tiles_per_row) + 1) * tile_size

tile_picker = tk.Toplevel()  # Create an independent Tkinter window
tile_picker.title("Tile Picker")
tile_picker.geometry(f"{picker_width}x{picker_height}")

canvas = Canvas(tile_picker, width=picker_width, height=picker_height)
canvas.pack()

def update_tile_picker():
    """Refreshes the tile picker when switching tilesets."""
    global tile_images, my_map, selected_tile

    # Clear previous content
    canvas.delete("all")
    tile_images.clear()

    tileset = my_map.tileset
    tile_size = tileset.tile_size
    picker_width = tiles_per_row * tile_size
    picker_height = ((len(tileset.tiles) // tiles_per_row) + 1) * tile_size

    tile_picker.geometry(f"{picker_width}x{picker_height}")
    canvas.config(width=picker_width, height=picker_height)

    for i, tile in enumerate(tileset.tiles):
        pygame_surface = tile.get_tile([0] * 8)
        image = pygame.surfarray.array3d(pygame_surface)
        image = Image.fromarray(image.swapaxes(0, 1))
        tk_image = ImageTk.PhotoImage(image)
        tile_images.append(tk_image)

        x = (i % tiles_per_row) * tile_size
        y = (i // tiles_per_row) * tile_size

        def select_tile(event, t=tile):
            """Handles tile selection from the picker."""
            global selected_tile
            selected_tile = t
            print(f"Selected tile: {selected_tile}")

        # Draw the tile image
        img_id = canvas.create_image(x, y, anchor="nw", image=tk_image)

        # Create a transparent clickable rectangle
        rect_id = canvas.create_rectangle(x, y, x + tile_size, y + tile_size, outline="black")

        # Bind the correct selection function to BOTH elements
        canvas.tag_bind(img_id, "<Button-1>", lambda event, t=tile: select_tile(event, t))
        canvas.tag_bind(rect_id, "<Button-1>", lambda event, t=tile: select_tile(event, t))

# Initialize tile picker
update_tile_picker()

# === Mouse State Tracking for Continuous Placement ===
mouse_held = {"placing": False, "removing": False}

def handle_tile_placement(mouse_pos, is_removal=False):
    """Handles continuous tile placement and removal."""
    x, y = get_tile_pos(mouse_pos)
    if 0 <= x < my_map.size[0] and 0 <= y < my_map.size[1]:
        if is_removal:
            my_map.tilemap[current_layer_id][y][x] = None
        else:
            my_map.tilemap[current_layer_id][y][x] = selected_tile

def handle_mouse_drag():
    """Handles tile placement while dragging the mouse."""
    if mouse_held["placing"]:
        handle_tile_placement(pygame.mouse.get_pos(), is_removal=False)
    elif mouse_held["removing"]:
        handle_tile_placement(pygame.mouse.get_pos(), is_removal=True)

# === Editor Functions ===
def display_tile_selection(tiles):
    """Display the tile selection panel (deprecated due to Tkinter picker)."""
    pass  # No longer needed as we use a separate Tkinter window

def get_tile_pos(mouse_pos):
    """Convert mouse position to tile grid coordinates."""
    x, y = (mouse_pos[0] + scroll_x) // tile_size, (mouse_pos[1] + scroll_y) // tile_size
    return x, y

def handle_drag(event):
    """Handles map dragging with middle mouse button."""
    global scroll_x, scroll_y
    if event.type == MOUSEBUTTONDOWN and event.button == 2:
        dragging["active"] = True
        dragging["start_pos"] = event.pos
    elif event.type == MOUSEBUTTONUP and event.button == 2:
        dragging["active"] = False
    elif event.type == MOUSEMOTION and dragging["active"]:
        dx, dy = event.pos[0] - dragging["start_pos"][0], event.pos[1] - dragging["start_pos"][1]
        scroll_x = max(0, min(my_map.size[0] * tile_size - viewport_width, scroll_x - dx))
        scroll_y = max(0, min(my_map.size[1] * tile_size - viewport_height, scroll_y - dy))
        dragging["start_pos"] = event.pos
                        
def draw_map():
    global current_layer_id, my_map
    # Get the rendered layers dictionary from map_obj
    layers = my_map.render_layers((0, 0))
    
    for layer_id, surface in layers.items():
        # If it's the focused layer, render normally
        if layer_id < current_layer_id:
            # Apply a black alpha filter to non-focused layers
            filtered_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            filtered_surface.fill((0, 0, 0, 128))  # Transparent black filter

            # Apply the filter to the tile graphics
            surface.blit(filtered_surface, (0, 0))
            screen.blit(surface, (-scroll_x, -scroll_y))
        elif layer_id == current_layer_id:
            screen.blit(surface, (-scroll_x, -scroll_y))
        else:
            surface.set_alpha(128)
            screen.blit(surface, (-scroll_x, -scroll_y))

# Function to create a new map
def create_new_map():
    global my_map, current_layer_id, num_layers
    # Prompt user for map dimensions
    name = input("Enter map name: ")
    width = int(input("Enter map width: "))
    height = int(input("Enter map height: "))
    start_layer = int(input("Enter start id for layers: "))
    num_layers = int(input("Enter number of layers: "))
    
    map_data = {
        "name": name,
        "size": [width, height],
        "bgm": "",
        "bgs": "",
        "layer_id_range": [start_layer, start_layer+num_layers+1],
        "tileset": "Outside",
        "layers": [{"id": layer_id, "tiles":[[-1]*width]*height} for layer_id in range(start_layer, start_layer+num_layers+1)]
    }
    with open(f"Data\\Maps\\{name}.json", 'w') as file:
        json.dump(map_data, file, indent=4)  # Save the map data to the JSON file
    my_map = Map(name)
    current_layer_id = 0  # Start with the first layer
    print(f"New map created: {width}x{height}, {num_layers} layers.")

# Function to load a map from file
def load_map():
    global my_map, current_layer_id, num_layers
    file_path = filedialog.askopenfilename(defaultextension=".json", filetypes=[("Map Files", "*.json")])
    
    if file_path:
        my_map = Map(file_path[:-5])

# Function to save the current map to file
def save_map():
    file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("Map Files", "*.json")])
    
    if file_path:
        map_data = {
            "name": my_map.name,
            "size": my_map.size,
            "bgm": "",
            "bgs": "",
            "layer_id_range": my_map.layer_id_range,
            "tileset": my_map.tileset.name,
            "layers": []
        }

        # Prepare layers data
        for layer_id, tiles in my_map.tilemap.items():
            layer_data = {
                "id": layer_id,
                "tiles": [[tile.tile_id if tile else -1 for tile in row] for row in tiles]
            }
            map_data["layers"].append(layer_data)

        with open(file_path, 'w') as file:
            json.dump(map_data, file)  # Save the map data to the JSON file
            print(f"Map saved to {file_path}")

def draw_layer_info():
    """Displays the current active layer at the top of the screen."""
    font = pygame.font.Font(None, 24)
    text = font.render(f"Current Layer: {current_layer_id}", True, (255, 255, 255))
    screen.blit(text, (10, 10))  # Position near tile panel

# === Main Loop ===
running = True
while running:
    screen.fill((255, 255, 255))
    draw_map()
    draw_layer_info()

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 1:  # Left-click (start placing tiles)
                mouse_held["placing"] = True
                handle_tile_placement(event.pos)
            elif event.button == 3:  # Right-click (start removing tiles)
                mouse_held["removing"] = True
                handle_tile_placement(event.pos, is_removal=True)
        elif event.type == MOUSEBUTTONUP:
            if event.button == 1:  # Left button released
                mouse_held["placing"] = False
            elif event.button == 3:  # Right button released
                mouse_held["removing"] = False
        elif event.type == KEYDOWN:
            if event.key == K_UP:  # Move up to the next layer within valid range
                if current_layer_id < my_map.layer_id_range[-1]-1:
                    current_layer_id += 1
                else:
                    answer = askyesno("new layer", f"Do you want to create a new layer above layer {current_layer_id} ?")
                    if answer:
                        current_layer_id += 1
                        my_map.layer_id_range[-1] += 1
                        my_map.tilemap[current_layer_id] = [[None for _ in range(my_map.size[0])] for _ in range(my_map.size[1])]
            elif event.key == K_DOWN:  # Move down to the previous layer within valid range
                if current_layer_id > my_map.layer_id_range[0]:
                    current_layer_id -= 1
                else:
                    answer = askyesno("new layer", f"Do you want to create a new layer under layer {current_layer_id} ?")
                    if answer:
                        current_layer_id -= 1
                        my_map.layer_id_range[0] -= 1
                        my_map.tilemap[current_layer_id] = [[None]*my_map.size[0]]*my_map.size[1]
            elif event.key == K_n:
                create_new_map()
            elif event.key == K_o:
                load_map()
            elif event.key == K_s:
                save_map()

        handle_drag(event)
        
    handle_mouse_drag()

    pygame.display.flip()
    tile_picker.update()  # Keep Tkinter running

pygame.quit()