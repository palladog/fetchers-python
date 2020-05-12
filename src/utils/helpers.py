import os
import pandas as pd
from pandas import DataFrame
from typing import Tuple, List


class AdmTranslator:
    def __init__(self, csv_fname: str):
        self.translation_pd = self.load_translation_csv(csv_fname)

    def load_translation_csv(self, csv_fname) -> DataFrame:
        colnames = ['input_adm_area_1', 'input_adm_area_2', 'input_adm_area_3',
                    'adm_area_1', 'adm_area_2', 'adm_area_3', 'gid']
        if not os.path.exists(csv_fname):
            return None
        translation_pd = pd.read_csv(csv_fname, names=colnames, header=None)
        translation_pd = translation_pd.where((pd.notnull(translation_pd)), None)
        return translation_pd

    def tr(self, input_adm_area_1: str = None, input_adm_area_2: str = None, input_adm_area_3: str = None,
           return_original_if_failure: bool = False) -> Tuple[bool, str, str, str, List]:
        for index, row in self.translation_pd.iterrows():
            if row.input_adm_area_1 == input_adm_area_1 \
                    and row.input_adm_area_2 == input_adm_area_2 \
                    and row.input_adm_area_3 == input_adm_area_3:
                return True, row.adm_area_1, row.adm_area_2, row.adm_area_3, row.gid.split(':')
        if return_original_if_failure:
            return False, input_adm_area_1, input_adm_area_2, input_adm_area_3, None
        else:
            return False, None, None, None, None