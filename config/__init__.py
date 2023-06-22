import configargparse

parser = configargparse.get_argument_parser(
    default_config_files=['config/defaults.ini'],
    description='Aloha NCR/POS Date Corrections - '
                'Source: <url>',
    formatter_class=configargparse.ArgumentDefaultsHelpFormatter
)

parser.add_argument('--log-file', env_var='LOG_FILE', type=str, required=False,
                    default='/usr/src/app/logs/aloha-NCR-POS.log', help='Log file name.')

parser.add_argument('--log-level', env_var='LOG_LEVEL', type=str, required=False,
                    default='INFO', help='Log level parameter.')

parser.add_argument('--listening-port', env_var='LISTENING_PORT', type=int, required=False,
                    default=8083, help='Port to listen on for incoming requests.')

parser.add_argument('--forwarding-port', env_var='FORWARDING_PORT', type=int, required=False,
                    default=8080, help='Port to forward to.')

parser.add_argument('--date-format', env_var='DATE_FORMAT', type=str, required=False,
                    default='%Y-%m-%d', help='The expected date format.')

parser.add_argument('--target-host', env_var='TARGET_HOST', type= str, required=False,
                    default='localhost', help='The host to forward requests to.')

parser.add_argument('--protocol', env_var='PROTOCOL', type=str, required=False,
                    default='http', help='The protocol with which to send requests.')

parser.add_argument('--uri', env_var='URI', type=str, required=False,
                    default='/some/url', help='URI path to expose.')

cfg = parser.parse_known_args()[0]
