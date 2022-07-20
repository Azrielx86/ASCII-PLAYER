from os import name, system, path, remove, rmdir, makedirs, get_terminal_size
from PIL import Image
from pygame import mixer
from threading import Thread
import moviepy.editor as mp
import cv2 as cv
import fpstimer
import sys

progress_format = '>{:.2f}% ({} of {})\u001b[1000D'

class AsciiPlayer:
    def __init__(self, path) -> None:
        self._path = path
        self._ascii_frames = []
        self._height = 60
        self._width = 170

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, height):
        self._height = height

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, width):
        self._width = width

    def makeDir(self) -> None:
        try:
            makedirs(path.join('files', 'output'))
        except Exception:
            pass

    def verifyFiles(self, path: str) -> bool:
        try:
            with open(path, 'r'):
                return True
        except Exception:
            return False

    def getAudioFile(self) -> None:
        try:
            if self.verifyFiles(path.join("files", "audio.wav")):
                sys.stdout.write('Audio file already exists.\n')
            else:
                audio = mp.VideoFileClip(self._path)
                audio.audio.write_audiofile(path.join("files", "audio.wav"), bitrate='320k')
        except Exception as e:
            sys.stdout.write(f'Error while getting audio file\n')

    def getFrameCount(self) -> int:
        video = cv.VideoCapture(self._path)
        nFrames = int(video.get(cv.CAP_PROP_FRAME_COUNT))
        return nFrames

    def getFPS(self) -> float:
        video = cv.VideoCapture(self._path)
        fps = float(video.get(cv.CAP_PROP_FPS))
        return fps

    def getFrames(self) -> None:
        frames = cv.VideoCapture(self._path)
        nFrame = 0
        sys.stdout.write(f'Extracting frames from: {self._path}\n')
        end = self.getFrameCount()
        while(True):
            success, frame = frames.read()
            if success:
                if not self.verifyFiles(path.join('files', 'output', 'frame_%s.jpg' % nFrame)):
                    cv.imwrite(path.join('files', 'output','frame_%s.jpg' % nFrame), frame)
            else:
                break
            nFrame += 1

            sys.stdout.write(progress_format.format(nFrame * 100 / end, nFrame, end))
            
        sys.stdout.write("\u001b[2K")
        frames.release()

    def getASCII(self) -> None:
        if self.verifyFiles(path.join('files', 'frames.txt')):
            return
        ASCII_CHARS = [' ', '.', '"', ':', '!', '~', '+', '*', '#', '$', '@']

        sys.stdout.write(f'Writing ASCII file...\n')
        end = self.getFrameCount()
        for i in range(self.getFrameCount()):
            try:
                frame = Image.open(path.join('files', 'output', 'frame_%s.jpg' % i))
                frame = frame.resize(size=[self._width, self._height])

                frame = frame.convert('L')
                pixel_data = frame.getdata()

                new_pixel = ''.join(ASCII_CHARS[pixel//25] for pixel in pixel_data)

                count_pixels = len(new_pixel)
                img_ascii = [new_pixel[index: index + self._width] for index in range(0, count_pixels, self._width)]
                img_ascii = '\n'.join(img_ascii)

                try:
                    with open(path.join("files", "frames.txt"), 'a') as txt:
                        txt.write(img_ascii)
                        txt.write('\n')
                except Exception as e:
                    sys.stdout.write(f'An error occurred while the opening file: {e}\n')

                sys.stdout.write(progress_format.format(i * 100 / end, i, end))

            except Exception as e:
                sys.stdout.write(f'An error occurred while getting ASCII image: {e}\n')
        sys.stdout.write("\u001b[2K")

    def getTxtFile(self) -> None:
        self.getSize()
        self._ascii_frames = [[]*k for k in range(self.getFrameCount())]
        try:
            with open(path.join("files", "frames.txt"), 'r') as frames:
                for i in range(self.getFrameCount()):
                    tmp = ''.join(frames.readline() for i in range(self._height))
                    self._ascii_frames[i] = tmp
        except Exception as e:
            sys.stdout.write(f'An error occurred while opening the file: {e}\n')

    def prepareFiles(self):
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()

        if not self.verifyFiles(path.join("files", "size.txt")):
            self.saveSize()
        self.makeDir()
        self.getAudioFile()
        self.getSize()
        if self.verifyFiles(path.join("files", "frames.txt")):
            self.getTxtFile()
        else:
            self.getFrames()
            self.getASCII()
            self.saveSize()

        sys.stdout.write("\033[?25h")
        sys.stdout.flush()

    def saveSize(self) -> None:
        try:
            with open(path.join('files', 'size.txt'), 'w') as sizeFile:
                sizeFile.write(f'height={self.height}\n')
                sizeFile.write(f'width={self.width}\n')
        except Exception:
            pass

    def getSize(self) -> None:
        try:
            with open(path.join('files', 'size.txt'), 'r') as sizeFile:
                self.height = int(sizeFile.readline().strip('height='))
                self.width = int(sizeFile.readline().strip('width='))
        except Exception:
            pass

    def deleteFiles(self) -> None:
        try:
            remove(path.join('files', 'audio.wav'))
            remove(path.join('files', 'frames.txt'))
            remove(path.join('files', 'size.txt'))
            for i in range(self.getFrameCount()):
                remove(path.join('files', 'output', 'frame_%s.jpg' % (i)))
            rmdir(path.join('files', 'output'))
            rmdir('files')
        except Exception as e:
            sys.stdout.write(
                f'An error occurred while deleting the files: {e}\n')

    def reloadFiles(self) -> None:
        try:
            remove(path.join('files', 'size.txt'))
            remove(path.join('files', 'frames.txt'))
        except Exception as e:
            pass

    def playSong(self) -> None:
        mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=2048)
        mixer.init()
        mixer.music.load(path.join("files", "audio.wav"))
        mixer.music.play()

    def playFrames(self) -> None:
        system('cls' if name == 'nt' else 'clear')
        timer = fpstimer.FPSTimer(self.getFPS())
        for i in range(self.getFrameCount()):
            sys.stdout.write("\033[H")
            sys.stdout.write(self._ascii_frames[i][:-1])
            timer.sleep()

    def player(self) -> None:
        audio = Thread(target=self.playSong())
        txt = Thread(target=self.playFrames())

        audio.start()
        txt.start()

        txt.join()
        audio.join()

    def getScreenSize(self) -> None:
        self._height = get_terminal_size().lines
        self._width = get_terminal_size().columns


if __name__ == '__main__':
    system('cls' if name == 'nt' else 'clear')

    while True:
        print('ASCII Video Player'.center(50, '='))
        ruta = input("File Name (Enter for 'bad_apple.mp4'):").strip()
        if ruta == '':
            ruta = 'bad_apple.mp4'
        try:
            with open(ruta, 'r'):
                video = AsciiPlayer(ruta)
                break
        except Exception as e:
            print(f'An error occurred: {e}')
            input()

    while True:
        system('cls' if name == 'nt' else 'clear')
        print(' ASCII Video Player '.center(50, '='))
        print(f'File: {ruta}')
        print('[1] Play')
        print(f'[2] Use terminal size ({get_terminal_size().lines}x{get_terminal_size().columns})')
        print('[3] Use custom size')
        print('[4] Delete Files')
        print('[5] Exit')
        opc = input('> ')
        print("\033[F", end="")

        if opc == '1':
            video.prepareFiles()
            if video.verifyFiles(path.join('files', 'frames.txt')) and video.verifyFiles(path.join('files', 'audio.wav')):
                video.getTxtFile()
                video.player()

        elif opc == '2':
            video.getScreenSize()
            video.reloadFiles()
            video.prepareFiles()

        elif opc == '3':
            print('Default size: 60x170')
            video.height = int(input('New height: '))
            video.width = int(input('New width: '))
            print(f'Reloading files...')
            video.reloadFiles()
            video.prepareFiles()

        elif opc == '4':
            print('Delete files? [y/n]', end=' ')
            opc = input()
            if opc == 'y' or opc == 'Y':
                video.deleteFiles()
            elif opc == 'n' or opc == 'N':
                pass
            else:
                print('Not Valid')

        elif opc == '5':
            break

        else:
            print('Invalid Option!')
