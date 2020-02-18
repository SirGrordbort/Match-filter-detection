from PIL import Image
import tkinter
import glob


def next_images(image_num, picked_waveforms, repicked_waveforms, picked, repicked):
    if(image_num != 0):
        picked.close()
        repicked.close()
    picked = Image.open(picked_waveforms[image_num])
    repicked = Image.open(repicked_waveforms[image_num])
    image_num += 1


picked_waveforms = sorted(glob.glob("picked_waveforms" + '/*'))
repicked_waveforms = sorted(glob.glob("repicked_waveforms" + '/*'))
image_num = 0
picked = None
repicked = None
window = tkinter.Tk()
button = tkinter.Button(window, text = "next images", command = next_images(image_num, picked_waveforms, repicked_waveforms, picked, repicked))

