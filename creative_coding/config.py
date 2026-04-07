import sys
import math
import random
from datetime import datetime
import pygame

# =========================================================
# --- CONFIGURATION & CONSTANTS ---
# =========================================================
WIDTH, HEIGHT = 1400, 900
BG_COLOR = (12, 38, 86) 
GRID_MINOR_COLOR = (25, 65, 125)
GRID_MAJOR_COLOR = (45, 90, 160)
TECHNICAL_LINE_COLOR = (180, 240, 255)

# Texture intensity (0 to 255). Lower = fainter/subtle.
TEXTURE_ALPHA = 160

# Blueprint colors
BLUEPRINT_WHITE = (255, 255, 255)
ROOM_COLOR = BLUEPRINT_WHITE
CORRIDOR_COLOR = BLUEPRINT_WHITE
AIRLOCK_COLOR = BLUEPRINT_WHITE
TEXT_COLOR = BLUEPRINT_WHITE

# Style controls (1 = thin, 2 = standard, 3+ = bold)
LINE_WEIGHT = 2 

# Shading & Topography
SHADOW_COLOR = (4, 15, 35, 160)   
CRATER_SHADOW = (2, 8, 20, 20)    
TOPO_LINE_COLOR = (80, 150, 190) 
TOPO_TEXT_COLOR = TECHNICAL_LINE_COLOR
GLOBAL_SHIFT_X = -3500

# Initialize Pygame and Fonts
pygame.init()
font_notes = pygame.font.SysFont("Consolas", 12)
font_dim = pygame.font.SysFont("Consolas", 10)
font_base = pygame.font.SysFont("Verdana", 76, bold=True) 
ui_font_large = pygame.font.SysFont("Verdana", 16, bold=True)
ui_font_small = pygame.font.SysFont("Verdana", 10)
font_topo = pygame.font.SysFont("Verdana", 10, bold=False)


# =========================================================
# --- LAYOUT DATA ---
# =========================================================
ROOMS = [
    # --- FAR NORTH SECTOR (Landing Strip & Upper Processing) ---
    {"name": "Landing Strip", "type": "rect", "x": -2062, "y": 6625, "w": 468, "h": 848, "rotation": 0},
    {"name": "Airlock", "x": -461, "y": 6830, "w": 96, "h": 88, "rotation": 0, "type": "airlock"},
    {"name": "Airlock", "x": 801, "y": 6830, "w": 96, "h": 88, "rotation": 0, "type": "airlock"},
    {"name": "Airlock", "x": 2568, "y": 6830, "w": 96, "h": 88, "rotation": 0, "type": "airlock"},
    {"name": "Corridor", "type": "corridor", "x": -411, "y": 6850, "w": 1212, "h": 48, "rotation": 0},
    {"name": "Corridor", "type": "corridor", "x": 897, "y": 6850, "w": 1670, "h": 48, "rotation": 0},
    {"name": "Corridor", "type": "corridor", "x": 2640, "y": 6918, "w": 1119, "h": 48, "rotation": -90},
    {"name": "Corridor", "type": "corridor", "x": -389, "y": 6934, "w": 647, "h": 48, "rotation": -90},
    {"name": "Corridor", "type": "corridor", "x": -1846, "y": 7472, "w": 97, "h": 48, "rotation": -90},
    {"name": "Processing-1", "type": "chamfered", "x": -1506, "y": 7517, "w": 410, "h": 219, "rotation": 0},
    {"name": "Airlock", "x": -1924, "y": 7569, "w": 96, "h": 88, "rotation": 0, "type": "airlock"},
    {"name": "Airlock", "x": -461, "y": 7581, "w": 96, "h": 88, "rotation": 0, "type": "airlock"},
    {"name": "Corridor", "type": "corridor", "x": -1828, "y": 7584, "w": 322, "h": 48, "rotation": 0},
    {"name": "Corridor", "type": "corridor", "x": -387, "y": 7660, "w": 647, "h": 48, "rotation": -90},
    {"name": "Corridor", "type": "corridor", "x": -1277, "y": 7736, "w": 176, "h": 48, "rotation": -90},
    {"name": "Processing-2", "type": "chamfered", "x": -1506, "y": 7912, "w": 410, "h": 219, "rotation": 0},
    {"name": "Airlock", "x": -1876, "y": 7978, "w": 96, "h": 88, "rotation": 0, "type": "airlock"},
    {"name": "Airlock", "x": -774, "y": 7978, "w": 96, "h": 88, "rotation": 0, "type": "airlock"},
    {"name": "Corridor", "type": "corridor", "x": -1852, "y": 7998, "w": 346, "h": 48, "rotation": 0},
    {"name": "Corridor", "type": "corridor", "x": -1096, "y": 7998, "w": 346, "h": 48, "rotation": 0},

    # --- NORTH SECTOR (Embarkation Hub, Rainforest Dome & Sky Bridge) ---
    {"name": "Airlock", "x": 2567, "y": 8037, "w": 96, "h": 88, "rotation": 0, "type": "airlock"},
    {"name": "Corridor", "type": "corridor", "x": -1804, "y": 8066, "w": 241, "h": 48, "rotation": -90},
    {"name": "Corridor", "type": "corridor", "x": -702, "y": 8066, "w": 241, "h": 48, "rotation": -90},
    {"name": "Corridor", "type": "corridor", "x": 2631, "y": 8123, "w": 186, "h": 48, "rotation": -90},
    {"name": "Rainforest Dome", "type": "dome", "x": -4146, "y": 8172, "w": 864, "h": 864, "rotation": 0},
    {"name": "Construction Zone", "type": "zone", "x": 2515, "y": 8306, "w": 700, "h": 462, "rotation": 0},
    {"name": "Embarkation Hub", "type": "capsule", "x": -2153, "y": 8307, "w": 1883, "h": 305, "rotation": 0},
    {"name": "Elevator", "type": "diamond", "x": 8900, "y": 8371, "w": 400, "h": 400, "rotation": 0},
    {"name": "Airlock", "x": -2780, "y": 8416, "w": 96, "h": 88, "rotation": 0, "type": "airlock"},
    {"name": "Corridor", "type": "corridor", "x": -3306, "y": 8436, "w": 526, "h": 48, "rotation": 0},
    {"name": "Corridor", "type": "corridor", "x": -2679, "y": 8436, "w": 526, "h": 48, "rotation": 0},
    {"name": "Corridor", "type": "corridor", "x": 3195, "y": 8513, "w": 196, "h": 48, "rotation": 0},
    {"name": "Sky Bridge", "type": "corridor", "x": 3390, "y": 8513, "w": 5560, "h": 48, "rotation": 0},
    {"name": "Airlock", "x": 3360, "y": 8580, "w": 96, "h": 88, "rotation": 90, "type": "airlock"},
    {"name": "Corridor", "type": "corridor", "x": -610, "y": 8604, "w": 664, "h": 48, "rotation": -90},
    {"name": "Corridor", "type": "corridor", "x": -3330, "y": 8612, "w": 280, "h": 48, "rotation": -90},
    {"name": "Corridor", "type": "corridor", "x": -4047, "y": 8749, "w": 664, "h": 48, "rotation": -90},
    {"name": "Corridor", "type": "corridor", "x": 2640, "y": 8770, "w": 176, "h": 48, "rotation": -90},
    {"name": "Corridor", "type": "corridor", "x": -3330, "y": 8892, "w": 336, "h": 48, "rotation": -90},
    {"name": "Airlock", "x": 2567, "y": 8943, "w": 96, "h": 88, "rotation": 0, "type": "airlock"},

    # --- MID SECTOR (Agriculture Dome, Power Sector, Central Hubs) ---
    {"name": "Corridor", "type": "corridor", "x": 2631, "y": 9029, "w": 176, "h": 48, "rotation": -90},
    {"name": "Agriculture Dome", "type": "dome", "x": -2704, "y": 9143, "w": 864, "h": 864, "rotation": 0},
    {"name": "Airlock", "x": -3402, "y": 9184, "w": 96, "h": 88, "rotation": 0, "type": "airlock"},
    {"name": "Power Sector", "type": "chamfered", "x": 2344, "y": 9205, "w": 576, "h": 720, "rotation": 0},
    {"name": "Airlock", "x": -682, "y": 9221, "w": 96, "h": 88, "rotation": 0, "type": "airlock"},
    {"name": "Corridor", "type": "corridor", "x": -2516, "y": 9252, "w": 838, "h": 48, "rotation": -180},
    {"name": "Corridor", "type": "corridor", "x": -610, "y": 9277, "w": 664, "h": 48, "rotation": -90},
    {"name": "Airlock", "x": -4119, "y": 9366, "w": 96, "h": 88, "rotation": 0, "type": "airlock"},
    {"name": "Corridor", "type": "corridor", "x": -4047, "y": 9422, "w": 664, "h": 48, "rotation": -90},
    
    # --- LOWER MID SECTOR (Arctic Dome, Desert Dome & Connections) ---
    {"name": "Arctic Dome", "type": "dome", "x": -4214, "y": 9899, "w": 864, "h": 864, "rotation": 0},
    {"name": "Desert Dome", "type": "dome", "x": -1229, "y": 9899, "w": 864, "h": 864, "rotation": 0},
    {"name": "Airlock", "x": -3040, "y": 9920, "w": 96, "h": 88, "rotation": 0, "type": "airlock"},
    {"name": "Airlock", "x": -1634, "y": 9920, "w": 96, "h": 88, "rotation": 0, "type": "airlock"},
    {"name": "Corridor", "type": "corridor", "x": 2656, "y": 9925, "w": 176, "h": 48, "rotation": -90},
    {"name": "Corridor", "type": "corridor", "x": -2150, "y": 9928, "w": 664, "h": 48, "rotation": -90},
    {"name": "Corridor", "type": "corridor", "x": -3560, "y": 9940, "w": 567, "h": 48, "rotation": 0},
    {"name": "Corridor", "type": "corridor", "x": -2993, "y": 9940, "w": 568, "h": 48, "rotation": 0},
    {"name": "Corridor", "type": "corridor", "x": -2153, "y": 9940, "w": 567, "h": 48, "rotation": 0},
    {"name": "Corridor", "type": "corridor", "x": -1586, "y": 9940, "w": 568, "h": 48, "rotation": 0},
    {"name": "Airlock", "x": 2583, "y": 10100, "w": 96, "h": 88, "rotation": 0, "type": "airlock"},
    {"name": "Corridor", "type": "corridor", "x": 2656, "y": 10186, "w": 669, "h": 57, "rotation": -90},
    {"name": "Airlock", "x": -2222, "y": 10549, "w": 96, "h": 88, "rotation": 0, "type": "airlock"},
    {"name": "Corridor", "type": "corridor", "x": -3480, "y": 10568, "w": 566, "h": 48, "rotation": 0},
    {"name": "Corridor", "type": "corridor", "x": -2914, "y": 10568, "w": 740, "h": 48, "rotation": 0},
    {"name": "Corridor", "type": "corridor", "x": -2174, "y": 10568, "w": 350, "h": 48, "rotation": 0},
    {"name": "Corridor", "type": "corridor", "x": -1824, "y": 10568, "w": 706, "h": 48, "rotation": 0},
    {"name": "Corridor", "type": "corridor", "x": -2150, "y": 10637, "w": 664, "h": 48, "rotation": -90},
    {"name": "Corridor", "type": "corridor", "x": -3758, "y": 10763, "w": 664, "h": 48, "rotation": -90},
    {"name": "Corridor", "type": "corridor", "x": -774, "y": 10763, "w": 664, "h": 48, "rotation": -90},

    # --- SOUTH SECTOR (Control Rooms, Research Core & Observatory) ---
    {"name": "Control Room-1", "type": "chamfered", "x": -3189, "y": 11301, "w": 673, "h": 1054, "rotation": 0},
    {"name": "Control Room-2", "type": "chamfered", "x": -2334, "y": 11301, "w": 673, "h": 1054, "rotation": 0},
    {"name": "Research Core", "type": "rect", "x": 65, "y": 11334, "w": 700, "h": 1021, "rotation": 0},
    {"name": "Airlock", "x": -846, "y": 11423, "w": 96, "h": 88, "rotation": 0, "type": "airlock"},
    {"name": "Airlock", "x": -3830, "y": 11427, "w": 96, "h": 88, "rotation": 0, "type": "airlock"},
    {"name": "Corridor", "type": "corridor", "x": -1661, "y": 11443, "w": 815, "h": 48, "rotation": 0},
    {"name": "Corridor", "type": "corridor", "x": -3734, "y": 11447, "w": 545, "h": 48, "rotation": 0},
    {"name": "Airlock", "x": 1006, "y": 11522, "w": 96, "h": 88, "rotation": -88, "type": "airlock"},
    {"name": "Panoramic Observatory", "type": "capsule", "x": 1142, "y": 11540, "w": 1674, "h": 192, "rotation": 29},
    {"name": "Corridor", "type": "corridor", "x": 1182, "y": 11588, "w": 176, "h": 48, "rotation": -178},
    {"name": "Corridor", "type": "corridor", "x": 923, "y": 11589, "w": 242, "h": 48, "rotation": -178},
    {"name": "Airlock", "x": -846, "y": 12156, "w": 96, "h": 88, "rotation": 0, "type": "airlock"},
    {"name": "Corridor", "type": "corridor", "x": -1661, "y": 12176, "w": 815, "h": 48, "rotation": 0},
    {"name": "Corridor", "type": "corridor", "x": -750, "y": 12176, "w": 815, "h": 48, "rotation": 0},
    {"name": "Corridor", "type": "corridor", "x": -2520, "y": 12250, "w": 810, "h": 48, "rotation": -90},
    {"name": "Corridor", "type": "corridor", "x": 137, "y": 12355, "w": 664, "h": 48, "rotation": -90},
    
    # --- DEEP SOUTH (Bottom perimeter routing) ---
    {"name": "Airlock", "x": -2592, "y": 13019, "w": 96, "h": 88, "rotation": 0, "type": "airlock"},
    {"name": "Airlock", "x": -1701, "y": 13023, "w": 96, "h": 88, "rotation": 0, "type": "airlock"},
    {"name": "Airlock", "x": 65, "y": 13023, "w": 96, "h": 88, "rotation": 0, "type": "airlock"},
    {"name": "Corridor", "type": "corridor", "x": -2516, "y": 13043, "w": 815, "h": 48, "rotation": 0},
    {"name": "Corridor", "type": "corridor", "x": -1605, "y": 13043, "w": 1670, "h": 48, "rotation": 0}
]
