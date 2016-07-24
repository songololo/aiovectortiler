# Installation

## Compatibility and Requirements

Due to the use of Python's asyncio, Python 3.5 is an absolute requirement.

You'll also need access to a running PostGIS database which hosts your data.

## Installation from source

```
git clone https://github.com/shongololo/aiovectortiler.git
cd aiovectortiler
pip install .

python aiovectortiler/serve.py --server_configs=/path/to/server_config.yaml --layer_recipes=/path/to/recipes_folder/
```

## Installation from PyPI

```
pip install aiovectortiler
```

`example_python_script.py` containing your server config and recipes folder path, which can then be run directly:
```
from aiovectortiler.serve import serve_tiles

server_configs = '/path/to/server_config.yaml'
layer_recipes = '/path/to/recipes_folder/'
host = '0.0.0.0'  # this parameter is optional if req'd for overriding the default host
port = '8080'  # this parameter is optional if req'd for overriding the default host port

serve_tiles(server_configs, layer_recipes, host, port)
```
Then run from the command line per usual: `python example_python_script.py`

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
