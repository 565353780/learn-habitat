import os
import cv2
import shutil
from getch import getch

from habitat_sim_manage.Config.config import SIM_SETTING
from habitat_sim_manage.Module.sim_manager import SimManager

class DataCollector(SimManager):
    def __init__(self, glb_file_path=None, control_mode=None, save_dataset_folder_path=None):
        super().__init__()

        self.save_dataset_folder_path = None
        self.image_folder_path = None
        self.sparse_folder_path = None
        self.image_pose_file = None
        self.image_idx = 1

        if glb_file_path is not None:
            self.loadSettings(glb_file_path)

        if control_mode is not None:
            self.setControlMode(control_mode)

        if save_dataset_folder_path is not None:
            self.createDataset(save_dataset_folder_path)
        return

    def reset(self):
        super().reset()
        self.save_dataset_folder_path = None
        self.image_folder_path = None
        self.sparse_folder_path = None
        self.image_pose_file = None
        self.image_idx = 1
        return True

    def saveSceneInfo(self):
        camera_txt = '1 PINHOLE ' + \
            str(SIM_SETTING['width']) + ' ' + \
            str(SIM_SETTING['height']) + ' ' + \
            '800.1 800.1 ' + \
            str(SIM_SETTING['width'] / 2.0) + ' ' + \
            str(SIM_SETTING['height'] / 2.0)

        with open(self.sparse_folder_path + 'cameras.txt', 'w') as f:
            f.write(camera_txt + '\n')

        points_txt = '1 0 0 0 0 0 0 0 1'
        with open(self.sparse_folder_path + 'points3D.txt', 'w') as f:
            f.write(points_txt + '\n')
        return True

    def createDataset(self, save_dataset_folder_path):
        self.save_dataset_folder_path = save_dataset_folder_path

        if self.save_dataset_folder_path[-1] != '/':
            self.save_dataset_folder_path += '/'

        if os.path.exists(self.save_dataset_folder_path):
            shutil.rmtree(self.save_dataset_folder_path)

        self.image_folder_path = self.save_dataset_folder_path + 'images/'
        self.sparse_folder_path = self.save_dataset_folder_path + 'sparse/0/'
        self.image_pose_file = self.sparse_folder_path + 'images.txt'

        os.makedirs(self.image_folder_path, exist_ok=True)
        os.makedirs(self.sparse_folder_path, exist_ok=True)

        self.saveSceneInfo()
        return True


    def saveImage(self, image):
        cv2.imwrite(self.image_folder_path + str(self.image_idx) + '.png', image)

        agent_state = self.sim_loader.getAgentState()

        pos = agent_state.position
        quat = agent_state.rotation

        pose_txt = str(self.image_idx)
        pose_txt += ' ' + str(quat.w)
        pose_txt += ' ' + str(quat.x)
        pose_txt += ' ' + str(quat.y)
        pose_txt += ' ' + str(quat.z)
        for i in range(3):
            pose_txt += ' ' + str(pos[i])
        pose_txt += ' 1'
        pose_txt += str(self.image_idx) + '.png'

        with open(self.image_pose_file, 'a') as f:
            f.write(pose_txt + '\n')

        self.image_idx += 1
        return True

    def startKeyBoardControlRender(self, wait_key):
        #  self.resetAgentPose()
        self.cv_renderer.init()

        while True:
            image = self.cv_renderer.renderFrame(self.sim_loader.observations)
            if image is None:
                break

            self.saveImage(image)

            self.cv_renderer.waitKey(wait_key)

            agent_state = self.sim_loader.getAgentState()
            print("agent_state: position", agent_state.position, "rotation",
                  agent_state.rotation)

            input_key = getch()
            if not self.keyBoardControl(input_key):
                break
        self.cv_renderer.close()
        return True