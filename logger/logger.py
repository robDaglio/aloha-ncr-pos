import logging


class SystemLogFilter(logging.Filter):
    def filter(self, record):
        if not hasattr(record, 'task_id'):
            record.task_id = 'N/A'

        return True


def configure_logging(log_file: str, log_level: str) -> logging.Logger:

    logging.basicConfig(
        format='%(asctime)s - %(funcName)s - %(task_id)s - %(levelname)s: %(message)s',
        datefmt='%m-%d-%Y %H:%M:%S',
        level=logging.getLevelName(log_level.upper()),
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file, 'a+', 'utf-8')
        ]
    )

    system_log = logging.getLogger()

    for handler in system_log.handlers:
        handler.addFilter(SystemLogFilter())

    return system_log
