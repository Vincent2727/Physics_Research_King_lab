import os
import gphoto2 as gp
import time
import datetime
import subprocess

WORK_DIR = '/Users/vincentdegaetano/Documents/VsCodeProjects/PhysicsResearch/Image_Saves/NikonSaves'
template = os.path.join(WORK_DIR, 'frame%04d.jpg')

# # initialize the camrea
# camera = gp.Camera()
# camera.init()

# # print the cam name
# print(camera.get_summary())

# # take a picture and display the path
# path = camera.capture(gp.GP_CAPTURE_IMAGE)
# print(f'Picture path: {path.folder+path.name}')

# # get the location of the picure to save
# camera_file = camera.file_get(path.folder, path.name, gp.GP_FILE_TYPE_NORMAL)
# camera_file.save(template % time.time())
# # delete the pciture from the camera
# camera.file_delete(path.folder, path.name)

class Camera():
    def __init__(self, save_dir):
        """Instantiate the Camera from the gphoto2 package. Requires a directory to save the photos to."""
        self.camera = gp.Camera() # get the camera from the USB port
        self.camera.init() # initialize the camera
        self.info = str(self.camera.get_summary())[:9] # Only keep the first couple lines... there is a large amount of info
        # Template name to save the photo to
        self.save_dir = save_dir

    def capture(self, save_on_camera=False, time_lapse=False, count=0):
        # Create the save name data
        if time_lapse:
            save_name_base = os.path.join(self.save_dir, 'frame%04d.jpg')
            save_name = save_name_base % count
        else:
            save_name = f'{os.path.join(self.save_dir, 'frame')}_{datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")}.jpg'
        path = self.camera.capture(gp.GP_CAPTURE_IMAGE)
        print(f'Picture path: {path.folder+path.name}')
        camera_file = self.camera.file_get(path.folder, path.name, gp.GP_FILE_TYPE_NORMAL)
        camera_file.save(save_name)
        if not save_on_camera:
            # delete the pciture from the camera
            self.camera.file_delete(path.folder, path.name)
        if time_lapse:
            return save_name_base
    
    def time_lapse(self, space_interval, time_length):
        # Broken Right now
        next_shot = time.time() + 1.0
        count = 0
        try:
            while count < time_length:
                sleep = next_shot - time.time()
                if sleep < 0.0:
                    break
                time.sleep(sleep)
            save = self.capture(time_lapse=True, count=count)
            next_shot += space_interval
            count += 1
        except KeyboardInterrupt:
            pass
        # self.compress(save)

    def compress(self, savename):
        subprocess.check_call(['ffmpeg', '-r', '25',
                           '-i', savename, '-c:v', 'h264', 'time_lapse.mp4'])

cam = Camera(WORK_DIR)

cam.capture()

cam.time_lapse(1, 50)