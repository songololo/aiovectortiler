# Installation

## Compatibility and Requirements

Due to the use of Python's asyncio, Python 3.5 is an absolute requirement.

You'll also need access to a running PostGIS database which hosts your data.

## Installation from source

1. Clone aiovectortiler:  

`git clone https://github.com/shongololo/aiovectortiler.git`

2. Install:  

`cd aiovectortiler`

`pip install .`
        
3. Run from the command line:  

`python aiovectortiler/serve.py --server_configs=/path/to/server_config.yaml --layer_recipes=/path/to/recipes_folder/`

## Installation from PyPI

1. Install using pip  

`pip install aiovectortiler`

2. Create a python file containing your server config and recipes folder path, which can then be run directly:  
```
from aiovectortiler.serve import serve_tiles

server_configs = '/path/to/server_config.yaml'
layer_recipes = '/path/to/recipes_folder/'
host = '0.0.0.0'  # this parameter is optional if req'd for overriding the default host
port = '8080'  # this parameter is optional if req'd for overriding the default host port

serve_tiles(server_configs, layer_recipes, host, port)
```

## Installation using docker

1. Pull the docker image  

`docker pull shongololo:aiovectortiler`

2. Run the docker image, passing-in environment variable for your server config and recipes folder, and map the container port to the preferred host port.  
```
docker run \
    -e AIOVECTORTILER_SERVER_CONFIGS=/path/to/server_config.yaml \
    -e AIOVECTORTILER_LAYER_RECIPES=/path/to/recipes_folder \
    -p 8080:8080 \
    shongololo:aiovectortiler
```

## Next steps

Setup your [server and layer configurations](config.md).
