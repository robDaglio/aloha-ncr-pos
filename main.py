# =======================================================================
# Application name: Aloha NCR/POS Date Corrections
# Description: This program acts as a forwarder for POS payloads destined for QPM.
# It will parse the date within the XML payload, compare it to the current date
# and correct it if necessary before forwarding to QPM.
# Author: Rob Daglio
# Repository: http://sckgit.fastinc.com/QPM/aloha-ncr-pos
# =======================================================================

import json
import logging

from config import cfg
from aiohttp import web
from logger.logger import configure_logging


log = configure_logging(cfg.log_file, cfg.log_level)


def read_version_properties(properties_file: str) -> str:
    try:
        with open(properties_file, 'r') as f:
            version = f.read()
            return version.split('=')[-1] if '=' in version else version
    except (FileNotFoundError, IOError) as e:
        logging.exception(f'Unable to read properties file:\n{e}')
        return 'na'


if __name__ == '__main__':
    log.info(f'Service version: {read_version_properties("version.properties")}')
    log.info(f'Configuration: {json.dumps(vars(cfg), indent=4)}')

    from forwarder.forwarder import Forwarder

    app = web.Application()
    handler = Forwarder()

    app.add_routes([
        web.get(cfg.uri, handler.handler),
        web.post(cfg.uri, handler.handler)
    ])

    web.run_app(app, port=cfg.listening_port, access_log=None)
