# Customer churn prediction


This sample is an update of the customer churn sample previously made available as part of the real world scenario under Azure Machine learning workbench.

https://github.com/Azure-Samples/MachineLearningSamples-ChurnPrediction

The latest Azureml-sdk tested wirh 1.0.57

## Changes introduced:
- Training using Azure Machine Learning Service pipeline.
- Model training done with a probabilistic deep network using deep kernel learning approach.
- Hyperparameters tunning using Azure ML's Hyperdrive

## Prerequisites:

Before running this notebook, make sure you have gone through the steps listed below:

- You have a workspace created listed [here](https://docs.microsoft.com/en-us/azure/machine-learning/service/quickstart-get-started )  

- In order to get started with Azure Machine learning SDK, please go through the getting started tutorials on [Azure ML official repo](https://github.com/Azure/MachineLearningNotebooks)


## Pipeline

### Preprocessing

The preprocessing done consist of one hot encoding the categorical features and normalizing the numeric features.

### Model architecture

The model  consist of training a binary classifier using a Deep kernel learning approach which combines the non-parametric flexibility of gaussian process with the inductive biases of deep learning architectures using stochastic variational inference to tackle the intractable marginal likelihood.

This novel DKL appoach used in this example,named stochastic-variational deep kernel learning (SV-DKL) is described in the paper[1]. 
The model was built using Gpytorch[2]. An awesome Gaussian process library built using pytorch

<img style='margin:40px;width: 40%;' 
src='https://amlgitsamples.blob.core.windows.net/churn/network.PNG'/>

As depicted in the figure above, the input features matrix is fed to a fully connected network with relu activation function and batch normalization that learns a 2 dimensional top level features corresponding to the number of classes, next we place a Gaussian process on each dimension of these features using spectral mixing kernels[2].This additive Gaussian processes layer is then followed by a linear mixing layer that is finally mapped to labels. 

Finally, the weights of the deep network, spectral mixture kernels, and mixing layer are all learned jointly through the variational marginal likelihood of the SV-DKL model[1]. 

The resulting model can be viewed as a Gaussian process which uses an additive series of deep kernels with weight sharing.


### Result

The pipeline is composed as a DAG using Azure ML pipeline[6]. The model is trained on Azure ML Compute[4] on a GPU based cluster and hyperparameters are tuned throught Azure ML hyperdrive[5].

The experiment was set to run for twenty run on a four nodes based GPU cluster. The overall execution last for a duration around ~39 minutes.

<img style='margin:40px;width: 40%;' 
src='https://amlgitsamples.blob.core.windows.net/churn/hyperdrive.PNG'/>

The best run achieve an AUC of 86% on evaluation set.

<img style='margin:40px;width: 40%;' 
src='https://amlgitsamples.blob.core.windows.net/churn/auc.PNG'/>

## References
[1] Stochastic Variational Deep Kernel Learning https://arxiv.org/pdf/1611.00336.pdf

[2] Gpytroch 
```
@inproceedings{gardner2018gpytorch,
  title={GPyTorch: Blackbox Matrix-Matrix Gaussian Process Inference with GPU Acceleration},
  author={Gardner, Jacob R and Pleiss, Geoff and Bindel, David and Weinberger, Kilian Q and Wilson, Andrew Gordon},
  booktitle={Advances in Neural Information Processing Systems},
  year={2018}
}
```

[3] Specture Mixture kernel https://arxiv.org/pdf/1302.4245.pdf

[4] Azure ML compute https://docs.microsoft.com/en-us/azure/machine-learning/service/how-to-set-up-training-targets#amlcompute

[5] Azure ML Hyperparameters tuning https://docs.microsoft.com/en-us/azure/machine-learning/service/how-to-tune-hyperparameters

[6] Azure ML pipeline https://docs.microsoft.com/en-us/azure/machine-learning/service/concept-ml-pipelines





