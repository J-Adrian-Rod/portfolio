import pygame
import sys
from config import *
import blueprint 

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Astra-9 Dev Tool - PATH RECORDER")
    clock = pygame.time.Clock()
    blueprint.screen = screen

    # Camera settings
    camera_x, camera_y = -4000, 11000 
    zoom = 0.15
    move_keys = {pygame.K_LEFT: False, pygame.K_RIGHT: False, pygame.K_UP: False, pygame.K_DOWN: False}
    
    # Target Cursor settings
    target_keys = {pygame.K_w: False, pygame.K_s: False, pygame.K_a: False, pygame.K_d: False}
    target_x, target_y = -5671, 11457 # Spawns near the control rooms
    
    is_dragging = False
    last_mouse_pos = (0, 0)
    
    recorded_path = []
    gui_font = pygame.font.SysFont(None, 24)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.MOUSEWHEEL: zoom += event.y * 0.05 * zoom
            
            # Camera Dragging
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: 
                is_dragging, last_mouse_pos = True, event.pos
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1: 
                is_dragging = False
            if event.type == pygame.MOUSEMOTION and is_dragging:
                camera_x -= (event.pos[0] - last_mouse_pos[0]) / zoom
                camera_y -= (event.pos[1] - last_mouse_pos[1]) / zoom
                last_mouse_pos = event.pos
                
            # Key Presses
            if event.type == pygame.KEYDOWN:
                if event.key in move_keys: move_keys[event.key] = True
                if event.key in target_keys: target_keys[event.key] = True
                
                # Drop a waypoint
                if event.key == pygame.K_SPACE:
                    recorded_path.append((int(target_x), int(target_y), 'MOVE'))
                    print(f"Point Added: ({int(target_x)}, {int(target_y)})")
                    
                # Undo last waypoint
                if event.key == pygame.K_z: 
                    if recorded_path:
                        removed = recorded_path.pop()
                        print(f"Removed: {removed}")
                        
                # Export and Save
                if event.key == pygame.K_RETURN:
                    print("\n========================================")
                    print("recorded_route = [")
                    for wp in recorded_path:
                        print(f"    ({wp[0]}, {wp[1]}, '{wp[2]}'),")
                    print("]")
                    print("========================================\n")
                    
                    with open("custom_path_output.txt", "w") as f:
                        f.write("recorded_route = [\n")
                        for wp in recorded_path:
                            f.write(f"    ({wp[0]}, {wp[1]}, '{wp[2]}'),\n")
                        f.write("]\n")
                    print("SUCCESS: Path saved to 'custom_path_output.txt'!")
                    
            # Key Releases
            if event.type == pygame.KEYUP:
                if event.key in move_keys: move_keys[event.key] = False
                if event.key in target_keys: target_keys[event.key] = False

        # Apply Camera Movement
        zoom = max(blueprint.MIN_ZOOM, min(blueprint.MAX_ZOOM, zoom))
        speed = 15 / zoom
        if move_keys[pygame.K_LEFT]:  camera_x -= speed
        if move_keys[pygame.K_RIGHT]: camera_x += speed
        if move_keys[pygame.K_UP]:    camera_y -= speed
        if move_keys[pygame.K_DOWN]:  camera_y += speed
        
        camera_x = max(blueprint.min_x, min(blueprint.max_x, camera_x))
        camera_y = max(blueprint.min_y, min(blueprint.max_y, camera_y))
        blueprint.camera_x, blueprint.camera_y, blueprint.zoom = camera_x, camera_y, zoom

        # Apply Precision Target Movement
        keys = pygame.key.get_pressed()
        nudge_speed = 10 if keys[pygame.K_LSHIFT] else 1
        if target_keys[pygame.K_w]: target_y -= nudge_speed
        if target_keys[pygame.K_s]: target_y += nudge_speed
        if target_keys[pygame.K_a]: target_x -= nudge_speed
        if target_keys[pygame.K_d]: target_x += nudge_speed

        # --- DRAWING ---
        screen.fill(BG_COLOR)
        blueprint.draw_grid()
        blueprint.draw_topography()
        blueprint.draw_map()
        
        # Draw the recorded path lines
        if len(recorded_path) > 1:
            screen_pts = []
            for wp in recorded_path:
                sx, sy = blueprint.world_to_screen(wp[0], wp[1])
                screen_pts.append((sx, sy))
            pygame.draw.lines(screen, (0, 255, 200), False, screen_pts, 3)
            
        # Draw the recorded path dots
        for wp in recorded_path:
            sx, sy = blueprint.world_to_screen(wp[0], wp[1])
            pygame.draw.circle(screen, (255, 255, 255), (int(sx), int(sy)), 4)
            
        # Draw the Precision Target Crosshair
        tx, ty = blueprint.world_to_screen(target_x, target_y)
        pygame.draw.line(screen, (255, 50, 50), (tx - 15, ty), (tx + 15, ty), 2)
        pygame.draw.line(screen, (255, 50, 50), (tx, ty - 15), (tx, ty + 15), 2)
        pygame.draw.circle(screen, (255, 255, 0), (int(tx), int(ty)), 3)
        
        # Draw the UI Panel
        ui_texts = [
            "ASTRA-9 PATH RECORDER",
            "---------------------------",
            "Arrow Keys / Mouse Drag: Pan Camera",
            "W, A, S, D: Move Precision Crosshair",
            "(Hold SHIFT to move crosshair 10x faster)",
            "SPACE: Drop Waypoint at Crosshair",
            "Z: Undo Last Waypoint",
            "ENTER: Save Path to Text File",
            "",
            f"Crosshair Position: ({int(target_x)}, {int(target_y)})",
            f"Waypoints Recorded: {len(recorded_path)}"
        ]
        
        # Draw a dark background for the UI so it's readable
        pygame.draw.rect(screen, (20, 20, 20), (10, 10, 380, 290), border_radius=8)
        
        for i, text in enumerate(ui_texts):
            color = (0, 255, 100) if "Position" in text else (255, 255, 255)
            surf = gui_font.render(text, True, color)
            screen.blit(surf, (20, 20 + i * 25))

        pygame.display.flip()
        clock.tick(60)
        
if __name__ == "__main__":
    main()