import onnxruntime as ort
import cv2
import numpy as np

class YOLO_ONNX():
    def __init__(self,onnx_path) -> None:
        self.onnx_session = ort.InferenceSession(onnx_path,providers=['TensorrtExecutionProvider', 'CUDAExecutionProvider', 'CPUExecutionProvider'])
        self.input_name = self.get_input_name()
        self.output_name = self.get_output_name()
    
    def get_input_name(self):
        """
        获取输入节点名称
        """
        input_name = []
        for node in self.onnx_session.get_inputs():
            input_name.append(node.name)
        # print(input_name)
        return input_name
    
    def get_output_name(self):
        """
        获取输出节点名称
        """
        output_name = []
        for node in self.onnx_session.get_outputs():
            output_name.append(node.name)
        # print(output_name)
        return output_name
    
    def get_input_feed(self,image_numpy):
        """
        获取输入numpy
        """
        input_feed = {}
        for name in self.input_name:
            input_feed[name] = image_numpy
        return input_feed
    
    def inference(self,img):
        """
        1.CV读取图像并resize
        2.图像转BGR2RGB和HWC2HWC(因为yolov5的onnx模型输入为 1x3x640x640)
        3.图像归一化
        4.图像增加维度
        5.onnx_session推理
        """
        # img = cv2.imread(img_path)
        or_img = cv2.resize(img,(640,640))
        img = or_img[:,:,::-1].transpose(2,0,1)
        img = img.astype(np.float32)
        img /= 255.0
        img = np.expand_dims(img,axis=0)
        input_feed = self.get_input_feed(img)
        pred = self.onnx_session.run(None,input_feed)[0]
        return pred,or_img
