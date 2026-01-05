import logging
from app.core.config import settings


class LogSetup(object):
    def __init__(self, config=None, **kwargs):
        if config:
            self.init_config(config, **kwargs)

    def init_config(self, settings):
        log_type = settings.LOG_TYPE
        log_level = settings.LOG_LEVEL
        if log_type not in ["stream", "stream_and_kafka"]:
            try:
                log_directory = settings.LOG_DIR
                app_log_file_name = settings.APP_LOG_NAME
                access_log_file_name = settings.WWW_LOG_NAME
            except KeyError as e:
                exit(code="{} is a required parameter for log type '{}'".format(e, log_type))
            app_log = "/".join([log_directory, app_log_file_name])
            www_log = "/".join([log_directory, access_log_file_name])

        if log_type == "stream":
            logging_policy = "logging.StreamHandler"
        elif log_type == "stream_and_kafka":
            logging_policy = "logging.StreamHandler"
            logging_policy_kafka = "app.utils.kafka_logging_handler.KafkaLoggingHandler"
        elif log_type == "watched":
            logging_policy = "logging.handlers.WatchedFileHandler"
        else:
            log_max_bytes = settings["LOG_MAX_BYTES"]
            log_copies = settings["LOG_COPIES"]
            logging_policy = "logging.handlers.RotatingFileHandler"

        std_format = {
            "formatters": {
                "default": {
                    "format": "[%(asctime)s.%(msecs)03d] %(levelname)s %(name)s:%(funcName)s: %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S"
                },
                "access": {"format": "%(message)s"}
            }
        }
        std_logger = {
            "loggers": {
                "": {
                    "level": log_level,
                    "handlers": ["default"],
                    "propagate": True
                },
                "app.access": {
                    "level": log_level,
                    "handlers": ["access_logs"],
                    "propagate": False
                },
                "root": {
                    "level": log_level,
                    "handlers": ["default"]
                },
                "uvicorn.error": {
                    "level": log_level,
                    "handlers": ["default"],
                    "propagate": False
                },
                # "uvicorn.access": {
                #     "level": log_level,
                #     "handlers": ["default"],
                #     "propagate": False
                # }
            }
        }
        kafka_logger = {
            "loggers": {
                "": {
                    "level": log_level,
                    "handlers": ["default", "kafka_handlers"],
                    "propagate": True
                },
                "app.access": {
                    "level": log_level,
                    "handlers": ["access_logs"],
                    "propagate": False
                },
                "root": {
                    "level": log_level,
                    "handlers": ["default", "kafka_handlers"]
                },
                "uvicorn.error": {
                    "level": log_level,
                    "handlers": ["default", "kafka_handlers"],
                    "propagate": False
                },
                # "uvicorn.access": {
                #     "level": log_level,
                #     "handlers": ["default", "kafka_handlers"],
                #     "propagate": False
                # }
            }
        }

        if log_type == "stream":
            logging_handler = {
                "handlers": {
                    "default": {
                        "level": log_level,
                        "formatter": "default",
                        "class": logging_policy
                    },
                    "access_logs": {
                        "level": log_level,
                        "formatter": "access",
                        "class": logging_policy
                    }
                }
            }
        elif log_type == "stream_and_kafka":
            logging_handler = {
                "handlers": {
                    "default": {
                        "level": log_level,
                        "formatter": "default",
                        "class": logging_policy
                    },
                    "access_logs": {
                        "level": log_level,
                        "formatter": "access",
                        "class": logging_policy
                    },
                    "kafka_handlers": {
                        "level": log_level,
                        "formatter": "default",
                        "class": logging_policy_kafka,
                        "hosts_list": settings.KAFKA_BOOTSTRAP_SERVERS,
                        "topic": settings.KAFKA_TOPIC_LOG,
                        "security_protocol": settings.KAFKA_SECURITY_PROTOCOL,
                        "ssl_cafile": settings.KAFKA_SSL_CAFILE if settings.KAFKA_SSL_CAFILE != "" else None,
                        "kafka_producer_args": {
                            "api_version_auto_timeout_ms": settings.KAFKA_ARGS_API_VERSION_AUTO_TIMEOUT_MS,
                            "request_timeout_ms": settings.KAFKA_ARGS_REQUEST_TIMEOUT_MS
                        },
                        "additional_fields": {
                            "host_name": settings.LOG_HOST_NAME,
                            "clientMessageId": "",
                            "status_code": ""
                        }
                    }
                }
            }
        elif log_type == "watched":
            logging_handler = {
                "handlers": {
                    "default": {
                        "level": log_level,
                        "formatter": "default",
                        "class": logging_policy,
                        "filename": app_log,
                        "delay": True
                    },
                    "access_logs": {
                        "level": log_level,
                        "formatter": "access",
                        "class": logging_policy,
                        "filename": www_log,
                        "delay": True
                    }
                }
            }
        else:
            logging_handler = {
                "handlers": {
                    "default": {
                        "level": log_level,
                        "formatter": "default",
                        "class": logging_policy,
                        "filename": app_log,
                        "delay": True,
                        "maxBytes": log_max_bytes,
                        "backupCount": log_copies
                    },
                    "access_logs": {
                        "level": log_level,
                        "formatter": "access",
                        "class": logging_policy,
                        "filename": www_log,
                        "delay": True,
                        "maxBytes": log_max_bytes,
                        "backupCount": log_copies
                    }
                }
            }

        if log_type == "stream_and_kafka":
            log_config = {
                "version": 1,
                "formatters": std_format["formatters"],
                "loggers": kafka_logger["loggers"],
                "handlers": logging_handler["handlers"]
            }
        else:
            log_config = {
                "version": 1,
                "formatters": std_format["formatters"],
                "loggers": std_logger["loggers"],
                "handlers": logging_handler["handlers"]
            }
        return log_config


# setup log
logs = LogSetup()
logging.config.dictConfig(logs.init_config(settings))
logger = logging.getLogger(__name__)
