"""
Helper class to facilitate working with Statistics Denmark's API. See the
official API documentation here
https://www.dst.dk/da/Statistik/brug-statistikken/muligheder-i-statistikbanken/api

Minor modification for JupyterLite: Local file version.
"""
import requests
import warnings
import pandas as pd
from io import StringIO

class DstApi:
    def __init__(self, tablename) -> None:
        self.apiip = "https://api.statbank.dk/v1"
        self.tablename = str(tablename).lower()
        self._tableinfo = None

    def _get_tableinfo(self, language="da"):
        url = f"{self.apiip}/tableinfo/{self.tablename}?lang={language}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error fetching table info: {response.status_code}")

    def _wrap_tableinfo_variables(self, tableinfo):
        return pd.DataFrame(tableinfo['variables'])

    def tablesummary(self, verbose=True, language="da") -> pd.DataFrame:
        if self._tableinfo is None:
            self._tableinfo = self._get_tableinfo(language=language)
        if verbose:
            print(f"Table {self._tableinfo['id']}: {self._tableinfo['description']}")
            print(f"Last update: {self._tableinfo['updated']}")
        table = self._wrap_tableinfo_variables(self._tableinfo)
        return table

    def variable_levels(self, varname, language="da") -> pd.DataFrame:
        if self._tableinfo is None:
            self._tableinfo = self._get_tableinfo(language=language)
        try:
            return pd.DataFrame(
                [i for i in self._tableinfo["variables"] if i["id"] == varname][0][
                    "values"
                ]
            )
        except IndexError as err:
            print("Error: Variable not found.")
            return err

    def _define_base_params(self, language="da"):
        if self._tableinfo is None:
            self._tableinfo = self._get_tableinfo(language=language)
        params = {'table': self.tablename, 'format': 'BULK', 'variables': []}
        for v in self._tableinfo['variables']:
            params['variables'].append({'code': v['id'], 'values': ['*']})
        return params

    def get_data(self, params=None, language="da", as_DataFrame=True, override_warning=False) -> pd.DataFrame:
        if params is None:
            params = self._define_base_params(language=language)
        
        url = f"{self.apiip}/data"
        response = requests.post(url, json=params)
        if response.status_code == 200:
            if as_DataFrame:
                return pd.read_csv(StringIO(response.text), sep=';')
            return response
        else:
            raise Exception(f"Error fetching data: {response.status_code}")
