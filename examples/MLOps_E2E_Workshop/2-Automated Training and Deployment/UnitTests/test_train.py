from dsdevops.training.train import train_model, main
from azureml.core.run import Run

import argparse
import pytest
import pandas as pd
import warnings
warnings.filterwarnings('ignore', category=pytest.PytestCollectionWarning)


class TestTrain:

    @staticmethod
    def test_train_model(mocker):
        # Given
        test_data = {"train": {"X": [[1, 2, 3]], "y": [0]},
                     "test": {"X": [[4, 5, 6]], "y": [0]}}
        mock_lgbm_train = mocker.patch('lightgbm.train')
        mock_roc_curve = mocker.patch('sklearn.metrics.roc_curve')
        mock_roc_curve.return_value = [0.1, 0.1, 5]
        mock_auc = mocker.patch('sklearn.metrics.auc')

        # When
        train_model(Run.get_context(), test_data)

        # Then
        mock_lgbm_train.assert_called()
        mock_roc_curve.assert_called()
        mock_auc.assert_called()

    @staticmethod
    def test_main(mocker):

        # Given
        mock_pd_read_csv = mocker.patch('pandas.read_csv')
        mock_data = {'target': [0, 1]}
        mock_pd_read_csv.return_value = pd.DataFrame(
            mock_data, columns=['target'])
        mock_train_model = mocker.patch('dsdevops.training.train.train_model')
        mock_joblib_dump = mocker.patch('joblib.dump')

        mock_parse_args = mocker.patch('argparse.ArgumentParser.parse_args')
        mock_parse_args.return_value = argparse.Namespace(
            build_id='',
            model_name=''
        )

        # When
        main()

        # Then
        mock_pd_read_csv.assert_called()
        mock_train_model.assert_called()
        mock_joblib_dump.assert_called()
