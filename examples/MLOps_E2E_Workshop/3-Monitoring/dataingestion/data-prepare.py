# The data preparation Python notebook running on a Databricks cluster
import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedShuffleSplit

# Parsing the notebook parameters
data_file_name = getArgument("data_file_name")  # noqa: F821

# Source data file (csv) is stored in a blob storage in the inputdata container
# The training and testing data (bin) will be saved to the training data
# and testing data containers respectively
# All containers are mounted to dbfs file system in the Databricks workspace
input_mount_point_name = "/dbfs" + getArgument("input_mount_point_name")  # noqa: F821, E501
training_mount_point_name = "/dbfs" + getArgument("training_mount_point_name")  # noqa: F821, E501
testing_mount_point_name = "/dbfs" + getArgument("testing_mount_point_name")  # noqa: F821, E501

# Read and clean the data from the scouce file
data = pd.read_csv(input_mount_point_name + "/" + data_file_name)
# Replace all Non-alphanumeric Characters with Underscore
data.columns = ["".join (c if c.isalnum() else "_" for c in str(x)) for x in data.columns]  # noqa: E211, E501

# Split Data into Features and Labels
labels = np.array(data['target'])
features = data.drop('target', axis=1)

# Create Stratified Folds
sss = StratifiedShuffleSplit(n_splits=2, test_size=0.2, random_state=0)
sss.get_n_splits(features, labels)

# Split Data into Training and Testing Sets
train_index, test_index = next(sss.split(features, labels))
train_data = data.iloc[train_index]
test_data = data.iloc[test_index]

# Save Data to CSV
train_data.to_csv(training_mount_point_name + "/" + data_file_name)
test_data.to_csv(testing_mount_point_name + "/" + data_file_name)
