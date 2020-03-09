# Phase 6: Monitoring Deployed Model

Now that you've deployed a trained model to either Azure Container Instances(ACI) or Azure Kubernetes Services(AKS). Let's start monitoring the model and the deployed ML model web service for any performance issues.


## Prerequisites

Complete all the tasks in **reproducible training** and **automated training and deployment** folders. 


## Resources

* [Documentation - Enabling Application Insights for ACI deployment](https://github.com/Azure/MachineLearningNotebooks/blob/master/how-to-use-azureml/deployment/enable-app-insights-in-production-service/enable-app-insights-in-production-service.ipynb)
* [Documentation - Monitor and collect data from ML web service endpoints](https://docs.microsoft.com/en-us/azure/machine-learning/how-to-enable-app-insights)
* [Documentation - What is Application Insights?](https://docs.microsoft.com/en-us/azure/azure-monitor/app/app-insights-overview)
* [Documentation - Set Alerts in Application Insights](https://docs.microsoft.com/en-us/azure/azure-monitor/app/alerts)
* [Documentation - Monitor the availability of any website](https://docs.microsoft.com/en-us/azure/azure-monitor/app/monitor-web-app-availability)


## Tasks

1. Start collecting model data i.e model inputs and model prediction outputs from the deployed model. This will be further used to detect data drifts or validate the model ***(data drift detection is not a requirement for this challenge).***
2. Enable telemetry collection on the ML model web service to measure the performance of the web service.
3. Built visual dashboards where your team can take a look at the performance of the web service.
4. Configure automated alerts to notify your team members of any performance degradation on web service.
5. Setup one availability test for the ML web service to ensure the service is always running and responding.

### Hints

* Use an **Application Insights** instance attached to your AML workspace as a commonplace to collect all telemetry.
  
### Success Criteria

To successfully complete this task, you must: 

* Successfully see model inputs and predictions in Application Insights traces.
* Successfully configure a chart tile on one of the standard metrics like request rates, response times, and failure rates collected from ML model web service and pined the tile to Azure Dashboard.
* Successfully configure an alert based on the standard metrics like request rates, response times, and failure rates collected from ML model web service that sends an email to the respective team.
* Successfully configure at least one availability test that notifies your team if the ML web service is not responding.


## Reflect

After completing this challenge, consider the following questions:

* What is the benefit of monitoring my ML model web service?
* What actions can I take based on the telemetry collected from ML model web service?
* How can I further leverage the model data collected from the deployed model?
