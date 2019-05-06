# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license.

from sklearn.externals import joblib
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler,OneHotEncoder
from sklearn_pandas import DataFrameMapper
import os
import pandas as pd

from azureml.core import Run
from azureml.contrib.explain.model.tabular_explainer import TabularExplainer
from azureml.contrib.explain.model.explanation.explanation_client import ExplanationClient

os.makedirs('./outputs', exist_ok=True)

# Get the IBM employee attrition dataset
attritionData = pd.read_csv('./WA_Fn-UseC_-HR-Employee-Attrition.csv')

# Dropping Employee count as all values are 1 and hence attrition is independent of this feature
attritionData = attritionData.drop(['EmployeeCount'], axis=1)
# Dropping Employee Number since it is merely an identifier
attritionData = attritionData.drop(['EmployeeNumber'], axis=1)
attritionData = attritionData.drop(['Over18'], axis=1)
# Since all values are 80
attritionData = attritionData.drop(['StandardHours'], axis=1)

# Converting target variables from string to numerical values
target_map = {'Yes': 1, 'No': 0}
attritionData["Attrition_numerical"] = attritionData["Attrition"].apply(lambda x: target_map[x])
target = attritionData["Attrition_numerical"]

attritionXData = attritionData.drop(['Attrition_numerical', 'Attrition'], axis=1)

# Creating dummy columns for each categorical feature
categorical = []
for col, value in attritionXData.iteritems():
    if value.dtype == 'object':
        categorical.append(col)

# Store the numerical columns in a list numerical
numerical = attritionXData.columns.difference(categorical)

numeric_transformations = [([f], Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler())])) for f in numerical]
    
categorical_transformations = [([f], OneHotEncoder(handle_unknown='ignore', sparse=False)) for f in categorical]

transformations = numeric_transformations + categorical_transformations

# Append classifier to preprocessing pipeline.
# Now we have a full prediction pipeline.
clf = Pipeline(steps=[('preprocessor', DataFrameMapper(transformations)),
                      ('classifier', LogisticRegression(solver='lbfgs'))])

# Split data into train and test
from sklearn.model_selection import train_test_split
x_train, x_test, y_train, y_test = train_test_split(attritionXData, 
                                                    target, 
                                                    test_size = 0.2,
                                                    random_state=0,
                                                    stratify=target)

# write x_text out as a pickle file for later visualization
x_test_pkl = 'x_test.pkl'
with open(x_test_pkl, 'wb') as file:
    joblib.dump(value=x_test, filename=os.path.join('./outputs/', x_test_pkl))

# preprocess the data and fit the classification model
clf.fit(x_train, y_train)
model = clf.steps[-1][1]

model_file_name = 'log_reg.pkl'

# save model in the outputs folder so it automatically get uploaded
with open(model_file_name, 'wb') as file:
    joblib.dump(value=clf, filename=os.path.join('./outputs/',
                                                 model_file_name))

# Explain predictions on your local machine
tabular_explainer = TabularExplainer(model, initialization_examples=x_train, features=attritionXData.columns, classes=["Not leaving", "leaving"], transformations=transformations)

# Explain overall model predictions (global explanation)
# Passing in test dataset for evaluation examples - note it must be a representative sample of the original data
# x_train can be passed as well, but with more examples explanations it will
# take longer although they may be more accurate
global_explanation = tabular_explainer.explain_global(x_test)

# Uploading model explanation data for storage or visualization in webUX
# The explanation can then be downloaded on any compute
comment = 'Global explanation on classification model trained on IBM employee attrition dataset'

# ScoringExplainer
scoring_explainer = tabular_explainer.create_scoring_explainer(x_test)
# Pickle scoring explainer locally
scoring_explainer_path = scoring_explainer.save('scoring_explainer_deploy')

run = Run.get_context()
client = ExplanationClient.from_run(run)
client.upload_model_explanation(global_explanation, comment=comment)
# upload x_test, pickled above
run.upload_file('x_test_ibm.pkl', os.path.join('./outputs/', x_test_pkl))

# Register original model
run.upload_file('original_model.pkl', os.path.join('./outputs/', model_file_name))
original_model = run.register_model(model_name='IBM_attrition_model', model_path='original_model.pkl')

# Register scoring explainer
run.upload_file('IBM_attrition_explainer.pkl', scoring_explainer_path)
scoring_explainer_model = run.register_model(model_name='IBM_attrition_explainer', model_path='IBM_attrition_explainer.pkl')
