#-*-coding:utf-8-*-

# Import built-in modules
from typing import Self, Any
from os.path import join
from json import load as jsload
from pygame.image import load
from pygame import Surface, Rect

# Import game components
from .constants import MAP as cts

# Create constants of the module
BITMASKS: dict[str, list[int]] = {
    "tl": [0, 3, 1],
    "tr": [2, 1, 4],
    "bl": [5, 6, 3],
    "br": [7, 4, 6]
}
BITMASKS_VARIANTS: dict[str, list[dict[str, tuple[int, int]]]] = {
    "field": [
        {"tl":(0, 0), "tr":(0, 0), "br":(0, 0), "bl":(0, 0)},
        {"tl":(1, 1), "tr":(1, 2), "br":(0, 2), "bl":(0, 1)},
        {"tl":(0, 2), "tr":(0, 1), "br":(1, 1), "bl":(1, 2)},
        {"tl":(1, 0), "tr":(1, 0), "br":(1, 0), "bl":(1, 0)},
        {"tl":(1, 2), "tr":(0, 2), "br":(1, 1), "bl":(0, 1)}
    ],
    "wall": [
        {"tl":(0, 0), "tr":(1, 0), "br":(1, 1), "bl":(0, 1)},
        {"tl":(1, 0), "tr":(1, 1), "br":(0, 1), "bl":(0, 0)},
        {"tl":(0, 1), "tr":(0, 0), "br":(1, 0), "bl":(1, 1)},
        {"tl":(1, 1), "tr":(0, 1), "br":(1, 0), "bl":(0, 0)},
        {"tl":(1, 1), "tr":(0, 1), "br":(1, 0), "bl":(0, 0)}
    ],
    "fall": [
        {"tl":(0, 0), "tr":(0, 1), "br":(0, 1), "bl":(0, 0)},
        {"tl":(0, 1), "tr":(0, 1), "br":(0, 0), "bl":(0, 0)},
        {"tl":(0, 0), "tr":(0, 0), "br":(0, 1), "bl":(0, 1)},
        {"tl":(0, 1), "tr":(0, 0), "br":(0, 0), "bl":(0, 1)},
        {"tl":(0, 1), "tr":(0, 0), "br":(0, 0), "bl":(0, 1)}
    ],
    "unique": [
        {"tl":(0, 0), "tr":(0, 0), "br":(0, 0), "bl":(0, 0)},
        {"tl":(0, 0), "tr":(0, 0), "br":(0, 0), "bl":(0, 0)},
        {"tl":(0, 0), "tr":(0, 0), "br":(0, 0), "bl":(0, 0)},
        {"tl":(0, 0), "tr":(0, 0), "br":(0, 0), "bl":(0, 0)},
        {"tl":(0, 0), "tr":(0, 0), "br":(0, 0), "bl":(0, 0)}
    ]
}
GRAPHICS_FORMATS: dict[str, tuple[int, int]] = {
    "field": (2, 3),
    "wall": (2, 2),
    "fall": (2, 1),
    "unique": (1, 1)
}


# Create the Tile object
class Tile:
    """
    Instance of a Tile object
    """
    def __init__(self: Self, type: str, size: int, hitbox: int, graphics: list[Surface]) -> None:
        self.type: str = type
        self.size = size
        self.hitbox: int = hitbox
        self.graphics: list[Surface] = graphics
    
    def get_tile(self: Self, neighborhood: list[int], frame: int) -> Surface:
        tile = Surface((self.size, self.size), cts.flags)
        
        # Pick correct graphics according to parameters
        for i, corner in enumerate(["tl", "tr", "bl", "br"]):
            # First we calcul the offset of the corner
            offsetx, offsety = (self.size//2) * (i%2), (self.size//2) * (i//2)
            
            #Then we generate a bitmask according to neighborhood
            bitmask = sum([neighborhood[bit]*2**j for j, bit in enumerate(BITMASKS[corner])])
            
            # Then we pick the right corner according to bitmask
            x, y = BITMASKS_VARIANTS[self.type][bitmask//2+int(bitmask==7)][corner]
            corner_graphic = self.graphics[frame].subsurface(Rect(x*self.size+offsetx, y*self.size+offsety, self.size//2, self.size//2))
            
            # Then e blit it on our tile
            tile.blit(corner_graphic, (offsetx, offsety))
            
        # Finally we return the graphic of our tile
        return tile.convert_alpha()
    

# Create the Tileset object
class Tileset:
    """
    Tileset Object
    """
    def __init__(self: Self, name: str) -> None:
        self.name = name
        self.tiles: list[Tile] = []
        self.load_json()
        
    def load_json(self: Self) -> None:
        with open(join(cts.tileset_folder, f"{self.name}.json"), "r") as file:
            data = jsload(file)
            tile_size = data["tile_size"]
            graphics = {filename: load(join(cts.tileset_graphics_folder, self.name, filename)).convert_alpha() for filename in data["files"]}
            for tile_infos in data["tiles"]:
                tile_graphics = []
                for frame in tile_infos["frames"]:
                    x, y = frame[0]*tile_size, frame[1]*tile_size
                    sizex, sizey = GRAPHICS_FORMATS[tile_infos["type"]][0]*tile_size, GRAPHICS_FORMATS[tile_infos["type"]][1]*tile_size
                    tile_graphics.append(graphics[tile_infos["file"]].subsurface(Rect(x, y, sizex, sizey)))
                self.tiles.append(Tile(tile_infos["type"], tile_size, tile_infos["hitbox"], tile_graphics))
            file.close()
            
    def get_tile(self: Self, id: int) -> Tile:
        return self.tiles[id]


# Create Map object
class Map:
    """
    Instance of a Map object
    """
    def __init__(self: Self, name: str) -> None:
        self.name: str = name
        self.size: list[int]
        self.bgm: str
        self.bgs: str
        self.layer_id_range: list[int]
        self.tileset: Tileset
        self.tilemap: dict[int, list[list[Tile]]] = {}
        
        # Load map from json file
        self.load_json()
        
    def load_json(self: Self) -> None:
        with open(join(cts.map_folder, f"{self.name}.json"), "r") as file:
            data = jsload(file)
            self.size = data["size"]
            self.bgm = data["bgm"]
            self.bgs = data["bgs"]
            self.layer_id_range = [data["layer_id_range"][0], data["layer_id_range"][1]+1]
            self.tileset = Tileset(data["tileset"])
            for layer in data["layers"]:
                self.tilemap[layer["id"]] = [
                    [
                        self.tileset.get_tile(layer["tiles"][j][i]) for i in range(self.size[0])
                    ] for j in range(self.size[1])
                ]
            file.close()
            
    def render_layers(self: Self, frame: int, player_pos: tuple[int, int]) -> dict[int, Surface]:
        layers = {}
        
        # Generate The different layers
        for layer_id in range(*self.layer_id_range):
            surface = Surface(cts.size, cts.flags)
        
        return layers