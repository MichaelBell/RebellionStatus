#!/usr/bin/env python

import time
import pygame
import requests

from rebellion_netstatus import NetStatus
import rebellion_battery

black = (0,0,0)
dark_blue = (128,0,0)
blue = (255,0,0)
red = (255,0,0)
green = (0,255,0)
yellow = (255,192,0)
orange = (255,64,0)
white = (255,255,255)

pygame.font.init()
large_font = pygame.font.Font(pygame.font.get_default_font(), 75)
small_font = pygame.font.Font(pygame.font.get_default_font(), 50)
smaller_font = pygame.font.Font(pygame.font.get_default_font(), 35)

class DisplayEnd(Exception):
  def __init__(self, str, extra=""):
    self.str = str
    self.extra = extra

  def __str__(self):
    return "%s (%s)" % (self.str, self.extra)

def get_weather():
  weather = {'Temp': 'unknown', 'Pres': 'unknown'}
  try:
    r = requests.get('http://bowpi:8080/status')
    if r.status_code == 200:
      weather['Temp'] = str(round(r.json()['Temp'],1))
      weather['Pres'] = str(round(r.json()['Pres'],1))
  except requests.exceptions.RequestException:
    pass
  return weather

class BackDisplay:
  def __init__(self):
    pygame.display.init()
    pygame.mouse.set_visible(False)
    self.size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
    self.screen = pygame.display.set_mode(self.size, pygame.FULLSCREEN)
    self.rebellion_status = NetStatus()
    self.lion = pygame.image.load('lion.png')

  def drawScreen(self):
    operator = self.rebellion_status.get_operator()
    #if operator == 'EE':
    #  self.screen.fill(black)
    #else:
    #  self.screen.fill(dark_blue)
    self.screen.fill(black)
    curtime = time.strftime('%H:%M')
    msg = small_font.render(curtime, False, white)
    self.screen.blit(msg, (65 - msg.get_rect().centerx, 150))
    conn_type = self.rebellion_status.get_conn_type()
    msg = large_font.render(operator, False, white)
    self.screen.blit(msg, (550, 35))
    msg = large_font.render(conn_type, False, white)
    self.screen.blit(msg, (550, 125))
    data_left = self.rebellion_status.get_data_remaining()
    if data_left > -1:
        status = "Data left: %.1fGB" % data_left
    else:
        status = ""
    msg = small_font.render(status, False, white)
    self.screen.blit(msg, (self.size[0]/2 - msg.get_rect().centerx, 350))
    status = rebellion_battery.get_status_string()
    msg = small_font.render(status, False, white)
    self.screen.blit(msg, (self.size[0]/2 - msg.get_rect().centerx, 400))
    if conn_type == '4G':
        status_colour = green
    elif conn_type == '3G':
        status_colour = yellow
    else:
        status_colour = red
    strength = self.rebellion_status.get_signal_strength()

    if strength > 0:
        pygame.draw.rect(self.screen, status_colour, (280, 160, 40, 40))
    if strength > 1:
        pygame.draw.rect(self.screen, status_colour, (330, 120, 40, 80))
    if strength > 2:
        pygame.draw.rect(self.screen, status_colour, (380, 80, 40, 120))
    if strength > 3:
        pygame.draw.rect(self.screen, status_colour, (430, 40, 40, 160))
    if strength > 4:
        pygame.draw.rect(self.screen, status_colour, (480, 0, 40, 200))

    weather = get_weather()
    status = "%sC" % weather['Temp']
    msg = small_font.render(status, False, white)
    self.screen.blit(msg, (4, 240))
    status = "%smB" % weather['Pres']
    msg = smaller_font.render(status, False, white)
    self.screen.blit(msg, (4, 300))

    self.screen.blit(self.lion, (20,10))

  def update(self, dt):
    self.drawScreen()
    pygame.display.update()

FRAME_TIME = 10

def loop():
  while True:
    display.update(FRAME_TIME)
    time.sleep(FRAME_TIME)

if __name__ == '__main__':
    display = BackDisplay()
    try:
      loop()
    except DisplayEnd, e:
      screen = display.screen
      msg = large_font.render(e.str, False, white)
      screen.blit(msg, (display.size[0]/2 - msg.get_rect().centerx, 200))
      msg = small_font.render(e.extra, False, white)
      screen.blit(msg, (display.size[0]/2 - msg.get_rect().centerx, 200 + large_font.get_linesize() * 1.5))
      pygame.display.update()
    except KeyboardInterrupt:
      print "\nExit"

