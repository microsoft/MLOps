import cv2
import os
import shutil
import numpy as np
import argparse
import urllib.request
import tensorflow as tf
import core.utils as utils
from azureml.core import Model, Run, Datastore
from core.config import cfg
from core.yolov3 import YOLOv3, decode
from urllib.parse import urlparse
from scripts.compress import zipFolder, unzipFolder
from os.path import splitext, basename


class Evaluate():
    
    def __init__(self):
        self._parser = argparse.ArgumentParser("evaluate")
        self._parser.add_argument("--release_id", type=str, help="The ID of the release triggering this pipeline run")
        self._parser.add_argument("--model_name", type=str, help="Name of the tf model")
        self._parser.add_argument("--ckpt_path", type=str, help="Chekpoint path", default="checkpoint/yolov3.ckpt")
        self._parser.add_argument("--datastore", type=str, help="Name of the datastore", default="epis_datastore")
        self._parser.add_argument("--storage_container", type=str, help="Name of the storage container", default="ppe")

        self._args = self._parser.parse_args()
        self._run = Run.get_context()
        self._exp = self._run.experiment
        self._ws = self._run.experiment.workspace
        self._datastore = Datastore.get(self._ws, datastore_name=self._args.datastore)

        self._INPUT_SIZE = 416
        self._NUM_CLASS = len(utils.read_class_names(cfg.YOLO.CLASSES))
        self._CLASSES = utils.read_class_names(cfg.YOLO.CLASSES)

        self._predicted_dir_path = 'mAP/predicted'
        self._ground_truth_dir_path = 'mAP/ground-truth'


    def evaluation(self):

        all_runs = self._exp.get_runs(properties={"release_id": self._args.release_id,
                                            "run_type": "train"}, include_children=True)
        new_model_run = next(all_runs)
        print(f'New Run found with Run ID of: {new_model_run.id}')

        new_model_run.download_file(name="check.zip", output_file_path="./checkpoint")
        unzipFolder('checkpoint/check.zip')

        new_model_run.download_file(name="model.zip", output_file_path=".")

        self.__createPaths()
        self.__getDataset()
        model = self.__loadModel()

        with open(cfg.TEST.ANNOT_PATH, 'r') as annotation_file:
            for num, line in enumerate(annotation_file):
                annotation = line.strip().split()
                image_path = annotation[0]
                disassembled = urlparse(image_path)
                filename, file_ext = splitext(basename(disassembled.path))
                resp = urllib.request.urlopen(image_path)
                image = np.asarray(bytearray(resp.read()), dtype="uint8")
                image = cv2.imdecode(image, cv2.IMREAD_COLOR)
                bbox_data_gt = np.array([list(map(int, box.split(','))) for box in annotation[1:]])

                if len(bbox_data_gt) == 0:
                    bboxes_gt=[]
                    classes_gt=[]
                else:
                    bboxes_gt, classes_gt = bbox_data_gt[:, :4], bbox_data_gt[:, 4]
                ground_truth_path = os.path.join(self._ground_truth_dir_path, filename + '.txt')

                self.__createGroundTruth(image_path, bboxes_gt, ground_truth_path, classes_gt)

                predict_result_path = os.path.join(self._predicted_dir_path, filename + '.txt')
                image_size = image.shape[:2]
                image_data = utils.image_preporcess(np.copy(image), [self._INPUT_SIZE, self._INPUT_SIZE])
                image_data = image_data[np.newaxis, ...].astype(np.float32)

                pred_bbox = model.predict(image_data)
                pred_bbox = [tf.reshape(x, (-1, tf.shape(x)[-1])) for x in pred_bbox]
                pred_bbox = tf.concat(pred_bbox, axis=0)
                bboxes = utils.postprocess_boxes(pred_bbox, image_size, self._INPUT_SIZE, cfg.TEST.SCORE_THRESHOLD)
                bboxes = utils.nms(bboxes, cfg.TEST.IOU_THRESHOLD, method='nms')

                self.__createPredictResults(image_path, predict_result_path, bboxes)
        
        zipFolder("grtruth.zip", "mAP/ground-truth")
        zipFolder("predicts.zip", "mAP/predicted")
        
        self._run.upload_file(name='grtruth.zip', path_or_stream ="grtruth.zip")
        print(f"Uploaded the ground-truth to experiment {self._run.experiment.name}")

        self._run.upload_file(name='predicts.zip', path_or_stream ="predicts.zip")
        print(f"Uploaded the predictions to experiment {self._run.experiment.name}")

        self._run.upload_file(name='model.zip', path_or_stream ="model.zip")
        print(f"Uploaded the model to experiment {self._run.experiment.name}")

        print("Following files are uploaded ")
        print(self._run.get_file_names())

        self._run.add_properties({"release_id": self._args.release_id, "run_type": "eval"})
        print(f"added properties: {self._run.properties}")

        self._run.complete()


    def __createPaths(self):
        if os.path.exists(self._predicted_dir_path): shutil.rmtree(self._predicted_dir_path)
        if os.path.exists(self._ground_truth_dir_path): shutil.rmtree(self._ground_truth_dir_path)
        if os.path.exists(cfg.TEST.DECTECTED_IMAGE_PATH): shutil.rmtree(cfg.TEST.DECTECTED_IMAGE_PATH)

        os.mkdir(self._predicted_dir_path)
        os.mkdir(self._ground_truth_dir_path)
        os.mkdir(cfg.TEST.DECTECTED_IMAGE_PATH)
    
    def __getDataset(self):
        voc_train = self._datastore.blob_service.list_blobs(self._args.storage_container, prefix='voc_train.txt')
        voc_test = self._datastore.blob_service.list_blobs(self._args.storage_container, prefix='voc_test.txt')

        voc_train_imagesets = list(voc_train)
        print("Succesfully get voc_train.txt")
        voc_test_imagesets = list(voc_test)
        print("Succesfully get voc_test.txt")

        self._datastore.blob_service.get_blob_to_path(self._args.storage_container, 
                                                voc_train_imagesets[0].name,
                                                f'./data/dataset/{voc_train_imagesets[0].name}')
        self._datastore.blob_service.get_blob_to_path(self._args.storage_container,
                                                voc_test_imagesets[0].name,
                                                f'./data/dataset/{voc_test_imagesets[0].name}')


    def __loadModel(self):
        input_layer  = tf.keras.layers.Input([self._INPUT_SIZE, self._INPUT_SIZE, 3])
        feature_maps = YOLOv3(input_layer)

        bbox_tensors = []
        for i, fm in enumerate(feature_maps):
            bbox_tensor = decode(fm, i)
            bbox_tensors.append(bbox_tensor)

        model = tf.keras.Model(input_layer, bbox_tensors)
        model.load_weights(self._args.ckpt_path)

        return model
    
    def __createGroundTruth(self, image_path, bboxes_gt, ground_truth_path, classes_gt):
        print('=> ground truth of %s:' % image_path)
        num_bbox_gt = len(bboxes_gt)
        with open(ground_truth_path, 'w') as f:
            for i in range(num_bbox_gt):
                class_name = self._CLASSES[classes_gt[i]]
                xmin, ymin, xmax, ymax = list(map(str, bboxes_gt[i]))
                bbox_mess = ' '.join([class_name, xmin, ymin, xmax, ymax]) + '\n'
                f.write(bbox_mess)

    def __createPredictResults(self, image_path, predict_result_path, bboxes):
        print('=> predict of %s:' % image_path)
        with open(predict_result_path, 'w') as f:
            for bbox in bboxes:
                coor = np.array(bbox[:4], dtype=np.int32)
                score = bbox[4]
                class_ind = int(bbox[5])
                class_name = self._CLASSES[class_ind]
                score = '%.4f' % score
                xmin, ymin, xmax, ymax = list(map(str, coor))
                bbox_mess = ' '.join([class_name, score, xmin, ymin, xmax, ymax]) + '\n'
                f.write(bbox_mess)
        

if __name__ == '__main__':
    evaluate = Evaluate()
    evaluate.evaluation()