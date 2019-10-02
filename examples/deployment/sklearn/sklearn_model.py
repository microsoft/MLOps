import joblib
import numpy as np
import os
from typing import List

class SKLearnModel(): #pylint:disable=c-extension-no-member
    def __init__(self, name: str, model_dir: str, model_file: str):
        super().__init__(name)
        self.name = name
        self.model_dir = model_dir
        self.model_file = model_file
        self.ready = False

    def load(self):
        model_file = os.path.join(self.model_dir, self.model_file) #pylint:disable=c-extension-no-member
        self._model = joblib.load(model_file) #pylint:disable=attribute-defined-outside-init
        self.ready = True

    def predict(self, body: List) -> List:
        try:
            inputs = np.array(body)
        except Exception as e:
            raise Exception(
                "Failed to initialize NumPy array from inputs: %s, %s" % (e, inputs))
        try:
            result = self._model.predict(inputs).tolist()
            return result
        except Exception as e:
            raise Exception("Failed to predict %s" % e)
