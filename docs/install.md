# Installation

## Compatibility and Requirements

aiovectortiler uses Python 3.5's new asyncio module to provide asynchronous handling of HTTP requests and database communication.
Python 3.5 is therefore an absolute requirement.

You'll also need access to a running PostGIS database which hosts your data.

## Installation from source

First make sure that your context has `python 3.5`, `pip`, `git`, `psycopg2` and `shapely` installed.
If not, then the installation of the python requirements via `pip install` is likely to fail.

For example, on Ubuntu:
```
# If using an Ubuntu version earlier than 16.04, first add the deadsnakes PPA.
sudo add-apt-repository -y ppa:fkrull/deadsnakes

# Install the packages
apt-get update \
    && apt-get install -y git build-essential python3 python3-pip python3-psycopg2 python3-shapely \
    && pip3 install pip --upgrade
```
On a Mac, the conda python package manager is recommended as an easy manner for installing these packages.

On Windows, the easiest manner is to download prebuilt binaries.

Once these packages are available in your environment, proceed with:
```
git clone https://github.com/shongololo/aiovectortiler.git
cd aiovectortiler
pip install .
```

You can now run the aiovectortiler server from the command line:
```
python aiovectortiler/serve.py \
    --server_configs=/path/to/server_config.yaml \
    --layer_recipes=/path/to/recipes_folder/
```

## Installation from PyPI

As with installing from source, installation from `pip` can fail if `shapely` and `psycopg2` aren't already installed.
Follow the above instructions for installing these in your environment. 

Then install via pip:
```
pip install aiovectortiler
```

Once installed as a module, you can use an `example_aiovectortiler_script.py` to wrap the server in your own code:
```
from aiovectortiler.serve import serve_tiles

server_configs = '/path/to/server_config.yaml'
layer_recipes = '/path/to/recipes_folder/'
host = '0.0.0.0'  # this parameter is optional if req'd for overriding the default host
port = '8080'  # this parameter is optional if req'd for overriding the default host port

serve_tiles(server_configs, layer_recipes, host, port)
```
Such a script can then be run from the command line, e.g.: `python example_python_script.py`

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
