# Installation

## Compatibility and Requirements

Due to the use of Python's asyncio, Python 3.5 is an absolute requirement.

You'll also need access to a running PostGIS database which hosts your data.

## Installation from source

First make sure that your context has `python 3.5`, `pip`, `git`, `psycopg2` and `shapely` installed.

For example, on Ubuntu 16.04:
```
apt-get update \
    && apt-get install -y git build-essential python3 python3-pip python3-psycopg2 python3-shapely \
    && pip3 install pip --upgrade
```
On Mac, the conda python package manager is recommended as an easy manner for installing these packages.

Once these packages are available in your environment, proceed with:
```
git clone https://github.com/shongololo/aiovectortiler.git
cd aiovectortiler
pip install .
```

You can now run the aiovectortiler server from the command line:
```
python aiovectortiler/serve.py --server_configs=/path/to/server_config.yaml --layer_recipes=/path/to/recipes_folder/
```

## Installation from PyPI

Installation from `pip` can fail if `shapely` and `psycopg2` aren't already installed. It is therefore recommended to install these first. 

Then run:
```
pip install aiovectortiler
```

You can then use an `example_aiovectortiler_script.py` to invoke the server as follows:
```
from aiovectortiler.serve import serve_tiles

server_configs = '/path/to/server_config.yaml'
layer_recipes = '/path/to/recipes_folder/'
host = '0.0.0.0'  # this parameter is optional if req'd for overriding the default host
port = '8080'  # this parameter is optional if req'd for overriding the default host port

serve_tiles(server_configs, layer_recipes, host, port)
```
Such a script would be run from the command line, e.g.: `python example_python_script.py`

## Installation using docker

1. Pull the docker image
```
docker pull shongololo:aiovectortiler
```

2. Run the docker image, passing-in environment variables for your server config and recipes folder, and map the container port to the preferred host port.
```
docker run -p 8080:80 shongololo:aiovectortiler
```

## Next steps

Setting up your [server and layer configurations](config.md).
