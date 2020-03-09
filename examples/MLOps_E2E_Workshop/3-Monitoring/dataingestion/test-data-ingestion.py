data_file_name = getArgument("data_file_name")  # noqa: F821, E501
training_mount_point_name = getArgument("training_mount_point_name") + "/" + data_file_name  # noqa: F821, E501
testing_mount_point_name = getArgument("testing_mount_point_name") + "/" + data_file_name  # noqa: F821, E501

dbutils.fs.ls(training_mount_point_name)  # noqa: F821
dbutils.fs.ls(testing_mount_point_name)  # noqa: F821
