# Distributed Mask R-CNN 

This sample show how to perform distributed training of Mask R-CNN using  Azure Machine Learning 

Latest azureml SDK tested: 1.1.5


## Prerequisites:

Before running this notebook, make sure you have gone through the steps listed below:

- You have a workspace created listed [here](https://docs.microsoft.com/en-us/azure/machine-learning/service/quickstart-get-started ) 

## References

- Distributed training in Azure Machine Learning:  https://github.com/Azure/MachineLearningNotebooks/tree/master/how-to-use-azureml/training-with-deep-learning

- Matterport's Mask R-CNN distributed training implementation
https://github.com/datashinobi/Mask_RCNN/tree/yassine/horovod

- Matterport Mask R-CNN 
```
@misc{matterport_maskrcnn_2017,
  title={Mask R-CNN for object detection and instance segmentation on Keras and TensorFlow},
  author={Waleed Abdulla},
  year={2017},
  publisher={Github},
  journal={GitHub repository},
  howpublished={\url{https://github.com/matterport/Mask_RCNN}},
}
```