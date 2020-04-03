# Distributed training of transformers based languaged model using torch.distributed.launch module on Azure Machine Learning

This sample show how to perform distributed training using Azure Machine Learning pytorch estimator(1) and NCCL backend and distributed launch utility.

The example also show how to train transformers based-language models from HuggingFace(3)
The distributed training scenarios covered are:
 - Single-gpu/mutli node
 - Multi-gpu/multi nodes *This required some changes to HF example which is available in(2)* '  


Latest Azureml-sdk tested: 1.1.5

Pytorch 1.4


## Prerequisites:

Before running this notebook, make sure you have gone through the steps listed below:

- You have a workspace created listed [here](https://docs.microsoft.com/en-us/azure/machine-learning/service/quickstart-get-started )  

#References

1.  https://docs.microsoft.com/en-us/python/api/azureml-train-core/azureml.train.dnn.pytorch?view=azure-ml-py

2. https://github.com/datashinobi/transformers/tree/yassine/aml_distributed

3. HuggingFace citation

  ```bibtex
@article{Wolf2019HuggingFacesTS,
  title={HuggingFace's Transformers: State-of-the-art Natural Language Processing},
  author={Thomas Wolf and Lysandre Debut and Victor Sanh and Julien Chaumond and Clement Delangue and Anthony Moi and Pierric Cistac and Tim Rault and R'emi Louf and Morgan Funtowicz and Jamie Brew},
  journal={ArXiv},
  year={2019},
  volume={abs/1910.03771}
}


