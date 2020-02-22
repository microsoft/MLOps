import cv2
import time
import numpy as np
import core.utils as utils
import tensorflow as tf
from core.yolov3 import YOLOv3, decode


class Tracker():
    def __init__(self):
        self._num_classes = 2
        self._input_size = 416

    def __enter__(self):
        self._vid = cv2.VideoCapture("")
        self._input_layer  = tf.keras.layers.Input([self._input_size, self._input_size, 3])
        self._feature_maps = YOLOv3(self._input_layer)
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if exc_type:
            print(exc_type, exc_value, exc_traceback)

    def run(self):
        bbox_tensors = []
        for i, fm in enumerate(self._feature_maps):
            bbox_tensor = decode(fm, i)
            bbox_tensors.append(bbox_tensor)

        model = tf.keras.Model(self._input_layer, bbox_tensors)
        utils.load_weights(model, "./checkpoint/yolov3.ckpt")
        model.summary()
        
        while True:
            return_value, frame = self._vid.read()
            if return_value:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            else:
                raise ValueError("No image!")
            frame_size = frame.shape[:2]
            image_data = utils.image_preporcess(np.copy(frame), [self._input_size, self._input_size])
            image_data = image_data[np.newaxis, ...].astype(np.float32)

            prev_time = time.time()
            pred_bbox = model.predict(image_data)
            curr_time = time.time()
            exec_time = curr_time - prev_time

            pred_bbox = [tf.reshape(x, (-1, tf.shape(x)[-1])) for x in pred_bbox]
            pred_bbox = tf.concat(pred_bbox, axis=0)
            bboxes = utils.postprocess_boxes(pred_bbox, frame_size, self._input_size, 0.3)
            bboxes = utils.nms(bboxes, 0.45, method='nms')
            image = utils.draw_bbox(frame, bboxes)

            result = np.asarray(image)
            info = "time: %.2f ms" %(1000*exec_time)
            cv2.putText(result, text=info, org=(50, 70), fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=1, color=(255, 0, 0), thickness=2)
            cv2.namedWindow("result", cv2.WINDOW_AUTOSIZE)
            result = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            cv2.imshow("result", result)
            if cv2.waitKey(1) & 0xFF == ord('q'): break

if __name__ == '__main__':
    with Tracker() as trk:
        trk.run()