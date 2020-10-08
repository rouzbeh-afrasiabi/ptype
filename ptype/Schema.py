import pandas as pd


class Schema:
    def __init__(
        self,
        df,
        cols,
    ):
        self.df = df
        self.cols = cols

    def show(self):
        df = self.df.iloc[0:0, :].copy()
        df.loc[0] = [col.type for _, col in self.cols.items()]
        df.loc[1] = [col.get_normal_values() for _, col in self.cols.items()]
        df.loc[2] = [col.get_missing_values() for _, col in self.cols.items()]
        df.loc[3] = [col.get_anomalous_values() for _, col in self.cols.items()]
        return df.rename(
            index={
                0: "type",
                1: "normal values",
                2: "missing values",
                3: "anomalous values",
            }
        )

    def show_ratios(self):
        df = self.df.iloc[0:0, :].copy()
        df.loc[0] = [col.type for _, col in self.cols.items()]
        df.loc[1] = [col.get_normal_ratio() for _, col in self.cols.items()]
        df.loc[2] = [col.get_missing_ratio() for _, col in self.cols.items()]
        df.loc[3] = [col.get_anomalous_ratio() for _, col in self.cols.items()]
        return df.rename(
            index={
                0: "type",
                1: "ratio of normal values",
                2: "ratio of missing values",
                3: "ratio of anomalous values",
            }
        )

    def as_normal(self):
        return lambda series: series.map(
            lambda v: v if v in self.cols[series.name].get_normal_values() else pd.NA
        )

    def transform(self, df):
        """Transforms a dataframe according to the schema.

         Parameters
         ----------
         df: Pandas dataframe object.

         Returns
         -------
         Transformed Pandas dataframe object.
         """
        df = df.apply(self.as_normal(), axis=0)
        ptype_pandas_mapping = {
            "integer": "Int64",
            "date-iso-8601": "datetime64",
            "date-eu": "datetime64",
            "date-non-std": "datetime64",
            "string": "string",
            "boolean": "boolean",  # will remove boolean later
            "float": "float64",
        }
        for col_name in df:
            new_dtype = ptype_pandas_mapping[self.cols[col_name].type]
            if new_dtype == "boolean":
                df[col_name] = df[col_name].apply(
                    lambda x: False
                    if str(x) in ["F"]
                    else (True if str(x) in ["T"] else x)
                )

            try:
                df[col_name] = df[col_name].astype(new_dtype)
            except TypeError:
                # TODO: explain why this case needed
                df[col_name] = pd.to_numeric(df[col_name], errors="coerce").astype(
                    new_dtype
                )
        return df

