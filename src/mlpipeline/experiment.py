"""Experiment module to create, run and store experiments' artifacts."""
from .pipeline import Pipeline
from .context import Context
from .metrics import Metrics
from .data import Data
import mlflow


class Experiment:
    """
    Experiment class that orchestrates the execution of an experiment.
    """
    mlflow_uri_path = '$PROJECT_PATHS$/../../mlruns'
    def __init__(self, conf=None, data=None, pipeline=None):
        self.config = conf
        self.data = data
        self.pipeline = pipeline
        self.results = None

    @property
    def config(self):
        return self._conf

    @config.setter
    def config(self, conf):
        if isinstance(conf, Context) or conf is None:
            self._conf = conf
        else:
            raise ValueError("Configuration must be a Context object.")

    @property
    def name(self):
        return self.config.exp_name

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data_conf):
        if data_conf is None and self.config is None:
            raise ValueError("Data object must be provided if conf parameter is None")
        if data_conf is None and self.config is not None:
            self._data = Data(train=self.config.train,
                              test=self.config.test,
                              target=self.config.target,
                              features=self.config.features)
        if isinstance(data_conf, Data):
            self._data = data_conf

    @property
    def pipeline(self):
        return self._pipeline

    @pipeline.setter
    def pipeline(self, pipeline_conf):
        if pipeline_conf is None and self.config is None:
            raise ValueError("Pipeline object must be provided if conf parameter is None")

        if pipeline_conf is None and self.config is not None:
            self._pipeline = Pipeline(self.config.transformers,
                                      self.config.vectorizer,
                                      self.config.estimators).init()

        if isinstance(pipeline_conf, Pipeline):
            self._pipeline = pipeline_conf.init()

    def run(self, probabilities=False):
        pipeline_fitted = self.pipeline.fit(self.data.train_X,
                                            self.data.train_Y)
        classes_ = pipeline_fitted._pipeline.steps[-1][1].classes_ if probabilities else 'outcome'
        func = pipeline_fitted.predict_proba if probabilities else pipeline_fitted.predict
        predicted = func(self.data.test_X)

        self.results = Metrics(exp_name=self.name,
                               classes=classes_,
                               test_Y=self.data.test_Y,
                               results=predicted)
        return self

    def save_to_mlflow(self):
        mlflow.set_tracking_uri(Experiment.mlflow_uri_path)
        print(mlflow.get_tracking_uri())
        with mlflow.start_run(run_name=self.name):
            mlflow.log_param('file name', 'TESTTEST')
            mlflow.log_metric('accuracy', self.results.accuracy_score)