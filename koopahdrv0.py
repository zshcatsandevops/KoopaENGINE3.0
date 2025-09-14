# Super Mario Bros 3: Mario Forever Community Edition
# Complete 8-World Engine with Photonic Gaussian Splatting
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

# Game States
class GameState(Enum):
    WORLD_MAP = 1
    LEVEL = 2
    BONUS = 3
    CASTLE = 4
    AIRSHIP = 5
    GAME_OVER = 6
    VICTORY = 7

# Power-up States
class PowerUp(Enum):
    SMALL = 0
    SUPER = 1
    FIRE = 2
    RACCOON = 3
    TANOOKI = 4
    HAMMER = 5
    FROG = 6
    CLOUD = 7

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
        # AlphaEvolve algorithm for particle optimization
        if len(self.particles) > 100:
            # Calculate fitness based on screen coverage
            positions = np.array([p['pos'] for p in self.particles])
            fitness = np.std(positions) / SCREEN_WIDTH
            
            if fitness < self.evolution_params['fitness_threshold']:
                # Mutate particles for better distribution
                for particle in random.sample(self.particles, int(len(self.particles) * self.evolution_params['mutation_rate'])):
                    particle['vel'] += np.random.randn(2) * 0.5
            
            self.evolution_params['generation'] += 1

# ============= SMB3 ENGINE CORE =============
class SMB3Engine:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Super Mario Bros 3: Mario Forever - Photonic Edition")
        self.clock = pygame.time.Clock()
        self.photonic = PhotonicGaussianEngine()
        
        # Game state
        self.state = GameState.WORLD_MAP
        self.current_world = 1
        self.current_level = 1
        self.lives = 5
        self.coins = 0
        self.score = 0
        self.cards = []  # End-level cards
        
        # Mario state
        self.mario = {
            'pos': np.array([100.0, 400.0]),
            'vel': np.array([0.0, 0.0]),
            'power': PowerUp.SMALL,
            'p_meter': 0,  # Running power meter
            'on_ground': False,
            'facing_right': True,
            'invincible': 0,
            'can_shoot': True,
            'shoot_cooldown': 0
        }
        
        # World definitions
        self.worlds = self._define_worlds()
        self.current_level_data = None
        
    def _define_worlds(self):
        return {
            1: {  # Grass Land
                'name': 'Grass Land',
                'theme': 'overworld',
                'boss': 'Larry Koopa',
                'levels': {
                    1: {'type': 'standard', 'exit_type': 'flag', 'secret': False},
                    2: {'type': 'standard', 'exit_type': 'flag', 'secret': True},
                    3: {'type': 'standard', 'exit_type': 'card', 'secret': False},
                    4: {'type': 'fortress', 'exit_type': 'boom_boom', 'secret': False},
                    5: {'type': 'standard', 'exit_type': 'flag', 'secret': True},
                    6: {'type': 'standard', 'exit_type': 'card', 'secret': False},
                    'castle': {'type': 'castle', 'exit_type': 'larry', 'secret': False},
                    'airship': {'type': 'airship', 'exit_type': 'larry_airship', 'secret': False}
                }
            },
            2: {  # Desert Land
                'name': 'Desert Land',
                'theme': 'desert',
                'boss': 'Morton Koopa Jr.',
                'levels': {
                    1: {'type': 'standard', 'exit_type': 'flag', 'secret': False, 'sun': True},
                    2: {'type': 'pyramid', 'exit_type': 'card', 'secret': True},
                    3: {'type': 'standard', 'exit_type': 'flag', 'secret': False},
                    4: {'type': 'quicksand', 'exit_type': 'flag', 'secret': False},
                    5: {'type': 'fortress', 'exit_type': 'boom_boom', 'secret': False},
                    'pyramid': {'type': 'pyramid_inside', 'exit_type': 'treasure', 'secret': True},
                    'castle': {'type': 'castle', 'exit_type': 'morton', 'secret': False},
                    'airship': {'type': 'airship', 'exit_type': 'morton_airship', 'secret': False}
                }
            },
            3: {  # Water Land
                'name': 'Water Land',
                'theme': 'ocean',
                'boss': 'Wendy O. Koopa',
                'levels': {
                    1: {'type': 'water', 'exit_type': 'flag', 'secret': False},
                    2: {'type': 'standard', 'exit_type': 'flag', 'secret': False},
                    3: {'type': 'underwater', 'exit_type': 'pipe', 'secret': True},
                    4: {'type': 'big_island', 'exit_type': 'card', 'secret': False},
                    5: {'type': 'fortress', 'exit_type': 'boom_boom', 'secret': False},
                    6: {'type': 'water', 'exit_type': 'flag', 'secret': False},
                    7: {'type': 'spike', 'exit_type': 'flag', 'secret': False},
                    8: {'type': 'underwater', 'exit_type': 'pipe', 'secret': True},
                    9: {'type': 'bridge', 'exit_type': 'card', 'secret': False},
                    'castle': {'type': 'castle', 'exit_type': 'wendy', 'secret': False},
                    'airship': {'type': 'airship', 'exit_type': 'wendy_airship', 'secret': False}
                }
            },
            4: {  # Giant Land
                'name': 'Giant Land',
                'theme': 'giant',
                'boss': 'Iggy Koopa',
                'levels': {
                    1: {'type': 'giant', 'exit_type': 'flag', 'secret': False},
                    2: {'type': 'giant_pipes', 'exit_type': 'flag', 'secret': False},
                    3: {'type': 'giant_blocks', 'exit_type': 'card', 'secret': False},
                    4: {'type': 'giant_water', 'exit_type': 'flag', 'secret': True},
                    5: {'type': 'fortress', 'exit_type': 'boom_boom', 'secret': False},
                    6: {'type': 'giant_enemies', 'exit_type': 'card', 'secret': False},
                    'castle': {'type': 'castle', 'exit_type': 'iggy', 'secret': False},
                    'airship': {'type': 'airship', 'exit_type': 'iggy_airship', 'secret': False}
                }
            },
            5: {  # Sky Land
                'name': 'Sky Land',
                'theme': 'sky',
                'boss': 'Roy Koopa',
                'levels': {
                    1: {'type': 'clouds', 'exit_type': 'flag', 'secret': False},
                    2: {'type': 'rotating_platforms', 'exit_type': 'flag', 'secret': True},
                    3: {'type': 'chain_chomps', 'exit_type': 'card', 'secret': False},
                    4: {'type': 'parabeetles', 'exit_type': 'flag', 'secret': False},
                    5: {'type': 'fortress', 'exit_type': 'boom_boom', 'secret': False},
                    6: {'type': 'clouds', 'exit_type': 'flag', 'secret': False},
                    7: {'type': 'tower', 'exit_type': 'pipe', 'secret': True},
                    8: {'type': 'parabeetles', 'exit_type': 'card', 'secret': False},
                    9: {'type': 'fortress', 'exit_type': 'boom_boom', 'secret': False},
                    'tower': {'type': 'spiral_tower', 'exit_type': 'treasure', 'secret': True},
                    'castle': {'type': 'castle', 'exit_type': 'roy', 'secret': False},
                    'airship': {'type': 'airship', 'exit_type': 'roy_airship', 'secret': False}
                }
            },
            6: {  # Ice Land
                'name': 'Ice Land',
                'theme': 'ice',
                'boss': 'Lemmy Koopa',
                'levels': {
                    1: {'type': 'ice', 'exit_type': 'flag', 'secret': False},
                    2: {'type': 'ice_blocks', 'exit_type': 'flag', 'secret': False},
                    3: {'type': 'ice_fortress', 'exit_type': 'boom_boom', 'secret': False},
                    4: {'type': 'slippery', 'exit_type': 'card', 'secret': False},
                    5: {'type': 'ice_underwater', 'exit_type': 'pipe', 'secret': True},
                    6: {'type': 'ice', 'exit_type': 'flag', 'secret': False},
                    7: {'type': 'ice_spikes', 'exit_type': 'card', 'secret': False},
                    8: {'type': 'fortress', 'exit_type': 'boom_boom', 'secret': False},
                    9: {'type': 'ice_maze', 'exit_type': 'flag', 'secret': True},
                    10: {'type': 'ice', 'exit_type': 'flag', 'secret': False},
                    'castle': {'type': 'castle', 'exit_type': 'lemmy', 'secret': False},
                    'airship': {'type': 'airship', 'exit_type': 'lemmy_airship', 'secret': False}
                }
            },
            7: {  # Pipe Land
                'name': 'Pipe Land',
                'theme': 'pipes',
                'boss': 'Ludwig von Koopa',
                'levels': {
                    1: {'type': 'pipes', 'exit_type': 'flag', 'secret': False},
                    2: {'type': 'pipe_maze', 'exit_type': 'flag', 'secret': True},
                    3: {'type': 'underwater_pipes', 'exit_type': 'pipe', 'secret': False},
                    4: {'type': 'giant_pipes', 'exit_type': 'card', 'secret': False},
                    5: {'type': 'fortress', 'exit_type': 'boom_boom', 'secret': False},
                    6: {'type': 'piranha_garden', 'exit_type': 'flag', 'secret': False},
                    7: {'type': 'pipe_maze', 'exit_type': 'card', 'secret': True},
                    8: {'type': 'fortress', 'exit_type': 'boom_boom', 'secret': False},
                    9: {'type': 'fast_pipes', 'exit_type': 'flag', 'secret': False},
                    'piranha': {'type': 'piranha_boss', 'exit_type': 'treasure', 'secret': True},
                    'castle': {'type': 'castle', 'exit_type': 'ludwig', 'secret': False},
                    'airship': {'type': 'airship', 'exit_type': 'ludwig_airship', 'secret': False}
                }
            },
            8: {  # Dark Land
                'name': 'Dark Land',
                'theme': 'dark',
                'boss': 'Bowser',
                'levels': {
                    1: {'type': 'tanks', 'exit_type': 'flag', 'secret': False},
                    2: {'type': 'battleships', 'exit_type': 'flag', 'secret': False},
                    'fortress1': {'type': 'fortress', 'exit_type': 'boom_boom', 'secret': False},
                    3: {'type': 'hand_traps', 'exit_type': 'flag', 'secret': False},
                    'airforce': {'type': 'airship_fleet', 'exit_type': 'flag', 'secret': False},
                    'fortress2': {'type': 'fortress', 'exit_type': 'boom_boom', 'secret': False},
                    'super_tank': {'type': 'super_tank', 'exit_type': 'flag', 'secret': False},
                    'bowser_castle': {'type': 'final_castle', 'exit_type': 'bowser', 'secret': False}
                }
            }
        }
    
    # ============= LEVEL GENERATION =============
    def generate_level(self, world_num, level_num):
        world_data = self.worlds[world_num]
        level_info = world_data['levels'].get(level_num, world_data['levels'][1])
        
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
        
        # Generate based on level type
        if level_info['type'] == 'standard':
            level = self._generate_standard_level(world_num)
        elif level_info['type'] == 'water' or level_info['type'] == 'underwater':
            level = self._generate_water_level(world_num)
        elif level_info['type'] == 'fortress':
            level = self._generate_fortress_level(world_num)
        elif level_info['type'] == 'castle':
            level = self._generate_castle_level(world_num)
        elif level_info['type'] == 'airship':
            level = self._generate_airship_level(world_num)
        elif level_info['type'] == 'giant':
            level = self._generate_giant_level(world_num)
        elif level_info['type'] == 'ice':
            level = self._generate_ice_level(world_num)
        elif level_info['type'] == 'pipes':
            level = self._generate_pipe_level(world_num)
        elif level_info['type'] == 'desert' or 'pyramid' in level_info['type']:
            level = self._generate_desert_level(world_num)
        elif level_info['type'] == 'clouds' or level_info['type'] == 'sky':
            level = self._generate_sky_level(world_num)
        elif level_info['type'] == 'tanks' or level_info['type'] == 'battleships':
            level = self._generate_vehicle_level(world_num)
        elif level_info['type'] == 'final_castle':
            level = self._generate_bowser_castle()
        else:
            level = self._generate_standard_level(world_num)
        
        # Add photonic enhancements
        level['photonic_zones'] = self._add_photonic_zones(level_info['type'])
        
        return level
    
    def _generate_standard_level(self, world_num):
        level = {
            'platforms': [],
            'enemies': [],
            'powerups': [],
            'pipes': [],
            'blocks': [],
            'decorations': [],
            'checkpoints': []
        }
        
        # Generate terrain
        y_base = 500
        for x in range(0, 4000, 200):
            width = random.randint(150, 400)
            height = random.randint(20, 100)
            gap = random.randint(50, 150)
            
            # Main platform
            level['platforms'].append({
                'rect': pygame.Rect(x, y_base, width, height),
                'type': 'ground',
                'collision': True
            })
            
            # Floating platforms
            if random.random() > 0.5:
                level['platforms'].append({
                    'rect': pygame.Rect(x + width//2, y_base - 150, 100, 20),
                    'type': 'floating',
                    'collision': True
                })
            
            # Add enemies
            if random.random() > 0.3:
                enemy_type = random.choice(['goomba', 'koopa_green', 'koopa_red', 'hammer_bro'])
                level['enemies'].append({
                    'type': enemy_type,
                    'pos': [x + width//2, y_base - 50],
                    'vel': [-1, 0],
                    'patrol_range': [x, x + width]
                })
            
            # Add blocks
            if random.random() > 0.4:
                block_y = y_base - 200
                for bx in range(x, x + width, 40):
                    if random.random() > 0.6:
                        block_type = random.choice(['brick', 'question', 'hidden'])
                        level['blocks'].append({
                            'rect': pygame.Rect(bx, block_y, 40, 40),
                            'type': block_type,
                            'contains': random.choice(['coin', 'mushroom', 'flower', 'star', 'leaf'])
                            if block_type == 'question' else 'coin',
                            'hit': False
                        })
            
            # Add pipes
            if random.random() > 0.7:
                pipe_height = random.randint(80, 200)
                level['pipes'].append({
                    'rect': pygame.Rect(x + width - 60, y_base - pipe_height, 60, pipe_height),
                    'type': 'green',
                    'enterable': random.random() > 0.7,
                    'destination': 'bonus' if random.random() > 0.5 else 'secret'
                })
        
        return level
    
    def _generate_water_level(self, world_num):
        level = self._generate_standard_level(world_num)
        level['water_line'] = 300
        level['current'] = random.uniform(-0.5, 0.5)
        
        # Add water enemies
        for i in range(20):
            level['enemies'].append({
                'type': random.choice(['cheep_cheep', 'blooper', 'big_bertha']),
                'pos': [random.randint(100, 3900), random.randint(320, 500)],
                'vel': [random.uniform(-2, 2), random.uniform(-1, 1)],
                'patrol_range': [0, 4000]
            })
        
        return level
    
    def _generate_fortress_level(self, world_num):
        level = {
            'platforms': [],
            'enemies': [],
            'powerups': [],
            'blocks': [],
            'hazards': [],
            'checkpoints': []
        }
        
        # Fortress architecture
        for x in range(0, 3000, 300):
            # Floor
            level['platforms'].append({
                'rect': pygame.Rect(x, 550, 300, 50),
                'type': 'fortress_floor',
                'collision': True
            })
            
            # Ceiling
            level['platforms'].append({
                'rect': pygame.Rect(x, 0, 300, 50),
                'type': 'fortress_ceiling',
                'collision': True
            })
            
            # Add thwomps
            if random.random() > 0.6:
                level['hazards'].append({
                    'type': 'thwomp',
                    'pos': [x + 150, 100],
                    'trigger_distance': 100,
                    'fall_speed': 10
                })
            
            # Add roto-discs
            if random.random() > 0.5:
                level['hazards'].append({
                    'type': 'roto_disc',
                    'center': [x + 150, 300],
                    'radius': 100,
                    'speed': 0.05
                })
            
            # Add dry bones
            if random.random() > 0.4:
                level['enemies'].append({
                    'type': 'dry_bones',
                    'pos': [x + 100, 500],
                    'vel': [-0.5, 0],
                    'patrol_range': [x, x + 300]
                })
        
        # Boss room
        level['boss_room'] = {
            'rect': pygame.Rect(2700, 200, 300, 350),
            'boss': 'boom_boom'
        }
        
        return level
    
    def _generate_castle_level(self, world_num):
        level = self._generate_fortress_level(world_num)
        
        # Add lava
        level['lava_y'] = 550
        level['lava_bubbles'] = []
        
        for x in range(0, 3000, 200):
            if random.random() > 0.6:
                level['lava_bubbles'].append({
                    'x': x,
                    'timer': random.randint(0, 120),
                    'height': random.randint(100, 300)
                })
        
        # Koopa Kid boss room
        koopa_kids = ['larry', 'morton', 'wendy', 'iggy', 'roy', 'lemmy', 'ludwig']
        level['boss_room']['boss'] = koopa_kids[world_num - 1] if world_num <= 7 else 'bowser'
        
        return level
    
    def _generate_airship_level(self, world_num):
        level = {
            'platforms': [],
            'enemies': [],
            'powerups': [],
            'cannons': [],
            'propellers': [],
            'checkpoints': [],
            'scroll_speed': 2
        }
        
        # Airship segments
        for x in range(0, 5000, 500):
            # Deck
            level['platforms'].append({
                'rect': pygame.Rect(x, 400, 400, 30),
                'type': 'airship_deck',
                'collision': True
            })
            
            # Masts and platforms
            if random.random() > 0.5:
                level['platforms'].append({
                    'rect': pygame.Rect(x + 200, 300, 100, 20),
                    'type': 'mast_platform',
                    'collision': True
                })
            
            # Cannons
            for cx in range(x, x + 400, 100):
                if random.random() > 0.6:
                    level['cannons'].append({
                        'pos': [cx, 380],
                        'type': random.choice(['standard', 'giant', 'rotating']),
                        'fire_rate': random.randint(60, 180)
                    })
            
            # Rocky Wrench
            if random.random() > 0.5:
                level['enemies'].append({
                    'type': 'rocky_wrench',
                    'pos': [x + random.randint(50, 350), 400],
                    'emerge_timer': random.randint(0, 120)
                })
        
        return level
    
    def _generate_giant_level(self, world_num):
        level = self._generate_standard_level(world_num)
        
        # Scale everything up
        for platform in level['platforms']:
            platform['rect'].width *= 2
            platform['rect'].height *= 2
            platform['rect'].x *= 2
            platform['rect'].y = (platform['rect'].y - 300) * 2 + 300
        
        for enemy in level['enemies']:
            enemy['size_multiplier'] = 2
            enemy['pos'][0] *= 2
            enemy['pos'][1] = (enemy['pos'][1] - 300) * 2 + 300
        
        for block in level['blocks']:
            block['rect'].width *= 2
            block['rect'].height *= 2
            block['rect'].x *= 2
            block['rect'].y = (block['rect'].y - 300) * 2 + 300
        
        return level
    
    def _generate_ice_level(self, world_num):
        level = self._generate_standard_level(world_num)
        
        # Make all platforms slippery
        for platform in level['platforms']:
            platform['friction'] = 0.02  # Very low friction
            platform['type'] = 'ice'
        
        # Add ice-specific enemies
        level['enemies'] = []
        for i in range(15):
            level['enemies'].append({
                'type': random.choice(['flurry', 'cooligan', 'ice_bro']),
                'pos': [random.randint(200, 3800), random.randint(200, 400)],
                'vel': [random.uniform(-1, 1), 0],
                'patrol_range': [0, 4000]
            })
        
        # Add icicles
        level['hazards'] = []
        for x in range(0, 4000, 150):
            if random.random() > 0.6:
                level['hazards'].append({
                    'type': 'icicle',
                    'pos': [x, 50],
                    'falling': False,
                    'trigger_distance': 50
                })
        
        return level
    
    def _generate_pipe_level(self, world_num):
        level = {
            'platforms': [],
            'pipes': [],
            'enemies': [],
            'powerups': [],
            'pipe_network': {},
            'checkpoints': []
        }
        
        # Create pipe maze
        pipe_id = 0
        for x in range(0, 4000, 250):
            for y in range(100, 500, 150):
                if random.random() > 0.3:
                    pipe_height = random.randint(60, 200)
                    orientation = random.choice(['up', 'down', 'left', 'right'])
                    
                    pipe = {
                        'rect': pygame.Rect(x, y, 60, pipe_height),
                        'type': random.choice(['green', 'red', 'yellow']),
                        'orientation': orientation,
                        'id': pipe_id,
                        'connected_to': None
                    }
                    
                    # Create connections
                    if pipe_id > 0 and random.random() > 0.5:
                        pipe['connected_to'] = random.randint(0, pipe_id - 1)
                    
                    level['pipes'].append(pipe)
                    pipe_id += 1
                    
                    # Add piranha plants
                    if random.random() > 0.5:
                        level['enemies'].append({
                            'type': 'piranha_plant',
                            'pipe_id': pipe_id - 1,
                            'pos': [x + 30, y],
                            'emerge_timer': random.randint(0, 180)
                        })
        
        # Add platforms between pipes
        for x in range(0, 4000, 200):
            if random.random() > 0.4:
                level['platforms'].append({
                    'rect': pygame.Rect(x, random.randint(300, 500), 150, 20),
                    'type': 'metal',
                    'collision': True
                })
        
        return level
    
    def _generate_desert_level(self, world_num):
        level = self._generate_standard_level(world_num)
        
        # Add quicksand
        level['quicksand'] = []
        for x in range(500, 3500, 300):
            if random.random() > 0.6:
                level['quicksand'].append({
                    'rect': pygame.Rect(x, 500, 200, 100),
                    'sink_speed': 0.5
                })
        
        # Add angry sun
        level['angry_sun'] = {
            'active': True,
            'pos': [400, 100],
            'attack_timer': 0,
            'attack_cooldown': 300
        }
        
        # Add desert enemies
        for enemy in level['enemies']:
            enemy['type'] = random.choice(['pokey', 'lakitu', 'spiny', 'fire_snake'])
        
        return level
    
    def _generate_sky_level(self, world_num):
        level = {
            'platforms': [],
            'enemies': [],
            'powerups': [],
            'clouds': [],
            'checkpoints': []
        }
        
        # Cloud platforms
        for x in range(0, 5000, 200):
            y = random.randint(100, 450)
            level['clouds'].append({
                'rect': pygame.Rect(x, y, random.randint(100, 250), 30),
                'type': random.choice(['solid', 'bouncy', 'moving']),
                'collision': True,
                'speed': random.uniform(-1, 1) if random.random() > 0.7 else 0
            })
        
        # Flying enemies
        for i in range(30):
            level['enemies'].append({
                'type': random.choice(['paragoomba', 'paratroopa', 'lakitu', 'parabeetle']),
                'pos': [random.randint(100, 4900), random.randint(50, 400)],
                'vel': [random.uniform(-2, 2), random.uniform(-1, 1)],
                'patrol_range': [0, 5000]
            })
        
        # Donut lifts
        for x in range(500, 4500, 400):
            if random.random() > 0.5:
                level['platforms'].append({
                    'rect': pygame.Rect(x, random.randint(200, 400), 80, 20),
                    'type': 'donut_lift',
                    'collision': True,
                    'fall_timer': 0,
                    'falling': False
                })
        
        return level
    
    def _generate_vehicle_level(self, world_num):
        level = {
            'platforms': [],
            'enemies': [],
            'cannons': [],
            'vehicles': [],
            'scroll_speed': 3,
            'checkpoints': []
        }
        
        # Generate tanks/ships
        for x in range(0, 6000, 600):
            vehicle_type = random.choice(['tank', 'battleship'])
            vehicle = {
                'rect': pygame.Rect(x, 450, 500, 100),
                'type': vehicle_type,
                'cannons': [],
                'collision': True
            }
            
            # Add cannons to vehicle
            for cx in range(0, 500, 100):
                if random.random() > 0.4:
                    vehicle['cannons'].append({
                        'offset': [cx, -20],
                        'type': 'rotating',
                        'angle': 0,
                        'fire_timer': random.randint(0, 120)
                    })
            
            level['vehicles'].append(vehicle)
            
            # Add flame jets
            if random.random() > 0.6:
                level['enemies'].append({
                    'type': 'flame_jet',
                    'pos': [x + 250, 430],
                    'direction': random.choice(['up', 'diagonal']),
                    'fire_pattern': random.choice(['continuous', 'burst', 'wave'])
                })
        
        return level
    
    def _generate_bowser_castle(self):
        level = {
            'platforms': [],
            'enemies': [],
            'hazards': [],
            'bowser_arena': None,
            'checkpoints': []
        }
        
        # Pre-boss gauntlet
        for x in range(0, 3000, 200):
            # Platforms
            level['platforms'].append({
                'rect': pygame.Rect(x, 500, 150, 50),
                'type': 'castle_block',
                'collision': True,
                'destructible': random.random() > 0.7
            })
            
            # Hazards
            hazard_type = random.choice(['firebar', 'thwomp', 'laser', 'spike_ceiling'])
            level['hazards'].append({
                'type': hazard_type,
                'pos': [x + 75, random.randint(100, 400)],
                'params': self._get_hazard_params(hazard_type)
            })
        
        # Bowser arena
        level['bowser_arena'] = {
            'rect': pygame.Rect(3000, 200, 800, 400),
            'floor_blocks': [],
            'bowser_spawn': [3400, 300],
            'phases': 3
        }
        
        # Destructible floor
        for x in range(3000, 3800, 40):
            level['bowser_arena']['floor_blocks'].append({
                'rect': pygame.Rect(x, 500, 40, 100),
                'hp': 3,
                'destroyed': False
            })
        
        return level
    
    def _get_hazard_params(self, hazard_type):
        params = {
            'firebar': {'length': random.randint(3, 6), 'speed': random.uniform(0.02, 0.05)},
            'thwomp': {'trigger_distance': 100, 'fall_speed': 12},
            'laser': {'charge_time': 60, 'fire_duration': 30, 'beam_width': 10},
            'spike_ceiling': {'fall_speed': 2, 'rise_speed': 1}
        }
        return params.get(hazard_type, {})
    
    def _add_photonic_zones(self, level_type):
        zones = []
        
        # Define photonic enhancement zones based on level type
        zone_configs = {
            'standard': {'particle_density': 500, 'color': (100, 255, 100), 'effect': 'nature'},
            'water': {'particle_density': 1000, 'color': (100, 150, 255), 'effect': 'caustics'},
            'fortress': {'particle_density': 300, 'color': (255, 100, 100), 'effect': 'embers'},
            'castle': {'particle_density': 800, 'color': (255, 150, 50), 'effect': 'lava_glow'},
            'airship': {'particle_density': 600, 'color': (200, 200, 255), 'effect': 'wind_particles'},
            'ice': {'particle_density': 700, 'color': (200, 230, 255), 'effect': 'snow'},
            'pipes': {'particle_density': 400, 'color': (50, 255, 50), 'effect': 'steam'},
            'desert': {'particle_density': 900, 'color': (255, 220, 150), 'effect': 'sand'},
            'clouds': {'particle_density': 1200, 'color': (255, 255, 255), 'effect': 'cloud_wisps'},
            'final_castle': {'particle_density': 1500, 'color': (255, 50, 50), 'effect': 'chaos'}
        }
        
        config = zone_configs.get(level_type, zone_configs['standard'])
        
        # Create zones throughout level
        for x in range(0, 5000, 500):
            zones.append({
                'rect': pygame.Rect(x, 0, 500, 600),
                'config': config,
                'intensity': random.uniform(0.5, 1.0)
            })
        
        return zones
    
    # ============= RENDERING =============
    def render_game(self):
        if self.state == GameState.WORLD_MAP:
            self.render_world_map()
        elif self.state == GameState.LEVEL:
            self.render_level()
        elif self.state == GameState.CASTLE:
            self.render_castle()
        elif self.state == GameState.AIRSHIP:
            self.render_airship()
    
    def render_level(self):
        # Background gradient with photonic enhancement
        for y in range(SCREEN_HEIGHT):
            color_val = int(50 + (y/SCREEN_HEIGHT) * 150)
            pygame.draw.line(self.screen, 
                           (color_val//3, color_val//2, color_val),
                           (0, y), (SCREEN_WIDTH, y))
        
        if not self.current_level_data:
            return
        
        # Camera offset
        camera_x = max(0, self.mario['pos'][0] - SCREEN_WIDTH//2)
        
        # Render platforms with photonic edges
        for platform in self.current_level_data.get('platforms', []):
            rect = platform['rect'].copy()
            rect.x -= camera_x
            
            if rect.right > 0 and rect.left < SCREEN_WIDTH:
                # Platform base
                color = {
                    'ground': (139, 69, 19),
                    'ice': (200, 230, 255),
                    'metal': (150, 150, 150),
                    'fortress_floor': (100, 100, 100),
                    'castle_block': (80, 80, 80),
                    'airship_deck': (120, 80, 40)
                }.get(platform['type'], (100, 100, 100))
                
                pygame.draw.rect(self.screen, color, rect)
                
                # Photonic edge glow
                for i in range(5):
                    px = rect.x + random.randint(0, rect.width)
                    py = rect.y
                    self.photonic.emit_photon_burst(px, py, 3, color, 2)
        
        # Render blocks
        for block in self.current_level_data.get('blocks', []):
            if not block['hit']:
                rect = block['rect'].copy()
                rect.x -= camera_x
                
                if rect.right > 0 and rect.left < SCREEN_WIDTH:
                    color = {
                        'brick': (150, 75, 0),
                        'question': (255, 200, 0) if not block['hit'] else (100, 100, 100),
                        'hidden': (0, 0, 0, 0)
                    }.get(block['type'], (100, 100, 100))
                    
                    if block['type'] != 'hidden' or block['hit']:
                        pygame.draw.rect(self.screen, color, rect)
                        
                        # Question block animation
                        if block['type'] == 'question' and not block['hit']:
                            glow = abs(math.sin(pygame.time.get_ticks() * 0.005)) * 50
                            self.photonic.emit_photon_burst(
                                rect.centerx, rect.centery, 
                                int(glow/10), (255, 255, 100), 3
                            )
        
        # Render enemies with trails
        for enemy in self.current_level_data.get('enemies', []):
            ex = enemy['pos'][0] - camera_x
            ey = enemy['pos'][1]
            
            if 0 < ex < SCREEN_WIDTH:
                enemy_colors = {
                    'goomba': (150, 75, 0),
                    'koopa_green': (0, 200, 0),
                    'koopa_red': (200, 0, 0),
                    'hammer_bro': (50, 150, 50),
                    'dry_bones': (200, 200, 200),
                    'lakitu': (100, 100, 100),
                    'piranha_plant': (200, 0, 0)
                }
                
                color = enemy_colors.get(enemy['type'], (100, 100, 100))
                size = enemy.get('size_multiplier', 1)
                
                pygame.draw.rect(self.screen, color,
                               (ex, ey, 30*size, 30*size))
                
                # Enemy particle trail
                self.photonic.emit_photon_burst(
                    ex + 15*size, ey + 30*size,
                    5, color, 3
                )
        
        # Render pipes
        for pipe in self.current_level_data.get('pipes', []):
            rect = pipe['rect'].copy()
            rect.x -= camera_x
            
            if rect.right > 0 and rect.left < SCREEN_WIDTH:
                pipe_color = {
                    'green': (0, 200, 0),
                    'red': (200, 0, 0),
                    'yellow': (200, 200, 0)
                }.get(pipe['type'], (0, 150, 0))
                
                pygame.draw.rect(self.screen, pipe_color, rect)
                pygame.draw.rect(self.screen, (0, 0, 0), rect, 3)
                
                # Pipe top
                top_rect = pygame.Rect(rect.x - 10, rect.y, rect.width + 20, 30)
                pygame.draw.rect(self.screen, pipe_color, top_rect)
                pygame.draw.rect(self.screen, (0, 0, 0), top_rect, 3)
        
        # Render Mario with power-up state
        mx = self.mario['pos'][0] - camera_x
        my = self.mario['pos'][1]
        
        if 0 <= mx <= SCREEN_WIDTH:
            mario_colors = {
                PowerUp.SMALL: (255, 0, 0),
                PowerUp.SUPER: (255, 0, 0),
                PowerUp.FIRE: (255, 100, 100),
                PowerUp.RACCOON: (150, 75, 0),
                PowerUp.TANOOKI: (150, 100, 50),
                PowerUp.HAMMER: (100, 100, 100),
                PowerUp.FROG: (0, 200, 0)
            }
            
            color = mario_colors.get(self.mario['power'], (255, 0, 0))
            height = 40 if self.mario['power'] != PowerUp.SMALL else 30
            
            pygame.draw.rect(self.screen, color, (mx, my, 30, height))
            
            # P-meter visualization
            if self.mario['p_meter'] > 0:
                meter_width = int(self.mario['p_meter'] / 100 * 60)
                pygame.draw.rect(self.screen, (255, 255, 0),
                               (mx - 15, my - 10, meter_width, 5))
                
                # Speed particles
                for i in range(int(self.mario['p_meter'] / 20)):
                    self.photonic.emit_photon_burst(
                        mx, my + height,
                        10, (255, 255, 100), 5
                    )
            
            # Invincibility stars
            if self.mario['invincible'] > 0:
                for i in range(10):
                    angle = (pygame.time.get_ticks() * 0.01 + i * 36) % 360
                    sx = mx + 15 + math.cos(math.radians(angle)) * 40
                    sy = my + height//2 + math.sin(math.radians(angle)) * 40
                    self.photonic.emit_photon_burst(sx, sy, 5, 
                                                   (random.randint(100, 255),
                                                    random.randint(100, 255),
                                                    random.randint(100, 255)), 2)
        
        # Update and render particles
        self.photonic.evolve_particles()
        for particle in self.photonic.particles[:]:
            particle['pos'][0] += particle['vel'][0]
            particle['pos'][1] += particle['vel'][1]
            particle['vel'][1] += 0.1  # Gravity
            particle['life'] -= 2
            
            if particle['life'] <= 0:
                self.photonic.particles.remove(particle)
            else:
                # Render particle with gaussian splat
                px = particle['pos'][0] - camera_x
                py = particle['pos'][1]
                
                if 0 <= px <= SCREEN_WIDTH:
                    alpha = particle['life']
                    color = tuple(particle['color'])
                    
                    # Gaussian blur effect
                    for dx in range(-3, 4):
                        for dy in range(-3, 4):
                            dist = math.sqrt(dx*dx + dy*dy)
                            if dist < 3:
                                blur_alpha = int(alpha * math.exp(-dist*dist/2))
                                if blur_alpha > 0:
                                    s = pygame.Surface((2, 2))
                                    s.set_alpha(blur_alpha)
                                    s.fill(color)
                                    self.screen.blit(s, (px + dx, py + dy))
        
        # HUD
        self.render_hud()
    
    def render_world_map(self):
        # World map background
        world_colors = {
            1: (100, 200, 100),  # Grass Land
            2: (255, 220, 150),  # Desert Land
            3: (100, 150, 255),  # Water Land
            4: (150, 100, 50),   # Giant Land
            5: (200, 230, 255),  # Sky Land
            6: (180, 220, 255),  # Ice Land
            7: (50, 150, 50),    # Pipe Land
            8: (50, 50, 50)      # Dark Land
        }
        
        bg_color = world_colors.get(self.current_world, (100, 100, 100))
        self.screen.fill(bg_color)
        
        # Draw world name
        font = pygame.font.Font(None, 48)
        world_name = self.worlds[self.current_world]['name']
        text = font.render(world_name, True, (255, 255, 255))
        self.screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 50))
        
        # Draw level nodes
        levels = self.worlds[self.current_world]['levels']
        node_positions = self._calculate_node_positions(len(levels))
        
        for i, (level_key, level_data) in enumerate(levels.items()):
            x, y = node_positions[i]
            
            # Node color based on completion
            color = (255, 255, 0)  # Current level
            if i < self.current_level - 1:
                color = (0, 255, 0)  # Completed
            elif i > self.current_level - 1:
                color = (100, 100, 100)  # Locked
            
            pygame.draw.circle(self.screen, color, (x, y), 20)
            
            # Level label
            label = str(level_key) if isinstance(level_key, int) else level_key[:3].upper()
            font = pygame.font.Font(None, 16)
            text = font.render(label, True, (0, 0, 0))
            self.screen.blit(text, (x - 10, y - 8))
            
            # Draw paths between nodes
            if i > 0:
                prev_x, prev_y = node_positions[i-1]
                pygame.draw.line(self.screen, (255, 255, 255),
                               (prev_x, prev_y), (x, y), 3)
            
            # Add photonic effects to current node
            if i == self.current_level - 1:
                for j in range(5):
                    angle = (pygame.time.get_ticks() * 0.01 + j * 72) % 360
                    px = x + math.cos(math.radians(angle)) * 30
                    py = y + math.sin(math.radians(angle)) * 30
                    self.photonic.emit_photon_burst(px, py, 2, (255, 255, 100), 1)
        
        # Mario icon on current level
        current_pos = node_positions[min(self.current_level - 1, len(node_positions) - 1)]
        pygame.draw.rect(self.screen, (255, 0, 0),
                        (current_pos[0] - 5, current_pos[1] - 25, 10, 15))
        
        # Update particles
        for particle in self.photonic.particles[:]:
            particle['pos'][0] += particle['vel'][0]
            particle['pos'][1] += particle['vel'][1]
            particle['life'] -= 3
            
            if particle['life'] <= 0:
                self.photonic.particles.remove(particle)
            else:
                pygame.draw.circle(self.screen, tuple(particle['color']),
                                 (int(particle['pos'][0]), int(particle['pos'][1])),
                                 max(1, particle['life'] // 50))
    
    def _calculate_node_positions(self, num_nodes):
        positions = []
        rows = 3
        cols = (num_nodes + rows - 1) // rows
        
        for i in range(num_nodes):
            row = i // cols
            col = i % cols
            
            x = 150 + col * 150
            y = 200 + row * 120
            
            # Zigzag pattern for odd rows
            if row % 2 == 1:
                x = SCREEN_WIDTH - x
            
            positions.append((x, y))
        
        return positions
    
    def render_hud(self):
        # Score
        font = pygame.font.Font(None, 24)
        score_text = font.render(f"SCORE: {self.score:07d}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))
        
        # Coins
        coin_text = font.render(f"COINS: {self.coins:02d}", True, (255, 255, 0))
        self.screen.blit(coin_text, (10, 35))
        
        # Lives
        lives_text = font.render(f"LIVES: {self.lives}", True, (255, 255, 255))
        self.screen.blit(lives_text, (10, 60))
        
        # World and Level
        level_text = font.render(f"WORLD {self.current_world}-{self.current_level}", 
                                True, (255, 255, 255))
        self.screen.blit(level_text, (SCREEN_WIDTH - 150, 10))
        
        # Power-up
        power_names = {
            PowerUp.SMALL: "SMALL",
            PowerUp.SUPER: "SUPER",
            PowerUp.FIRE: "FIRE",
            PowerUp.RACCOON: "RACCOON",
            PowerUp.TANOOKI: "TANOOKI",
            PowerUp.HAMMER: "HAMMER",
            PowerUp.FROG: "FROG"
        }
        power_text = font.render(power_names.get(self.mario['power'], ""), 
                                True, (255, 255, 255))
        self.screen.blit(power_text, (SCREEN_WIDTH - 150, 35))
        
        # P-Meter
        if self.mario['p_meter'] > 0:
            pygame.draw.rect(self.screen, (100, 100, 100),
                           (SCREEN_WIDTH - 150, 60, 100, 10))
            pygame.draw.rect(self.screen, (255, 255, 0),
                           (SCREEN_WIDTH - 150, 60, self.mario['p_meter'], 10))
        
        # Cards collected
        for i, card in enumerate(self.cards[-3:]):
            card_colors = {
                'mushroom': (255, 0, 0),
                'flower': (255, 255, 0),
                'star': (255, 255, 255)
            }
            pygame.draw.rect(self.screen, card_colors.get(card, (100, 100, 100)),
                           (SCREEN_WIDTH - 50 - i*20, 80, 15, 20))
    
    # ============= GAME LOGIC =============
    def update(self):
        if self.state == GameState.LEVEL:
            self.update_level()
        elif self.state == GameState.WORLD_MAP:
            self.update_world_map()
    
    def update_level(self):
        # Update Mario physics
        self.update_mario_physics()
        
        # Update enemies
        if self.current_level_data:
            for enemy in self.current_level_data.get('enemies', []):
                self.update_enemy(enemy)
        
        # Update P-meter
        if abs(self.mario['vel'][0]) > 4:
            self.mario['p_meter'] = min(100, self.mario['p_meter'] + 2)
        else:
            self.mario['p_meter'] = max(0, self.mario['p_meter'] - 1)
        
        # Update invincibility
        if self.mario['invincible'] > 0:
            self.mario['invincible'] -= 1
        
        # Check level completion
        # (Implementation would check if Mario reached the end)
    
    def update_mario_physics(self):
        # Gravity
        if not self.mario['on_ground']:
            self.mario['vel'][1] += 0.5
        
        # Max fall speed
        self.mario['vel'][1] = min(self.mario['vel'][1], 15)
        
        # Update position
        self.mario['pos'][0] += self.mario['vel'][0]
        self.mario['pos'][1] += self.mario['vel'][1]
        
        # Platform collision
        if self.current_level_data:
            self.mario['on_ground'] = False
            mario_rect = pygame.Rect(self.mario['pos'][0], self.mario['pos'][1],
                                    30, 40 if self.mario['power'] != PowerUp.SMALL else 30)
            
            for platform in self.current_level_data.get('platforms', []):
                if platform['collision'] and mario_rect.colliderect(platform['rect']):
                    if self.mario['vel'][1] > 0:  # Falling
                        self.mario['pos'][1] = platform['rect'].top - mario_rect.height
                        self.mario['vel'][1] = 0
                        self.mario['on_ground'] = True
                        
                        # Apply ice physics
                        if platform.get('friction'):
                            self.mario['vel'][0] *= (1 - platform['friction'])
    
    def update_enemy(self, enemy):
        # Basic enemy movement
        enemy['pos'][0] += enemy['vel'][0]
        enemy['pos'][1] += enemy['vel'][1]
        
        # Patrol boundaries
        if 'patrol_range' in enemy:
            if enemy['pos'][0] < enemy['patrol_range'][0] or \
               enemy['pos'][0] > enemy['patrol_range'][1]:
                enemy['vel'][0] *= -1
        
        # Special enemy behaviors
        if enemy['type'] == 'lakitu':
            # Float above Mario
            target_x = self.mario['pos'][0]
            enemy['pos'][0] += (target_x - enemy['pos'][0]) * 0.02
        elif enemy['type'] == 'hammer_bro':
            # Jump occasionally
            if random.random() < 0.01 and enemy.get('on_ground', True):
                enemy['vel'][1] = -8
    
    def update_world_map(self):
        # World map navigation handled by input
        pass
    
    def handle_input(self, keys):
        if self.state == GameState.LEVEL:
            # Left/Right movement
            if keys[pygame.K_LEFT]:
                self.mario['vel'][0] = -5 if not keys[pygame.K_LSHIFT] else -8
                self.mario['facing_right'] = False
            elif keys[pygame.K_RIGHT]:
                self.mario['vel'][0] = 5 if not keys[pygame.K_LSHIFT] else 8
                self.mario['facing_right'] = True
            else:
                self.mario['vel'][0] *= 0.9
            
            # Jump
            if keys[pygame.K_SPACE] and self.mario['on_ground']:
                jump_power = -12
                if self.mario['power'] == PowerUp.FROG:
                    jump_power = -15
                elif self.mario['p_meter'] >= 100:
                    jump_power = -14
                
                self.mario['vel'][1] = jump_power
                
                # Jump particles
                for i in range(10):
                    self.photonic.emit_photon_burst(
                        self.mario['pos'][0] + 15,
                        self.mario['pos'][1] + 40,
                        10, (255, 255, 100), 5
                    )
            
            # Fire/Hammer/Tail attack
            if keys[pygame.K_LCTRL] and self.mario['can_shoot']:
                if self.mario['power'] == PowerUp.FIRE:
                    self.shoot_fireball()
                elif self.mario['power'] == PowerUp.HAMMER:
                    self.throw_hammer()
                elif self.mario['power'] in [PowerUp.RACCOON, PowerUp.TANOOKI]:
                    self.tail_whip()
                
                self.mario['can_shoot'] = False
                self.mario['shoot_cooldown'] = 20
            
            # Cooldown
            if self.mario['shoot_cooldown'] > 0:
                self.mario['shoot_cooldown'] -= 1
            else:
                self.mario['can_shoot'] = True
        
        elif self.state == GameState.WORLD_MAP:
            # Navigate world map
            if keys[pygame.K_LEFT]:
                self.current_level = max(1, self.current_level - 1)
            elif keys[pygame.K_RIGHT]:
                max_level = len(self.worlds[self.current_world]['levels'])
                self.current_level = min(max_level, self.current_level + 1)
            elif keys[pygame.K_RETURN]:
                # Enter level
                self.state = GameState.LEVEL
                self.current_level_data = self.generate_level(self.current_world, 
                                                             self.current_level)
    
    def shoot_fireball(self):
        # Fireball logic
        direction = 1 if self.mario['facing_right'] else -1
        self.photonic.emit_photon_burst(
            self.mario['pos'][0] + (30 if direction > 0 else 0),
            self.mario['pos'][1] + 20,
            20, (255, 100, 0), 8
        )
    
    def throw_hammer(self):
        # Hammer throw logic
        direction = 1 if self.mario['facing_right'] else -1
        self.photonic.emit_photon_burst(
            self.mario['pos'][0] + (30 if direction > 0 else 0),
            self.mario['pos'][1],
            15, (150, 150, 150), 6
        )
    
    def tail_whip(self):
        # Tail attack logic
        self.photonic.emit_photon_burst(
            self.mario['pos'][0] + 15,
            self.mario['pos'][1] + 20,
            30, (150, 75, 0), 10
        )
    
    def run(self):
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # Toggle between world map and level
                        if self.state == GameState.LEVEL:
                            self.state = GameState.WORLD_MAP
                        elif self.state == GameState.WORLD_MAP:
                            self.state = GameState.LEVEL
                    
                    # Debug: Switch worlds with number keys
                    if pygame.K_1 <= event.key <= pygame.K_8:
                        self.current_world = event.key - pygame.K_0
                        self.current_level = 1
                        self.state = GameState.WORLD_MAP
                    
                    # Debug: Change power-up with P key
                    if event.key == pygame.K_p:
                        powers = list(PowerUp)
                        current_index = powers.index(self.mario['power'])
                        self.mario['power'] = powers[(current_index + 1) % len(powers)]
            
            # Handle continuous input
            keys = pygame.key.get_pressed()
            self.handle_input(keys)
            
            # Update game state
            self.update()
            
            # Render
            self.render_game()
            
            # Update display
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()

# ============= MAIN EXECUTION =============
if __name__ == "__main__":
    print("=" * 60)
    print("SUPER MARIO BROS 3: MARIO FOREVER")
    print("PHOTONIC GAUSSIAN SPLATTING EDITION")
    print("=" * 60)
    print("\nControls:")
    print("Arrow Keys - Move")
    print("Space - Jump")
    print("Shift - Run")
    print("Ctrl - Fire/Attack")
    print("1-8 - Switch Worlds")
    print("P - Cycle Power-ups")
    print("ESC - Toggle World Map/Level")
    print("Enter - Select Level (on World Map)")
    print("\n" + "=" * 60)
    
    # Initialize and run the game
    game = SMB3Engine()
    game.run()
