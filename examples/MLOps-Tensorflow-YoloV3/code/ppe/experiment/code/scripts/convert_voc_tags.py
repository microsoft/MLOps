import os
import re
import argparse
import xml.etree.ElementTree as ET
from azureml.core import Workspace
from azureml.core.model import Model
from azureml.core import Datastore
from azureml.core.authentication import ServicePrincipalAuthentication

def convert_voc_annotation(ws, ds, data_type, container_name, use_difficult_bbox=True):
    classes = ['yellow', 'white', 'blue', 'red', 'hat']

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
    for image_ind in image_inds:
        image_path = datastore.blob_service.make_blob_url(container_name, 'VOC/JPEGImages/'+ image_ind + '.jpg')
        annotation = image_path
        label_path = datastore.blob_service.get_blob_to_text(container_name, 'VOC/Annotations/'+ image_ind + '.xml').content
        print(f'XML {image_ind}')
        with open(f"./Test/{image_ind}.xml", 'w') as f:
            root = ET.fromstring(label_path)
            root.set('verified', '')
            root.find('path').text = f'{image_ind}.xml'
            root.find('folder').text = ''
            objects = root.findall('object')
            for obj in objects:
                class_ind = obj.find('name').text.lower().strip()
                if (class_ind in classes):
                    obj.find('name').text = 'helmet'
                elif(class_ind == "person"):
                    obj.find('name').text = 'none'
            f.write(ET.tostring(root, encoding='unicode'))

if __name__ == '__main__':

    TENANT_ID = ""
    APP_ID = ""
    APP_SECRET = ""
    WORKSPACE_NAME = ""
    SUBSCRIPTION_ID = ""
    RESOURCE_GROUP = ""
    EPIS_CONTAINER = ""
    EPIS_DATASTORE = ""

    SP_AUTH = ServicePrincipalAuthentication(
        tenant_id=TENANT_ID,
        service_principal_id=APP_ID,
        service_principal_password=APP_SECRET)

    ws = Workspace.get(
        WORKSPACE_NAME,
        SP_AUTH,
        SUBSCRIPTION_ID,
        RESOURCE_GROUP
    )

    convert_voc_annotation(ws, EPIS_DATASTORE, "trainval", EPIS_CONTAINER, use_difficult_bbox=True)
    convert_voc_annotation(ws, EPIS_DATASTORE, "test", EPIS_CONTAINER, use_difficult_bbox=True)