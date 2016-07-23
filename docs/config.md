# Configuration


## Examples 

Looking at examples is often the best way to learn, so here are some:

- [https://github.com/etalab/utilery-osm-recipe/blob/master/utilery.yml](https://github.com/etalab/utilery-osm-recipe/blob/master/utilery.yml)
- [https://github.com/etalab/utilery-recipe-jurpol/blob/master/jurpol.yml](https://github.com/etalab/utilery-recipe-jurpol/blob/master/jurpol.yml)
- [https://github.com/etalab/utilery-recipe-ban/blob/master/ban.yml](https://github.com/etalab/utilery-recipe-ban/blob/master/ban.yml)


## Overview

Application configuration is provided by means of a YAML [server configuration file](#server-configuration).

Layer recipe configuration is provided by YAML [recipe configuration files](#recipes).


## Server configuration

The server configuration file sets several important parameters for your app.

#### databases (list) - *required*

At least one database connection must be provided. Use the `default` key for your primary (or only) database.

    databases:
    - default: dsn_connection_string
    - another_db: another_dsn_connection_string

The DSN strings are per the [LibPQ connection string format](http://www.postgresql.org/docs/current/static/libpq-connect.html#LIBPQ-CONNSTRING)

#### default_recipe - *required*

The name for your primary (or only) recipe file, without the extension. This recipe file will be used when no recipe is defined in the endpoint request.

    default_recipe: my_default_recipe_name

#### log_level - *required*

The preferred log level based on standard python logging levels, e.g. debug, info, warning, error, critical.
 
    log_level: info

#### SRID - *required*

The SRID system for the tile system. This should ordinarily be 3857.
 
    SRID: 3857

#### CORS - *required*

Domains for permitted CORS requests. Set this to * to permit all cross origin requests. This is useful for development.
 
    CORS: '*'

#### builtin_plugins (list)

    builtin_plugins:
    - 'aiovectortiler.plugins.builtins.plugin_name'

A list of built-in [plugins](plugins.md) to activate.

#### lugins (list)

    plugins:
    - /path/to/plugin

A list of paths to optional [plugins](plugins.md).


#### tileJSON_spec (dict)

    tileJSON_spec: >
      {tilejson: '2.1.0',
      name: 'aiovectortiler',
      description: 'Asynchronous micro vector tile server for PostGIS.',
      scheme: 'xyz',
      format: 'pbf',
      tiles: [
        'http://vector.myserver.org/all/{z}/{x}/{y}.pbf'
      ]}

Default dict to use when serving the `/tilejson/` endpoint.


#### A note on global layer keys

The `scale`, `buffer`, `clip`, and `SRID` keys can be set in individual recipe, layer, or query levels. They can also be set at the server config file level as a global fallback default value for all recipes, layers.


## Recipes

Each recipe is a single YAML file.

### **Inheritable keys**

These keys can be set at the first level of the YAML file, at the layer level, or at the query level.
These keys can also be defined in the server configs file for global defaults across all recipes.

##### buffer (integer) — *optional* — default: 0
Optional buffer (in pixels) to use when querying data.

##### clip (boolean) — *optional* — default: false
Whether or not to clip the data to the tile bbox.

##### dbname (string) — *optional* — default: "default"
Name of the database to use. This name *must* be referenced in the `databases` key
of the python configuration.

##### SRID (integer) — *optional* — default: 3857
SRID to use.

### **First level keys**

##### layers (sequence) - *required*
A sequence of [layers](#layer-keys) mappings.

##### name (string) — *optional* — default: "default"
**Required** when you have more than one recipe.

### **Layer keys**
The keys to use in each layer entry.

##### name (string) — *required*
The name of the layer. This is the name to be used when requesting for only one layer
in the API endpoints.

##### queries (sequence) - *required*
A sequence of [query](#query-keys) mappings.

### **Query keys**

##### maxzoom (integer) — *optional* — default: 0
Maximum zoom this query should be run at.

##### minzoom (integer) — *optional* — default: 0
Minimum zoom this query should be run at.

##### sql (string) — *required*
The actual sql to be run for this query. Must expose the geometry column as `way`.
Available variables: `!bbox!`, `!zoom!`, `!pixel_width!`.
