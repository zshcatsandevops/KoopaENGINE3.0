# Super Mario Bros 3: Mario Forever Community Edition
# Fixed Controls and Physics - Photonic Gaussian Splatting Engine
# CatOS 0.4 IndyCat-Evolve Compatible

import pygame
import numpy as np
import random
import math
import json
from collections import deque
from enum import Enum
from dataclasses import dataclass

# Initialize Pygame
pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Mario Forever Physics Constants
MARIO_WALK_SPEED = 3.5
MARIO_RUN_SPEED = 6.5
MARIO_MAX_SPEED = 8.0
MARIO_ACCELERATION = 0.3
MARIO_FRICTION = 0.15
MARIO_AIR_FRICTION = 0.05
MARIO_JUMP_POWER = -11.5
MARIO_RUN_JUMP_POWER = -13.0
MARIO_GRAVITY = 0.45
MARIO_MAX_FALL = 12.0
MARIO_JUMP_HOLD_GRAVITY = 0.25  # Reduced gravity when holding jump

# Game States
class GameState(Enum):
    WORLD_MAP = 1
    LEVEL = 2
    BONUS = 3
    CASTLE = 4
    AIRSHIP = 5
    GAME_OVER = 6
    VICTORY = 7
    PAUSE = 8

# Power-up States (Mario Forever style)
class PowerUp(Enum):
    SMALL = 0
    SUPER = 1
    FIRE = 2
    BEET = 3  # Mario Forever special
    HAMMER = 4
    TANOOKI = 5

# ============= PHOTONIC ENGINE =============
class PhotonicGaussianEngine:
    def __init__(self):
        self.particles = []
        self.gaussian_kernel = self._create_gaussian_kernel(5, 1.0)
        self.splat_buffer = np.zeros((SCREEN_WIDTH, SCREEN_HEIGHT, 4))
        self.light_sources = []
        self.photon_limit = 10000
        self.evolution_params = {
            'mutation_rate': 0.1,
            'fitness_threshold': 0.7,
            'generation': 0
        }
        
    def _create_gaussian_kernel(self, size, sigma):
        kernel = np.zeros((size, size))
        center = size // 2
        for i in range(size):
            for j in range(size):
                x, y = i - center, j - center
                kernel[i, j] = np.exp(-(x**2 + y**2) / (2 * sigma**2))
        return kernel / kernel.sum()
    
    def emit_photon_burst(self, x, y, count, color, spread=10):
        for _ in range(min(count, self.photon_limit - len(self.particles))):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, spread)
            self.particles.append({
                'pos': np.array([x, y], dtype=float),
                'vel': np.array([math.cos(angle) * speed, math.sin(angle) * speed]),
                'color': np.array(color),
                'life': 255,
                'trail': deque(maxlen=15),
                'type': 'burst'
            })
    
    def evolve_particles(self):
        if len(self.particles) > 100:
            positions = np.array([p['pos'] for p in self.particles])
            fitness = np.std(positions) / SCREEN_WIDTH
            
            if fitness < self.evolution_params['fitness_threshold']:
                for particle in random.sample(self.particles, int(len(self.particles) * self.evolution_params['mutation_rate'])):
                    particle['vel'] += np.random.randn(2) * 0.5
            
            self.evolution_params['generation'] += 1

# ============= SMB3 MARIO FOREVER ENGINE =============
class MarioForeverEngine:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Super Mario Bros 3: Mario Forever Community Edition")
        self.clock = pygame.time.Clock()
        self.photonic = PhotonicGaussianEngine()
        
        # Game state
        self.state = GameState.WORLD_MAP
        self.current_world = 1
        self.current_level = 1
        self.lives = 5
        self.coins = 0
        self.score = 0
        self.time = 400
        self.paused = False
        
        # Mario state - Mario Forever style
        self.mario = {
            'pos': np.array([100.0, 400.0]),
            'vel': np.array([0.0, 0.0]),
            'power': PowerUp.SMALL,
            'on_ground': False,
            'facing_right': True,
            'invincible': 0,
            'can_shoot': True,
            'shoot_cooldown': 0,
            'running': False,
            'jumping': False,
            'jump_held': False,
            'jump_timer': 0,
            'ducking': False,
            'in_pipe': False,
            'animation_frame': 0,
            'animation_timer': 0
        }
        
        # Control settings (Mario Forever defaults)
        self.controls = {
            'left': pygame.K_LEFT,
            'right': pygame.K_RIGHT,
            'jump': pygame.K_z,  # Z key for jump
            'run': pygame.K_x,   # X key for run/fire
            'down': pygame.K_DOWN,
            'up': pygame.K_UP,
            'pause': pygame.K_ESCAPE
        }
        
        # Alternative controls
        self.alt_controls = {
            'jump': [pygame.K_UP, pygame.K_w],  # Up arrow or W also jumps
            'run': [pygame.K_LSHIFT, pygame.K_LCTRL]  # Shift/Ctrl also runs
        }
        
        # World definitions
        self.worlds = self._define_worlds()
        self.current_level_data = None
        
        # Sound flags (for future implementation)
        self.sounds_enabled = True
        self.music_enabled = True
        
    def _define_worlds(self):
        """Define all 8 worlds Mario Forever style"""
        return {
            1: {  # Grass Land
                'name': 'Grass Land',
                'theme': 'overworld',
                'boss': 'Larry Koopa',
                'time_limit': 400,
                'levels': {
                    1: {'type': 'standard', 'exit_type': 'flag', 'bonus_areas': 2},
                    2: {'type': 'underground', 'exit_type': 'flag', 'bonus_areas': 1},
                    3: {'type': 'athletic', 'exit_type': 'flag', 'bonus_areas': 1},
                    4: {'type': 'fortress', 'exit_type': 'boss', 'bonus_areas': 0},
                    5: {'type': 'standard', 'exit_type': 'flag', 'bonus_areas': 3},
                    'castle': {'type': 'castle', 'exit_type': 'koopaling', 'bonus_areas': 0}
                }
            },
            2: {  # Desert Land
                'name': 'Desert Land',
                'theme': 'desert',
                'boss': 'Morton Koopa Jr.',
                'time_limit': 400,
                'levels': {
                    1: {'type': 'desert', 'exit_type': 'flag', 'angry_sun': True},
                    2: {'type': 'pyramid', 'exit_type': 'flag', 'bonus_areas': 2},
                    3: {'type': 'quicksand', 'exit_type': 'flag', 'bonus_areas': 1},
                    4: {'type': 'fortress', 'exit_type': 'boss', 'bonus_areas': 0},
                    5: {'type': 'oasis', 'exit_type': 'flag', 'bonus_areas': 1},
                    'castle': {'type': 'castle', 'exit_type': 'koopaling', 'bonus_areas': 0}
                }
            },
            3: {  # Water Land
                'name': 'Water Land',
                'theme': 'ocean',
                'boss': 'Wendy O. Koopa',
                'time_limit': 400,
                'levels': {
                    1: {'type': 'water', 'exit_type': 'flag', 'bonus_areas': 1},
                    2: {'type': 'bridge', 'exit_type': 'flag', 'bonus_areas': 2},
                    3: {'type': 'underwater', 'exit_type': 'pipe', 'bonus_areas': 1},
                    4: {'type': 'fortress', 'exit_type': 'boss', 'bonus_areas': 0},
                    5: {'type': 'island', 'exit_type': 'flag', 'bonus_areas': 2},
                    6: {'type': 'underwater', 'exit_type': 'flag', 'bonus_areas': 1},
                    'castle': {'type': 'castle', 'exit_type': 'koopaling', 'bonus_areas': 0}
                }
            },
            4: {  # Giant Land
                'name': 'Giant Land',
                'theme': 'giant',
                'boss': 'Iggy Koopa',
                'time_limit': 400,
                'levels': {
                    1: {'type': 'giant', 'exit_type': 'flag', 'bonus_areas': 2},
                    2: {'type': 'giant_enemies', 'exit_type': 'flag', 'bonus_areas': 1},
                    3: {'type': 'giant_blocks', 'exit_type': 'flag', 'bonus_areas': 2},
                    4: {'type': 'fortress', 'exit_type': 'boss', 'bonus_areas': 0},
                    5: {'type': 'giant_pipes', 'exit_type': 'flag', 'bonus_areas': 3},
                    'castle': {'type': 'castle', 'exit_type': 'koopaling', 'bonus_areas': 0}
                }
            },
            5: {  # Sky Land
                'name': 'Sky Land',
                'theme': 'sky',
                'boss': 'Roy Koopa',
                'time_limit': 400,
                'levels': {
                    1: {'type': 'clouds', 'exit_type': 'flag', 'bonus_areas': 2},
                    2: {'type': 'athletic', 'exit_type': 'flag', 'bonus_areas': 1},
                    3: {'type': 'tower', 'exit_type': 'door', 'bonus_areas': 2},
                    4: {'type': 'fortress', 'exit_type': 'boss', 'bonus_areas': 0},
                    5: {'type': 'airship', 'exit_type': 'pipe', 'bonus_areas': 1},
                    6: {'type': 'clouds', 'exit_type': 'flag', 'bonus_areas': 2},
                    'castle': {'type': 'castle', 'exit_type': 'koopaling', 'bonus_areas': 0}
                }
            },
            6: {  # Ice Land
                'name': 'Ice Land',
                'theme': 'ice',
                'boss': 'Lemmy Koopa',
                'time_limit': 400,
                'levels': {
                    1: {'type': 'ice', 'exit_type': 'flag', 'bonus_areas': 1},
                    2: {'type': 'cave', 'exit_type': 'flag', 'bonus_areas': 2},
                    3: {'type': 'slippery', 'exit_type': 'flag', 'bonus_areas': 1},
                    4: {'type': 'fortress', 'exit_type': 'boss', 'bonus_areas': 0},
                    5: {'type': 'frozen_pipes', 'exit_type': 'flag', 'bonus_areas': 2},
                    6: {'type': 'ice_bridge', 'exit_type': 'flag', 'bonus_areas': 1},
                    'castle': {'type': 'castle', 'exit_type': 'koopaling', 'bonus_areas': 0}
                }
            },
            7: {  # Pipe Land
                'name': 'Pipe Land',
                'theme': 'pipes',
                'boss': 'Ludwig von Koopa',
                'time_limit': 400,
                'levels': {
                    1: {'type': 'pipes', 'exit_type': 'flag', 'bonus_areas': 3},
                    2: {'type': 'maze', 'exit_type': 'flag', 'bonus_areas': 2},
                    3: {'type': 'underwater_pipes', 'exit_type': 'pipe', 'bonus_areas': 1},
                    4: {'type': 'fortress', 'exit_type': 'boss', 'bonus_areas': 0},
                    5: {'type': 'piranha_garden', 'exit_type': 'flag', 'bonus_areas': 2},
                    6: {'type': 'vertical', 'exit_type': 'flag', 'bonus_areas': 1},
                    'castle': {'type': 'castle', 'exit_type': 'koopaling', 'bonus_areas': 0}
                }
            },
            8: {  # Dark Land
                'name': 'Dark Land',
                'theme': 'dark',
                'boss': 'Bowser',
                'time_limit': 500,
                'levels': {
                    1: {'type': 'tanks', 'exit_type': 'flag', 'bonus_areas': 0},
                    2: {'type': 'fortress', 'exit_type': 'boss', 'bonus_areas': 0},
                    3: {'type': 'battleships', 'exit_type': 'flag', 'bonus_areas': 0},
                    4: {'type': 'fortress', 'exit_type': 'boss', 'bonus_areas': 0},
                    5: {'type': 'airforce', 'exit_type': 'flag', 'bonus_areas': 0},
                    'castle': {'type': 'bowser_castle', 'exit_type': 'bowser', 'bonus_areas': 0}
                }
            }
        }
    
    # ============= MARIO PHYSICS (MARIO FOREVER STYLE) =============
    def update_mario_physics(self):
        """Update Mario with Mario Forever physics"""
        
        # Store previous position for collision detection
        prev_pos = self.mario['pos'].copy()
        
        # Horizontal movement
        target_speed = 0
        if self.mario['running']:
            max_speed = MARIO_RUN_SPEED
        else:
            max_speed = MARIO_WALK_SPEED
        
        # Apply acceleration
        if self.mario['vel'][0] < target_speed:
            self.mario['vel'][0] = min(self.mario['vel'][0] + MARIO_ACCELERATION, target_speed)
        elif self.mario['vel'][0] > target_speed:
            self.mario['vel'][0] = max(self.mario['vel'][0] - MARIO_ACCELERATION, target_speed)
        
        # Apply friction
        if self.mario['on_ground']:
            if abs(self.mario['vel'][0]) < MARIO_FRICTION:
                self.mario['vel'][0] = 0
            else:
                self.mario['vel'][0] *= (1 - MARIO_FRICTION)
        else:
            self.mario['vel'][0] *= (1 - MARIO_AIR_FRICTION)
        
        # Vertical movement (gravity)
        if not self.mario['on_ground']:
            # Variable jump height - less gravity when holding jump button
            if self.mario['jump_held'] and self.mario['vel'][1] < 0:
                self.mario['vel'][1] += MARIO_JUMP_HOLD_GRAVITY
            else:
                self.mario['vel'][1] += MARIO_GRAVITY
            
            # Terminal velocity
            self.mario['vel'][1] = min(self.mario['vel'][1], MARIO_MAX_FALL)
        
        # Update position
        self.mario['pos'][0] += self.mario['vel'][0]
        self.mario['pos'][1] += self.mario['vel'][1]
        
        # Level boundaries
        self.mario['pos'][0] = max(0, self.mario['pos'][0])
        
        # Check collisions
        self.check_collisions()
        
        # Update animation
        self.update_mario_animation()
    
    def check_collisions(self):
        """Check Mario collisions with level geometry"""
        if not self.current_level_data:
            return
        
        mario_rect = self.get_mario_rect()
        self.mario['on_ground'] = False
        
        # Platform collisions
        for platform in self.current_level_data.get('platforms', []):
            if platform['collision'] and mario_rect.colliderect(platform['rect']):
                # Landing on top
                if self.mario['vel'][1] > 0 and mario_rect.bottom > platform['rect'].top:
                    self.mario['pos'][1] = platform['rect'].top - mario_rect.height
                    self.mario['vel'][1] = 0
                    self.mario['on_ground'] = True
                    self.mario['jump_timer'] = 0
                # Hitting from below
                elif self.mario['vel'][1] < 0 and mario_rect.top < platform['rect'].bottom:
                    self.mario['pos'][1] = platform['rect'].bottom
                    self.mario['vel'][1] = 0
                # Side collisions
                elif self.mario['vel'][0] > 0 and mario_rect.right > platform['rect'].left:
                    self.mario['pos'][0] = platform['rect'].left - mario_rect.width
                    self.mario['vel'][0] = 0
                elif self.mario['vel'][0] < 0 and mario_rect.left < platform['rect'].right:
                    self.mario['pos'][0] = platform['rect'].right
                    self.mario['vel'][0] = 0
        
        # Block collisions
        for block in self.current_level_data.get('blocks', []):
            if not block.get('hit', False) and mario_rect.colliderect(block['rect']):
                # Hit from below
                if self.mario['vel'][1] < 0 and mario_rect.top < block['rect'].bottom:
                    self.hit_block(block)
                    self.mario['pos'][1] = block['rect'].bottom
                    self.mario['vel'][1] = 1  # Small bounce down
        
        # Enemy collisions
        for enemy in self.current_level_data.get('enemies', []):
            enemy_rect = pygame.Rect(enemy['pos'][0], enemy['pos'][1], 30, 30)
            if mario_rect.colliderect(enemy_rect):
                if self.mario['invincible'] > 0:
                    # Destroy enemy
                    self.current_level_data['enemies'].remove(enemy)
                    self.score += 100
                    self.photonic.emit_photon_burst(enemy['pos'][0], enemy['pos'][1], 20, (255, 255, 0), 10)
                elif self.mario['vel'][1] > 0 and mario_rect.bottom < enemy_rect.centery:
                    # Stomp enemy
                    self.current_level_data['enemies'].remove(enemy)
                    self.score += 100
                    self.mario['vel'][1] = -8  # Bounce
                    self.photonic.emit_photon_burst(enemy['pos'][0], enemy['pos'][1], 15, (255, 100, 0), 8)
                else:
                    # Take damage
                    self.damage_mario()
    
    def get_mario_rect(self):
        """Get Mario's collision rectangle"""
        width = 24
        if self.mario['power'] == PowerUp.SMALL:
            height = 30
        else:
            height = 40
            if self.mario['ducking']:
                height = 30
        
        return pygame.Rect(self.mario['pos'][0], self.mario['pos'][1], width, height)
    
    def hit_block(self, block):
        """Handle block hit"""
        if block['type'] == 'question' and not block['hit']:
            block['hit'] = True
            contents = block.get('contains', 'coin')
            
            if contents == 'coin':
                self.coins += 1
                self.score += 200
                self.photonic.emit_photon_burst(block['rect'].centerx, block['rect'].top, 10, (255, 255, 0), 5)
            elif contents == 'mushroom':
                if self.mario['power'] == PowerUp.SMALL:
                    self.mario['power'] = PowerUp.SUPER
                else:
                    self.score += 1000
                self.photonic.emit_photon_burst(block['rect'].centerx, block['rect'].top, 15, (255, 0, 0), 7)
            elif contents == 'flower':
                self.mario['power'] = PowerUp.FIRE
                self.photonic.emit_photon_burst(block['rect'].centerx, block['rect'].top, 15, (255, 150, 0), 7)
            elif contents == 'star':
                self.mario['invincible'] = 600  # 10 seconds
                self.photonic.emit_photon_burst(block['rect'].centerx, block['rect'].top, 20, (255, 255, 100), 10)
        elif block['type'] == 'brick':
            if self.mario['power'] != PowerUp.SMALL:
                # Destroy brick
                block['hit'] = True
                self.score += 50
                self.photonic.emit_photon_burst(block['rect'].centerx, block['rect'].centery, 25, (150, 75, 0), 12)
    
    def damage_mario(self):
        """Handle Mario taking damage"""
        if self.mario['invincible'] > 0:
            return
        
        if self.mario['power'] != PowerUp.SMALL:
            self.mario['power'] = PowerUp.SMALL
            self.mario['invincible'] = 120  # 2 seconds of invincibility
            self.photonic.emit_photon_burst(self.mario['pos'][0], self.mario['pos'][1], 20, (255, 0, 0), 10)
        else:
            self.lives -= 1
            if self.lives <= 0:
                self.state = GameState.GAME_OVER
            else:
                # Reset level
                self.reset_level()
    
    def update_mario_animation(self):
        """Update Mario's animation frame"""
        self.mario['animation_timer'] += 1
        
        if self.mario['on_ground']:
            if abs(self.mario['vel'][0]) > 0.5:
                # Walking/running animation
                if self.mario['animation_timer'] % 8 == 0:
                    self.mario['animation_frame'] = (self.mario['animation_frame'] + 1) % 3
            else:
                # Standing
                self.mario['animation_frame'] = 0
        else:
            # Jumping
            self.mario['animation_frame'] = 4
    
    def reset_level(self):
        """Reset current level"""
        self.mario['pos'] = np.array([100.0, 400.0])
        self.mario['vel'] = np.array([0.0, 0.0])
        self.mario['invincible'] = 0
        self.time = 400
        self.current_level_data = self.generate_level(self.current_world, self.current_level)
    
    # ============= INPUT HANDLING =============
    def handle_input(self):
        """Handle input Mario Forever style"""
        keys = pygame.key.get_pressed()
        
        if self.state == GameState.LEVEL:
            # Pause
            if keys[self.controls['pause']]:
                self.paused = not self.paused
                return
            
            if self.paused:
                return
            
            # Movement
            moving = False
            if keys[self.controls['left']]:
                self.mario['vel'][0] = -MARIO_WALK_SPEED if not self.mario['running'] else -MARIO_RUN_SPEED
                self.mario['facing_right'] = False
                moving = True
            elif keys[self.controls['right']]:
                self.mario['vel'][0] = MARIO_WALK_SPEED if not self.mario['running'] else MARIO_RUN_SPEED
                self.mario['facing_right'] = True
                moving = True
            
            # Run button (also fire when powered up)
            self.mario['running'] = keys[self.controls['run']] or any(keys[k] for k in self.alt_controls['run'])
            
            if self.mario['running'] and self.mario['power'] == PowerUp.FIRE and self.mario['can_shoot']:
                self.shoot_fireball()
                self.mario['can_shoot'] = False
                self.mario['shoot_cooldown'] = 15
            
            # Jump button
            jump_pressed = keys[self.controls['jump']] or any(keys[k] for k in self.alt_controls['jump'])
            
            if jump_pressed:
                if self.mario['on_ground'] and not self.mario['jumping']:
                    # Start jump
                    jump_power = MARIO_RUN_JUMP_POWER if abs(self.mario['vel'][0]) > MARIO_WALK_SPEED else MARIO_JUMP_POWER
                    self.mario['vel'][1] = jump_power
                    self.mario['jumping'] = True
                    self.mario['jump_timer'] = 0
                    
                    # Jump particles
                    for i in range(8):
                        self.photonic.emit_photon_burst(
                            self.mario['pos'][0] + 12,
                            self.mario['pos'][1] + 30,
                            8, (200, 200, 100), 4
                        )
                
                self.mario['jump_held'] = True
            else:
                self.mario['jumping'] = False
                self.mario['jump_held'] = False
            
            # Duck
            self.mario['ducking'] = keys[self.controls['down']] and self.mario['on_ground']
            
            # Enter pipe
            if keys[self.controls['down']] and self.mario['on_ground']:
                # Check if on pipe
                for pipe in self.current_level_data.get('pipes', []):
                    mario_rect = self.get_mario_rect()
                    if pipe.get('enterable', False) and mario_rect.colliderect(pipe['rect']):
                        self.enter_pipe(pipe)
            
            # Shoot cooldown
            if self.mario['shoot_cooldown'] > 0:
                self.mario['shoot_cooldown'] -= 1
            else:
                self.mario['can_shoot'] = True
        
        elif self.state == GameState.WORLD_MAP:
            # World map navigation
            pass  # Simplified for this version
    
    def shoot_fireball(self):
        """Shoot fireball Mario Forever style"""
        if self.mario['power'] != PowerUp.FIRE:
            return
        
        direction = 1 if self.mario['facing_right'] else -1
        fireball_x = self.mario['pos'][0] + (24 if direction > 0 else 0)
        fireball_y = self.mario['pos'][1] + 20
        
        # Create fireball entity (simplified)
        self.photonic.emit_photon_burst(fireball_x, fireball_y, 15, (255, 100, 0), 6)
    
    def enter_pipe(self, pipe):
        """Enter a pipe"""
        self.mario['in_pipe'] = True
        # Teleport to bonus area or different location
        # Simplified for this version
        self.photonic.emit_photon_burst(
            self.mario['pos'][0], self.mario['pos'][1],
            20, (0, 255, 0), 8
        )
    
    # ============= LEVEL GENERATION =============
    def generate_level(self, world_num, level_num):
        """Generate a Mario Forever style level"""
        level = {
            'platforms': [],
            'enemies': [],
            'powerups': [],
            'pipes': [],
            'blocks': [],
            'decorations': [],
            'checkpoints': [],
            'exit': None
        }
        
        # Ground generation
        for x in range(0, 5000, 200):
            # Random gaps
            if random.random() > 0.8:
                continue
            
            level['platforms'].append({
                'rect': pygame.Rect(x, 500, 200, 100),
                'type': 'ground',
                'collision': True
            })
            
            # Floating platforms
            if random.random() > 0.6:
                plat_y = random.randint(300, 450)
                level['platforms'].append({
                    'rect': pygame.Rect(x + 50, plat_y, 100, 20),
                    'type': 'floating',
                    'collision': True
                })
            
            # Question blocks
            if random.random() > 0.7:
                block_y = random.randint(300, 400)
                for i in range(random.randint(1, 4)):
                    level['blocks'].append({
                        'rect': pygame.Rect(x + i*40, block_y, 32, 32),
                        'type': 'question',
                        'contains': random.choice(['coin', 'mushroom', 'flower', 'star']),
                        'hit': False
                    })
            
            # Enemies
            if random.random() > 0.5:
                level['enemies'].append({
                    'type': random.choice(['goomba', 'koopa_green', 'koopa_red']),
                    'pos': [x + random.randint(20, 180), 470],
                    'vel': [-1, 0],
                    'patrol_range': [x, x + 200]
                })
            
            # Pipes
            if random.random() > 0.8:
                pipe_height = random.randint(60, 150)
                level['pipes'].append({
                    'rect': pygame.Rect(x + 100, 500 - pipe_height, 64, pipe_height),
                    'type': 'green',
                    'enterable': random.random() > 0.5,
                    'destination': 'bonus'
                })
        
        # End flag
        level['exit'] = {
            'pos': [4800, 400],
            'type': 'flag'
        }
        
        return level
    
    # ============= RENDERING =============
    def render(self):
        """Main render function"""
        if self.state == GameState.LEVEL:
            self.render_level()
        elif self.state == GameState.WORLD_MAP:
            self.render_world_map()
        elif self.state == GameState.GAME_OVER:
            self.render_game_over()
    
    def render_level(self):
        """Render level Mario Forever style"""
        # Sky gradient
        for y in range(SCREEN_HEIGHT):
            blue = min(255, 100 + y // 4)
            self.screen.fill((100, 150, blue), (0, y, SCREEN_WIDTH, 1))
        
        if not self.current_level_data:
            return
        
        # Camera
        camera_x = max(0, min(self.mario['pos'][0] - SCREEN_WIDTH//3, 5000 - SCREEN_WIDTH))
        
        # Render platforms
        for platform in self.current_level_data.get('platforms', []):
            rect = platform['rect'].copy()
            rect.x -= camera_x
            
            if -100 < rect.x < SCREEN_WIDTH + 100:
                color = (139, 69, 19) if platform['type'] == 'ground' else (150, 150, 150)
                pygame.draw.rect(self.screen, color, rect)
                
                # Photonic edge glow
                if random.random() < 0.1:
                    self.photonic.emit_photon_burst(
                        rect.x + random.randint(0, rect.width),
                        rect.y, 2, color, 1
                    )
        
        # Render blocks
        for block in self.current_level_data.get('blocks', []):
            if not block.get('hit', False):
                rect = block['rect'].copy()
                rect.x -= camera_x
                
                if -50 < rect.x < SCREEN_WIDTH + 50:
                    if block['type'] == 'question':
                        color = (255, 200, 0)
                        pygame.draw.rect(self.screen, color, rect)
                        pygame.draw.rect(self.screen, (200, 150, 0), rect, 2)
                        
                        # Question mark
                        font = pygame.font.Font(None, 24)
                        text = font.render("?", True, (255, 255, 255))
                        self.screen.blit(text, (rect.x + 10, rect.y + 4))
                    elif block['type'] == 'brick':
                        color = (150, 75, 0)
                        pygame.draw.rect(self.screen, color, rect)
                        pygame.draw.rect(self.screen, (100, 50, 0), rect, 2)
        
        # Render pipes
        for pipe in self.current_level_data.get('pipes', []):
            rect = pipe['rect'].copy()
            rect.x -= camera_x
            
            if -100 < rect.x < SCREEN_WIDTH + 100:
                # Pipe body
                pygame.draw.rect(self.screen, (0, 200, 0), rect)
                pygame.draw.rect(self.screen, (0, 150, 0), rect, 3)
                
                # Pipe top
                top_rect = pygame.Rect(rect.x - 8, rect.y, rect.width + 16, 32)
                pygame.draw.rect(self.screen, (0, 200, 0), top_rect)
                pygame.draw.rect(self.screen, (0, 150, 0), top_rect, 3)
        
        # Render enemies
        for enemy in self.current_level_data.get('enemies', []):
            ex = enemy['pos'][0] - camera_x
            ey = enemy['pos'][1]
            
            if -50 < ex < SCREEN_WIDTH + 50:
                colors = {
                    'goomba': (150, 75, 0),
                    'koopa_green': (0, 200, 0),
                    'koopa_red': (200, 0, 0)
                }
                color = colors.get(enemy['type'], (100, 100, 100))
                pygame.draw.rect(self.screen, color, (ex, ey, 30, 30))
                
                # Enemy eyes
                pygame.draw.circle(self.screen, (255, 255, 255), (int(ex + 8), int(ey + 10)), 4)
                pygame.draw.circle(self.screen, (255, 255, 255), (int(ex + 22), int(ey + 10)), 4)
                pygame.draw.circle(self.screen, (0, 0, 0), (int(ex + 8), int(ey + 10)), 2)
                pygame.draw.circle(self.screen, (0, 0, 0), (int(ex + 22), int(ey + 10)), 2)
        
        # Render Mario
        mx = self.mario['pos'][0] - camera_x
        my = self.mario['pos'][1]
        
        if -50 < mx < SCREEN_WIDTH + 50:
            mario_rect = self.get_mario_rect()
            mario_rect.x -= camera_x
            
            # Mario colors based on power-up
            colors = {
                PowerUp.SMALL: (255, 0, 0),
                PowerUp.SUPER: (255, 0, 0),
                PowerUp.FIRE: (255, 100, 100),
                PowerUp.BEET: (200, 0, 200),
                PowerUp.HAMMER: (100, 100, 100),
                PowerUp.TANOOKI: (150, 75, 0)
            }
            color = colors.get(self.mario['power'], (255, 0, 0))
            
            # Draw Mario
            pygame.draw.rect(self.screen, color, mario_rect)
            
            # Mario details
            if self.mario['power'] != PowerUp.SMALL:
                # Hat
                pygame.draw.rect(self.screen, color, (mario_rect.x, mario_rect.y, mario_rect.width, 8))
            
            # Face
            face_color = (255, 220, 177)
            pygame.draw.rect(self.screen, face_color, 
                           (mario_rect.x + 4, mario_rect.y + 8, mario_rect.width - 8, 10))
            
            # Eyes
            eye_x = mario_rect.x + (16 if self.mario['facing_right'] else 4)
            pygame.draw.circle(self.screen, (0, 0, 0), (eye_x, mario_rect.y + 12), 2)
            
            # Invincibility effect
            if self.mario['invincible'] > 0:
                if self.mario['invincible'] % 4 < 2:  # Flashing
                    for i in range(5):
                        angle = (pygame.time.get_ticks() * 0.02 + i * 72) % 360
                        sx = mx + 12 + math.cos(math.radians(angle)) * 25
                        sy = my + 20 + math.sin(math.radians(angle)) * 25
                        pygame.draw.circle(self.screen, 
                                         (random.randint(100, 255), 
                                          random.randint(100, 255), 
                                          random.randint(100, 255)), 
                                         (int(sx), int(sy)), 3)
        
        # Update and render particles
        for particle in self.photonic.particles[:]:
            particle['pos'][0] += particle['vel'][0]
            particle['pos'][1] += particle['vel'][1]
            particle['vel'][1] += 0.2
            particle['life'] -= 3
            
            if particle['life'] <= 0:
                self.photonic.particles.remove(particle)
            else:
                px = particle['pos'][0] - camera_x
                py = particle['pos'][1]
                
                if 0 <= px <= SCREEN_WIDTH:
                    alpha = min(255, particle['life'])
                    color = tuple(map(int, particle['color']))
                    size = max(1, particle['life'] // 100)
                    pygame.draw.circle(self.screen, color, (int(px), int(py)), size)
        
        # HUD
        self.render_hud()
    
    def render_hud(self):
        """Render HUD Mario Forever style"""
        # Black bar at top
        pygame.draw.rect(self.screen, (0, 0, 0), (0, 0, SCREEN_WIDTH, 40))
        
        font = pygame.font.Font(None, 24)
        
        # Score
        score_text = font.render(f"SCORE: {self.score:06d}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))
        
        # Coins
        coin_text = font.render(f"x{self.coins:02d}", True, (255, 255, 0))
        self.screen.blit(coin_text, (200, 10))
        pygame.draw.circle(self.screen, (255, 255, 0), (190, 20), 8)
        
        # World
        world_text = font.render(f"WORLD {self.current_world}-{self.current_level}", True, (255, 255, 255))
        self.screen.blit(world_text, (350, 10))
        
        # Time
        time_color = (255, 255, 255) if self.time > 100 else (255, 0, 0)
        time_text = font.render(f"TIME: {self.time:03d}", True, time_color)
        self.screen.blit(time_text, (550, 10))
        
        # Lives
        lives_text = font.render(f"x{self.lives}", True, (255, 255, 255))
        self.screen.blit(lives_text, (700, 10))
        # Mario icon
        pygame.draw.rect(self.screen, (255, 0, 0), (680, 12, 12, 16))
    
    def render_world_map(self):
        """Render world map"""
        self.screen.fill((100, 150, 200))
        
        font = pygame.font.Font(None, 48)
        title = font.render("WORLD MAP", True, (255, 255, 255))
        self.screen.blit(title, (SCREEN_WIDTH//2 - 100, 50))
        
        font = pygame.font.Font(None, 32)
        text = font.render(f"World {self.current_world}: {self.worlds[self.current_world]['name']}", 
                          True, (255, 255, 255))
        self.screen.blit(text, (SCREEN_WIDTH//2 - 150, 150))
        
        text = font.render("Press Z to start level", True, (255, 255, 255))
        self.screen.blit(text, (SCREEN_WIDTH//2 - 120, 300))
    
    def render_game_over(self):
        """Render game over screen"""
        self.screen.fill((0, 0, 0))
        
        font = pygame.font.Font(None, 72)
        text = font.render("GAME OVER", True, (255, 0, 0))
        self.screen.blit(text, (SCREEN_WIDTH//2 - 180, SCREEN_HEIGHT//2 - 50))
        
        font = pygame.font.Font(None, 32)
        text = font.render(f"Final Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(text, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 50))
    
    # ============= MAIN GAME LOOP =============
    def run(self):
        """Main game loop"""
        running = True
        
        # Start in level for testing
        self.state = GameState.LEVEL
        self.current_level_data = self.generate_level(self.current_world, self.current_level)
        
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if self.state == GameState.WORLD_MAP:
                        if event.key == self.controls['jump']:
                            self.state = GameState.LEVEL
                            self.current_level_data = self.generate_level(
                                self.current_world, self.current_level
                            )
                    elif self.state == GameState.GAME_OVER:
                        if event.key == pygame.K_RETURN:
                            self.__init__()  # Reset game
            
            # Update
            if self.state == GameState.LEVEL and not self.paused:
                self.handle_input()
                self.update_mario_physics()
                
                # Update timer
                if pygame.time.get_ticks() % 1000 < 16:  # Once per second
                    self.time -= 1
                    if self.time <= 0:
                        self.damage_mario()
                        self.time = 400
                
                # Update invincibility
                if self.mario['invincible'] > 0:
                    self.mario['invincible'] -= 1
            
            # Render
            self.render()
            
            # Update display
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()

# ============= MAIN EXECUTION =============
if __name__ == "__main__":
    print("=" * 60)
    print("SUPER MARIO BROS 3: MARIO FOREVER COMMUNITY EDITION")
    print("Photonic Gaussian Splatting Engine")
    print("=" * 60)
    print("\nControls:")
    print("Arrow Keys - Move")
    print("Z - Jump (also Up Arrow)")
    print("X - Run/Fire (also Shift)")
    print("Down - Duck/Enter Pipe")
    print("ESC - Pause")
    print("\n" + "=" * 60)
    
    game = MarioForeverEngine()
    game.run()
