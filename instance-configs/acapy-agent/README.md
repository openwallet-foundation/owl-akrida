# ACA-Py Agent

Within this folder, we have a `sample.env`, a `docker-compose.yml` file, a `configs` folder, and a `docker` folder. 

The `sample.env` is used, for reference, to be able to more easily copy the `.env` necessary for spinning up the ACA-Py agent. 

The `docker-compose.yml` file is used for the image for the ACA-Py issuer, where the image we are using is `acapy-cache-redis`, built from the `Dockerfile` within our `docker` folder here. This `Dockerfile` instructs how to build the image for the ACA-Py issuer, where we are using a redis cache for increased performance and, eventually, better scalability. 

Within this `docker-compose.yml` file, we set each of the issuers to point to the same database. Additionally, we also set the genesis URL and account information needed for the wallet. The issuer is spun up with configurations set by the `issuer.yml` file, within our `configs` folder. Here [within this configuration file] we specify the plugin for `acapy-cache-redis`, our inbound transport port, our ACA-Py admin port, and more. Within this configuration file, we also point the `redis_cache.connection` to point to the aforementioned database. The database is for persisting the ACA-Py agent DID, Schema, and Credential Definition, without needing to reanchor these for each agent we spin up and, thus, the cache is for easier retrieval. 

Additionally, still within our `docker-compose.yml` file, we export the ACA-Py admin endpoint `8150` and communicate to start ACA-Py with its transport port as `8151`. It is also during this time where we can optionally choose the log level (set to `debug` by default). 
