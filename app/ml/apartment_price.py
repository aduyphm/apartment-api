import joblib
import pandas as pd
from app.core.config import settings
from app.utils.preprocessing import __cast_num_type__, __cast_cat_type__


class ApartmentPricePreProcessing:
    def __init__(self, area,
                 pn,
                 duong,
                 ref_tinh_code,
                 ref_huyen_code,
                 ref_xa_code,
                 prj_name):
        self.area = area
        self.pn = pn
        self.duong = duong
        self.ref_tinh_code = ref_tinh_code
        self.ref_huyen_code = ref_huyen_code
        self.ref_xa_code = ref_xa_code
        self.prj_name = prj_name
        self.flag_valid_data = False

    def numeric_procesing(self):
        self.area = __cast_num_type__(self.area)
        self.pn = __cast_num_type__(self.pn)
        self.ref_tinh_code = __cast_num_type__(self.ref_tinh_code)
        self.ref_huyen_code = __cast_num_type__(self.ref_huyen_code)
        self.ref_xa_code = __cast_num_type__(self.ref_xa_code)
        return self

    def cat_processing(self):
        self.prj_name = __cast_cat_type__(self.prj_name)
        self.duong = __cast_cat_type__(self.duong)
        return self

    def check_valid_data(self):
        self.flag_valid_data = settings.APARTMENT_PRICE_MODEL_AREA_MIN <= self.area <= settings.APARTMENT_PRICE_MODEL_AREA_MAX
        return self

    def processing_data(self):
        self.numeric_procesing()
        self.cat_processing()
        self.check_valid_data()
        return self


class ApartmentPriceModelling:
    def __init__(self, model_path):
        self.model_path = model_path
        self.model = None
        self.__load_model__()

    def __load_model__(self):
        self.model = joblib.load(self.model_path)
        return self

    def predict(self, **kwargs):
        data = ApartmentPricePreProcessing(**kwargs).processing_data()
        if not data.flag_valid_data:
            return settings.APARTMENT_PRICE_MODEL_DEFAULT_INVALID_VALUE_RETURN
        else:
            feature = [data.area, data.pn, data.duong,
                       data.ref_tinh_code, data.ref_huyen_code,
                       data.ref_xa_code, data.prj_name]
            val = pd.DataFrame(columns=settings.APARTMENT_PRICE_MODEL_FINAL_FEATURES_NAMES)
            val.loc[0] = feature
            val = self.model.predict(val)
            val = int(val)
            val = max(val, 1e7)
            val = min(val, 3e8)
            return val
