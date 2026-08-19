import pygame
import pyaudio
import numpy as np
import os
import json
import sys
from pathlib import Path
from PIL import Image, ImageSequence

# ============ РАБОТА С НАСТРОЙКАМИ ============
DOCUMENTS_FOLDER = Path(os.path.expanduser("~/Documents/FruityWidget"))
SETTINGS_FILE = DOCUMENTS_FOLDER / "Config" / "settings.json"

# Настройки по умолчанию
DEFAULT_SETTINGS = {
    "window_width": 200,
    "window_height": 200,
    "frame_delay": 100,
    "smoothing": 0.7,
    "threshold_waiting": 0.05,
    "threshold_hula": 0.15,
    "threshold_stepping": 0.30,
    "threshold_jumping": 0.50,
    "threshold_windmill": 0.70,
    "animation_names": ["waiting", "hula", "stepping", "jumping", "windmill"],
    "held_animation": "held",
    "close_on_escape": True,
    "show_debug": False
}

def load_settings():
    settings_folder = SETTINGS_FILE.parent
    settings_folder.mkdir(parents=True, exist_ok=True)
    
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return DEFAULT_SETTINGS.copy()
    else:
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
        return True
    except:
        return False

# ============ ЗАГРУЗКА АНИМАЦИЙ ============
def load_gif_frames(gif_path):
    frames = []
    try:
        gif = Image.open(gif_path)
        for frame in ImageSequence.Iterator(gif):
            frame_rgba = frame.convert("RGBA")
            mode = frame_rgba.mode
            size = frame_rgba.size
            data = frame_rgba.tobytes()
            surf = pygame.image.fromstring(data, size, mode)
            frames.append(surf)
        return frames
    except:
        return None

def load_all_animations(settings):
    animations = {}
    anim_folder = DOCUMENTS_FOLDER / "Animations"
    
    if not anim_folder.exists():
        anim_folder.mkdir(parents=True, exist_ok=True)
        return None
    
    for name in settings.get("animation_names", []):
        gif_path = anim_folder / f"{name}.gif"
        if gif_path.exists():
            frames = load_gif_frames(gif_path)
            if frames:
                animations[name] = frames
    
    held_name = settings.get("held_animation", "held")
    held_path = anim_folder / f"{held_name}.gif"
    if held_path.exists():
        frames = load_gif_frames(held_path)
        if frames:
            animations["held"] = frames
    
    return animations if animations else None

def create_default_frames(settings):
    default = {}
    colors = {
        "waiting": (100,100,100),
        "hula": (0,200,100),
        "stepping": (200,200,0),
        "jumping": (200,100,0),
        "windmill": (200,0,0),
        "held": (150,50,150)
    }
    
    for name in settings.get("animation_names", []) + ["held"]:
        frames = []
        for i in range(8):
            surf = pygame.Surface((150, 150), pygame.SRCALPHA)
            color = colors.get(name, (150,150,150))
            surf.fill((*color, 200))
            font = pygame.font.SysFont(None, 24)
            text = font.render(f"{name}\n{i+1}/8", True, (255,255,255))
            text_rect = text.get_rect(center=(75,75))
            surf.blit(text, text_rect)
            frames.append(surf)
        default[name] = frames
    return default

# ============ АНАЛИЗ ЗВУКА ============
class AudioAnalyzer:
    def __init__(self, settings):
        self.settings = settings
        self.volume = 0.0
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        self.smoothing = settings.get("smoothing", 0.7)
        self.stream = None
        
        self.p = pyaudio.PyAudio()
        try:
            self.stream = self.p.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk
            )
        except:
            pass
    
    def get_volume(self):
        if self.stream is None:
            return 0.0
        try:
            data = self.stream.read(self.chunk, exception_on_overflow=False)
            audio_data = np.frombuffer(data, dtype=np.int16)
            rms = np.sqrt(np.mean(audio_data.astype(np.float32)**2))
            raw = rms / 32768.0
            self.volume = self.volume * self.smoothing + raw * (1 - self.smoothing)
            return self.volume
        except:
            return self.volume
    
    def close(self):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.p.terminate()

# ============ ВИДЖЕТ ============
class FruityWidget:
    def __init__(self):
        self.settings = load_settings()
        pygame.init()
        
        self.size = (self.settings.get("window_width", 200),
                     self.settings.get("window_height", 200))
        self.screen = pygame.display.set_mode(self.size, pygame.NOFRAME | pygame.SRCALPHA)
        pygame.display.set_caption("FruityWidget")
        
        info = pygame.display.Info()
        self.x = info.current_w // 2 - self.size[0] // 2
        self.y = info.current_h // 2 - self.size[1] // 2
        os.environ['SDL_VIDEO_WINDOW_POS'] = f"{self.x},{self.y}"
        
        self.clock = pygame.time.Clock()
        self.running = True
        self.dragging = False
        self.drag_x = 0
        self.drag_y = 0
        self.is_held = False
        self.show_hint = False
        
        self.animations = load_all_animations(self.settings)
        if not self.animations:
            self.animations = create_default_frames(self.settings)
            self.show_hint = True
        
        self.current_animation = "waiting"
        self.current_frame = 0
        self.frame_timer = 0
        self.frame_delay = self.settings.get("frame_delay", 100)
        
        self.animation_names = self.settings.get("animation_names", 
            ["waiting", "hula", "stepping", "jumping", "windmill"])
        self.thresholds = {
            name: self.settings.get(f"threshold_{name}", 1.0)
            for name in self.animation_names
        }
        
        self.audio = AudioAnalyzer(self.settings)
        
        print("\n🎵 FruityWidget")
        print("="*40)
        print("🖱️ ЛКМ — перетащить | ПКМ — закрыть")
        print("🖱️ Колесико — перезагрузить настройки")
        print("⌨️ ESC — закрыть | R — перезагрузить настройки")
        print("="*40)
    
    def get_animation_by_volume(self, volume):
        for name in self.animation_names:
            if volume < self.thresholds.get(name, 1.0):
                return name
        return self.animation_names[-1] if self.animation_names else "waiting"
    
    def save_position(self):
        self.settings["window_x"] = self.x
        self.settings["window_y"] = self.y
        save_settings(self.settings)
    
    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 3:  # ПКМ — закрыть
                        self.running = False
                        self.save_position()
                    elif event.button == 2:  # Колесико — перезагрузить настройки
                        print("🔄 Перезагружаю настройки...")
                        self.settings = load_settings()
                        self.frame_delay = self.settings.get("frame_delay", 100)
                    elif event.button == 1:  # ЛКМ — перетаскивание
                        self.dragging = True
                        self.is_held = True
                        self.drag_x, self.drag_y = event.pos
                        self.current_frame = 0
                        self.frame_timer = 0
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.dragging = False
                        self.is_held = False
                        self.current_frame = 0
                        self.frame_timer = 0
                elif event.type == pygame.MOUSEMOTION:
                    if self.dragging:
                        new_x = self.x + event.pos[0] - self.drag_x
                        new_y = self.y + event.pos[1] - self.drag_y
                        self.x, self.y = new_x, new_y
                        os.environ['SDL_VIDEO_WINDOW_POS'] = f"{self.x},{self.y}"
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE and self.settings.get("close_on_escape", True):
                        self.running = False
                        self.save_position()
                    elif event.key == pygame.K_r:  # R — перезагрузить настройки
                        print("🔄 Перезагружаю настройки...")
                        self.settings = load_settings()
                        self.frame_delay = self.settings.get("frame_delay", 100)
            
            # Выбор анимации
            if self.is_held and "held" in self.animations:
                current_frames = self.animations["held"]
            else:
                volume = self.audio.get_volume()
                new_animation = self.get_animation_by_volume(volume)
                if new_animation != self.current_animation:
                    self.current_animation = new_animation
                    self.current_frame = 0
                    self.frame_timer = 0
                current_frames = self.animations.get(self.current_animation, [])
            
            # Обновление кадра
            if current_frames:
                self.frame_timer += self.clock.get_time()
                if self.frame_timer >= self.frame_delay:
                    self.frame_timer = 0
                    self.current_frame = (self.current_frame + 1) % len(current_frames)
            else:
                if not hasattr(self, 'fallback_surf'):
                    self.fallback_surf = pygame.Surface((100, 100), pygame.SRCALPHA)
                    self.fallback_surf.fill((200, 50, 50, 200))
                current_frames = [self.fallback_surf]
                self.current_frame = 0
            
            # Рендеринг
            self.screen.fill((0, 0, 0, 0))
            
            if current_frames:
                current_surf = current_frames[self.current_frame % len(current_frames)]
                rect = current_surf.get_rect(center=(self.size[0]//2, self.size[1]//2))
                self.screen.blit(current_surf, rect)
            
            if self.show_hint:
                font = pygame.font.SysFont(None, 16)
                text1 = font.render("Положи GIF в:", True, (255, 255, 255))
                text2 = font.render(str(DOCUMENTS_FOLDER / "Animations"), True, (200, 200, 200))
                self.screen.blit(text1, (10, 10))
                self.screen.blit(text2, (10, 30))
            
            pygame.display.flip()
            self.clock.tick(60)
        
        self.audio.close()
        pygame.quit()

# ============ ЗАПУСК ============
if __name__ == "__main__":
    try:
        widget = FruityWidget()
        widget.run()
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        input("\nНажми Enter, чтобы закрыть...")
