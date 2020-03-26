
import os
ROOT_DIR = os.path.abspath("../../")

def run(is_distributed,logs_dir):
    from dataset import ShapesDataset
    from mrcnn.config import Config
    
    ######################
    class ShapesConfig(Config):
        NAME = "shapes"
        GPU_COUNT = 2
        IMAGES_PER_GPU =2 
        NUM_CLASSES = 1 + 3
        IMAGE_MIN_DIM = 128
        IMAGE_MAX_DIM = 128
        RPN_ANCHOR_SCALES = (8, 16, 32, 64, 128)
        TRAIN_ROIS_PER_IMAGE = 32
        STEPS_PER_EPOCH = 10
        VALIDATION_STEPS = 5

    config = ShapesConfig()
    config.display()
    
    # Training dataset
    dataset_train = ShapesDataset()
    dataset_train.load_shapes(500000, config.IMAGE_SHAPE[0], config.IMAGE_SHAPE[1])
    dataset_train.prepare()

    # Validation dataset
    dataset_val = ShapesDataset()
    dataset_val.load_shapes(5000, config.IMAGE_SHAPE[0], config.IMAGE_SHAPE[1])
    dataset_val.prepare()
    if is_distributed:
        import mrcnn.distributed_model as modellib
    else:
        import mrcnn.model as modellib
        
    from mrcnn import utils

    # Local path to trained weights file
    COCO_MODEL_PATH = os.path.join(ROOT_DIR, "mask_rcnn_coco.h5")

    # Download COCO trained weights from Releases if needed
    if not os.path.exists(COCO_MODEL_PATH):
        utils.download_trained_weights(COCO_MODEL_PATH)


    # number of found devices by TF
    from tensorflow.python.client import device_lib
    device_lib.list_local_devices()
    
    # Create model in training mode
    model = modellib.MaskRCNN("training", config, logs_dir)

    # Load weights trained on MS COCO, but skip layers that
        # are different due to the different number of classes
        # See README  @ https://github.com/matterport/Mask_RCNNfor instructions to download the COCO weights
    model.load_weights(COCO_MODEL_PATH, by_name=True,
                       exclude=["mrcnn_class_logits", "mrcnn_bbox_fc", 
                                "mrcnn_bbox", "mrcnn_mask"])


    
    model.train(dataset_train, dataset_val, 
                learning_rate=config.LEARNING_RATE, 
                epochs=1000, 
                layers='heads')
