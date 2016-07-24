# Configuration


## Overview

Application configuration is provided by means of a YAML [server configuration file](#server-configuration).

Layer recipe configuration is provided by means of a folder containing one or more YAML [recipe configuration files](#recipes).


## Server configuration

The server configuration file sets several important parameters for your app.

#### databases (list) - *required*

At least one database connection must be provided. Use the `default` key for your primary (or only) database.

    databases:
    - default: dsn_connection_string
    - another_db: another_dsn_connection_string

The DSN strings are per the [LibPQ connection string format](http://www.postgresql.org/docs/current/static/libpq-connect.html#LIBPQ-CONNSTRING)

#### default_recipe - *optional*

If a default recipe is not provided, then the app will select the first or only recipe file as the 'default'.
When a URL request is made without a request for a specific layer, then the default layer will be used. 
If you have more than one layer, then by setting this key you can determine which of the layers is the 'default' layer.

    default_recipe: my_default_recipe_name

#### log_level - *optional*

The preferred log level based on standard python logging levels, e.g. debug, info, warning, error, critical.
 
    log_level: info

#### SRID - *optional*

The global SRID system for the tile system. This should ordinarily be 3857.
 
    SRID: 3857

#### CORS - *optional*

Domains for permitted CORS requests. Set this to * to permit all cross origin requests. This is useful for development.
 
    CORS: '*'

#### builtin_plugins (list)

    builtin_plugins:
    - 'aiovectortiler.plugins.builtins.plugin_name'

A list of built-in [plugins](plugins.md) to optionally activate.

#### plugins (list)

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


## Recipes

Each recipe is a single YAML file.

### Recipe Examples 

Looking at examples is often the best way to learn:

- [https://github.com/etalab/utilery-osm-recipe/blob/master/utilery.yml](https://github.com/etalab/utilery-osm-recipe/blob/master/utilery.yml)
- [https://github.com/etalab/utilery-recipe-jurpol/blob/master/jurpol.yml](https://github.com/etalab/utilery-recipe-jurpol/blob/master/jurpol.yml)
- [https://github.com/etalab/utilery-recipe-ban/blob/master/ban.yml](https://github.com/etalab/utilery-recipe-ban/blob/master/ban.yml)

### **Inheritable keys**

The `scale`, `buffer`, `clip`, and `SRID` keys can be set in the [recipe configuration file's](#recipes) recipe, layer, or query levels. 
However, these can be omitted where preferred and a global default value can be provided in the server config file instead. 
This global value will only apply in cases where these keys have not been provided at the local recipe, layer, or query level.

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

