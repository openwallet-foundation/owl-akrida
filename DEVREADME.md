# Framework Developers

This file is intended for developers working on the internals of the framework. If you're just looking how to get started with the framework, see the [docs](./docs)

## Making Changes

The general structure of the Aries Akrida project is broken into three parts. 

### AFJ Agent

The AFJ agent code lives in the agent.ts file. This file can be manually run using json strings to command the agent.

The basic design goal is to have a simplified interface, where one command results in one and only one response via stdout.

### Issuer and Verifier Modules

The issuer and verifier modules are designed to allow additional modules to be written to support different issuers and verifiers to test against. They have a basic interface to fulfill, and then a modification in locustClient.py to allow selecting the new module.

Currently there is one module written for Aca-py

```
        # Load modules here depending on config
        if ISSUER_TYPE == 'acapy':
            self.issuer = AcapyIssuer()
            
        if VERIFIER_TYPE == 'acapy':
            self.verifier = AcapyVerifier()
```

The basic interface allows for easy understanding of the requirements to fulfill to implement an issuer or verifier.

For example, in the base.py for the issuerAgent, we can see that get_invite takes no input parameters, and returns an invitation_url and connection_id. The connection_id is used for other commands, such as issuing a credential.

```
        def get_invite(self):
                # return  {'invitation_url': , 'connection_id': }
                raise NotImplementedError
```

### locustClient and tests

locustClient.py contains most of the logic for different interactions between the AFJ Agent and the Issuer and Verifier Agents.

The individual test specifications live in the other locust files. These files define the test workflow, and what core features will be used in the test.

## Debugging

TODO