import moviepy.editor as mp
import sys
from os import name, system
import cv2 as cv
from PIL import Image
import progressbar
import fpstimer
from pygame import mixer
from threading import Thread

class AsciiPlayer:
    def __init__(self, path) -> None:
        self.preparar_directorios()
        self._path = path
        self._ascii_frames = []
        self._height = 60
        self._width = 170

    @classmethod
    def preparar_directorios(cls):
        if name == 'nt':
            system('mkdir .\\files\\output')
        else:
            system('mkdir ./files/output')

    def verificar_archivos(self, ruta: str) -> bool:
        try:
            with open(ruta, 'r'):
                return True
        except Exception:
            return False

    def convertir_audio(self) -> None:
        if self.verificar_archivos('./files/bad_apple.mp3'):
            sys.stdout.write('El archivo de audio ya existe')
        else:
            audio = mp.VideoFileClip(self._path)
            audio.audio.write_audiofile('./files/bad_apple.mp3')

    def contar_frames(self) -> int:
        video = cv.VideoCapture(self._path)
        nFrames = int(video.get(cv.CAP_PROP_FRAME_COUNT))
        return nFrames
    
    def obtener_fps(self) -> float:
        video = cv.VideoCapture(self._path)
        fps = float(video.get(cv.CAP_PROP_FPS))
        return fps

    def obtener_frames(self) -> None:
        capturas = cv.VideoCapture(self._path)
        nFrame = 0
        progreso = progressbar.ProgressBar(max_value=self.contar_frames())
        progreso.start()
        while(True):
            success, frame = capturas.read()
            if success:
                if self.verificar_archivos(f'./files/output/frame_{nFrame}.jpg') == False:
                    cv.imwrite(f'./files/output/frame_{nFrame}.jpg', frame)
            else:
                break
            nFrame += 1

            progreso.update(nFrame)

        progreso.finish()
        capturas.release()

    def obtener_ascii(self) -> None:
        if self.verificar_archivos('./files/frames.txt'):
            return
        ASCII_CHARS = [' ', ':', '!', '*', '%', '$', 'S', 'O', '&', '#', '@']

        for i in range(self.contar_frames()):
            try:
                frame = Image.open('./files/output/frame_%s.jpg'%i)
                frame = frame.resize(size=[self._width, self._height])

                frame = frame.convert('L')
                pixel_data = frame.getdata()

                new_pixel = ''.join(ASCII_CHARS[pixel//25] for pixel in pixel_data)

                count_pixels = len(new_pixel)
                img_ascii = [new_pixel[index: index + self._width] for index in range(0, count_pixels, self._width)]
                img_ascii = '\n'.join(img_ascii)

                self._ascii_frames.append(img_ascii)

                try:
                    with open('./files/frames.txt', 'a') as txt:
                        txt.write(img_ascii)
                        txt.write('\n')
                except Exception as e:
                    sys.stdout.write(f'Ocurrio un error al abrir el archivo: {e}')

            except Exception as e:
                sys.stdout.write(f'Ocurrio un error al formar la imagen ASCII: {e}')

    def recuperar_txt(self) -> None:
        self._ascii_frames = [[]*k for k in range(self.contar_frames())]
        try:
            with open('./files/frames.txt', 'r') as frames:
                for i in range(self.contar_frames()):
                    tmp = ''.join(frames.readline() for i in range(60))
                    self._ascii_frames[i] = tmp
        except Exception as e:
            sys.stdout.write(f'Ocurrio un error al abrir el archivo: {e}')

    def reproducir_cancion(self) -> None:
        mixer.init()
        mixer.music.load("./files/bad_apple.mp3")
        mixer.music.play()

    def reproducir_frames(self) -> None:
        system('mode %s, %s'%(self._width, self._height))
        timer = fpstimer.FPSTimer(self.obtener_fps())
        for i in range(self.contar_frames()):
            sys.stdout.write(self._ascii_frames[i])
            timer.sleep()

    def player(self) -> None:
        audio = Thread(target=self.reproducir_cancion())
        txt = Thread(target=self.reproducir_frames())

        audio.start()
        txt.start()

        txt.join()
        audio.join()
        

if __name__ == '__main__':
    ruta = str('./bad_apple.mp4')
    BadApple = AsciiPlayer(ruta)

    #BadApple.reproducir_cancion()
    BadApple.convertir_audio()
    #BadApple.obtener_frames()
    BadApple.obtener_ascii()
    BadApple.recuperar_txt()
    BadApple.reproducir_frames()
    
    #BadApple.player()
