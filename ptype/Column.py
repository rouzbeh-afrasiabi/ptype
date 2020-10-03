from collections import OrderedDict
from enum import Enum
import joblib
import numpy as np
from ptype.utils import project_root
from ptype.Model import TYPE_INDEX, MISSING_INDEX, ANOMALIES_INDEX


def get_unique_vals(col, return_counts=False):
    """List of the unique values found in a column."""
    return np.unique([str(x) for x in col.tolist()], return_counts=return_counts)


# Use same names and values as the constants in Model.py. Could consolidate.
class Status(Enum):
    TYPE = 1
    MISSING = 2
    ANOMALOUS = 3


class Feature(Enum):
    U_RATIO = 5
    U_RATIO_CLEAN = 6
    U = 7
    U_CLEAN = 8


class Column:
    def __init__(
        self,
        series,
        counts,
        p_t,
        p_z,
    ):
        self.series = series
        self.p_t = p_t
        self.p_t_canonical = {}
        self.p_z = p_z
        self.type = self.inferred_type()
        self.unique_vals, self.unique_vals_counts = get_unique_vals(self.series, return_counts=True)
        self.initialise_missing_anomalies()
        self.unique_vals_status = [
            Status.TYPE
            if i in self.normal_indices
            else Status.MISSING
            if i in self.missing_indices
            else Status.ANOMALOUS
            if i in self.anomalous_indices
            else None  # only happens in the "all identical" case?
            for i, _ in enumerate(self.unique_vals)
        ]
        self.features = self.get_features(counts)
        self.arff_type = column2ARFF.get_arff(self.features)[0]
        self.arff_posterior = column2ARFF.get_arff(self.features)[1]
        self.categorical_values = (
            self.get_normal_values() if self.arff_type == "nominal" else None
        )

    def __repr__(self):
        ptype_pandas_mapping = {
            "integer": "Int64",
            "date-iso-8601": "datetime64",
            "date-eu": "datetime64",
            "date-non-std": "datetime64",
            "string": "string",
            "boolean": "bool",  # will remove boolean later
            "float": "float64",
        }  # ouch
        props = {
            "type": self.type,
            "dtype": ptype_pandas_mapping[self.type],
            "arff_type": self.arff_type,
            "normal_values": self.get_normal_values(),
            "missing_values": self.get_missing_values(),
            "missingness_ratio": self.get_missing_ratio(),
            "anomalies": self.get_anomalous_values(),
            "anomalous_ratio": self.get_anomalous_ratio(),
            "categorical_values": self.categorical_values,
        }
        return repr(props)

    def inferred_type(self):
        # Unpleasant special case when posterior vector has entries which are equal
        if len(set(self.p_t.values())) == 1:
            return "all identical"
        else:
            return max(self.p_t, key=self.p_t.get)

    def initialise_missing_anomalies(self):
        if self.type != "all identical":
            row_posteriors = self.p_z[self.type]
            max_row_posterior_indices = np.argmax(row_posteriors, axis=1)

            self.normal_indices = list(np.where(max_row_posterior_indices == TYPE_INDEX)[0])
            self.missing_indices = list(np.where(max_row_posterior_indices == MISSING_INDEX)[0])
            self.anomalous_indices = list(np.where(max_row_posterior_indices == ANOMALIES_INDEX)[0])
        else:
            self.normal_indices = []
            self.missing_indices = []
            self.anomalous_indices = []

    def has_missing(self):
        return self.get_missing_values() != []

    def has_anomalous(self):
        return self.get_anomalous_values() != []

    def get_normal_ratio(self):
        return round(sum(self.unique_vals_counts[self.normal_indices]) / sum(self.unique_vals_counts), 2)

    def get_missing_ratio(self):
        return round(sum(self.unique_vals_counts[self.missing_indices]) / sum(self.unique_vals_counts), 2)

    def get_anomalous_ratio(self):
        return round(sum(self.unique_vals_counts[self.anomalous_indices]) / sum(self.unique_vals_counts), 2)

    def get_normal_values(self):
        return list(self.unique_vals[self.normal_indices])

    def get_missing_values(self):
        return list(self.unique_vals[self.missing_indices])

    def get_anomalous_values(self):
        return list(self.unique_vals[self.anomalous_indices])

    def get_features(self, counts):
        posterior = OrderedDict()
        for t, p in sorted(self.p_t.items()):
            # aggregate date subtypes
            t_0 = t.split("-")[0]
            if t_0 in posterior.keys():
                posterior[t_0] += p
            else:
                posterior[t_0] = p
        posterior = posterior.values()

        entries = [str(int_element) for int_element in self.series.tolist()]
        U = len(np.unique(entries))
        U_clean = len(self.normal_indices)

        N = len(entries)
        N_clean = sum([counts[index] for index in self.normal_indices])

        u_ratio = U / N
        if U_clean == 0 and N_clean == 0:
            u_ratio_clean = 0.0
        else:
            u_ratio_clean = U_clean / N_clean

        return np.array(list(posterior) + [u_ratio, u_ratio_clean, U, U_clean])

    def set_row_types(self, normal_values, missing_values, anomalous_values):

        self.normal_indices = normal_values
        self.missing_indices = missing_values
        self.anomalous_indices = anomalous_values

        self.unique_vals_status = [
            Status.TYPE
            if i in self.normal_indices
            else Status.MISSING
            if i in self.missing_indices
            else Status.ANOMALOUS
            if i in self.anomalous_indices
            else None  # only happens in the "all identical" case?
            for i, _ in enumerate(self.unique_vals)
        ]

        # update arff related things


class Column2ARFF:
    def __init__(self, model_folder="models"):
        self.normalizer = joblib.load(model_folder + "robust_scaler.pkl")
        self.clf = joblib.load(model_folder + "LR.sav")

    def get_arff(self, features):
        features[[Feature.U.value, Feature.U_CLEAN.value]] = self.normalizer.transform(
            features[[Feature.U.value, Feature.U_CLEAN.value]].reshape(1, -1)
        )[0]
        arff_type = self.clf.predict(features.reshape(1, -1))[0]

        if arff_type == "categorical":
            arff_type = "nominal"
        # find normal values for categorical type

        arff_type_posterior = self.clf.predict_proba(features.reshape(1, -1))[0]

        return arff_type, arff_type_posterior


column2ARFF = Column2ARFF(project_root() + "/../models/")
