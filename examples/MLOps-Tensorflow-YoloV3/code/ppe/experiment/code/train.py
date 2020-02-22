import os
import time
import shutil
import numpy as np
import argparse
import tensorflow as tf
import core.utils as utils

from tqdm import tqdm
from azureml.core.run import Run
from azureml.core import Datastore
from azureml.tensorboard import Tensorboard
from core.dataset import Dataset
from core.yolov3 import YOLOv3, decode, compute_loss
from core.config import cfg
from scripts.mime import mime_content_type
from scripts.compress import zipFolder
from azure.storage.blob import ContentSettings


class Train():

    def __init__(self):
        self._parser = argparse.ArgumentParser("train")
        self._parser.add_argument("--release_id", type=str, help="The ID of the release triggering this pipeline run")
        self._parser.add_argument("--model_name", type=str, help="Name of the tf model")
        self._parser.add_argument("--ckpt_path", type=str, help="Chekpoint path", default="checkpoint/yolov3.ckpt")
        self._parser.add_argument("--datastore", type=str, help="Name of the datastore", default="epis_datastore")
        self._parser.add_argument("--storage_container", type=str, help="Name of the storage container", default="ppe")

        self._args = self._parser.parse_args()
        self._run = Run.get_context()
        self._exp = self._run.experiment
        self._ws = self._run.experiment.workspace
        self._tb = Tensorboard([self._run])
        self._datastore = Datastore.get(self._ws, datastore_name=self._args.datastore)
    
    def __get_mime_type(self, file_path):
        return mime_content_type(file_path)

    def training(self):

        self.__getDataset()

        trainset = Dataset('train')
        logdir = "./data/log"
        steps_per_epoch = len(trainset)
        global_steps = tf.Variable(1, trainable=False, dtype=tf.int64)
        warmup_steps = cfg.TRAIN.WARMUP_EPOCHS * steps_per_epoch
        total_steps = cfg.TRAIN.EPOCHS * steps_per_epoch

        input_tensor = tf.keras.layers.Input([416, 416, 3])
        conv_tensors = YOLOv3(input_tensor)

        output_tensors = []
        for i, conv_tensor in enumerate(conv_tensors):
            pred_tensor = decode(conv_tensor, i)
            output_tensors.append(conv_tensor)
            output_tensors.append(pred_tensor)
        
        model = tf.keras.Model(input_tensor, output_tensors)
        optimizer = tf.keras.optimizers.Adam()
        if os.path.exists(logdir): shutil.rmtree(logdir)
        writer = tf.summary.create_file_writer(logdir)

        self._tb.start()
        for epoch in range(cfg.TRAIN.EPOCHS):
            print(epoch)
            for image_data, target in trainset:
                self.__train_step(image_data, target, model,
                                global_steps, writer, optimizer,
                                warmup_steps, total_steps)
            model.save_weights(self._args.ckpt_path)
        self._tb.stop()
        model.save(f"./models")

        zipFolder("check.zip", "checkpoint")
        zipFolder("log.zip", "data/log")
        zipFolder("model.zip", "models")

        self._run.upload_file(name='check.zip', path_or_stream ="check.zip")
        print(f"Uploaded the checkpoints to experiment {self._run.experiment.name}")
        self._run.upload_file(name='log.zip', path_or_stream ="log.zip")
        print(f"Uploaded the tfruns to experiment {self._run.experiment.name}")
        self._run.upload_file(name='model.zip', path_or_stream ="model.zip")
        print(f"Uploaded the model to experiment {self._run.experiment.name}")

        print("Following files are uploaded")
        print(self._run.get_file_names())

        self._run.add_properties({"release_id": self._args.release_id, "run_type": "train"})
        print(f"added properties: {self._run.properties}")

        self._run.complete()


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


    def __train_step(self, image_data, target, model, global_steps, writer, optimizer, warmup_steps, total_steps):
        with tf.GradientTape() as tape:
            pred_result = model(image_data, training=True)
            giou_loss=conf_loss=prob_loss=0

            for i in range(3):
                conv, pred = pred_result[i*2], pred_result[i*2+1]
                loss_items = compute_loss(pred, conv, *target[i], i)
                giou_loss += loss_items[0]
                conf_loss += loss_items[1]
                prob_loss += loss_items[2]

            total_loss = giou_loss + conf_loss + prob_loss

            gradients = tape.gradient(total_loss, model.trainable_variables)
            optimizer.apply_gradients(zip(gradients, model.trainable_variables))
            tf.print("=> STEP %4d   lr: %.6f   giou_loss: %4.2f   conf_loss: %4.2f   "
                    "prob_loss: %4.2f   total_loss: %4.2f" %(global_steps, optimizer.lr.numpy(),
                                                            giou_loss, conf_loss,
                                                            prob_loss, total_loss))
            global_steps.assign_add(1)
            if global_steps < warmup_steps:
                lr = global_steps / warmup_steps *cfg.TRAIN.LR_INIT
            else:
                lr = cfg.TRAIN.LR_END + 0.5 * (cfg.TRAIN.LR_INIT - cfg.TRAIN.LR_END) * (
                    (1 + tf.cos((global_steps - warmup_steps) / (total_steps - warmup_steps) * np.pi))
                )
            optimizer.lr.assign(lr.numpy())

            with writer.as_default():
                tf.summary.scalar("lr", optimizer.lr, step=global_steps)
                tf.summary.scalar("loss/total_loss", total_loss, step=global_steps)
                tf.summary.scalar("loss/giou_loss", giou_loss, step=global_steps)
                tf.summary.scalar("loss/conf_loss", conf_loss, step=global_steps)
                tf.summary.scalar("loss/prob_loss", prob_loss, step=global_steps)
            writer.flush()


if __name__ == '__main__':
    train = Train()
    train.training()