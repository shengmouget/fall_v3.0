from tool.onnx_run import filter_box,writer_image,draw
from tool.yolo_onnx import YOLO_ONNX
import cv2

onnx_path = "/home/neuedu/桌面/跌倒3.0/config/best-sim.onnx"
model = YOLO_ONNX(onnx_path)
cap = cv2.VideoCapture(0)
frame_count = 0
save_interval = 50
while True:
    ret,frame = cap.read()
    if not ret:
        break
    frame_count += 1
    frame = cv2.resize(frame, (640, 640))
    output,or_img = model.inference(frame)
    outbox = filter_box(output, 0.5,0.7)
    if outbox.shape[0] > 0:
        # print("框位置坐标:",outbox[:,:])
        data = draw(frame,outbox,frame_count,save_interval)
        print(data)
    cv2.imshow("frame",frame)
    if cv2.waitKey(1) == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
