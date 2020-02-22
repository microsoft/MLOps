import os
import re
import argparse
import xml.etree.ElementTree as ET

from scripts.mime import mime_content_type
from azureml.core import Datastore
from azure.storage.blob import ContentSettings

def __get_mime_type(file_path):
        return mime_content_type(file_path)

def convert_voc_annotation(ws, ds, data_type, anno_path, container_name, use_difficult_bbox=True):
    classes = ['helmet', 'none']

    datastore = Datastore.get(ws, datastore_name=ds)
    voc_dataset_annotations = datastore.blob_service.list_blobs(container_name, prefix='VOC/Annotations')
    voc_dataset_images = datastore.blob_service.list_blobs(container_name, prefix='VOC/JPEGImages')
    voc_dataset_imagesets = datastore.blob_service.list_blobs(container_name, prefix=f'VOC/ImageSets/Main/{data_type}.txt')

    voc_list_annotations = list(voc_dataset_annotations)
    print("Succesfully list annotations")
    voc_list_images = list(voc_dataset_images)
    print("Succesfully list images")
    voc_list_imagesets = list(voc_dataset_imagesets)
    print("Succesfully list imagesets")

    txt = datastore.blob_service.get_blob_to_text(container_name, voc_list_imagesets[0].name)
    txt_split = txt.content.splitlines()
    image_inds = [line.strip() for line in txt_split]
    with open(anno_path, 'a') as f:
        for image_ind in image_inds:
            image_path = datastore.blob_service.make_blob_url(container_name, 'VOC/JPEGImages/'+ image_ind + '.jpg')
            annotation = image_path
            label_path = datastore.blob_service.get_blob_to_text(container_name, 'VOC/Annotations/'+ image_ind + '.xml').content
            root = ET.fromstring(label_path)
            objects = root.findall('object')
            for obj in objects:
                difficult = obj.find('difficult').text.strip()
                if (not use_difficult_bbox) and(int(difficult) == 1):
                    continue
                bbox = obj.find('bndbox')
                class_ind = classes.index(obj.find('name').text.lower().strip())
                xmin = bbox.find('xmin').text.strip()
                xmax = bbox.find('xmax').text.strip()
                ymin = bbox.find('ymin').text.strip()
                ymax = bbox.find('ymax').text.strip()
                annotation += ' ' + ','.join([xmin, ymin, xmax, ymax, str(class_ind)])
            print(annotation)
            f.write(annotation + "\n")
    datastore.blob_service.create_blob_from_path(container_name,
                                                anno_path,
                                                anno_path,
                                                content_settings=ContentSettings(content_type=__get_mime_type(anno_path)))