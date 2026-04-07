import pygame
import math

class RideVehicle:
    def __init__(self, start_x, start_y, color, name):
        self.x = start_x
        self.y = start_y
        self.color = color
        self.name = name  
        self.speed = 10 
        self.waypoints = [] 
        self.current_target_idx = 0
        
        self.is_waiting = False
        self.wait_start_time = 0
        self.active = True 

    def set_route(self, waypoints):
        self.waypoints = waypoints
        self.current_target_idx = 0
        if self.waypoints:
            self.x = self.waypoints[0][0]
            self.y = self.waypoints[0][1]

    def update(self, block_system):
        if not self.active: return
        if self.current_target_idx >= len(self.waypoints): return 

        # Waypoint Format: (X, Y, COMMAND, TARGET_ZONE)
        wp = self.waypoints[self.current_target_idx]
        target_x, target_y = wp[0], wp[1]
        command = wp[2] if len(wp) > 2 else 'MOVE'
        zone = wp[3] if len(wp) > 3 else None

        # 1. TRANSIT LOGIC
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.hypot(dx, dy)

        if dist >= self.speed and not self.is_waiting:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed
            return

        # 2. WE ARRIVED AT A WAYPOINT! SNAP TO GRID.
        self.x, self.y = target_x, target_y

        if command == 'MOVE':
            self.current_target_idx += 1
            return
            
        if command == 'RELEASE':
            # Free the room for the next vehicle!
            if zone in block_system and block_system[zone] == self.name:
                block_system[zone] = None 
            self.current_target_idx += 1
            return

        # 3. AIRLOCK REQUEST & HOLD LOGIC
        if not self.is_waiting:
            if command == 'REQUEST':
                # Check your algorithmic dictionary! Is the room ahead occupied?
                if block_system[zone] is not None and block_system[zone] != self.name:
                    # OCCUPIED! Do absolutely nothing. Stall here indefinitely.
                    return
                
                # EMPTY! Claim the room in the dictionary so no one else enters.
                block_system[zone] = self.name

            # Start the physical 5-second airlock decompression timer
            self.is_waiting = True
            self.wait_start_time = pygame.time.get_ticks()
        else:
            # Check if the 5 seconds are up. If so, open the doors!
            if pygame.time.get_ticks() - self.wait_start_time >= 5000:
                self.is_waiting = False
                self.current_target_idx += 1

    def draw(self, screen, world_to_screen_fn, zoom):
        sx, sy = world_to_screen_fn(self.x, self.y)
        width, height = screen.get_size()
        
        if 0 < sx < width and 0 < sy < height:
            color = (255, 200, 0) if self.is_waiting else self.color
            blip_radius = max(6, int(15 * zoom)) 
            pulse = math.sin(pygame.time.get_ticks() * 0.005) * 3
            
            glow_surf = pygame.Surface((blip_radius * 4, blip_radius * 4), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (color[0], color[1], color[2], 50), (blip_radius * 2, blip_radius * 2), blip_radius + pulse + 4)
            screen.blit(glow_surf, (sx - blip_radius * 2, sy - blip_radius * 2))
            
            pygame.draw.circle(screen, color, (int(sx), int(sy)), blip_radius)
            pygame.draw.circle(screen, (255, 255, 255), (int(sx), int(sy)), blip_radius - 2)