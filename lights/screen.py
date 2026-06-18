import os
import threading
from typing import Iterable
import tools

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import pygame


FPS = 60

_colors: list[tuple[int, int, int]] = [(0, 0, 0)]
_colors_lock = threading.Lock()
_window_thread: threading.Thread | None = None
_running = False


def _clamp_channel(value: int) -> int:
	return max(0, min(255, int(value)))


def _sanitize_colors(values: Iterable[Iterable[int]]) -> list[tuple[int, int, int]]:
	sanitized: list[tuple[int, int, int]] = []
	for item in values:
		if isinstance(item, (list, tuple)) and len(item) == 3:
			r, g, b = item
			sanitized.append((_clamp_channel(r), _clamp_channel(g), _clamp_channel(b)))
	return sanitized or [(0, 0, 0)]


def set_colors(new_colors: list[list[int]]) -> None:
	global _colors
	with _colors_lock:
		_colors = _sanitize_colors(new_colors)


def _draw_columns(surface: pygame.Surface, colors: list[tuple[int, int, int]]) -> None:
	width, height = surface.get_size()
	if width <= 0 or height <= 0:
		return
	
	colors = tools.batch_gamma_correction(colors.copy())

	if len(colors) == 1:
		surface.fill(colors[0])
		return

	# Resize color list to current window width using nearest-neighbor mapping.
	for x in range(width):
		idx = (x * len(colors)) // width
		pygame.draw.line(surface, colors[idx], (x, 0), (x, height))


def run_window() -> None:
	global _running
	pygame.init()
	clock = pygame.time.Clock()

	info = pygame.display.Info()
	start_size = (max(320, info.current_w // 2), max(240, info.current_h // 2))
	surface = pygame.display.set_mode(start_size, pygame.RESIZABLE)
	pygame.display.set_caption("light show")

	while _running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				_running = False
			elif event.type == pygame.VIDEORESIZE:
				surface = pygame.display.set_mode((max(1, event.w), max(1, event.h)), pygame.RESIZABLE)

		with _colors_lock:
			colors_snapshot = list(_colors)

		_draw_columns(surface, colors_snapshot)
		pygame.display.flip()
		clock.tick(FPS)

	pygame.quit()


def start_window() -> None:
	global _window_thread, _running
	if _window_thread is not None and _window_thread.is_alive():
		return

	_running = True
	_window_thread = threading.Thread(target=run_window, daemon=True)
	_window_thread.start()


def stop_window() -> None:
	global _running
	_running = False

if __name__ == "__main__":
	start_window()
	import time
	while True:
		set_colors([(255, 0, 0), (0, 255, 0), (0, 0, 255)])
		time.sleep(1)
		set_colors([(255, 255, 0), (0, 255, 255), (255, 0, 255)])
		time.sleep(1)