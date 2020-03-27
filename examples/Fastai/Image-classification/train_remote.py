
import fastai
from fastai.vision import (ImageDataBunch, get_transforms, cnn_learner, models, imagenet_stats, accuracy)
from pathlib import Path 
from azureml.core.run import Run 
import numpy as np
import joblib

# get the Azure ML run object
run = Run.get_context()

# get images
path = Path('data')
np.random.seed(2)
data = ImageDataBunch.from_folder(path,
                                       train=".",
                                       valid_pct=0.2,
                                       ds_tfms=get_transforms(),
                                       size=224).normalize(imagenet_stats)

# build estimator based on ResNet 34
learn = cnn_learner(data, models.resnet34, metrics=accuracy)
learn.fit_one_cycle(2)

# do test time augmentation and get accuracy
acc = accuracy(*learn.TTA())


# log the accuracy to run
run.log('Accuracy', np.float(acc))
print("Accuracy: ", np.float(acc))



OUTPUT_DIR='./outputs'
os.makedirs(OUTPUT_DIR, exist_ok=True)
# save model file to the outputs/ folder to use outside the script
model_file_name = 'export.pkl'
joblib.dump(value=learn.export(), filename=os.path.join(OUTPUT_DIR, model_file_name))
