from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote

from app.core.config import settings
from app.utils.aes import aes_decode
from app.utils.logs import logger
import os

# logger.info(f"password database {settings.DATABASE_PASSWORD}")
# logger.info(f"password database {settings.ENCRYPT_KEY}")
# logger.info(f"DATABASE_PASSWORD: {os.getenv('DATABASE_PASSWORD')}")

# config_path = "/deployment/sc/config-sc.env"

# if os.path.exists(config_path):
#     try:
#         with open(config_path, "r") as f:
#             content = f.read()
#             logger.info(f"📄 Nội dung file config.env:\n{content}")
#     except Exception as e:
#         logger.error(f"❌ Lỗi khi đọc file config.env: {e}")
# else:
#     logger.warning(f"⚠️ File config.env không tồn tại tại đường dẫn: {config_path}")

SQLALCHEMY_DATABASE_URI = ('postgresql://{username}:%s@{host}:{port}/{database}'.format(
    username=settings.DATABASE_USERNAME,
    host=settings.DATABASE_HOST,
    port=settings.DATABASE_PORT,
    database=settings.DATABASE_DATABASE)) % quote(aes_decode(settings.DATABASE_PASSWORD))

engine = create_engine(
    SQLALCHEMY_DATABASE_URI,
    pool_size=20,
    max_overflow=100
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
