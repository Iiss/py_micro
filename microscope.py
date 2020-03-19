# -*- coding: utf-8 -*-
import pygame,sys
from pygame.locals import *
import pygame.camera
import configparser
import os
import time

class AbstractState(object):
    def __init__(self,stateManager):
        self.stateManager=stateManager

    def begin(self):
        pass
    def update(self):
        pass
    def destroy(self):
        pass

class ErrorState(AbstractState):
    def __init__(self,stateManager):
        self.foreground = (195,246,249)
        self.background = (0,0,0)
        self.cam_w = config.getint('Viewport','webcam_w')
        self.cam_h = config.getint('Viewport','webcam_h')
        self.screen_w = config.getint('Viewport','screen_w')
        self.screen_h = config.getint('Viewport','screen_h')
        self.size = (self.cam_w, self.cam_h)
        self.scale_x = float(self.screen_w) / self.cam_w
        self.scale_y = float(self.screen_h) / self.cam_h
        self.no_cam_msg = u'Микроскоп не обнаружен.'
        self.no_cam_desc1 = u'Проверьте подключение микроскопа' 
        self.no_cam_desc2 = u'и перезагрузите компьютер'
        # self.display = pygame.display.set_mode((self.screen_w,self.screen_h), 0)
        self.display=stateManager.display
        AbstractState.__init__(self,stateManager)

    def begin(self):
        global font
        self.error_surface = pygame.surface.Surface((self.screen_w,self.screen_h))
        self.error_surface.fill(self.background)
        msg = font.render(self.no_cam_msg,True,self.foreground)
        desc1 = font.render(self.no_cam_desc1,True,self.foreground)
        desc2 = font.render(self.no_cam_desc2,True,self.foreground)
        error_img = pygame.image.load("microScope_n.png").convert_alpha()

        self.error_surface.blit(error_img,(
                                .5*(self.screen_w-error_img.get_width()),
                                .5*(self.screen_h-error_img.get_height() - 40
                                )))

        self.error_surface.blit(desc1,(.5*(self.screen_w-desc1.get_width()),.5*(self.screen_h+error_img.get_height())))
        self.error_surface.blit(desc2,(.5*(self.screen_w-desc2.get_width()),.5*(self.screen_h+error_img.get_height()+40)))
        self.display.blit(self.error_surface, (0,0))
        pygame.display.flip()
        

    def update(self):
        if len(pygame.camera.list_cameras()):
            self.stateManager.setState(self.stateManager.cam_state)

class CamState(AbstractState):
    def __init__(self,stateManager,config):
        self.cam_w = config.getint('Viewport','webcam_w')
        self.cam_h = config.getint('Viewport','webcam_h')
        self.screen_w = config.getint('Viewport','screen_w')
        self.screen_h = config.getint('Viewport','screen_h')
        self.size = (self.cam_w, self.cam_h)
        self.scale_x = float(self.screen_w) / self.cam_w
        self.scale_y = float(self.screen_h) / self.cam_h
        self.display=stateManager.display
        self.cam=None
        # self.display = pygame.display.set_mode((self.screen_w,self.screen_h), 0)
        AbstractState.__init__(self,stateManager)

    def begin(self):
        clist = pygame.camera.list_cameras()
        print (self.cam)
        if self.cam:
            self.cam.stop
            print ('Stop')
            self.cam=None
            time.sleep(1)
            
        else:
            self.cam = pygame.camera.Camera(clist[0], self.size)        
            self.cam.start()

    def update(self):
        if len(pygame.camera.list_cameras()):
            try:
                if self.cam.query_image():
                
                    scaled_h = int(self.cam_h * self.scale_x)
                    scaled_w = int(self.cam_w * self.scale_y)
                    if scaled_h>=self.screen_h:
                        # if you don't want to tie the framerate to the camera, you can check 
                        # if the camera has an image ready.  note that while this works
                        # on most cameras, some will never return true.
                        
                        self.snapshot = pygame.transform.scale(self.cam.get_image(),(self.screen_w, scaled_h))
                        clip_rect = Rect(0,.5*abs(self.screen_h-scaled_h),self.screen_w, self.screen_h)
                        
                            
                                            
                    else:
                        
                        self.snapshot = pygame.transform.scale(self.cam.get_image(),(scaled_w,self.screen_h))
                        clip_rect = Rect(.5*abs(self.screen_w-scaled_w),0,self.screen_w, self.screen_h)
                        
                                
                    self.display.blit(self.snapshot.subsurface(clip_rect), (0,0))
                    pygame.display.flip()        
            except Exception:
                self.stateManager.setState(self.stateManager.error_state)
                
        else:
            self.stateManager.setState(self.stateManager.error_state) 

        


class Capture(object):
    def __init__(self,config):
        self.cur_state=None
        self.foreground = (195,246,249)
        self.background = (0,0,0)
        self.cam = None
        self.cam_w = config.getint('Viewport','webcam_w')
        self.cam_h = config.getint('Viewport','webcam_h')
        self.screen_w = config.getint('Viewport','screen_w')
        self.screen_h = config.getint('Viewport','screen_h')
        self.no_cam_msg = u'Микроскоп не обнаружен.'
        self.no_cam_desc1 = u'Проверьте подключение микроскопа' 
        self.no_cam_desc2 = u'и перезагрузите компьютер'
        #config.get('Locale','no_camera_msg')
        self.scale_x = float(self.screen_w) / self.cam_w
        self.scale_y = float(self.screen_h) / self.cam_h
        self.size = (self.cam_w, self.cam_h)
        # self.error_surface = None

        # create a display surface. standard pygame stuff
        self.display = pygame.display.set_mode((self.screen_w,self.screen_h), 0)
        
        # this is the same as what we saw before
        # self.clist = pygame.camera.list_cameras()
        
        self.error_state=ErrorState(self)
        self.cam_state=CamState(self,config)
        self.setState(self.error_state)

    def setState(self,state):
        if self.cur_state!=state:
            if self.cur_state:
                self.cur_state.destroy()
            self.cur_state=state
            self.cur_state.begin()
      
    


            
    def main(self):
        going = True
        while going:
            self.cur_state.update()
          
                
            
            events = pygame.event.get()
            for e in events:
                if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
                    # close the camera safely
                    if self.cam:
                        self.cam.stop()
                    going = False
                    pygame.quit()
                    sys.exit()


            

if __name__ == '__main__':
    app_dir = os.path.dirname(os.path.realpath(__file__))
    config = configparser.ConfigParser()
    config.read(os.path.join(app_dir,'config.ini'))
    pygame.init()
    pygame.mouse.set_visible(False)
    pygame.font.init()
    font = pygame.font.Font("Bicubik.OTF",18)
    pygame.camera.init()
    cap = Capture(config).main()