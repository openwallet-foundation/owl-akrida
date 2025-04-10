# Load testing Indy VDR Proxy

This README is documentation for setting up and running Locust load tests of Indy VDR proxies based on this package [here](https://github.com/2060-io/credo-ts-indy-vdr-proxy/tree/main/packages/server) such as the following BC Gov implementation [here.](https://github.com/bcgov/indy-vdr-proxy-server)

## Running load tests locally

You will need to clone two repos, this one and your chosen proxy server. We will use the BC Gov repo mentioned above as an example.

Ensure you have Docker setup on your machine and enough space for some fairly hefty images. 

Copy `sample.vdr.env` to `.env` and replace with values that fit for your use case - especially confirm that the schemas, cred defs, revocation registry definitions, and dids you are providing exist on the ledgers your Indy VDR Proxy Server connects to.

From the Indy VDR Proxy Server repo, run the following two commands:

```sh
docker build --no-cache --tag 'proxy' .
```
```sh
docker run --name vdr-proxy -p 3000:3000 --network vdr-load-test 'proxy'
```
These flags are necessary to more easily target the local proxy externally.

Next, from the root of this repo, execute the following command:
```sh
docker compose -f docker-compose.vdr-local.yml up --build
```

The `--build` flag helps prevent caching issues if you are doing development.

Finally, navigate to `http://0.0.0.0:8089`. You should see  choose your desired settings (num of users, spawn rate, you can leave host blank), then click "Start swarming"

When you are satisfied with the results, stop the test and feel free to download your results. That being said, for more accurate tests, you should run against a deployed version of your proxy server with the same resource allocation as your intended prod deployment.

**NOTES:**
If your proxy server includes a rate limiter, you may need to disable or greatly alter it for tests with higher numbers of simulated users.

As a very rough benchmark, running the VDR load tests against the BC Gov repo in a single container on an Intel Mac, spawning 50 users per second until reaching 500 users achieved the following results:
| Test Script                        | Average Request Time (ms) | RPS  | Average Size (bytes) | Failures/s |
|------------------------------------|---------------------------|------|----------------------|------------|
| locustIndyVDRProxyCredDef.py       | 113                       | 90.1 | 12865                | 0.0        |
| locustIndyVDRProxyDID.py           | 21                        | 90.9 | 1374                 | 0.0        |
| locustIndyVDRProxyRevRegDef.py     | 19                        | 92.1 | 1540                 | 0.0        |
| locustIndyVDRProxyRevStatusList.py | 32                        | 88.4 | 5607                 | 48.3       |
| locustIndyVDRProxySchema.py        | 20                        | 88.6 | 375                  | 0.0        |

As you can see from these results, it isn't recommended to use the `locustIndyVDRRevStatusList` load test script as it depends on a timestamp and the results currently can't be cached. This results in many repeated lookups on the ledger which will eventually block the IP of your proxy for spamming.