import pygame
import time


class Sound:
    sound = ""
    freq = 44100
    pygame.mixer.init(freq)

    def play_sound(self, file_name):
        self.sound = pygame.mixer.Sound(file_name)
        self.sound.play()

    def stop_sound(self):
        self.sound.stop()

    def get_busy(self):
        return pygame.mixer.get_busy()


if __name__ == '__main__':
    app = Sound()
