import logging
from opencensus.ext.azure.log_exporter import AzureLogHandler
from sfm.config import get_settings

app_settings = get_settings()


def create_logger(logger_name):
    logging.basicConfig(
        filename="logs.log",
        level=logging.DEBUG,
        format="%(asctime)s %(pathname)s %(levelname)s %(message)s",
    )

    logger = logging.getLogger(logger_name)
    logger.addHandler(
        AzureLogHandler(
            connection_string="InstrumentationKey="
            + app_settings.AZURE_LOGGING_CONN_STR
        )
    )

    return logger
