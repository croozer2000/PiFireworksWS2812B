import time
import board
import neopixel
import numpy
import random
from math import exp
    
pixel_pin = board.D18
    
# The number of Pixels
num_pixels = 300
    
# The order of the pixel colors - RGB or GRB. Some NeoPixels have red and green reversed!
# For RGBW NeoPixels, simply change the ORDER to RGBW or GRBW.
ORDER = neopixel.RGB
    
pixels = neopixel.NeoPixel(
    pixel_pin, num_pixels, brightness=0.2, auto_write=False, pixel_order=ORDER
)
    
class Explosion:
    maxTime = 30
    minTime = 10
    fadeTime = 10

    # individual particles fired from star
    class Particle:
        def __init__(self, initialColor, initialVelocity):
            self.color = initialColor
            self.velocity = random.randrange(1,8)
            self.startVelocity = self.velocity
            self.analogLocation = 0
            self.location = 0
            self.timeAlive = 0 
        
        def advance(self, timeAlive):
            # advance the particles
            self.analogLocation += self.velocity
            self.location = int(self.analogLocation)
            self.velocity = (self.startVelocity * exp((-(.9)*self.timeAlive)))
            self.timeAlive += 1
            return self.location

    def __init__(self):
        # instantiate store
        self.color = (random.randrange(0,256),random.randrange(0,256),random.randrange(0,256))
        self.location = random.randrange(0,num_pixels)
        # self.location = 150
        self.startVelocity = random.randrange(1,2)
        self.velocity = self.startVelocity
        self.timeTillDeath = random.randrange(Explosion.minTime,Explosion.maxTime) + self.fadeTime
        self.timeAlive = 0
        self.size = 1
        self.fade = [int(color / self.timeTillDeath) for color in self.color]
        self.pixels = []

    def colorFade(self):
        # fade the color of the explosion

        # print(self.color)
        self.color = tuple([self.color[i] - self.fade[i] for i in range(3)])

    def advance(self,pixels):
        # advance the aninmation 

        # Explode and fade white explosion in the first 10 frames
        if self.timeAlive < 10:
            temp = abs(255 - (int((255 / 10) * self.timeAlive)))
            # pixels[self.location] = (temp,temp,temp)
            pixels[self.location] = tuple([int((temp+pixels[self.location][j])/2) if pixels[self.location][j] != 0 else temp for j in range(3)])
            temp = int(temp*.5)
            if (self.location-1) > 0:
                # This formula mixes the colors of with the rest of the pixels
                pixels[self.location-1] = tuple([int((temp+pixels[self.location-1][j])/2) if pixels[self.location-1][j] != 0 else temp for j in range(3)])
            if (self.location+1) < num_pixels:
                pixels[self.location+1] = tuple([int((temp+pixels[self.location+1][j])/2) if pixels[self.location+1][j] != 0 else temp for j in range(3)])
        
        # advance each particle and its color
        elif self.timeTillDeath > 10:
            try:
                pixels[self.location] = self.color
            except:
                pass
            self.pixels.append(Explosion.Particle(self.color, self.velocity))
            for i in self.pixels:
                temp = i.advance(self.timeAlive)
                self.size = temp if temp > self.size else self.size

                # print(self.pixels)
            self.colorFade()
        # fade out the colors when running through the fade time
        else:
            self.color = tuple([int(self.color[i]*.75) for i in range(3)])
        self.timeTillDeath = self.timeTillDeath - 1
        self.timeAlive = self.timeAlive + 1

    # apply the particle colors and locations to the Strip pixel array
    def applyPixels(self, pixels):
        for i in self.pixels:
            pos = self.location + int(i.location)
            neg = self.location - int(i.location)
            try:
                if pos < num_pixels:
                    pixels[pos] = tuple([int((self.color[j]+pixels[pos][j])/2) if pixels[pos][j] != 0 else self.color[j] for j in range(3)])
                if neg >= 0:
                    pixels[neg] = tuple([int((self.color[j]+pixels[neg][j])/2) if pixels[neg][j] != 0 else self.color[j] for j in range(3)])
            except :
                print(pos, neg, self.color)

    # clear the pixels in the area of the star
    def clearFireworks(self, pixels):
        pixels[self.location] = (0,0,0)
        for i in range(self.size):
            pos = self.location + int(i+1)
            neg = self.location - int(i+1)
            try:
                if pos < num_pixels:
                    pixels[pos] = (0,0,0)
                if neg >= 0:
                    pixels[neg] = (0,0,0)
            except :
                print(pos, neg, self.color)

from os import system
def fireWorks():
    pixels.fill((0,0,0))
    queue = []
    popQueue = []

    while True:
        # first pop old stars
        popQueue.sort(reverse=True)
        for i in popQueue:
            queue[i].clearFireworks(pixels)
            queue.pop(i)
            # print("poped item\b")
        
        # display current count of stars in stystem
        print(str(len(queue)).zfill(2), end="\r", flush=True)

        # clear LEDs if Queue if no stars are in queue
        if len(queue) == 0:
            pixels.fill((0,0,0))
        popQueue = []

        # 1/5 probablility each frame for new explosion
        if random.randrange(0,5) == 2:
            queue.append(Explosion())
        
        # advance and apply each star in queue
        for i in range(len(queue)):
            queue[i].advance(pixels)
            queue[i].applyPixels(pixels)            

            # append dead stars to pop list
            if queue[i].timeTillDeath <= 0:
                popQueue.append(i)

        # send pixel array to LEDs
        pixels.show()
        time.sleep(.1)

while True:
    fireWorks()
