import pygame
import sys
import math
from config import *
import blueprint 

# Add your master speed dial right here!
GLOBAL_SIM_SPEED = 3.0 

# =======================================================
# --- ALIGNMENT CONTROL PANEL ---
# =======================================================
LEFT_CTRL_ROOM_OFFSET_X = 0   
LEFT_CTRL_ROOM_OFFSET_Y = 0

RIGHT_CTRL_ROOM_OFFSET_X = 0  
RIGHT_CTRL_ROOM_OFFSET_Y = 0

# =======================================================
# --- AIRLOCK CONTROL PANEL (Time in milliseconds) ---
# =======================================================
WHITE_WAIT_TIMES = {
    'AL_AG_A': 2500,     
    'AL_AG_B': 2500,     
    'AL_ARCTIC_A': 3300, 
    'AL_ARCTIC_B': 2300, 
    'AL_EXIT_A': 3800,      
    'AL_EXIT_B': 0       
}

# =======================================================
# --- THE ALGORITHMIC VEHICLE CLASS ---
# =======================================================
# =======================================================
# --- THE ALGORITHMIC VEHICLE CLASS ---
# =======================================================
# =======================================================
# --- THE ALGORITHMIC VEHICLE CLASS ---
# =======================================================
# =======================================================
# --- THE ALGORITHMIC VEHICLE CLASS ---
# =======================================================
# =======================================================
# --- THE ALGORITHMIC VEHICLE CLASS ---
# =======================================================
class RideVehicle:
    def __init__(self, start_x, start_y, color, name, route_id):
        self.x = start_x
        self.y = start_y
        self.color = color
        self.name = name  
        self.route_id = route_id 
        
        self.base_speed = 10 
        self.speed = 10
        
        self.waypoints = [] 
        self.current_target_idx = 0
        self.active = False 
        
        self.is_boarding = False
        self.boarding_progress = 0.0 
        
        self.remaining_wait = 0 
        self.zone = 'CORRIDOR' 

    def set_route(self, waypoints):
        self.waypoints = waypoints
        self.current_target_idx = 0
        if self.waypoints:
            self.x = self.waypoints[0][0]
            self.y = self.waypoints[0][1]

    def update(self, sys_state, sim_speed, dt, all_vehicles): 
        if not self.active: return
        if self.current_target_idx >= len(self.waypoints):
            self.active = False
            return

        delay_on = sys_state.get('delay_active', False)

        current_wp = self.waypoints[self.current_target_idx]
        current_tag = current_wp[2] if len(current_wp) > 2 else 'MOVE'
        
        # We ONLY lock down if we are parked exactly on an ENTERING airlock door.
        # Vehicles at EXIT doors should be allowed to enter the corridor!
        at_airlock = (self.x == current_wp[0] and self.y == current_wp[1] and current_tag.startswith('AL_'))

        # --- SPATIAL DOME DETECTION ---
        dome_centers = [
            (-7000, 8600),  # Rainforest
            (-7200, 10400), # Arctic
            (-5900, 9700),  # Agriculture
            (-4400, 10300)  # Desert
        ]
        
        # Expanded radius to 800 to ensure the entire physical dome is covered
        self.in_dome = False 
        for cx, cy in dome_centers:
            if math.hypot(self.x - cx, self.y - cy) < 800:
                self.in_dome = True
                break

        # --- 1. DETERMINE BASE SPEED & ZONE BEHAVIOR ---
        if delay_on:
            if at_airlock:
                self.speed = 0 # Absolute lockdown if sitting on a door
            elif self.in_dome: 
                self.speed = self.base_speed * sim_speed * 0.3 # Slow down in domes
            else: 
                self.speed = self.base_speed * sim_speed # Corridor: Keep driving!
        else:
            self.speed = self.base_speed * sim_speed

        # --- 2. NORMAL AIRLOCK COUNTDOWN ---
        if self.remaining_wait > 0:
            if not delay_on: 
                self.remaining_wait -= dt 
                
            if self.remaining_wait <= 0:
                if delay_on:
                    self.speed = 0
                    return 
                self.current_target_idx += 1
            else:
                self.speed = 0 
                return

        # --- 3. ANTI-COLLISION (TWEAKED FOR TIGHT CURVES) ---
        SAFE_DISTANCE = 120      
        WARNING_DISTANCE = 300   
        
        if self.speed > 0:
            for other in all_vehicles:
                if other is self or not other.active: continue
                
                if self.route_id == other.route_id:
                    index_diff = other.current_target_idx - self.current_target_idx
                    
                    # Only look up to 25 waypoints ahead to avoid looking "through walls"
                    if 0 < index_diff < 25: 
                        dist_between = math.hypot(self.x - other.x, self.y - other.y)
                        
                        if dist_between < SAFE_DISTANCE:
                            self.speed = 0 
                            break
                        elif dist_between < WARNING_DISTANCE:
                            brake_factor = (dist_between - SAFE_DISTANCE) / (WARNING_DISTANCE - SAFE_DISTANCE)
                            dynamic_speed_limit = (self.base_speed * sim_speed) * brake_factor
                            
                            if dynamic_speed_limit < self.speed:
                                self.speed = max(dynamic_speed_limit, 0.1) 

        if self.speed == 0:
            return 

        # --- 4. MOVEMENT LOOP ---
        distance_to_move = self.speed
        
        while distance_to_move > 0 and self.current_target_idx < len(self.waypoints):
            wp = self.waypoints[self.current_target_idx]
            target_x, target_y = wp[0], wp[1]
            tag = wp[2] if len(wp) > 2 else 'MOVE'
            
            dx = target_x - self.x
            dy = target_y - self.y
            dist = math.hypot(dx, dy)
            
            if dist > distance_to_move:
                self.x += (dx / dist) * distance_to_move
                self.y += (dy / dist) * distance_to_move
                distance_to_move = 0 
            else:
                self.x = target_x
                self.y = target_y
                distance_to_move -= dist 
                
                if tag.startswith('AL_'):
                    if delay_on:
                        self.speed = 0
                        return 
                        
                    if self.name.startswith("White"):
                        base_wait = WHITE_WAIT_TIMES.get(tag, 1000) 
                        
                        cyan_in_dome = False
                        for other in all_vehicles:
                            if other.name.startswith("Cyan") and other.active and other.route_id == self.route_id:
                                if getattr(other, 'in_dome', False): 
                                    cyan_in_dome = True
                                    break
                                    
                        if cyan_in_dome:
                            base_wait += 3000 

                        if base_wait > 0:
                            self.remaining_wait = base_wait / sim_speed
                            self.speed = 0 
                            return 
                    self.current_target_idx += 1
                    
                elif tag.startswith('EXIT_'):
                    # Removed the lockdown trap! Exiting vehicles keep moving into the corridor.
                    self.current_target_idx += 1
                    
                else:
                    self.current_target_idx += 1

    def draw(self, surface, world_to_screen_fn, zoom):
        sx, sy = world_to_screen_fn(self.x, self.y)
        blip_radius = max(6, int(15 * zoom)) 
        
        if self.is_boarding:
            pygame.draw.circle(surface, (50, 50, 50), (int(sx), int(sy)), blip_radius, 2)
            if self.boarding_progress > 0.01:
                center = (int(sx), int(sy))
                points = [center]
                start_angle = -math.pi / 2 
                end_angle = start_angle + (self.boarding_progress * 2 * math.pi)
                steps = max(3, int(self.boarding_progress * 30)) 
                for i in range(steps + 1):
                    angle = start_angle + (i / steps) * (end_angle - start_angle)
                    points.append((center[0] + blip_radius * math.cos(angle), center[1] + blip_radius * math.sin(angle)))
                if len(points) > 2:
                    pygame.draw.polygon(surface, self.color, points)
        else:
            is_stalled = self.remaining_wait > 0 or self.speed == 0
            color = (255, 200, 0) if is_stalled else self.color
            pulse = math.sin(pygame.time.get_ticks() * 0.005) * 3 if is_stalled else 0
            glow_surf = pygame.Surface((blip_radius * 4, blip_radius * 4), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (color[0], color[1], color[2], 50), (blip_radius * 2, blip_radius * 2), blip_radius + pulse + 4)
            surface.blit(glow_surf, (sx - blip_radius * 2, sy - blip_radius * 2))
            pygame.draw.circle(surface, color, (int(sx), int(sy)), blip_radius)
            pygame.draw.circle(surface, color, (int(sx), int(sy)), blip_radius - 2)
# --- GEOMETRY HELPERS ---
def get_bezier_curve(p0, p1, p2, steps=25):
    curve = []
    for t in range(1, steps + 1): 
        t = t / steps
        x = (1-t)**2 * p0[0] + 2*(1-t)*t * p1[0] + t**2 * p2[0]
        y = (1-t)**2 * p0[1] + 2*(1-t)*t * p1[1] + t**2 * p2[1]
        curve.append((int(x), int(y), 'MOVE'))
    return curve

def apply_offset(route_list, offset_x, offset_y):
    return [(wp[0] + offset_x, wp[1] + offset_y, wp[2]) for wp in route_list]

def main():
    pygame.init()
    
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
    pygame.display.set_caption("Astra-9 Master Schematic")
    clock = pygame.time.Clock()
    blueprint.screen = screen 

    camera_x, camera_y = -3200, 9700 
    zoom = 0.11111
    
    move_keys = {pygame.K_LEFT: False, pygame.K_RIGHT: False, pygame.K_UP: False, pygame.K_DOWN: False}
    is_dragging = False
    last_mouse_pos = (0, 0)
    current_sim_speed = 3.0
    
    # Fonts for Dashboard
    dash_font_title = pygame.font.SysFont("monospace", 22, bold=True)
    dash_font = pygame.font.SysFont("monospace", 18)
    gui_font = pygame.font.SysFont(None, 28)

    # === ANALYTICS & TIMELINE SETUP ===
    PASSENGERS_PER_VEHICLE = 12
    simulated_time_ms = 0
    sys_state = {'delay_active': False, 'delay_timer': 0} 
    total_dispatched_pax = 0
    planned_delays = [] 
    FORECAST_WINDOW_MS = 10 * 60 * 1000 
    
    # NEW: Rolling Window Analytics
    dispatch_history = [] # Stores timestamps of when vehicles leave
    ROLLING_WINDOW_MS = 5 * 60 * 1000 # Calculate PPH based on last 5 simulated minutes

    # =======================================================
    # --- ROUTE GENERATION ---
    # =======================================================
    Y_TOP, Y_MID, Y_BOT, Y_DEEP_BOT = 8460, 9964, 10593, 11471
    X_FAR_LEFT, X_LEFT, X_MID, X_RIGHT = -7282, -7571, -5674, -4134

    route_a = [(-5512, Y_TOP, 'MOVE'), (-6232, Y_TOP, 'MOVE'), (-6812, Y_TOP, 'MOVE')]
    route_a.extend(get_bezier_curve((-6812, Y_TOP), (-7050, 8250), (-7350, 8350)))
    route_a.extend(get_bezier_curve((-7350, 8350), (-7550, 8450), (-7214, 8604)))
    route_a.extend(get_bezier_curve((-7214, 8604), (-7000, 8750), (X_LEFT, 8800)))
    route_a.extend([(X_LEFT, 9410, 'AL_ARCTIC_A'), (X_LEFT, 9869, 'MOVE')])
    route_a.extend(get_bezier_curve((X_LEFT, 9869), (-7612, 10200), (-7612, 10500)))
    route_a.extend(get_bezier_curve((-7612, 10500), (-7469, 10655), (-7183, 10655)))
    route_a.extend(get_bezier_curve((-7183, 10655), (-6897, 10550), (-6897, 10226)))
    route_a.extend(get_bezier_curve((-6897, 10226), (-6897, Y_MID), (-7100, Y_MID)))
    route_a.extend([(-7100, Y_MID, 'EXIT_ARCTIC_A'), (-6492, Y_MID, 'AL_AG_A'), (-5900, Y_MID, 'MOVE')])
    route_a.extend(get_bezier_curve((-5900, Y_MID), (-5400, 9900), (-5500, 9400)))
    route_a.extend(get_bezier_curve((-5500, 9400), (-6200, 9100), (-6112, 9600)))
    route_a.extend(get_bezier_curve((-6112, 9600), (-6000, 9850), (X_MID, 9850)))
    route_a.extend([(X_MID, 9850, 'EXIT_AG_A'), (X_MID, 10593, 'AL_EXIT_A')])

    raw_right_ctrl_room = [
        (-5674, 11405, 'MOVE'), (-5668, 11564, 'MOVE'), (-5629, 11781, 'MOVE'), (-5502, 12075, 'MOVE'),
        (-5315, 12191, 'MOVE'), (-5020, 12197, 'MOVE'), (-4300, 12200, 'MOVE'), (-3426, 12200, 'MOVE'),
        (-3285, 12086, 'MOVE'), (-3212, 11994, 'MOVE'), (-3096, 11889, 'MOVE'), (-2984, 11796, 'MOVE'),
        (-2865, 11640, 'MOVE'), (-2768, 11580, 'MOVE'), (-2687, 11569, 'MOVE'), (-2300, 11567, 'MOVE'),
        (-2082, 11489, 'MOVE'), (-1810, 11358, 'MOVE'), (-1335, 11105, 'MOVE'), (-972, 10893, 'MOVE'),
        (-877, 10841, 'MOVE'), (-874, 10542, 'MOVE'), (-874, 10145, 'MOVE'), (-874, 9894, 'MOVE'),
        (-894, 9549, 'MOVE'), (-894, 9227, 'MOVE'), (-889, 8990, 'MOVE'), (-889, 8963, 'MOVE'),
        (-889, 8677, 'MOVE'), (-687, 8567, 'MOVE'), (-467, 8540, 'MOVE'), (-266, 8537, 'MOVE'),
        (91, 8537, 'MOVE'), (249, 8536, 'MOVE'), (5597, 8550, 'END')
    ]
    route_a.extend(apply_offset(raw_right_ctrl_room, RIGHT_CTRL_ROOM_OFFSET_X, RIGHT_CTRL_ROOM_OFFSET_Y))

    route_b = [(X_RIGHT, Y_TOP, 'MOVE'), (X_RIGHT, 9265, 'MOVE'), (X_RIGHT, 9931, 'MOVE')]
    route_b.extend(get_bezier_curve((X_RIGHT, 9931), (X_RIGHT, 10100), (-3950, 10200)))
    route_b.extend(get_bezier_curve((-3950, 10200), (-3930, 10550), (-4297, 10550)))
    route_b.extend(get_bezier_curve((-4297, 10550), (-4600, 10550), (-4600, 10300)))
    route_b.extend(get_bezier_curve((-4600, 10300), (-4600, Y_MID), (-4524, Y_MID)))
    route_b.extend([(-5086, Y_MID, 'AL_AG_B'), (-5585, Y_MID, 'MOVE')])
    route_b.extend(get_bezier_curve((-5585, Y_MID), (-5700, Y_MID), (-5450, 9600)))
    route_b.extend(get_bezier_curve((-5450, 9600), (-5450, 9250), (-5772, 9250)))
    route_b.extend(get_bezier_curve((-5772, 9250), (-6050, 9250), (-6050, 9600)))
    route_b.extend(get_bezier_curve((-6050, 9600), (-6050, 9850), (-5800, 9850)))
    route_b.extend(get_bezier_curve((-5800, 9850), (X_MID, 9850), (X_MID, 9995)))
    route_b.extend([(X_MID, 9995, 'EXIT_AG_B'), (X_MID, Y_BOT, 'AL_ARCTIC_B'), (-6939, Y_BOT, 'MOVE')])
    route_b.extend(get_bezier_curve((-6939, Y_BOT), (-7050, Y_BOT), (-6950, 10200)))
    route_b.extend(get_bezier_curve((-6950, 10200), (-6950, 10000), (-7282, 10000)))
    route_b.extend(get_bezier_curve((-7282, 10000), (-7550, 10000), (-7550, 10331)))
    route_b.extend(get_bezier_curve((-7550, 10331), (-7550, 10600), (-7450, 10600)))
    route_b.extend(get_bezier_curve((-7450, 10600), (X_FAR_LEFT, 10600), (X_FAR_LEFT, 10763)))
    route_b.extend([(X_FAR_LEFT, 10763, 'EXIT_ARCTIC_B'), (X_FAR_LEFT, 11420, 'MOVE'), (X_FAR_LEFT, Y_DEEP_BOT, 'AL_EXIT_B')])

    raw_left_ctrl_room = [
        (-6615, 11463, 'MOVE'), (-6515, 11593, 'MOVE'), (-6415, 11783, 'MOVE'), (-6335, 12043, 'MOVE'),
        (-6175, 12197, 'MOVE'), (-6064, 12267, 'MOVE'), (-6053, 12457, 'MOVE'), (-6053, 13064, 'MOVE'),
        (-5147, 13064, 'MOVE'), (-3387, 13064, 'MOVE'), (-3387, 12324, 'MOVE'), (-3257, 12104, 'MOVE'),
        (-3157, 11944, 'MOVE'), (-3067, 11794, 'MOVE'), (-2957, 11654, 'MOVE'), (-2827, 11594, 'MOVE'),
        (-2677, 11564, 'MOVE'), (-2537, 11564, 'MOVE'), (-2217, 11564, 'MOVE'), (-2027, 11484, 'MOVE'),
        (-1458, 11164, 'MOVE'), (-888, 10864, 'MOVE'), (-878, 10734, 'MOVE'), (-873, 10484, 'MOVE'),
        (-876, 10268, 'MOVE'), (-872, 10120, 'MOVE'), (-872, 9688, 'MOVE'), (-886, 9423, 'MOVE'),
        (-892, 9208, 'MOVE'), (-894, 9109, 'MOVE'), (-890, 8884, 'MOVE'), (-890, 8665, 'MOVE'),
        (-659, 8589, 'MOVE'), (-437, 8546, 'MOVE'), (-300, 8532, 'MOVE'), (706, 8532, 'MOVE'), (5597, 8550, 'END')
    ]
    route_b.extend(apply_offset(raw_left_ctrl_room, LEFT_CTRL_ROOM_OFFSET_X, LEFT_CTRL_ROOM_OFFSET_Y))

    def get_idx(route, tag):
        return next((i for i, wp in enumerate(route) if len(wp) > 2 and wp[2] == tag), -1)

    A_AG_IN = get_idx(route_a, 'AL_AG_A')

    all_vehicles = []
    cyan_l = RideVehicle(0, 0, (0, 255, 200), "Cyan_L", 'A')
    cyan_r = RideVehicle(0, 0, (0, 255, 200), "Cyan_R", 'B')
    cyan_l.set_route(route_a)
    cyan_r.set_route(route_b)
    cyan_l.active, cyan_r.active = True, True
    all_vehicles.extend([cyan_l, cyan_r])

    next_white_l = RideVehicle(0, 0, (255, 255, 255), "White_L", 'A')
    next_white_r = RideVehicle(0, 0, (255, 255, 255), "White_R", 'B')
    next_white_l.set_route(route_a)
    next_white_r.set_route(route_b)
    next_white_l.is_boarding, next_white_r.is_boarding = True, True
    all_vehicles.extend([next_white_l, next_white_r])

    current_cyan_leader = cyan_r
    current_white_follower = None
    next_cyan_l, next_cyan_r = None, None

    running = True
    while running:
        dt = clock.tick(60)
        simulated_time_ms += dt * current_sim_speed 
        
        if planned_delays and simulated_time_ms >= planned_delays[0]:
            sys_state['delay_active'] = True
            sys_state['delay_timer'] = 30000 
            planned_delays.pop(0) 

        if sys_state['delay_active']:
            sys_state['delay_timer'] -= dt * current_sim_speed
            if sys_state['delay_timer'] <= 0:
                sys_state['delay_active'] = False
                sys_state['delay_timer'] = 0

        current_w, current_h = screen.get_size()
        
        timeline_w = 600
        timeline_x = (current_w - timeline_w) // 2
        timeline_rect = pygame.Rect(timeline_x, current_h - 60, timeline_w, 40) 
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: running = False
                if event.key == pygame.K_h: 
                    camera_x, camera_y = -8400, 7500
                    zoom = 0.080
            if event.type == pygame.MOUSEWHEEL: zoom += event.y * 0.05 * zoom
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: 
                speed_rect = pygame.Rect(current_w - 180, 20, 160, 45)
                
                if speed_rect.collidepoint(event.pos):
                    current_sim_speed = 1.0 if current_sim_speed == 3.0 else 3.0
                elif timeline_rect.collidepoint(event.pos):
                    click_x = event.pos[0] - timeline_x
                    percentage = click_x / timeline_w
                    trigger_time = simulated_time_ms + (percentage * FORECAST_WINDOW_MS)
                    planned_delays.append(trigger_time)
                    planned_delays.sort() 
                else:
                    is_dragging, last_mouse_pos = True, event.pos
                    
            if event.type == pygame.MOUSEBUTTONUP: is_dragging = False
            if event.type == pygame.MOUSEMOTION and is_dragging:
                camera_x -= (event.pos[0] - last_mouse_pos[0]) / zoom
                camera_y -= (event.pos[1] - last_mouse_pos[1]) / zoom
                last_mouse_pos = event.pos

        zoom = max(blueprint.MIN_ZOOM, min(blueprint.MAX_ZOOM, zoom))
        blueprint.camera_x, blueprint.camera_y, blueprint.zoom = camera_x, camera_y, zoom

        # --- DISPATCH LOGIC ---
        if next_white_l and current_cyan_leader:
            progress = min(1.0, current_cyan_leader.current_target_idx / 102.0)
            next_white_l.boarding_progress = next_white_r.boarding_progress = progress
            if current_cyan_leader.current_target_idx > 102:
                next_white_l.is_boarding = next_white_r.is_boarding = False
                next_white_l.active = next_white_r.active = True
                
                # Update Analytics
                total_dispatched_pax += (PASSENGERS_PER_VEHICLE * 2) 
                dispatch_history.append(simulated_time_ms)
                
                current_white_follower = next_white_l
                next_cyan_l, next_cyan_r = RideVehicle(0, 0, (0, 255, 200), "Cyan_L", 'A'), RideVehicle(0, 0, (0, 255, 200), "Cyan_R", 'B')
                next_cyan_l.set_route(route_a); next_cyan_r.set_route(route_b)
                next_cyan_l.is_boarding = next_cyan_r.is_boarding = True
                all_vehicles.extend([next_cyan_l, next_cyan_r])
                next_white_l = next_white_r = None

        if next_cyan_l and current_white_follower:
            progress = min(1.0, current_white_follower.current_target_idx / A_AG_IN)
            next_cyan_l.boarding_progress = next_cyan_r.boarding_progress = progress
            if current_white_follower.current_target_idx > A_AG_IN:
                next_cyan_l.is_boarding = next_cyan_r.is_boarding = False
                next_cyan_l.active = next_cyan_r.active = True
                
                # Update Analytics
                total_dispatched_pax += (PASSENGERS_PER_VEHICLE * 2)
                dispatch_history.append(simulated_time_ms)
                
                current_cyan_leader = next_cyan_r 
                next_white_l, next_white_r = RideVehicle(0, 0, (255, 255, 255), "White_L", 'A'), RideVehicle(0, 0, (255, 255, 255), "White_R", 'B')
                next_white_l.set_route(route_a); next_white_r.set_route(route_b)
                next_white_l.is_boarding = next_white_r.is_boarding = True
                all_vehicles.extend([next_white_l, next_white_r])
                next_cyan_l = next_cyan_r = None

        for v in all_vehicles: v.update(sys_state, current_sim_speed, dt, all_vehicles)

        # --- DRAW ---
        screen.fill(BG_COLOR)
        blueprint.draw_grid(); blueprint.draw_topography(); blueprint.draw_map()
        for v in all_vehicles: v.draw(screen, blueprint.world_to_screen, zoom)
        blueprint.draw_ui(); blueprint.draw_blueprint_details(); blueprint.draw_hover_tooltip(); blueprint.draw_border()
        
        # Speed Button (Kept in top right)
        speed_rect = pygame.Rect(current_w - 180, 20, 160, 45)
        pygame.draw.rect(screen, (0, 255, 100) if current_sim_speed > 1.0 else (100, 100, 100), speed_rect, border_radius=5)
        btn_text = gui_font.render(f"SPEED: {int(current_sim_speed)}x", True, (0, 0, 0) if current_sim_speed > 1.0 else (255, 255, 255))
        screen.blit(btn_text, btn_text.get_rect(center=speed_rect.center))

        # =================================================================
        # --- NEW DASHBOARD PANEL ---
        # =================================================================
        dash_width = 320
        dash_height = 180
        dash_x = current_w - dash_width - 20
        dash_y = 80 # Sits right below the speed button
        
        # Draw translucent background panel
        dash_surface = pygame.Surface((dash_width, dash_height), pygame.SRCALPHA)
        pygame.draw.rect(dash_surface, (10, 20, 40, 200), dash_surface.get_rect(), border_radius=8)
        pygame.draw.rect(dash_surface, (100, 150, 255, 100), dash_surface.get_rect(), width=2, border_radius=8)
        screen.blit(dash_surface, (dash_x, dash_y))
        
        # Title
        title_text = dash_font_title.render("SYSTEM ANALYTICS", True, (150, 200, 255))
        screen.blit(title_text, (dash_x + 15, dash_y + 15))
        
        # Simulated Uptime
        sim_seconds = int(simulated_time_ms / 1000)
        uptime_str = f"{sim_seconds // 3600:02}:{(sim_seconds % 3600) // 60:02}:{sim_seconds % 60:02}"
        screen.blit(dash_font.render(f"Uptime:     {uptime_str}", True, (255, 255, 255)), (dash_x + 15, dash_y + 50))
        
        # Active Vehicles
        active_count = sum(1 for v in all_vehicles if v.active)
        screen.blit(dash_font.render(f"Active Veh: {active_count}", True, (255, 255, 255)), (dash_x + 15, dash_y + 75))
        
        # Total Pax
        screen.blit(dash_font.render(f"Total Pax:  {total_dispatched_pax}", True, (255, 255, 255)), (dash_x + 15, dash_y + 100))
        
        # Rolling PPH Calculation
        # Remove dispatches older than 5 minutes
        recent_dispatches = [t for t in dispatch_history if simulated_time_ms - t <= ROLLING_WINDOW_MS]
        
        if simulated_time_ms > 60000: # Wait 1 minute before showing math to avoid wild spikes
            time_window_hrs = min(simulated_time_ms, ROLLING_WINDOW_MS) / 1000 / 3600
            recent_pax = len(recent_dispatches) * (PASSENGERS_PER_VEHICLE * 2)
            stable_pph = int(recent_pax / time_window_hrs)
            pph_color = (0, 255, 100) if stable_pph > 2400 else (255, 200, 0)
            screen.blit(dash_font.render(f"Target PPH: {stable_pph}", True, pph_color), (dash_x + 15, dash_y + 125))
        else:
            screen.blit(dash_font.render("Target PPH: CALCULATING...", True, (150, 150, 150)), (dash_x + 15, dash_y + 125))

        # Show if System is actively delayed
        if sys_state['delay_active']:
            secs_left = int(sys_state['delay_timer'] / 1000)
            alert_text = dash_font_title.render(f"DELAY ACTIVE: {secs_left}s", True, (255, 50, 50))
            screen.blit(alert_text, (dash_x + 15, dash_y + 155))

        # Timeline Drawing
        timeline_y = current_h - 40
        pygame.draw.line(screen, (150, 150, 150), (timeline_x, timeline_y), (timeline_x + timeline_w, timeline_y), 4)
        
        for pd in planned_delays:
            time_diff = pd - simulated_time_ms
            if 0 <= time_diff <= FORECAST_WINDOW_MS:
                dot_x = timeline_x + int((time_diff / FORECAST_WINDOW_MS) * timeline_w)
                pygame.draw.circle(screen, (255, 50, 50), (dot_x, timeline_y), 8)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()