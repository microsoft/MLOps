# Distributed training using torch.distributed.launch module on Azure Machine Learning

This sample uses hugging face transformers based language modeling example to show how to perform distributed training using Azure Machine Learning pytorch estimator using pytorch distributed launch utility.

https://github.com/huggingface/transformers/blob/master/examples/run_language_modeling.py


Latest Azureml-sdk tested: 1.1.5

Pytorch 1.4


## Prerequisites:

Before running this notebook, make sure you have gone through the steps listed below:

- You have a workspace created listed [here](https://docs.microsoft.com/en-us/azure/machine-learning/service/quickstart-get-started )  

## References

- https://github.com/huggingface/transformers/tree/master/examples
- https://huggingface.co/transformers/v1.2.0/examples.html#introduction
- https://medium.com/huggingface/training-larger-batches-practical-tips-on-1-gpu-multi-gpu-distributed-setups-ec88c3e51255
- https://pytorch.org/docs/stable/distributed.html
- https://docs.microsoft.com/en-us/python/api/azureml-train-core/azureml.train.dnn.pytorch?view=azure-ml-py