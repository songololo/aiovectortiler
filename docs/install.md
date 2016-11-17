# Installation

## Compatibility and Requirements

aiovectortiler uses Python 3.5's new asyncio module to provide asynchronous handling of HTTP requests and database communication.
Python 3.5 is therefore an absolute requirement.

You'll also need access to a running PostGIS database which hosts your data.

## Installation using docker

To use with docker, you'll need a directory containing:
* Your `server_configs.yaml` file;
* A `layer_recipes` folder.

Your directory should now look something like this:
```
aiovectortiler_docker_folder
 - server_configs.yaml
 - layer_recipes
    - recipe_1.yaml
    - recipe_2.yaml
    - etc.
```
Then run the image, binding your docker container port to your desired localhost port, 
and mapping your folder to `/configs``:
```
docker run -i -t -p 8080:80 -v /path/to/local/configs:/configs shongololo/aiovectortiler
```
Your aiovectortiler server will now be running and available at `localhost:80`

## Installation from source

First make sure that your environment has `python 3.5`, `pip`, `git`, `shapely`, and `protobuf` installed.
If not, then the installation of the python requirements via `pip install .` may fail.

For example, on Ubuntu:
```
# If using an Ubuntu version earlier than 16.04, first add the deadsnakes PPA.
sudo add-apt-repository -y ppa:fkrull/deadsnakes

# Install the packages
sudo apt-get update \
    && sudo apt-get install -y git build-essential python3 python3-pip python3-psycopg2 python3-shapely protobuf-compiler\
    && pip3 install pip --upgrade
```
On a Mac, the conda python package manager is an easy manner to install these packages.

On Windows, downloaded prebuilt binaries tends to be the best option.

Once these packages are available in your environment, proceed with:
```
git clone https://github.com/shongololo/aiovectortiler.git
cd aiovectortiler
pip install .  # Note the trailing period
```
You can now run the app from the command line:
```
python /path/to/aiovectortiler/aiovectortiler/serve.py \
    --server_configs=/path/to/server_config.yaml \
    --layer_recipes=/path/to/recipes_folder/
```

## Installation from PyPI

As with installing from source, installation from PyPI can fail if `shapely` and `protobuf` aren't already separately installed.

You can then proceed to install aiovectortiler via pip: 
```
pip install aiovectortiler
```

Once installed as a module, you can use a python script to wrap the server in your own code context:
```
from aiovectortiler.serve import serve_tiles

server_configs = '/path/to/server_config.yaml'
layer_recipes = '/path/to/recipes_folder/'
host = '0.0.0.0'  # this parameter is optional if req'd for overriding the default host
port = '8080'  # this parameter is optional if req'd for overriding the default host port

serve_tiles(server_configs, layer_recipes, host, port)

# this script could then be run from the command line per: python /path/to/example_python_script.py
```

## Next steps

Set up your [server and layer configurations](config.md).
