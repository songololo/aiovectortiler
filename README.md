aiovectortiler
==============

> This was an experimental Python tile-server which is no longer maintained.

Documentation: http://aiovectortiler.readthedocs.org/

aiovectortiler is a Python asynchronous micro vector tile application that serves data from PostGIS. 
It is based on the [Utilery](https://github.com/tilery/utilery) package created by Yohan Boniface.

aiovectortiler can serve vector tiles in json, [geojson](http://geojson.org) and [Mapbox Vector Tile](https://www.mapbox.com/vector-tiles/) formats. 
It is compatible with with MVT client-side vector tile libraries such as [Mapbox GL JS](https://www.mapbox.com/mapbox-gl-js/api/). 
MVT encoding is performed by Mapzen's [mapbox-vector-tile](https://github.com/tilezen/mapbox-vector-tile) module.

Layer configuration is by means of YAML recipe files. Here is an [example recipe](https://github.com/etalab/utilery-osm-recipe/blob/master/utilery.yml) for OpenStreetMap data.

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
Then run the docker image, binding the docker container port `80` to your preferred localhost port, 
and mapping the docker container's `/configs` volume to your aiovectortiler configs directory.
For example:
```
docker run -i -t -p 80:80 -v /path/to/local/configs:/configs shongololo/aiovectortiler
```
> If running the docker container from the command line, use an absolute path to your configs directory.

Your aiovectortiler server will now be running and available at `localhost:80`

For higher throughput, deploy a separate aiovectortiler instance for each available CPU core. 
See `configs/docker-compose.yaml`file and the accompanying `configs/nginx.conf` file for an example load-balancing reverse-proxy configuration with caching.
