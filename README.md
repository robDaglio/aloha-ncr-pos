# Aloha-NCR-POS

## Description
The **Aloha-NCR-POS** microservice addresses business date issues within POS XML payloads, and acts as an
intermediary between QPM and any service that may be posting POS transactions. The service will listen
for incoming **GET** or **POST** requests on a specified port, check and verify that the value contained within 
the XML **\<Date\>\</Date\>** tag matches the **current** date value and modify it if it doesn't match.
It will then forward the payload to **QPM** for posting.

## Dependencies
The service can be run as a Python application or as a Docker microservice. Note that the script will
not function properly **without the presence of QPM**. It has been designed to run on the machine hosting
the QPM application.The dependencies for each are as follows:

### Pre-requisites
* **SSH** Access to a Kitchen Advisor (virtual or hardware appliance)
* **QPM** installed and configured

### Script Dependencies
* WSL2 / Ubuntu 18.04 LTS (Bionic) | Ubuntu 20.04 (Focal Fossa)
* Python 3.10.2+ / virtualenv
* git

### Microservice Dependencies
* Docker 20.10.17 or later
* Access to KB private docker registry or Docker hub

## Installation
The process for installing the service as a script is straightforward, and even moreover as a Docker microservice.
Please assure that the desired log directory is accessible and possesses all necessary permissions for read + write as
per the use the service will be running under. The application will default to **/usr/src/app/logs**. Please note
that this directory is designed for use within the Docker container. Please create a directory and configure permissions
as per your use case. Make note of this directory as it will need to be mapped to a virtual directory within the container
or passed as a commandline argument when running the application as a python script.

**Create the logging directory**
```
sudo mkdir -p /var/log/kb/aloha
sudo chown user:user /var/log/kb/aloha
```

### Installing as a Python Script
1. SSH to the target KA.
```
ssh <user>@<host>
```
2. Clone the repository.
```
git clone http://sckgit.fastinc.com/QPM/aloha-ncr-pos.git
```
2. Navigate to the project directory.
```
cd aloha-ncr-pos
```
3. Create a virtual environment using Python3.10.2 or later.
```
python3.10 -m venv venv
```
3. Activate the virtual environment.
```
source venv/bin/activate
```
4. Upgrade pip and install dependencies from requirements.txt
```
python -m pip install --upgrade pip; python -m pip install -r requirements.txt
```

### Installing as a Docker Microservice
1. SSH to the target KA.
```
ssh <user>@<host>
```
2. Log into the docker registry.
```
docker login -u <user> -p <password>
```
3. Use docker pull to download the latest image.
```
docker pull docker.mysck.net/snapshots/qpm/aloha_ncr_pos
```

## Running the Service
The application will run out-of-the-box with no arguments given it is being run on a machine where QPM
is installed and configured properly.

### Running as a Script
1. Run in project directory. (Assure virtual environment is activated.)
```
python main.py
```
You should see something similar to the following.
```
(venv) user@Ubuntu:~$ python main.py
08-24-2022 08:23:54 - <module> - N/A - INFO: Service version: 1.0.0.8
08-24-2022 08:23:54 - <module> - N/A - INFO: Configuration: {
    "log_file": "/usr/src/app/logs/aloha-NCR-POS.log",
    "log_level": "INFO",
    "listening_port": 8083,
    "forwarding_port": 8080,
    "date_format": "%Y-%m-%d",
    "target_host": "localhost",
    "protocol": "http",
    "uri": "/instore/posXml"
}
======== Running on http://0.0.0.0:8083 ========
(Press CTRL+C to quit)
```

### Running as a Microservice
1. Use the **docker run** command to build and run the container.
```
docker run \
	-v /etc/timezone:/etc/timezone \
	-v /etc/localtime:/etc/localtime \
	-v /var/log/kb/aloha:/usr/src/app/logs \
	--net=host \
	--name aloha_ncr_pos \
	--restart=always \
	-d docker.mysck.net/release/qpm/aloha_ncr_pos
```
2. Inspect the logs to verify the service started successfully.
```
docker logs -f $(docker ps -aqf 'name=aloha_ncr_pos')
```

You should see something similar to the following:
```
08-24-2022 08:23:54 - <module> - N/A - INFO: Service version: 1.0.0.8
08-24-2022 08:23:54 - <module> - N/A - INFO: Configuration: {
    "log_file": "/usr/src/app/logs/aloha-NCR-POS.log",
    "log_level": "INFO",
    "listening_port": 8083,
    "forwarding_port": 8080,
    "date_format": "%Y-%m-%d",
    "target_host": "localhost",
    "protocol": "http",
    "uri": "/instore/posXml"
}
======== Running on http://0.0.0.0:8083 ========
(Press CTRL+C to quit)
```

## Parameters
When running the service as a script, you may inspect the available arguments that can be passed to the application
with the following command(s).
```
python main.py -h | python main.py --help
```

This will output the available parameters that can be passed to the service, should your setup require an alternative
configuration.
```
(venv) user@Ubuntu:~$ python main.py -h
usage: main.py [-h] [--log-file LOG_FILE] [--log-level LOG_LEVEL] [--listening-port LISTENING_PORT]
               [--forwarding-port FORWARDING_PORT] [--date-format DATE_FORMAT] [--target-host TARGET_HOST] [--protocol PROTOCOL]
               [--uri URI]

Aloha NCR/POS Date Corrections - Source: http://sckgit.fastinc.com/QPM/aloha-ncr-pos/tree/master

options:
  -h, --help            show this help message and exit
  --log-file LOG_FILE   Log file name. [env var: LOG_FILE] (default: /usr/src/app/logs/aloha-NCR-POS.log)
  --log-level LOG_LEVEL
                        Log level parameter. [env var: LOG_LEVEL] (default: INFO)
  --listening-port LISTENING_PORT
                        Port to listen on for incoming requests. [env var: LISTENING_PORT] (default: 8083)
  --forwarding-port FORWARDING_PORT
                        Port to forward to. [env var: FORWARDING_PORT] (default: 8080)
  --date-format DATE_FORMAT
                        The expected date format. [env var: DATE_FORMAT] (default: %Y-%m-%d)
  --target-host TARGET_HOST
                        The host to forward requests to. [env var: TARGET_HOST] (default: localhost)
  --protocol PROTOCOL   The protocol with which to send requests. [env var: PROTOCOL] (default: http)
  --uri URI             URI path to expose. [env var: URI] (default: /instore/posXml)

Args that start with '--' (eg. --log-file) can also be set in a config file (config/defaults.ini). Config file syntax allows:
key=value, flag=true, stuff=[a,b,c] (for details, see syntax at https://goo.gl/R74nmi). If an arg is specified in more than one
place, then commandline values override environment variables which override config file values which override defaults.
```

The most notable or useful of these will be the **listening-port**, **forwarding-port** and **protocol** parameters,
which can be changed by passing them with their respective commandline arguments, or by way of environment variables
when running the application as a Docker microservice.

### Using Custom Forwarding and Listening Ports
**Example 1** - Running the application as a script.
```
python main.py --listening-port 9999 --forwarding-port 1234
```
**Example 2** - Running the application as a Docker microservice.
```
docker run \
    -v /etc/timezone:/etc/timezone \
    -v /etc/localtime:/etc/localtime \
    -v /var/log/kb/aloha:/usr/src/app/logs \
    -e LISTENING_PORT=9999 \
    -e FORWARDING_PORT=1234 \
    --net=host \
    --name aloha_ncr_pos \
    --restart=always \
    -d docker.mysck.net/snapshot/qpm/aloha_ncr_pos
```

Verify the changes to the configuration were applied by using the methods described in the above **Running the Service**
section.
```
(venv) user@Ubuntu:~$ python main.py
31852 - 07-27-2022 12:04:01 - <module> - INFO: Service version: 3.0.2
31852 - 07-27-2022 12:04:01 - <module> - INFO: Configuration: {
    "log_file": "/var/log/kb/aloha/aloha-NCR-POS.log",
    "log_level": "INFO",
    "listening_port": "9999",
    "forwarding_port": "1234",
    "date_format": "%Y-%m-%d",
    "target_host": "localhost",
    "protocol": "http"
}
======== Running on http://0.0.0.0:8083 ========
(Press CTRL+C to quit)
```

### Using a Custom Protocol
The application supports both **HTTP** and **HTTPS**, and will default to HTTP if no parameter specifying otherwise
is provided.

**Example 1** - Running the application as a script.
```
python main.py --protocol https
```

**Example 2** - Running the application as a Docker Microservice.
```
docker run \
    -v /etc/timezone:/etc/timezone \
    -v /etc/localtime:/etc/localtime \
    -v /var/log/kb/aloha:/usr/src/app/logs \
    -e PROTOCOL=https \
    --net=host \
    --name aloha_ncr_pos \
    --restart=always \
    -d docker.mysck.net/snapshot/qpm/aloha_ncr_pos
```

Don't forget to verify all changes made in initial configuration output.

For support, please contact saasteam@kitchenbrains.com.















