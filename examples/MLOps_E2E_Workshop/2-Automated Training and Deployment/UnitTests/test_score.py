import warnings
warnings.filterwarnings('ignore',
                        category=DeprecationWarning,
                        module="pywintypes")
from dsdevops.scoring.score import init, run  # noqa: E402


class TestScore:

    @staticmethod
    def test_init(mocker):
        # Given
        mock_model_get_model_path = mocker.patch(
            'azureml.core.model.Model.get_model_path')
        mock_joblib_load = mocker.patch('joblib.load')

        # When
        init()

        # Then
        mock_model_get_model_path.assert_called()
        mock_joblib_load.assert_called()

    @staticmethod
    def test_run():
        # Given
        test_row = '{"data":[[0,1,8,1,0,0,1,0,0,0,0,0,0,0,12,1,0,0,0.5,0.3,0.610327781,7,1,-1,0,-1,1,1,1,2,1,65,1,0.316227766,0.669556409,0.352136337,3.464101615,0.1,0.8,0.6,1,1,6,3,6,2,9,1,1,1,12,0,1,1,0,0,1]]}'  # noqa: E501
        init()

        # When
        result = run(test_row, {})

        # Then
        assert len(result) == 1
