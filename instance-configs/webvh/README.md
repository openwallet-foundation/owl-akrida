# WebVH Akrida Configurations

## What's included?
For load testing WebVH features, there are 2 agents configurations available:
- An ACApy Multitenant agent, meant to act as a wallet provider.
- An ACApy Single tenant agent, meant to act as a Witness, Issuer & Verifier.
*Caddy configuration is recommended for DIDCommm communication ports.*

Additionally, the following is provided:
- An integration instance of a WebVH server: https://id.test-suite.app
- An integration instance of a tails server: https://tails.anoncreds.vc

## How to get started?

### Configuring the agents

To deploy the agents, you will need to provide a public endpoint for the admin api interface and the didcomm inbound communication ports.

Additionally, you need to provide a seed to the single tenant agent. The ed25519 keypair created by this seed will be used to witness webvh did logs.
* The seed value `00000000000000000000000000000000` can be used for the provided webvh instance. *

You can view the agent's OpenAPI web interface by visiting the following pages in your local browser:
http://api.issuer.docker.localhost
http://api.holder.docker.localhost


`TEST_WITNESS_SEED=00000000000000000000000000000000 docker compose up --build`

### Running a load test

TBD, we are currently updating the AIP to version 2 in order to support additional AnonCreds registries.