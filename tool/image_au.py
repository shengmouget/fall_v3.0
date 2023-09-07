from .yolo_onnx import YOLO_ONNX
import cv2
import numpy as np
def inference(image,onnx_path):
    """
        1.CV读取图像并resize
        2.图像转BGR2RGB和HWC2HWC(因为yolov5的onnx模型输入为 1x3x640x640)
        3.图像归一化
        4.图像增加维度
        5.onnx_session推理
    """
    onnx_ort = YOLO_ONNX(onnx_path)
    or_img = cv2.resize(image,(640,640))
    img = or_img[:,:,::-1].transpose(2,0,1)
    img = img.astype(np.float32)
    img /= 255.0
    img = np.expand_dims(img,0)
    input_feed = onnx_ort.get_input_feed(img)
    pred = onnx_ort.onnx_session.run(None,input_feed)[0]
    return pred,or_img
