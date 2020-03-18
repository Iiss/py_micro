# -*- coding: utf-8 -*-
import pygame,sys
from pygame.locals import *
import pygame.camera
import configparser
import os


class Capture(object):
    def __init__(self,config):
        self.foreground = (239,127,26)
        self.background = (0,0,0)
        self.cam = None
        self.cam_w = config.getint('Viewport','webcam_w')
        self.cam_h = config.getint('Viewport','webcam_h')
        self.screen_w = config.getint('Viewport','screen_w')
        self.screen_h = config.getint('Viewport','screen_h')
        self.no_cam_msg = u'Микроскоп не обнаружен.'
        self.no_cam_desc = u'Проверьте подключение микроскопа и перезагрузите компьютер'

        #config.get('Locale','no_camera_msg')
        self.scale_x = float(self.screen_w) / self.cam_w
        self.scale_y = float(self.screen_h) / self.cam_h
        self.size = (self.cam_w, self.cam_h)
        self.error_surface = None

        # create a display surface. standard pygame stuff
        self.display = pygame.display.set_mode((self.screen_w,self.screen_h), 0)
        
        # this is the same as what we saw before
        self.clist = pygame.camera.list_cameras()
        
        try:
            self.cam = pygame.camera.Camera(self.clist[0], self.size)
            self.cam.start()

            # create a surface to capture to.  for performance purposes
            # bit depth is the same as that of the display surface.
            self.snapshot = pygame.surface.Surface(self.size)
        except Exception:
            self.show_error()

    def show_error(self):
        global font
        self.error_surface = pygame.surface.Surface((self.screen_w,self.screen_h))
        self.error_surface.fill(self.background)
        msg = font.render(self.no_cam_msg,True,self.foreground)
        desc = font.render(self.no_cam_desc,True,self.foreground)
        error_img = pygame.image.load("science.png").convert_alpha()

        self.error_surface.blit(error_img,(
                                .5*(self.screen_w-error_img.get_width()),
                                .5*(self.screen_h-error_img.get_height() - 40
                                )))

        self.error_surface.blit(desc,(.5*(self.screen_w-desc.get_width()),.5*(self.screen_h+error_img.get_height())))
        self.display.blit(self.error_surface, (0,0))
        pygame.display.flip()

    def get_and_flip(self):
        if self.error_surface:
            return
            
        scaled_h = int(self.cam_h * self.scale_x)
        scaled_w = int(self.cam_w * self.scale_y)
        if scaled_h>=self.screen_h:
            # if you don't want to tie the framerate to the camera, you can check 
            # if the camera has an image ready.  note that while this works
            # on most cameras, some will never return true.
            #if self.cam.query_image():
            self.snapshot = pygame.transform.scale(self.cam.get_image(),(self.screen_w, scaled_h))
            # blit it to the display surface.  simple!
            clip_rect = Rect(0,.5*abs(self.screen_h-scaled_h),self.screen_w, self.screen_h)
        else:
            self.snapshot = pygame.transform.scale(self.cam.get_image(),(scaled_w,self.screen_h))
            clip_rect = Rect(.5*abs(self.screen_w-scaled_w),0,self.screen_w, self.screen_h)

        self.display.blit(self.snapshot.subsurface(clip_rect), (0,0))
        pygame.display.flip()
        
    def main(self):
        going = True
        while going:
            events = pygame.event.get()
            for e in events:
                if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
                    # close the camera safely
                    if self.cam:
                        self.cam.stop()
                    going = False
                    pygame.quit()
                    sys.exit()

            self.get_and_flip()

if __name__ == '__main__':
    app_dir = os.path.dirname(os.path.realpath(__file__))
    config = configparser.ConfigParser()
    config.read(os.path.join(app_dir,'config.ini'))
    pygame.init()
    pygame.mouse.set_visible(False)
    pygame.font.init()
    font = pygame.font.Font("Bicubik.OTF",10)
    pygame.camera.init()
    cap = Capture(config).main()