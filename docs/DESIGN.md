# Aries Akrida Design

- Use proven load scale platform ( Locust )
- Support scaling with the use of clustering ( Locust )
- Provide easy to use interface with metrics ( Locust )
- Ensure each user scales independently ( Independent Aries Framework Javascript Subprocesses )
- Simulate real world clients ( Aries Framework Javascript )

## Why Locust

While there are some over-arching goals when picking a load testing framework, such as

- Clustering / Scaling
- Simplicity
- Community
- Open Source License
- Extendable

We also want the framework to be easy to develop against, and something the community is familiar with. This means that the programming languages for the testing framework are going to be either Python or Javascript. 

After reviewing Locust, JMeter, Taurus, nGrinder, The Grinder, k6, Tsung, and Siege, we found that Locust had the simplest interface to bring up and manage, was very capable, and was easily extendable. This is not saying the other frameworks aren't capable frameworks, but we found that for us, Locust was the best choice.

## Subprocess Design

Each user in Locust is represented by a gevent greenlet. This greenlet runs all of the tasks for each user. After completing the tasks, the greenlet will repeat all the tasks after some type of wait interval.

As we can see below, each greenlet represents a different User.

![Greenlet](./images/greenlet.png)

Greenlets works well when an individual user doesn't use too much CPU. In our case, we are doing some high CPU tasks, such as encryption and decryption of messages.

In this case, we have each gevent greenlet create a subprocess to handle the CPU intensive tasks. Commands are sent over stdin, and responses are received over stdout.

![Greenlet](./images/subprocess.png)

The commands are sent as JSON, and responses are received as JSON.

Example of a successful start command being sent and response:

```
stdin -> {"cmd": "start","withMediation": true,"port":"5555"}
stdout <- {"error":0,"result":"Initialized agent..."}
```

Example of a unsuccessful start command being sent and response:

```
stdin -> {"cmd": "start","withMediation": true,"port":"5555"}
stdout <- {"error":1,"result":{}} 
```

The design of the agent.js is such that a single stdin request is made, and a single stdout response is received. This simple pattern is used for all of the commands issued to agent.js.

This allows for manual testing of the interactions between Locust and agent.js. This pattern would also allow a new agent using Python or Rust to be defined as long as it followed the same input / output pattern.

### commmand: start 

cmd: start

description: Runs the initialization of the Aries Framework Javascript agent, including any connections to mediators. The startup command must be run before any other commands.

parameters: withMediation, port

withMediation: withMediation accepts a boolean value. With mediation indicates that Aries Framework Javascript should use the mediator defined in the .env file.

port: if withMediation is false, a port must be defined for agent.js to use for incoming DIDComm messages. The port must be mapped in docker-compose and the firewall so external services can access the port. The .env file specifies a starting and ending port. If more processes are started than ports are mapped, it can cause the Locust process to hang. If a large number of ports are mapped, it can cause a significant delay in docker-compose starting up.

Examples: 

Successful command

```
stdin -> {"cmd": "start","withMediation": true,"port":"5555"}
stdout <- {"error":0,"result":"Initialized agent..."}
```

Unsuccessful command

```
stdin -> {"cmd": "start","withMediation": true,"port":"5555"}
stdout <- {"error":1,"result":{}} 
```

### command: shutdown 

cmd: shutdown

description: Cleanly shuts down the Aries Framework Javascript agent and terminates the agent.js process. If the shutdown command is unsuccessful within the defined timeout, Locust will kill the subprocess.

parameters: None

Examples: 

Successful command

```
stdin -> {"cmd": "start","withMediation": true,"port":"5555"}
stdout <- {"error":0,"result":"Initialized agent..."}
stdin -> {"cmd":"shutdown"}
stdout <- {"error":0,"result":"Shutting down agent"}
```

### command: ping_mediator 

cmd: ping_mediator

description: The Ping Mediator command sends a trust ping to the mediator agent with response_requested. The mediator agent will then respond with ping-response over the mediation connection. This is used to verify agents are connected to the mediator. This is useful to test that an agent is still connected to the mediator. This function is used when testing the number of agents that can be connected to the mediator at the same time. If the Ping Mediator command doesn't respond within the specified timeout in the .env, an error will be received.

parameters: None

Examples:

Successful command

```
stdin -> {"cmd": "start","withMediation": true,"port":"5555"}
stdout <- {"error":0,"result":"Initialized agent..."}
stdin -> {"cmd":"ping_mediator"}
stdout <- {"error":0,"result":"Ping Mediator"}
```

Unsuccessful command

```
stdin -> {"cmd": "start","withMediation": true,"port":"5555"}
stdout <- {"error":1,"result":{}} 
stdin -> {"cmd":"ping_mediator"}
stdout <- {"error":1,"result":"Mediator timeout!"}
```

### command: receiveInvitation

cmd: receiveInvitation

description: This command receives an invitation from an issuer, verifier, or other didcomm agent. The command will return when the connection is in active state, or return an error on failure.

parameters: invitationUrl

invitationUrl: this is the url for the DIDComm invitation

Examples:

Successful command

```
stdin -> {"cmd": "start","withMediation": true,"port":"5555"}
stdout <- {"error":0,"result":"Initialized agent..."}
stdin -> {"cmd":"receiveInvitation", "invitationUrl": "https://ys40cgl5r2.execute-api.us-east-1.amazonaws.com/Prod/message?c_i=eyJAdHlwZSI6ICJkaWQ6c292OkJ6Q2JzTlloTXJqSGlxWkRUVUFTSGc7c3BlYy9jb25uZWN0aW9ucy8xLjAvaW52aXRhdGlvbiIsICJAaWQiOiAiZGRkY2M4NTYtZTU5MS00NzM3LWIyN2ItYmFkNzliZGQxZjMyIiwgInJlY2lwaWVudEtleXMiOiBbIjZ2OW1LSExGSDdDbVI4am5wVXZGY05OcUxybnZiY0hQazZvNGtaTHFSdDNrIl0sICJzZXJ2aWNlRW5kcG9pbnQiOiAiaHR0cHM6Ly95czQwY2dsNXIyLmV4ZWN1dGUtYXBpLnVzLWVhc3QtMS5hbWF6b25hd3MuY29tL1Byb2QvbWVzc2FnZSIsICJsYWJlbCI6ICJCb2IiLCAicm91dGluZ0tleXMiOiBbIjJrQXh1SnhEaUxjOGRGa2tncVM2WXBjS291RlJIVFUzUldyWjd6ZHZNZkhXIiwgIkZWUFJhZXZvRkhXVXJDaFFoa2UzMngyR1g4RnJLd3lob0JYN2h5M05SaHJqIl19"}
stdout <- {"error":0,"result":"Receive Connection","connection":{"_tags":{"role":"receiver","state":"initial","invitationId":"9337c8c3-bf14-4073-9d55-4398ba8456cd","recipientKeyFingerprints":["z6Mktevz4sdGgHwTBGXQwmYSis9B4rNhP5Bcuqf1nuYLVthm"]},"metadata":{},"id":"9a678433-b844-4ef3-9992-710d32e4084c","createdAt":"2023-10-10T14:09:59.489Z","outOfBandInvitation":{"@type":"https://didcomm.org/out-of-band/1.1/invitation","@id":"9337c8c3-bf14-4073-9d55-4398ba8456cd","label":"Bob","accept":["didcomm/aip1","didcomm/aip2;env=rfc19"],"handshake_protocols":["https://didcomm.org/connections/1.0"],"services":[{"id":"#inline","serviceEndpoint":"https://ys40cgl5r2.execute-api.us-east-1.amazonaws.com/Prod/message","type":"did-communication","recipientKeys":["did:key:z6Mktevz4sdGgHwTBGXQwmYSis9B4rNhP5Bcuqf1nuYLVthm"],"routingKeys":["did:key:z6MkgCS1VZCf3t6bjkbTNQPwPvAKdUXGhLiQ7XmUxGbwGt4t","did:key:z6MktweUAuBEapzwxhY7PKbst3aGLhXhjqE4VCS3YF1PLve7"]}]},"role":"receiver","state":"prepare-response","autoAcceptConnection":true,"reusable":false}}
```

Unsuccessful command

```
stdin -> {"cmd": "start","withMediation": true,"port":"5555"}
stdout <- {"error":1,"result":{}} 
stdin -> {"cmd":"receiveInvitation", "invitationUrl": "https://ys40cgl5r2.execute-api.us-east-1.amazonaws.com/Prod/message?c_i=eyJAdHlwZSI6ICJkaWQ6c292OkJ6Q2JzTlloTXJqSGlxWkRUVUFTSGc7c3BlYy9jb25uZWN0aW9ucy8xLjAvaW52aXRhdGlvbiIsICJAaWQiOiAiODIzNzE2NWUtMDJkNi00ZWE1LTg2MGItOWRhNGJiYTcxYzdkIiwgInJlY2lwaWVudEtleXMiOiBbIjR2UDd0MWI0ZWhlTXJwVjJrVUdTQUNqM2plbmkyUDJ1M0xmSkpaa0RWc3lHIl0sICJzZXJ2aWNlRW5kcG9pbnQiOiAiaHR0cHM6Ly95czQwY2dsNXIyLmV4ZWN1dGUtYXBpLnVzLWVhc3QtMS5hbWF6b25hd3MuY29tL1Byb2QvbWVzc2FnZSIsICJsYWJlbCI6ICJCb2IiLCAicm91dGluZ0tleXMiOiBbIjJrQXh1SnhEaUxjOGRGa2tncVM2WXBjS291RlJIVFUzUldyWjd6ZHZNZkhXIiwgIkZWUFJhZXZvRkhXVXJDaFFoa2UzMngyR1g4RnJLd3lob0JYN2h5M05SaHJqIl19"}
stdout <- {"error":1,"result":{}}
```

### command: receiveCredential

cmd: receiveCredential

description: This command receives an credential from an issuer. The command will return when the credential has been received, or return an error on failure.

parameters:

invitationUrl: this is the url for the DIDComm invitation

Examples:

```
stdin -> {"cmd": "start","withMediation": true,"port":"5555"}
stdout <- {"error":0,"result":"Initialized agent..."}
stdin -> {"cmd":"receiveInvitation", "invitationUrl": "https://ys40cgl5r2.execute-api.us-east-1.amazonaws.com/Prod/message?c_i=eyJAdHlwZSI6ICJkaWQ6c292OkJ6Q2JzTlloTXJqSGlxWkRUVUFTSGc7c3BlYy9jb25uZWN0aW9ucy8xLjAvaW52aXRhdGlvbiIsICJAaWQiOiAiZGRkY2M4NTYtZTU5MS00NzM3LWIyN2ItYmFkNzliZGQxZjMyIiwgInJlY2lwaWVudEtleXMiOiBbIjZ2OW1LSExGSDdDbVI4am5wVXZGY05OcUxybnZiY0hQazZvNGtaTHFSdDNrIl0sICJzZXJ2aWNlRW5kcG9pbnQiOiAiaHR0cHM6Ly95czQwY2dsNXIyLmV4ZWN1dGUtYXBpLnVzLWVhc3QtMS5hbWF6b25hd3MuY29tL1Byb2QvbWVzc2FnZSIsICJsYWJlbCI6ICJCb2IiLCAicm91dGluZ0tleXMiOiBbIjJrQXh1SnhEaUxjOGRGa2tncVM2WXBjS291RlJIVFUzUldyWjd6ZHZNZkhXIiwgIkZWUFJhZXZvRkhXVXJDaFFoa2UzMngyR1g4RnJLd3lob0JYN2h5M05SaHJqIl19"}
stdout <- {"error":0,"result":"Receive Connection","connection":{"_tags":{"role":"receiver","state":"initial","invitationId":"9337c8c3-bf14-4073-9d55-4398ba8456cd","recipientKeyFingerprints":["z6Mktevz4sdGgHwTBGXQwmYSis9B4rNhP5Bcuqf1nuYLVthm"]},"metadata":{},"id":"9a678433-b844-4ef3-9992-710d32e4084c","createdAt":"2023-10-10T14:09:59.489Z","outOfBandInvitation":{"@type":"https://didcomm.org/out-of-band/1.1/invitation","@id":"9337c8c3-bf14-4073-9d55-4398ba8456cd","label":"Bob","accept":["didcomm/aip1","didcomm/aip2;env=rfc19"],"handshake_protocols":["https://didcomm.org/connections/1.0"],"services":[{"id":"#inline","serviceEndpoint":"https://ys40cgl5r2.execute-api.us-east-1.amazonaws.com/Prod/message","type":"did-communication","recipientKeys":["did:key:z6Mktevz4sdGgHwTBGXQwmYSis9B4rNhP5Bcuqf1nuYLVthm"],"routingKeys":["did:key:z6MkgCS1VZCf3t6bjkbTNQPwPvAKdUXGhLiQ7XmUxGbwGt4t","did:key:z6MktweUAuBEapzwxhY7PKbst3aGLhXhjqE4VCS3YF1PLve7"]}]},"role":"receiver","state":"prepare-response","autoAcceptConnection":true,"reusable":false}}
stdin -> {"cmd": "receiveCredential"}
stdout <- {"error":0,"result":"Receive Credential"}
```

## Configuration Design



## Why Aries Javascript Framework

## Why not use Clustered Aries Framework Javascript or Aca-Py Users ?

