import pathlib

from pydantic import BaseSettings
import os
from dotenv import load_dotenv
from typing import List

# Project Directories
# ROOT = pathlib.Path(__file__).resolve().parent.parent

# Project Directories
ROOT = pathlib.Path(__file__).resolve().parent.parent

if os.path.isfile("/deployment/config/config.env"):
    config_file_path = "/deployment/config/config.env"
else:
    config_file_path = os.path.join(ROOT, "config_local.env")

load_dotenv(config_file_path, override=True)
load_dotenv("/deployment/sc/config-sc.env", override=True)

class Settings(BaseSettings):
    # ==== API ====
    API_V1_STR: str = "/api/v1"

    # ==== ENCRYPTION ====
    ENCRYPT_KEY: str = ""

    # ==== MODEL CONFIG ====
    ML_MODELS_DIRECTORY: str = "./app/ml_models/"
    APARTMENT_PRICE_MODEL_FILENAME: str = "apartment_price.joblib"
    APARTMENT_PRICE_MODEL_DEFAULT_INVALID_VALUE_RETURN: int = -1
    APARTMENT_PRICE_MODEL_AREA_MIN: int = 25
    APARTMENT_PRICE_MODEL_AREA_MAX: int = 300
    APARTMENT_PRICE_MODEL_FINAL_FEATURES_NAMES: List[str] = [
        'area', 'pn', 'duong', 'ref_tinh_code', 'ref_huyen_code', 'ref_xa_code', 'prj_name'
    ]

    # ==== DATABASE ====
    DATABASE_HOST: str = "10.1.16.49"
    DATABASE_PORT: str = "5432"
    DATABASE_USERNAME: str = ""
    DATABASE_PASSWORD: str = ""
    DATABASE_DATABASE: str = "postgres"
    DATABASE_SCHEMA: str = "price_prediction"

    # ==== OAUTH2 ====
    OAUTH2_TOKEN_URL: str = "http://localhost:8001/oauth2-server/oauth/token"
    OAUTH2_TOKEN_INSPECT_URL: str = "http://localhost:8001/oauth2-server/oauth/inspect-token"
    CALL_OAUTH2_SERVICE_TIMEOUT: int = 5

    # ==== KAFKA ====
    KAFKA_BOOTSTRAP_SERVERS: List[str] = [
        "10.1.16.247:9092",
        "10.1.16.248:9092",
        "10.1.16.249:9092",
    ]
    KAFKA_TOPIC_LOG: str = "LOG_EDP_BIGDATA"
    KAFKA_SECURITY_PROTOCOL: str = "PLAINTEXT"
    KAFKA_SSL_CAFILE: str = ""
    KAFKA_ARGS_API_VERSION_AUTO_TIMEOUT_MS: int = 1000000
    KAFKA_ARGS_REQUEST_TIMEOUT_MS: int = 1000000

    # ==== LOGGING ====
    LOG_TYPE: str = "stream"
    LOG_LEVEL: str = "INFO"
    LOG_DIR: str = "logs"
    APP_LOG_NAME: str = "app_log"
    WWW_LOG_NAME: str = "access_log"
    LOG_HOST_NAME: str = "apartment-price-prediction"

    class Config:
        case_sensitive = True
        # env_file = "../deployment/config/config.env"


settings = Settings()
