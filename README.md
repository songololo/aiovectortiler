# aiovectortiler

Documentation: http://aiovectortiler.readthedocs.org/

aiovectortiler is an asynchronous micro vector tile application that serves data from PostGIS. 
It is based on the [Utilery](https://github.com/tilery/utilery) package created by Yohan Boniface.

aiovectortiler can serve vector tiles in json, [geojson](http://geojson.org) and [Mapbox Vector Tile](https://www.mapbox.com/vector-tiles/) formats. 
It is compatible with with MVT client-side vector tile libraries such as [Mapbox GL JS](https://www.mapbox.com/mapbox-gl-js/api/). 
MVT encoding is performed by Mapzen's [mapbox-vector-tile](https://github.com/tilezen/mapbox-vector-tile) module.

It is easy to configure by means of SQL requests provided in YAML recipe files. An example recipe for OpenStreetMap data:
[https://github.com/etalab/utilery-osm-recipe/blob/master/utilery.yml](https://github.com/etalab/utilery-osm-recipe/blob/master/utilery.yml)

Note that tests are pending reimplementation for compatibility with the aiohttp ecosystem.

[![Build Status](https://travis-ci.org/shongololo/aiovectortiler.svg)](https://travis-ci.org/shongololo/aiovectortiler)
[![Coverage Status](https://coveralls.io/repos/github/shongololo/aiovectortiler/badge.svg?branch=master)](https://coveralls.io/github/shongololo/aiovectortiler?branch=master)
