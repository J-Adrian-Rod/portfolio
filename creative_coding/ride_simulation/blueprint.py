import pygame
import sys
import math
import random
from datetime import datetime

# Import your configuration
from config import *

# Placeholder for the screen surface (main.py will provide this)
screen = None


# Apply global offset to layout
for room in ROOMS:
    room["x"] += GLOBAL_SHIFT_X


# =========================================================
# --- HELPER & GEOMETRY FUNCTIONS ---
# =========================================================
def screen_to_world(sx, sy):
    """Converts screen pixel coordinates to world schematic coordinates."""
    wx = (sx - WIDTH // 2) / zoom + camera_x
    wy = (sy - HEIGHT // 2) / zoom + camera_y
    return wx, wy

def world_to_screen(wx, wy):
    """Converts world schematic coordinates to screen pixel coordinates."""
    sx = (wx - camera_x) * zoom + WIDTH // 2
    sy = (wy - camera_y) * zoom + HEIGHT // 2
    return int(sx), int(sy)

def rotate_pt(px, py, cx, cy, angle_deg):
    """Helper to rotate coordinate points around a center point."""
    rad = math.radians(-angle_deg)
    nx = math.cos(rad) * (px - cx) - math.sin(rad) * (py - cy) + cx
    ny = math.sin(rad) * (px - cx) + math.cos(rad) * (py - cy) + cy
    return nx, ny

def clean_name(name):
    """Removes trailing numbers from labels (e.g., 'Processing-1' -> 'Processing')."""
    if "-" in name: return name.split("-")[0]
    return name

# Shape Generators for standard Pygame drawing
def create_octagon_points(w, h):
    cut = min(w, h) * 0.25 
    return [(cut, 0), (w - cut, 0), (w, cut), (w, h - cut), (w - cut, h), (cut, h), (0, h - cut), (0, cut)]

def create_chamfered_points(w, h):
    cut = min(w, h) * 0.15 
    return [(cut, 0), (w - cut, 0), (w, cut), (w, h - cut), (w - cut, h), (cut, h), (0, h - cut), (0, cut)]

def create_hex_points(w, h):
    return [(w/2, 0), (w, h/4), (w, 3*h/4), (w/2, h), (0, 3*h/4), (0, h/4)]



print("Generating Lunar Regolith & Impact Texture...")
noise_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)


# 2. Micro Texture: High-Contrast Lunar Dust
for _ in range(150000):
    x = random.randint(0, WIDTH - 1)
    y = random.randint(0, HEIGHT - 1)
    color = random.choice([(255, 255, 255, 15), (255, 255, 255, 30), (0, 0, 0, 25), (0, 0, 0, 50)])
    if random.random() > 0.98:
        pygame.draw.rect(noise_surf, color, (x, y, 2, 2))
    else:
        noise_surf.set_at((x, y), color)

noise_surf.set_alpha(TEXTURE_ALPHA)
print("Texture complete!")

# Calculate bounds and map sizing for camera zoom limits
min_x = min(r["x"] for r in ROOMS)
max_x = max(r["x"] + r["w"] for r in ROOMS)
min_y = min(r["y"] for r in ROOMS)
max_y = max(r["y"] + r["h"] for r in ROOMS)

map_width = max_x - min_x
map_height = max_y - min_y
camera_x = min_x + (map_width / 2)
camera_y = min_y + (map_height / 2)

zoom_x = WIDTH / (map_width * 1.1)
zoom_y = HEIGHT / (map_height * 1.1)
zoom = min(zoom_x, zoom_y) 
MIN_ZOOM = zoom  
MAX_ZOOM = 5.2


# =========================================================
# --- DRAWING FUNCTIONS ---
# =========================================================
def draw_grid():
    """Renders the standard blueprint grid lines beneath the map."""
    minor_size_screen = 50 * zoom
    major_size_screen = 250 * zoom
    if minor_size_screen < 5: return
        
    offset_x = ((0 - camera_x) * zoom + WIDTH / 2)
    offset_y = ((0 - camera_y) * zoom + HEIGHT / 2)

    start_x = int(offset_x % minor_size_screen)
    for x in range(start_x, WIDTH, int(minor_size_screen)):
        pygame.draw.line(screen, GRID_MINOR_COLOR, (x, 0), (x, HEIGHT), 1)
        
    start_y = int(offset_y % minor_size_screen)
    for y in range(start_y, HEIGHT, int(minor_size_screen)):
        pygame.draw.line(screen, GRID_MINOR_COLOR, (0, y), (WIDTH, y), 1)

    start_x_major = int(offset_x % major_size_screen)
    for x in range(start_x_major, WIDTH, int(major_size_screen)):
        pygame.draw.line(screen, GRID_MAJOR_COLOR, (x, 0), (x, HEIGHT), max(1, int(1.5 * zoom)))
        
    start_y_major = int(offset_y % major_size_screen)
    for y in range(start_y_major, HEIGHT, int(major_size_screen)):
        pygame.draw.line(screen, GRID_MAJOR_COLOR, (0, y), (WIDTH, y), max(1, int(1.5 * zoom)))

def draw_topography():
    """Renders organic, rigid crater contour lines across the background."""
    topo_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    font_large = pygame.font.SysFont("Verdana", max(10, int(22 * zoom)))
    font_small = pygame.font.SysFont("Verdana", max(8, int(12 * zoom)))

    def draw_organic_contour(world_cx, world_cy, rx, ry, waves, amp, thickness=1, alpha=100, phase_offset=0):
        sx, sy = world_to_screen(world_cx, world_cy)
        srx, sry = rx * zoom, ry * zoom
        if sx + srx < -WIDTH or sx - srx > WIDTH*2 or sy + sry < -HEIGHT or sy - sry > HEIGHT*2: return

        points = []
        steps = min(800, max(250, int(srx * 0.8))) 
        for i in range(steps):
            angle = (i / steps) * math.pi * 2
            macro = (math.sin(angle * 2 + phase_offset * 0.5) * 0.08) + (math.cos(angle * 3 - phase_offset * 0.2) * 0.05)
            micro = (math.sin(angle * waves + phase_offset) * amp) + \
                    (math.cos(angle * waves * 1.8 + phase_offset) * (amp * 0.7)) + \
                    (math.sin(angle * waves * 4.2 + phase_offset) * (amp * 0.4)) + \
                    (math.cos(angle * waves * 9.5) * (amp * 0.2))
                    
            variation = macro + micro
            px = sx + (srx * (1 + variation)) * math.cos(angle)
            py = sy + (sry * (1 + variation)) * math.sin(angle)
            points.append((px, py))
            
        if len(points) > 2:
            draw_color = (TOPO_LINE_COLOR[0], TOPO_LINE_COLOR[1], TOPO_LINE_COLOR[2], alpha)
            pygame.draw.lines(topo_surf, draw_color, True, points, max(1, int(thickness * zoom)))

    elev_x = (6420 + GLOBAL_SHIFT_X) + (351 / 2) 
    elev_y = 8371 + (332 / 2)
    shift_amount = 2500 
    crater_x = elev_x + shift_amount
    crater_y = elev_y
    
    sx, sy = world_to_screen(crater_x, crater_y)
    max_depth_radius = int(7500 * zoom)
    
    # Shadow Gradient for crater depth
    if sx + max_depth_radius > 0 and sx - max_depth_radius < WIDTH and sy + max_depth_radius > 0 and sy - max_depth_radius < HEIGHT:
        depth_surf = pygame.Surface((max_depth_radius * 2, max_depth_radius * 2), pygame.SRCALPHA)
        center_pt = (max_depth_radius, max_depth_radius)
        
        for i in range(10, 0, -1):
            r = int(max_depth_radius * (i / 10.0))
            pygame.draw.ellipse(depth_surf, CRATER_SHADOW, pygame.Rect(center_pt[0]-r, center_pt[1]-int(r*0.9), r*2, int(r*1.8)))
            
        screen.blit(depth_surf, (sx - max_depth_radius, sy - int(max_depth_radius*0.9)))

    # Outer Crater Rim Lines
    for i in range(40):
        rad = 5000 + shift_amount + (i * 200) 
        is_major = (i % 5 == 0)
        draw_organic_contour(crater_x, crater_y, rad, rad * 0.98, 18 + (i % 6) * 4, 0.06 + (i % 3) * 0.01, 2 if is_major else 1, 80 if is_major else 25, i * 2.7)

    for i in range(12):
        rad = 3000 + shift_amount + (i * 150)
        is_major = (i % 5 == 0)
        draw_organic_contour(crater_x, crater_y, rad, rad * 0.95, 7, 0.04, 2 if is_major else 1, 100 if is_major else 40, i * 0.3)

    for i in range(8):
        rad = 3100 + shift_amount + (i * 40) 
        is_major = (i % 4 == 0)
        draw_organic_contour(crater_x, crater_y, rad, rad * 0.96, 11, 0.035, 2 if is_major else 1, 180 if is_major else 80, i * 0.7)

    # Inner Crater Detail
    for i in range(6):
        rad = 1000 + shift_amount + (i * 120)
        is_major = (i % 4 == 0)
        draw_organic_contour(crater_x, crater_y, rad, rad * 0.95, 7, 0.04, 2 if is_major else 1, 100 if is_major else 40, i * 0.5)

    for i in range(3):
        rad = 700 + shift_amount + (i * 35) 
        is_major = (i % 5 == 0)
        draw_organic_contour(crater_x, crater_y, rad, rad * 0.96, 11, 0.035, 2 if is_major else 1, 180 if is_major else 80, i * 0.8)

    for i in range(3):
        rad = 200 + shift_amount + (i * 150)
        draw_organic_contour(crater_x, crater_y, rad, rad * 0.98, 8, 0.04, 1, 40, i * 0.1)

    # Deep Crater Trench
    for i in range(9):
        rad = 2300 * (0.65 ** i) 
        if rad < 15: break
        is_major = (i % 5 == 0)
        draw_organic_contour(crater_x, crater_y, rad, rad * 0.95, 8, 0.05 + (i * 0.002), 2 if is_major else 1, min(200, 60 + (i * 5)), i * 0.6)

    # Focal depth target
    sx, sy = world_to_screen(crater_x, crater_y)
    if 0 < sx < WIDTH and 0 < sy < HEIGHT:
        pygame.draw.circle(topo_surf, (TOPO_LINE_COLOR[0], TOPO_LINE_COLOR[1], TOPO_LINE_COLOR[2], 200), (int(sx), int(sy)), int(15 * zoom), 1)
        pygame.draw.circle(topo_surf, (TOPO_LINE_COLOR[0], TOPO_LINE_COLOR[1], TOPO_LINE_COLOR[2], 255), (int(sx), int(sy)), max(1, int(3 * zoom)))
        depth_lbl = font_small.render("-14,500m (CRATER FLOOR)", True, TOPO_TEXT_COLOR)
        screen.blit(depth_lbl, (sx + 20, sy - 10))

    screen.blit(topo_surf, (0, 0))
    labels = [("CRATER CENTER", crater_x, 7600, font_large)]
    for text, wx, wy, font in labels:
        sx, sy = world_to_screen(wx, wy)
        if 0 < sx < WIDTH and 0 < sy < HEIGHT:
            lbl = font.render(text, True, TOPO_TEXT_COLOR)
            screen.blit(lbl, lbl.get_rect(center=(sx, sy)))

def draw_map():
    """Renders the Astra-9 base schematic in layered loops (Outline -> Cutout -> Structure)."""
    render_data = []
    thickness = max(1, int(LINE_WEIGHT * zoom))
    hollow_padding = max(1, int(LINE_WEIGHT * zoom)) 
    solid_padding = hollow_padding + (thickness * 2) 
    
    # 1. Prepare render data for all rooms
    for room in ROOMS:
        w, h = room["w"], room["h"]
        rot = room.get("rotation", 0)
        rtype = room.get("type", "rect").lower()
        
        rad = math.radians(-rot)
        cos_a, sin_a = math.cos(rad), math.sin(rad)
        local_cx, local_cy = w / 2, h / 2
        
        rot_cx = local_cx * cos_a - local_cy * sin_a
        rot_cy = local_cx * sin_a + local_cy * cos_a 
        world_cx, world_cy = room["x"] + rot_cx, room["y"] + rot_cy
        screen_cx, screen_cy = world_to_screen(world_cx, world_cy)

        overlap_margin = 20 if "corridor" in rtype else 0
        scaled_w = max(1, int((w + overlap_margin) * zoom))
        scaled_h = max(1, int(h * zoom))

        color = CORRIDOR_COLOR if "corridor" in rtype else (AIRLOCK_COLOR if "airlock" in rtype else ROOM_COLOR)

        render_data.append({
            "room": room, "rtype": rtype, "color": color, "rot": rot,
            "screen_cx": screen_cx, "screen_cy": screen_cy,
            "scaled_w": scaled_w, "scaled_h": scaled_h
        })

    base_data = [d for d in render_data if d["rtype"] != "airlock"]
    airlock_data = [d for d in render_data if d["rtype"] == "airlock"]

    # 2. Airlock Glow (Underneath)
    for data in airlock_data:
        glow_rad = int(max(data["scaled_w"], data["scaled_h"]) * 1.5)
        glow_surf = pygame.Surface((glow_rad * 2, glow_rad * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (AIRLOCK_COLOR[0], AIRLOCK_COLOR[1], AIRLOCK_COLOR[2], 25), (glow_rad, glow_rad), glow_rad)
        screen.blit(glow_surf, (data["screen_cx"] - glow_rad, data["screen_cy"] - glow_rad))

    # 3. Layer 1: Solid Base (Creates the white outline)
    for data in base_data:
        dome_boost = int(6 * zoom) if data["rtype"] == "dome" else 0
        draw_w = data["scaled_w"] + solid_padding + dome_boost
        draw_h = data["scaled_h"] + solid_padding + dome_boost
        
        item_surf = pygame.Surface((draw_w, draw_h), pygame.SRCALPHA)
        draw_rect = pygame.Rect(0, 0, draw_w, draw_h)

        if data["rtype"] == "dome":
            pygame.draw.ellipse(item_surf, BLUEPRINT_WHITE, draw_rect)
        elif data["rtype"] == "capsule":
            radius = min(draw_w, draw_h) // 2
            pygame.draw.rect(item_surf, data["color"], draw_rect, border_radius=radius)
        elif data["rtype"] == "diamond":
            points = [(draw_w//2, 0), (draw_w, draw_h//2), (draw_w//2, draw_h), (0, draw_h//2)]
            pygame.draw.polygon(item_surf, data["color"], points)
        elif data["rtype"] == "chamfered":
            pts = create_chamfered_points(draw_w, draw_h)
            pygame.draw.polygon(item_surf, data["color"], pts)
        elif data["rtype"] == "hex":
            pts = create_hex_points(draw_w, draw_h)
            pygame.draw.polygon(item_surf, data["color"], pts)
        else:
            pygame.draw.rect(item_surf, data["color"], draw_rect)

        final_surf = pygame.transform.rotate(item_surf, data["rot"])
        screen.blit(final_surf, (data["screen_cx"] - final_surf.get_width() // 2, data["screen_cy"] - final_surf.get_height() // 2))

    # 4. Layer 2: Hollow Cutout (Reveals the outline by covering the center)
    for data in base_data:
        if "corridor" in data["rtype"]:
            draw_w = data["scaled_w"] + solid_padding 
            draw_h = data["scaled_h"] + hollow_padding
        else:
            draw_w = data["scaled_w"] + hollow_padding
            draw_h = data["scaled_h"] + hollow_padding
            
        if draw_w <= 0 or draw_h <= 0: continue 

        item_surf = pygame.Surface((draw_w, draw_h), pygame.SRCALPHA)
        draw_rect = pygame.Rect(0, 0, draw_w, draw_h)

        if data["rtype"] == "dome": 
            pygame.draw.ellipse(item_surf, BG_COLOR, draw_rect)
        elif data["rtype"] == "capsule": 
            radius = min(draw_w, draw_h) // 2
            pygame.draw.rect(item_surf, BG_COLOR, draw_rect, border_radius=radius)
        elif data["rtype"] == "diamond":
            pygame.draw.polygon(item_surf, BG_COLOR, [(draw_w//2, 0), (draw_w, draw_h//2), (draw_w//2, draw_h), (0, draw_h//2)])
        elif data["rtype"] == "chamfered":
            pts = create_chamfered_points(draw_w, draw_h)
            pygame.draw.polygon(item_surf, BG_COLOR, pts)
        elif data["rtype"] == "hex":
            pts = create_hex_points(draw_w, draw_h)
            pygame.draw.polygon(item_surf, BG_COLOR, pts)
        else: 
            pygame.draw.rect(item_surf, BG_COLOR, draw_rect)

        final_surf = pygame.transform.rotate(item_surf, data["rot"])
        screen.blit(final_surf, (data["screen_cx"] - final_surf.get_width() // 2, data["screen_cy"] - final_surf.get_height() // 2))

    # 5. Layer 3: Inner Structural Lines
    for data in base_data:
        draw_w = data["scaled_w"] + hollow_padding
        draw_h = data["scaled_h"] + hollow_padding
        if draw_w <= 0 or draw_h <= 0: continue 

        item_surf = pygame.Surface((draw_w, draw_h), pygame.SRCALPHA)
        cx, cy = draw_w / 2, draw_h / 2
        struct_color = (data["color"][0], data["color"][1], data["color"][2], 70)
        line_thickness = max(1, thickness // 2)

        if data["rtype"] == "dome":
            rx, ry = draw_w / 2, draw_h / 2
            for i in range(16):
                angle = math.radians(i * (360 / 16))
                pygame.draw.line(item_surf, struct_color, (cx, cy), (cx + rx * math.cos(angle), cy + ry * math.sin(angle)), line_thickness)
            for i in range(1, 4):
                sc = i / 4
                pygame.draw.ellipse(item_surf, struct_color, pygame.Rect(cx - rx*sc, cy - ry*sc, rx*2*sc, ry*2*sc), line_thickness)
            pygame.draw.circle(item_surf, struct_color, (int(cx), int(cy)), max(4, int(8 * zoom)))
        elif data["rtype"] == "zone":
            hatch_spacing = max(10, int(30 * zoom))
            for i in range(-draw_h, draw_w + draw_h, hatch_spacing):
                pygame.draw.line(item_surf, struct_color, (i, 0), (i + draw_h, draw_h), line_thickness)
        elif data["room"]["name"] == "Landing Strip":
            dash_len = max(5, int(20 * zoom))
            for y in range(int(cy - draw_h/2.5), int(cy + draw_h/2.5), dash_len * 2):
                pygame.draw.line(item_surf, struct_color, (cx, y), (cx, y + dash_len), line_thickness * 2)

        final_surf = pygame.transform.rotate(item_surf, data["rot"])
        screen.blit(final_surf, (data["screen_cx"] - final_surf.get_width() // 2, data["screen_cy"] - final_surf.get_height() // 2))

    # 6. Airlocks
    for data in airlock_data:
        # Base
        draw_w = data["scaled_w"] + solid_padding
        draw_h = data["scaled_h"] + solid_padding
        item_surf = pygame.Surface((draw_w, draw_h), pygame.SRCALPHA)
        pygame.draw.polygon(item_surf, data["color"], create_octagon_points(draw_w, draw_h))
        final_surf = pygame.transform.rotate(item_surf, data["rot"])
        screen.blit(final_surf, (data["screen_cx"] - final_surf.get_width() // 2, data["screen_cy"] - final_surf.get_height() // 2))
        
        # Cutout
        draw_w = data["scaled_w"] + hollow_padding
        draw_h = data["scaled_h"] + hollow_padding
        if draw_w <= 0 or draw_h <= 0: continue 
        item_surf = pygame.Surface((draw_w, draw_h), pygame.SRCALPHA)
        pygame.draw.polygon(item_surf, BG_COLOR, create_octagon_points(draw_w, draw_h))
        final_surf = pygame.transform.rotate(item_surf, data["rot"])
        screen.blit(final_surf, (data["screen_cx"] - final_surf.get_width() // 2, data["screen_cy"] - final_surf.get_height() // 2))

    # 7. Room Names
    for data in render_data:
        if "airlock" in data["rtype"] or "corridor" in data["rtype"]: continue
        display_name = clean_name(data["room"]["name"])
        text_surf = font_base.render(display_name, True, TEXT_COLOR)
        text_surf.set_alpha(200)

        scale_factor = zoom * 0.9
        target_w = max(1, int(text_surf.get_width() * scale_factor))
        target_h = max(1, int(text_surf.get_height() * scale_factor))
        if target_h < 5: continue
            
        scaled_text = pygame.transform.smoothscale(text_surf, (target_w, target_h))
        rotated_text = pygame.transform.rotate(scaled_text, data["rot"])
        screen.blit(rotated_text, rotated_text.get_rect(center=(data["screen_cx"], data["screen_cy"])))

def draw_blueprint_details():
    """Draws dimension lines around major structures and textual engineering notes."""
    # Engineering Notes
    notes = [
        "PROJECT: ASTRA-9",
        "LOCATION: Shackleton Ridge (Sector 4)",
        "SURFACE CONDITIONS: HEAVY REGOLITH / HIGH CRATERING",
        "STRUCTURAL COMPLIANCE: ISO-9022",
        "FORCAST: EXPECTED SOLAR FLARES",
        "--------------------------------------------------",
        "ENGINEERING NOTES:",
        "1. All primary domes utilize rigid-frame composite",
        "   shell plating to withstand local micro-impacts.",
        "2. Vacuum-seal couplings mandatory at all hub joints.",
        "3. Surface topology mapped via orbital LiDAR.",
        "4. Redundant life-support routed via sub-floor ducting."
    ]
    
    note_x, note_y = 20, 20
    for i, line in enumerate(notes):
        screen.blit(font_notes.render(line, True, TECHNICAL_LINE_COLOR), (note_x, note_y + (i * 16)))

    # Dimension Lines
    for room in ROOMS:
        name = room.get("name", "")
        rtype = room.get("type", "rect")
        w, h, rot = room["w"], room["h"], room.get("rotation", 0)

        is_major = rtype in ["dome", "rect", "chamfered", "capsule", "zone"] and w >= 400
        is_specific = name in ["Sky Bridge", "Construction Zone", "Panoramic Observatory"]
        if not (is_major or is_specific): continue

        rad_orig = math.radians(-rot)
        local_cx, local_cy = w / 2, h / 2
        rot_cx = local_cx * math.cos(rad_orig) - local_cy * math.sin(rad_orig)
        rot_cy = local_cx * math.sin(rad_orig) + local_cy * math.cos(rad_orig) 
        world_cx, world_cy = room["x"] + rot_cx, room["y"] + rot_cy

        sx, sy = world_to_screen(world_cx, world_cy)
        sw, sh = w * zoom, h * zoom
        if sw < 30 or sx < -sw or sx > WIDTH + sw or sy < -sh or sy > HEIGHT + sh: continue 
            
        dim_color, offset, line_w = TECHNICAL_LINE_COLOR, 15 * zoom, max(1, int(1 * zoom))

        # Width Dimension
        w_start_x, w_start_y = sx - sw/2, sy - sh/2 - offset
        w_end_x, w_end_y = sx + sw/2, sy - sh/2 - offset
        rw_start = rotate_pt(w_start_x, w_start_y, sx, sy, rot)
        rw_end = rotate_pt(w_end_x, w_end_y, sx, sy, rot)
        pygame.draw.line(screen, dim_color, rw_start, rw_end, line_w)
        pygame.draw.line(screen, dim_color, rotate_pt(w_start_x, w_start_y - 4, sx, sy, rot), rotate_pt(w_start_x, w_start_y + 4, sx, sy, rot), line_w)
        pygame.draw.line(screen, dim_color, rotate_pt(w_end_x, w_end_y - 4, sx, sy, rot), rotate_pt(w_end_x, w_end_y + 4, sx, sy, rot), line_w)
        
        lbl_w = font_dim.render(f"{int(w)}m", True, dim_color)
        rot_lbl_w = pygame.transform.rotate(lbl_w, rot)
        txt_cx, txt_cy = rotate_pt(sx, sy - sh/2 - offset - 8, sx, sy, rot)
        screen.blit(rot_lbl_w, rot_lbl_w.get_rect(center=(txt_cx, txt_cy)))

        # Height Dimension
        if h >= 50:
            h_start_x, h_start_y = sx - sw/2 - offset, sy - sh/2
            h_end_x, h_end_y = sx - sw/2 - offset, sy + sh/2
            rh_start = rotate_pt(h_start_x, h_start_y, sx, sy, rot)
            rh_end = rotate_pt(h_end_x, h_end_y, sx, sy, rot)
            pygame.draw.line(screen, dim_color, rh_start, rh_end, line_w)
            pygame.draw.line(screen, dim_color, rotate_pt(h_start_x - 4, h_start_y, sx, sy, rot), rotate_pt(h_start_x + 4, h_start_y, sx, sy, rot), line_w)
            pygame.draw.line(screen, dim_color, rotate_pt(h_end_x - 4, h_end_y, sx, sy, rot), rotate_pt(h_end_x + 4, h_end_y, sx, sy, rot), line_w)
            
            lbl_h = font_dim.render(f"{int(h)}m", True, dim_color)
            rot_lbl_h = pygame.transform.rotate(lbl_h, rot + 90)
            txt_cx, txt_cy = rotate_pt(sx - sw/2 - offset - 8, sy, sx, sy, rot)
            screen.blit(rot_lbl_h, rot_lbl_h.get_rect(center=(txt_cx, txt_cy)))

def draw_ui():
    """Draws the static UI elements like the legend and title block."""
    # Legend Box
    leg_w, leg_h = 240, 195 
    leg_x, leg_y = 30, HEIGHT - leg_h - 30 
    
    # Background and Border
    leg_surf = pygame.Surface((leg_w, leg_h), pygame.SRCALPHA)
    pygame.draw.rect(leg_surf, (5, 20, 50, 200), (0, 0, leg_w, leg_h))
    screen.blit(leg_surf, (leg_x, leg_y))
    pygame.draw.rect(screen, TECHNICAL_LINE_COLOR, (leg_x, leg_y, leg_w, leg_h), 2)
    
    screen.blit(ui_font_large.render("LEGEND", True, TECHNICAL_LINE_COLOR), (leg_x + 15, leg_y + 10))
    pygame.draw.line(screen, TECHNICAL_LINE_COLOR, (leg_x + 10, leg_y + 35), (leg_x + leg_w - 10, leg_y + 35), 1)

    # Added "BOARDING" to the items list with a new "pie" shape type
    items = [
        ("TRANSIT CORRIDOR", CORRIDOR_COLOR, "rect"),
        ("PRESSURE AIRLOCK", AIRLOCK_COLOR, "octagon"),
        ("BOARDING", (0, 255, 200), "pie"), 
    ]

    start_item_y = leg_y + 55
    for i, (text, color, shape) in enumerate(items):
        item_y = start_item_y + (i * 45)
        icon_x = leg_x + 25
        
        if shape == "rect":
            pygame.draw.rect(screen, color, (icon_x - 10, item_y - 10, 20, 20), 2)
        elif shape == "octagon":
            pts = []
            for a in range(0, 360, 45):
                rad = math.radians(a + 22.5)
                pts.append((icon_x + 12 * math.cos(rad), item_y + 12 * math.sin(rad)))
            pygame.draw.polygon(screen, color, pts, 2)
        elif shape == "pie":
            # Draw the 3/4 pie chart for Boarding
            radius = 11
            # 1. Fill the 3/4 Cyan area
            points = [(icon_x, item_y)]
            s_angle = -math.pi / 2
            e_angle = s_angle + (0.75 * 2 * math.pi)
            for step in range(30):
                angle = s_angle + (step / 29) * (e_angle - s_angle)
                points.append((icon_x + radius * math.cos(angle), item_y + radius * math.sin(angle)))
            pygame.draw.polygon(screen, color, points)
            # 2. Draw the white outline ring
            pygame.draw.circle(screen, TECHNICAL_LINE_COLOR, (icon_x, item_y), radius, 2)

        screen.blit(ui_font_small.render(text, True, TECHNICAL_LINE_COLOR), (leg_x + 55, item_y - 8))
    # Title Block
    tb_w, tb_h = 320, 130
    tb_x, tb_y = WIDTH - tb_w - 30, HEIGHT - tb_h - 30 
    pygame.draw.rect(screen, (5, 20, 50, 200), (tb_x, tb_y, tb_w, tb_h))
    pygame.draw.rect(screen, TECHNICAL_LINE_COLOR, (tb_x, tb_y, tb_w, tb_h), 2)
    pygame.draw.line(screen, TECHNICAL_LINE_COLOR, (tb_x, tb_y + 50), (tb_x + tb_w, tb_y + 50), 2)
    pygame.draw.line(screen, TECHNICAL_LINE_COLOR, (tb_x, tb_y + 90), (tb_x + tb_w, tb_y + 90), 1)
    pygame.draw.line(screen, TECHNICAL_LINE_COLOR, (tb_x + 200, tb_y + 50), (tb_x + 200, tb_y + tb_h), 1)

    screen.blit(ui_font_large.render("ASTRA-9 Master Schematic", True, TECHNICAL_LINE_COLOR), (tb_x + 15, tb_y + 15))
    screen.blit(ui_font_small.render("DRAWING: BASE LAYOUT", True, TECHNICAL_LINE_COLOR), (tb_x + 10, tb_y + 60))
    screen.blit(ui_font_small.render("STATUS: ACTIVE", True, TECHNICAL_LINE_COLOR), (tb_x + 10, tb_y + 100))
    screen.blit(ui_font_small.render(f"DATE: {datetime.now().strftime('%Y-%m-%d')}", True, TECHNICAL_LINE_COLOR), (tb_x + 210, tb_y + 60))
    screen.blit(ui_font_small.render("REV: 4.1", True, TECHNICAL_LINE_COLOR), (tb_x + 210, tb_y + 100))

def draw_hover_tooltip():
    """Detects mouse position and draws an information tooltip over hovered rooms."""
    mx, my = pygame.mouse.get_pos()
    wx, wy = screen_to_world(mx, my)
    
    hovered_room = None
    for room in reversed(ROOMS):
        w, h, rot = room["w"], room["h"], room.get("rotation", 0)
        rad_orig = math.radians(-rot)
        local_cx, local_cy = w / 2, h / 2
        rot_cx = local_cx * math.cos(rad_orig) - local_cy * math.sin(rad_orig)
        rot_cy = local_cx * math.sin(rad_orig) + local_cy * math.cos(rad_orig) 
        world_cx, world_cy = room["x"] + rot_cx, room["y"] + rot_cy
        
        dx, dy = wx - world_cx, wy - world_cy
        rad = math.radians(rot)
        cos_a, sin_a = math.cos(rad), math.sin(rad)
        px = dx * cos_a + dy * sin_a
        py = -dx * sin_a + dy * cos_a
        
        if abs(px) <= w / 2 and abs(py) <= h / 2:
            hovered_room = room
            break
            
    if hovered_room:
        name_text = clean_name(hovered_room["name"])
        coord_text = f"COORD: {int(hovered_room['x'])}, {int(hovered_room['y'])}"
        lbl_name = ui_font_large.render(name_text, True, BG_COLOR)
        lbl_coord = ui_font_small.render(coord_text, True, BG_COLOR)
        
        box_w = max(lbl_name.get_width(), lbl_coord.get_width()) + 20
        box_h = lbl_name.get_height() + lbl_coord.get_height() + 15
        box_x, box_y = mx + 15, my + 15
        if box_x + box_w > WIDTH: box_x = mx - box_w - 15
        if box_y + box_h > HEIGHT: box_y = my - box_h - 15
        
        pygame.draw.rect(screen, BLUEPRINT_WHITE, (box_x, box_y, box_w, box_h))
        pygame.draw.rect(screen, TECHNICAL_LINE_COLOR, (box_x, box_y, box_w, box_h), 2)
        screen.blit(lbl_name, (box_x + 10, box_y + 5))
        screen.blit(lbl_coord, (box_x + 10, box_y + 5 + lbl_name.get_height()))
        
        sx, sy = world_to_screen(world_cx, world_cy)
        pygame.draw.circle(screen, TECHNICAL_LINE_COLOR, (int(sx), int(sy)), 4, 1)

def draw_border():
    """Draws the framing border and measurement ticks around the edge of the screen."""
    margin = 15
    border_rect = pygame.Rect(margin, margin, WIDTH - (margin * 2), HEIGHT - (margin * 2))
    pygame.draw.rect(screen, TECHNICAL_LINE_COLOR, border_rect, 1)
    pygame.draw.rect(screen, TECHNICAL_LINE_COLOR, pygame.Rect(margin-4, margin-4, WIDTH - (margin*2)+8, HEIGHT - (margin*2)+8), 3)
    
    tick_spacing = 100
    for i in range(margin + tick_spacing, WIDTH - margin, tick_spacing):
        pygame.draw.line(screen, TECHNICAL_LINE_COLOR, (i, margin), (i, margin + 8), 2)
        pygame.draw.line(screen, TECHNICAL_LINE_COLOR, (i, HEIGHT - margin), (i, HEIGHT - margin - 8), 2)
        
    for i in range(margin + tick_spacing, HEIGHT - margin, tick_spacing):
        pygame.draw.line(screen, TECHNICAL_LINE_COLOR, (margin, i), (margin + 8, i), 2)
        pygame.draw.line(screen, TECHNICAL_LINE_COLOR, (WIDTH - margin, i), (WIDTH - margin - 8, i), 2)
