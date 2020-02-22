from easydict import EasyDict as edict


__C                           = edict()
# Consumers can get config by: from config import cfg

cfg                           = __C

# YOLO options
__C.YOLO                      = edict()

# Set the class name
__C.YOLO.CLASSES              = "data/classes/voc.names"
__C.YOLO.ANCHORS              = "data/anchors/baseline_anchors.txt"
__C.YOLO.MOVING_AVE_DECAY       = 0.9995
__C.YOLO.STRIDES              = [8, 16, 32]
__C.YOLO.ANCHOR_PER_SCALE     = 3
__C.YOLO.IOU_LOSS_THRESH      = 0.5
__C.YOLO.UPSAMPLE_METHOD        = "resize"

# Train options
__C.TRAIN                     = edict()

__C.TRAIN.ANNOT_PATH          = "data/dataset/voc_train.txt"
__C.TRAIN.BATCH_SIZE          = 4
# __C.TRAIN.INPUT_SIZE            = [320, 352, 384, 416, 448, 480, 512, 544, 576, 608]
__C.TRAIN.INPUT_SIZE          = [416]
__C.TRAIN.DATA_AUG            = True
__C.TRAIN.LR_INIT             = 1e-3
__C.TRAIN.LR_END              = 1e-6
__C.TRAIN.WARMUP_EPOCHS       = 2
__C.TRAIN.EPOCHS              = 1



# TEST options
__C.TEST                      = edict()

__C.TEST.ANNOT_PATH           = "data/dataset/voc_test.txt"
__C.TEST.BATCH_SIZE           = 2
__C.TEST.INPUT_SIZE           = 544
__C.TEST.DATA_AUG             = False
__C.TEST.WRITE_IMAGE          = True
__C.TEST.DECTECTED_IMAGE_PATH = "mAP/detection/"
__C.TEST.WEIGHT_FILE          = "checkpoint/yolov3.ckpt"
__C.TEST.SHOW_LABEL           = True
__C.TEST.SCORE_THRESHOLD      = 0.3
__C.TEST.IOU_THRESHOLD        = 0.45