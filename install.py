from os import system

try:
    import pygame
    print('Pygame encontrado')
except Exception:
    system('pip install pygame')

try:
    import moviepy
    print('Moviepy encontrado')
except Exception:
    system('pip install moviepy')

try:
    import cv2 as cv
except Exception:
    print('CV2 encontrado')
    system('pip install opencv-python')

try:
    import progressbar
    print('progressbar encontrado')
except Exception:
    system('pip install progressbar2')

try:
    import fpstimer
    print('fpstimer encontrado')
except Exception:
    system('pip install fpstimer')

try:
    import PIL
    print('Pillow encontrado')
except Exception:
    system('pip install pillow')