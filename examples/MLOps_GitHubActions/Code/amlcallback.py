import tensorflow as tf


class AMLCallback(tf.keras.callbacks.Callback):

    def __init__(self, run):
        self.run = run
        self.offline = self.run.id.startswith('OfflineRun')
        if self.offline:
            print('Offline AML Context: {}'.format(self.offline))
        else:
            print('Online AML Context: {}'.format(run))

    def set_params(self, params):
        self.params = params
        self.metrics = self.params['metrics']

    def set_model(self, model):
        self.model = model

    def on_train_batch_end(self, batch, logs=None):
        if not self.offline:
            for item in self.metrics:
                if item in logs:
                    self.run.log(item, logs[item])

    def on_epoch_end(self, epoch, logs=None):
        if not self.offline:
            for item in self.metrics:
                if item in logs:
                    self.run.log('epoch_{}'.format(item), logs[item])