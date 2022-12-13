import numpy as np
from pymoo.core.problem import ElementwiseProblem
from sklearn.base import clone
import warnings

class FomoProblem(ElementwiseProblem):
    """ The evaluation function for each candidate sample weights. """

    def __init__(self, fomo_estimator=None):
        self.fomo_estimator=fomo_estimator
        n_var = len(self.fomo_estimator.X_)
        n_obj = (len(self.fomo_estimator.accuracy_metrics_)
                 +len(self.fomo_estimator.fairness_metrics_)
        )
        super().__init__(
            n_var = n_var,
            n_obj = n_obj,
            xl = np.zeros(n_var),
            xu = np.ones(n_var)
        )

    def _evaluate(self, x, out, *args, **kwargs):
        """Evaluate the weights, x, by fitting an estimator and evaluating."""

        X = self.fomo_estimator.X_
        y = self.fomo_estimator.y_
        est = clone(self.fomo_estimator.estimator)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            est.fit(X,y,sample_weight=x)
        f = np.empty(self.n_obj)
        j = 0
        for i, metric in enumerate(self.fomo_estimator.accuracy_metrics_):
            f[i] = metric(est, X, y)
            j += 1
        for metric in self.fomo_estimator.fairness_metrics_:
            f[j] = metric(est, X, y, **self.fomo_estimator.metric_kwargs)
            j += 1

        # f1 = 100 * (x[:, 0]**2 + x[:, 1]**2)
        # f2 = (x[:, 0]-1)**2 + x[:, 1]**2
        # out["F"] = np.column_stack([f1, f2])
        out['F'] = np.asarray(f)
