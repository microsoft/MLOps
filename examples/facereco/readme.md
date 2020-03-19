# Face recognition across Time  Lapse  Using  Convolutional  Neural Networks.

## Description

This notebook show how to use Machine Learning pipeline introduced in Azure Machine learning python SDK[1] through the reproduction of the paper *Face recognition across Time  Lapse  Using  Convolutional  Neural Networks*[2] by  El  Khiyari, H.and Wechsler,H.(2016).


## Model architecture

The overall architecture of the model  is depicted in the picture below, details of the pipepline compostion is further down the page.


<img style='margin:40px;width: 40%;' src='https://amlgitsamples.blob.core.windows.net/facereco/resources/Architecture.JPG'/>

## Dataset 

The FG-NET[4]  dataset contain multiple images per subject, thereby reflecting variability in age,  pose, illumination and expression. The sample used in this experiment is composed of 976 images of 82 subjects where subjects ages vary between 0 and 69. 

<img style='margin:40px;width: 40%;' 
src='https://amlgitsamples.blob.core.windows.net/facereco/resources/fgnet.jpg'/>

Given the different types of appearance variations in the images, i.e gray-scale or color,and some of the color images have a color cast. The preprocessing that was done consist of:

  - Face alignments
  - Image resize to (224,224,3) to match VGG-face network tensors input shape.
  - Conversion of Images color into gray-scale  to mitigate the inﬂuence of inconsistent colors.
        
To offload computation and make the notebook accessible, the processed images have been made available [here](https://amlgitsamples.blob.core.windows.net/facereco/training_set/fgnet).

## Pipeline

### Step 1: Image Preprocessing (preprocessing.py)

In this step we construct a "metadata" dataframe that contains the age, link to image on storage, and finally the label ID of the person, obtained from images names. please refer to FGNET codebook[4] for images naming convention details.


### Step 2:  VGG-face network features extraction (vggface.py)

The VGG-Face CNN descriptors are based on the VGG-Very-Deep-16 CNN architecture described in [3]. The network
is composed of a sequence of convolutional, pool, and fully-connected (FC) layers. The convolutional layers
use filters of dimension 3 while the pool layers perform subsampling with a factor of 2. 

The CNN features are extracted from the 1st fully connected layer resulting in a matrix of shape (976, 4096), at last we normalize each component by the L2-norm of the feature vector as described by the authors in their paper[2] 


The architecture of
the VGG-Face network is shown below


<img style='margin:40px;width: 40%;' src='https://amlgitsamples.blob.core.windows.net/facereco/resources/vggface.JPG'/>


### Step 3: Dimensionality reduction (pca.py)

We project the extracted features in step 2 into a 40 latent dimensional space whilst retaining +80% of the explained variance.

<img style='margin:40px;width: 40%;' 
src='https://amlgitsamples.blob.core.windows.net/facereco/resources/pca.JPG'/>

### Step 4: Classification (classifier.py)

In the last step, we train a KNN classifier  using 5 fold cross validation and finaly we report  mean training and testing accuracy across folds trough Azure ML run [5]. the results are comparable to the experiment results reported by the authors of the paper[2] 

<img style='margin:40px;width: 40%;' 
src='https://amlgitsamples.blob.core.windows.net/facereco/resources/acc.PNG'/>





## References
[1]  Azure Machine learning pipeline https://docs.microsoft.com/en-us/azure/machine-learning/service/concept-ml-pipelines

[2] Hachim El Khiyari, Harry Wechsler (2016) Face Recognition across Time Lapse Using Convolutional Neural Networks. Journal of Information Security,07,141-151. doi:[10.4236/jis.2016.73010](http://dx.doi.org/10.4236/jis.2016.73010)


[3] Parkhi, O.M., Vedaldi, A. and Zisserman, A. (2015) Deep Face Recognition. Proceedings of the British Machine Vision Conference (BMVC), Swansea, 7-10 September 2015.   

[4]  FGNET dataset: Face and Gesture Recognition Working Group (2000) http://www-prima.inrialpes.fr/FGnet/html/about.html, 
kudos to Yanwifu for making it available
https://github.com/yanweifu/yanweifu.github.io/tree/master/FG_NET_data

[5] Azure Machine learning Run https://docs.microsoft.com/en-us/python/api/azureml-core/azureml.core.run(class)?view=azure-ml-py

[6] Keras Vgg-face library https://github.com/rcmalli/keras-vggface






