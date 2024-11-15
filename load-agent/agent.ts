import {
  AnonCredsCredentialFormatService,
  AnonCredsModule, 
  AnonCredsProofFormatService, 
  DataIntegrityCredentialFormatService, 
  LegacyIndyCredentialFormatService,
  LegacyIndyProofFormatService,
  V1CredentialProtocol, 
  V1ProofProtocol
} from '@credo-ts/anoncreds';
import {ariesAskar} from '@hyperledger/aries-askar-nodejs'
import { IndyVdrAnonCredsRegistry, IndyVdrIndyDidResolver, IndyVdrModule, IndyVdrSovDidResolver } from '@credo-ts/indy-vdr'

import { AskarModule } from '@credo-ts/askar'

import {
  Agent, 
  AutoAcceptCredential, 
  BasicMessageEventTypes,
  ConnectionEventTypes,
  ConnectionsModule,
  ConsoleLogger, 
  CredentialEventTypes,
  CredentialsModule, 
  CredentialState,
  DidCommMimeType, 
  DidExchangeState,
  DidRecord,
  DidRepository,
  DidsModule, 
  DifPresentationExchangeProofFormatService, 
  HttpOutboundTransport,
  JsonLdCredentialFormatService,
  KeyDidRegistrar,
  KeyDidResolver,
  KeyType,
  LogLevel, 
  MediationRecipientModule, 
  MediatorPickupStrategy, 
  ProofEventTypes,
  ProofsModule, 
  ProofState,
  TransportEventTypes,
  TrustPingEventTypes,
  V2CredentialProtocol, 
  V2ProofProtocol, 
  WebDidResolver, 
  WsOutboundTransport
} from '@credo-ts/core';
import { PushNotificationsFcmModule } from '@credo-ts/push-notifications';
import { QuestionAnswerModule } from '@credo-ts/question-answer';

import { 
  agentDependencies, 
  HttpInboundTransport 
} from '@credo-ts/node';
import { anoncreds } from '@hyperledger/anoncreds-nodejs';
import { indyVdr } from '@hyperledger/indy-vdr-nodejs';

var config = require('./config.js')

var deferred = require('deferred')
var process = require('process')

const characters =
  'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
const legacyIndyCredentialFormat = new LegacyIndyCredentialFormatService()
const legacyIndyProofFormat = new LegacyIndyProofFormatService()

function generateString(length) {
  let result = ''
  const charactersLength = characters.length
  for (let i = 0; i < length; i++) {
    result += characters.charAt(Math.floor(Math.random() * charactersLength))
  }

  return result
}

const initializeAgent = async (withMediation, port, agentConfig = null) => {
  // Simple agent configuration. This sets some basic fields like the wallet
  // configuration and the label. It also sets the mediator invitation url,
  // because this is most likely required in a mobile environment.

  let mediation_url = config.mediation_url
  let endpoints = ['http://' + config.agent_ip + ':' + port]

  if (!agentConfig || agentConfig === null || agentConfig.length === 0) {
    agentConfig = {
      label: generateString(14),
      walletConfig: {
        id: generateString(32),
        key: generateString(32),
      },
      autoAcceptConnections: true,
      endpoints: endpoints,

      autoAcceptInvitation: true,
      // logger: new ConsoleLogger(LogLevel.trace),
      didCommMimeType: DidCommMimeType.V0,
    }
  }

  let modules = {
    // indySdk: new IndySdkModule({
    //   indySdk,
    //   networks: [config.ledger]
    // }),
    indyVdr: new IndyVdrModule({
      indyVdr,
      networks: [
        {
          isProduction: false,
          indyNamespace: 'bcovrin:test',
          genesisTransactions: `{"reqSignature":{},"txn":{"data":{"data":{"alias":"Node1","blskey":"4N8aUNHSgjQVgkpm8nhNEfDf6txHznoYREg9kirmJrkivgL4oSEimFF6nsQ6M41QvhM2Z33nves5vfSn9n1UwNFJBYtWVnHYMATn76vLuL3zU88KyeAYcHfsih3He6UHcXDxcaecHVz6jhCYz1P2UZn2bDVruL5wXpehgBfBaLKm3Ba","blskey_pop":"RahHYiCvoNCtPTrVtP7nMC5eTYrsUA8WjXbdhNc8debh1agE9bGiJxWBXYNFbnJXoXhWFMvyqhqhRoq737YQemH5ik9oL7R4NTTCz2LEZhkgLJzB3QRQqJyBNyv7acbdHrAT8nQ9UkLbaVL9NBpnWXBTw4LEMePaSHEw66RzPNdAX1","client_ip":"138.197.138.255","client_port":9702,"node_ip":"138.197.138.255","node_port":9701,"services":["VALIDATOR"]},"dest":"Gw6pDLhcBcoQesN72qfotTgFa7cbuqZpkX3Xo6pLhPhv"},"metadata":{"from":"Th7MpTaRZVRYnPiabds81Y"},"type":"0"},"txnMetadata":{"seqNo":1,"txnId":"fea82e10e894419fe2bea7d96296a6d46f50f93f9eeda954ec461b2ed2950b62"},"ver":"1"}
{"reqSignature":{},"txn":{"data":{"data":{"alias":"Node2","blskey":"37rAPpXVoxzKhz7d9gkUe52XuXryuLXoM6P6LbWDB7LSbG62Lsb33sfG7zqS8TK1MXwuCHj1FKNzVpsnafmqLG1vXN88rt38mNFs9TENzm4QHdBzsvCuoBnPH7rpYYDo9DZNJePaDvRvqJKByCabubJz3XXKbEeshzpz4Ma5QYpJqjk","blskey_pop":"Qr658mWZ2YC8JXGXwMDQTzuZCWF7NK9EwxphGmcBvCh6ybUuLxbG65nsX4JvD4SPNtkJ2w9ug1yLTj6fgmuDg41TgECXjLCij3RMsV8CwewBVgVN67wsA45DFWvqvLtu4rjNnE9JbdFTc1Z4WCPA3Xan44K1HoHAq9EVeaRYs8zoF5","client_ip":"138.197.138.255","client_port":9704,"node_ip":"138.197.138.255","node_port":9703,"services":["VALIDATOR"]},"dest":"8ECVSk179mjsjKRLWiQtssMLgp6EPhWXtaYyStWPSGAb"},"metadata":{"from":"EbP4aYNeTHL6q385GuVpRV"},"type":"0"},"txnMetadata":{"seqNo":2,"txnId":"1ac8aece2a18ced660fef8694b61aac3af08ba875ce3026a160acbc3a3af35fc"},"ver":"1"}
{"reqSignature":{},"txn":{"data":{"data":{"alias":"Node3","blskey":"3WFpdbg7C5cnLYZwFZevJqhubkFALBfCBBok15GdrKMUhUjGsk3jV6QKj6MZgEubF7oqCafxNdkm7eswgA4sdKTRc82tLGzZBd6vNqU8dupzup6uYUf32KTHTPQbuUM8Yk4QFXjEf2Usu2TJcNkdgpyeUSX42u5LqdDDpNSWUK5deC5","blskey_pop":"QwDeb2CkNSx6r8QC8vGQK3GRv7Yndn84TGNijX8YXHPiagXajyfTjoR87rXUu4G4QLk2cF8NNyqWiYMus1623dELWwx57rLCFqGh7N4ZRbGDRP4fnVcaKg1BcUxQ866Ven4gw8y4N56S5HzxXNBZtLYmhGHvDtk6PFkFwCvxYrNYjh","client_ip":"138.197.138.255","client_port":9706,"node_ip":"138.197.138.255","node_port":9705,"services":["VALIDATOR"]},"dest":"DKVxG2fXXTU8yT5N7hGEbXB3dfdAnYv1JczDUHpmDxya"},"metadata":{"from":"4cU41vWW82ArfxJxHkzXPG"},"type":"0"},"txnMetadata":{"seqNo":3,"txnId":"7e9f355dffa78ed24668f0e0e369fd8c224076571c51e2ea8be5f26479edebe4"},"ver":"1"}
{"reqSignature":{},"txn":{"data":{"data":{"alias":"Node4","blskey":"2zN3bHM1m4rLz54MJHYSwvqzPchYp8jkHswveCLAEJVcX6Mm1wHQD1SkPYMzUDTZvWvhuE6VNAkK3KxVeEmsanSmvjVkReDeBEMxeDaayjcZjFGPydyey1qxBHmTvAnBKoPydvuTAqx5f7YNNRAdeLmUi99gERUU7TD8KfAa6MpQ9bw","blskey_pop":"RPLagxaR5xdimFzwmzYnz4ZhWtYQEj8iR5ZU53T2gitPCyCHQneUn2Huc4oeLd2B2HzkGnjAff4hWTJT6C7qHYB1Mv2wU5iHHGFWkhnTX9WsEAbunJCV2qcaXScKj4tTfvdDKfLiVuU2av6hbsMztirRze7LvYBkRHV3tGwyCptsrP","client_ip":"138.197.138.255","client_port":9708,"node_ip":"138.197.138.255","node_port":9707,"services":["VALIDATOR"]},"dest":"4PS3EDQ3dW1tci1Bp6543CfuuebjFrg36kLAUcskGfaA"},"metadata":{"from":"TWwCRQRZ2ZHMJFn9TzLp7W"},"type":"0"},"txnMetadata":{"seqNo":4,"txnId":"aa5e817d7cc626170eca175822029339a444eb0ee8f0bd20d3b0b76e566fb008"},"ver":"1"}`,
          connectOnStartup: true,
        },
        {
          isProduction: false,
          indyNamespace: 'indicio:testnet',
          genesisTransactions: `{"reqSignature":{},"txn":{"data":{"data":{"alias":"OpsNode","blskey":"4i39oJqm7fVX33gnYEbFdGurMtwYQJgDEYfXdYykpbJMWogByocaXxKbuXdrg3k9LP33Tamq64gUwnm4oA7FkxqJ5h4WfKH6qyVLvmBu5HgeV8Rm1GJ33mKX6LWPbm1XE9TfzpQXJegKyxHQN9ABquyBVAsfC6NSM4J5t1QGraJBfZi","blskey_pop":"Qq3CzhSfugsCJotxSCRAnPjmNDJidDz7Ra8e4xvLTEzQ5w3ppGray9KynbGPH8T7XnUTU1ioZadTbjXaRY26xd4hQ3DxAyR4GqBymBn3UBomLRJHmj7ukcdJf9WE6tu1Fp1EhxmyaMqHv13KkDrDfCthgd2JjAWvSgMGWwAAzXEow5","client_ip":"13.58.197.208","client_port":"9702","node_ip":"3.135.134.42","node_port":"9701","services":["VALIDATOR"]},"dest":"EVwxHoKXUy2rnRzVdVKnJGWFviamxMwLvUso7KMjjQNH"},"metadata":{"from":"Pms5AZzgPWHSj6nNmJDfmo"},"type":"0"},"txnMetadata":{"seqNo":1,"txnId":"77ad6682f320be9969f70a37d712344afed8e3fba8d43fa5602c81b578d26088"},"ver":"1"}
{"reqSignature":{},"txn":{"data":{"data":{"alias":"cynjanode","blskey":"3xT22bdYb4dFWVamrRTUPvhXDnJ5piSoromxaqs2fLMbFvVv2dbQEtg4nw87oGiC9JQBo1S8DQo9HauGDKpj4NK574CaUyAU8E1vJy7XbXkMTBGMDoF5H5u4MdXZ3UBdu3SoAtR3ftKMFdbrgVUG59tTkYecJopx6of97HYH54bHNZW","blskey_pop":"QsWc3FDjqqFXqwJXdXRKgc11Zp2uDDVJTkFSJbqFbW3MmrWXZUjhnZFNe1Pd22KrxhxNvU3BQCniHtfiVpYEBeiCELdoyqaje3pouvMnj7ocMgVykKjhhw1UTvVmMdyw3XKkDGt8rKS1gjdduHufA7E3cdvj81ykyXo1R1wtm6WQxw","client_ip":"18.220.204.221","client_port":"9702","node_ip":"3.143.166.153","node_port":"9701","services":["VALIDATOR"]},"dest":"7R4qPxP9cyWK6LaZo9cZBjjxhWZfBVGAJR3NzdVBqUFK"},"metadata":{"from":"UedUo699qAv39zmGFmp8gE"},"type":"0"},"txnMetadata":{"seqNo":2,"txnId":"ce7361e44ec10a275899ece1574f6e38f2f3c7530c179fa07a2924e55775759b"},"ver":"1"}
{"reqSignature":{},"txn":{"data":{"data":{"alias":"GlobaliD","blskey":"4Behdr1KJfLTAPNospghtL7iWdCHca6MZDxAtzYNXq35QCUr4aqpLu6p4Sgu9wNbTACB3DbwmVgE2L7hX6UsasuvZautqUpf4nC5viFpH7X6mHyqLreBJTBH52tSwifQhRjuFAySbbfyRK3wb6R2Emxun9GY7MFNuy792LXYg4C6sRJ","blskey_pop":"RKYDRy8oTxKnyAV3HocapavH2jkw3PVe54JcEekxXz813DFbEy87N3i3BNqwHB7MH93qhtTRb7EZMaEiYhm92uaLKyubUMo5Rqjve2jbEdYEYVRmgNJWpxFKCmUBa5JwBWYuGunLMZZUTU3qjbdDXkJ9UNMQxDULCPU5gzLTy1B5kb","client_ip":"13.56.175.126","client_port":"9702","node_ip":"50.18.84.131","node_port":"9701","services":["VALIDATOR"]},"dest":"2ErWxamsNGBfhkFnwYgs4UW4aApct1kHUvu7jbkA1xX4"},"metadata":{"from":"4H8us7B1paLW9teANv8nam"},"type":"0"},"txnMetadata":{"seqNo":3,"txnId":"0c3b33b77e0419d6883be35d14b389c3936712c38a469ac5320a3cae68be1293"},"ver":"1"}
{"reqSignature":{},"txn":{"data":{"data":{"alias":"IdRamp","blskey":"LoYzqUMPDZEfRshwGSzkgATxcM5FAS1LYx896zHnMfXP7duDsCQ6CBG2akBkZzgH3tBMvnjhs2z7PFc2gFeaKUF9fKDHhtbVqPofxH3ebcRfA959qU9mgvmkUwMUgwd21puRU6BebUwBiYxMxcE5ChReBnAkdAv19gVorm3prBMk94","blskey_pop":"R1DjpsG7UxgwstuF7WDUL17a9Qq64vCozwJZ88bTrSDPwC1cdRn3WmhqJw5LpEhFQJosDSVVT6tS8dAZrrssRv2YsELbfGEJ7ZGjhNjZHwhqg4qeustZ7PZZE3Vr1ALSHY4Aa6KpNzGodxu1XymYZWXAFokPAs3Kho8mKcJwLCHn3h","client_ip":"207.126.128.12","client_port":"9702","node_ip":"207.126.129.12","node_port":"9701","services":["VALIDATOR"]},"dest":"5Zj5Aec6Kt9ki1runrXu87wZ522mnm3zwmaoHLUcHLx9"},"metadata":{"from":"AFLDFPoJuDQUHqnfmg8U7i"},"type":"0"},"txnMetadata":{"seqNo":4,"txnId":"c9df105558333ac8016610d9da5aad1e9a5dd50b9d9cc5684e94f439fa10f836"},"ver":"1"}
{"reqSignature":{},"txn":{"data":{"data":{"alias":"lorica-identity-node1","blskey":"wUh24sVCQ8PHDgSb343g2eLxjD5vwxsrETfuV2sbwMNnYon9nhbaK5jcWTekvXtyiwxHxuiCCoZwKS97MQEAeC2oLbbMeKjYm212QwSnm7aKLEqTStXht35VqZvZLT7Q3mPQRYLjMGixdn4ocNHrBTMwPUQYycEqwaHWgE1ncDueXY","blskey_pop":"R2sMwF7UW6AaD4ALa1uB1YVPuP6JsdJ7LsUoViM9oySFqFt34C1x1tdHDysS9wwruzaaEFui6xNPqJ8eu3UBqcFKkoWhdsMqCALwe63ytxPwvtLtCffJLhHAcgrPC7DorXYdqhdG2cevdqc5oqFEAaKoFDBf12p5SsbbM4PYWCmVCb","client_ip":"35.225.220.151","client_port":"9702","node_ip":"35.224.26.110","node_port":"9701","services":["VALIDATOR"]},"dest":"k74ZsZuUaJEcB8RRxMwkCwdE5g1r9yzA3nx41qvYqYf"},"metadata":{"from":"Ex6hzsJFYzNJ7kzbfncNeU"},"type":"0"},"txnMetadata":{"seqNo":5,"txnId":"6880673ce4ae4a2352f103d2a6ae20469dd070f2027283a1da5e62a64a59d688"},"ver":"1"}
{"reqSignature":{},"txn":{"data":{"data":{"alias":"lownode","blskey":"TrJT1dHqGSxGxq4idJ1fV6e2rkfQdtVDNVQppnNodrdts1fuPeT121KdRgbwmX3QcVSUQuNBFqEMWGW9o8YMLUDkF3PK1ScJKVwKRSphHJwh5qKpY3aND4Kex62hNUGi1HQZ48BVdNTG8qn5pjvqzFnxkcH2rsEB8DXeAX1FvK2T8A","blskey_pop":"RNZLCPb4UsRmeUeJgFF9hHtxTLwbxgMVuWDcXDQNwUr1TEKhwanmSP2pmXptMrevqw5pnhQUaJkXj6MpwbpLTg53msiaP5PNiPV9HAqn5M3o9q4ZArRU4gqVQmbFdLn4sG2Fi58MzfFeNc5CPXGCd9wJxzwDww2Uso2XbZF5hd89ef","client_ip":"52.42.153.16","client_port":"9702","node_ip":"44.240.137.192","node_port":"9701","services":["VALIDATOR"]},"dest":"fX62N1gkzXAJ3qLB98Jj1aReCzcnt2kfmeUXE2ZYN1N"},"metadata":{"from":"DqeYipfvXEmeByhnENRb6p"},"type":"0"},"txnMetadata":{"seqNo":6,"txnId":"bd18819c6978b77751e0a4732f5773b98fb3965df365a85eb3aceefb51822f19"},"ver":"1"}
{"reqSignature":{},"txn":{"data":{"data":{"alias":"lownode2","blskey":"3ozcCZ6iJj2KhKeqsEpZsHYJQ1YK5XWETupNUJq62WvHg6UVuBGrfDc1Gbadr7i25WzYgWtb9qS3Cufo5hfXpvRoZnyJJyod4ZCpaWcdsvfkTxsKQmyL2NbwGfVhgAp45aCPGKNqugQwwwCL5qkfTtQLorRLCK7o5jJCceX1f7RgnJ3","blskey_pop":"Qv26m5RPWCvKxPwHQJPJvspNobVBBNetGnpXuYvxbYuKfYb4L5v6NoskXsor2sfiaeYNZJQaGJk5rLZpbZMdLxxongkKoK5anb1cS5xrYTgbiQKjYBgCCnJtF7HJmqR9RcHM7anSd8GMLgr3myb8DUDYj7UtWnhvxrTEHMfhiJbNzb","client_ip":"34.116.101.212","client_port":"9702","node_ip":"34.87.221.59","node_port":"9701","services":["VALIDATOR"]},"dest":"2ZLwqHoDrGLoANd5HRHHpAosQwgRvVCgoXD1pqpzcmoh"},"metadata":{"from":"EnooFNvPJYXKx4fdpxgggj"},"type":"0"},"txnMetadata":{"seqNo":7,"txnId":"60ff83036b2e770947e308f3b9a50c1168f5dd6d0bb8bc73a1d274d50d2953f2"},"ver":"1"}`,
          connectOnStartup: true,
        },
      ],
    }),
    askar: new AskarModule({
      ariesAskar,
    }),
    mediationRecipient: new MediationRecipientModule({
      mediatorInvitationUrl: mediation_url,
      mediatorPickupStrategy: MediatorPickupStrategy.PickUpV2LiveMode,
      // mediatorPickupStrategy: MediatorPickupStrategy.Implicit,
    }),
    anoncreds: new AnonCredsModule({
      registries: [new IndyVdrAnonCredsRegistry()],
      anoncreds,
    }),
    proofs: new ProofsModule({
      proofProtocols: [
        new V1ProofProtocol({
          indyProofFormat: new LegacyIndyProofFormatService(),
        }),
        new V2ProofProtocol({
          proofFormats: [
            new LegacyIndyProofFormatService(),
            new AnonCredsProofFormatService(),
            new DifPresentationExchangeProofFormatService(),
          ],
        }),
      ],
    }),
    credentials: new CredentialsModule({
      autoAcceptCredentials: AutoAcceptCredential.ContentApproved,
      credentialProtocols: [
        new V1CredentialProtocol({
          indyCredentialFormat: legacyIndyCredentialFormat,
        }),
        new V2CredentialProtocol({
          credentialFormats: [
            new LegacyIndyCredentialFormatService(),
            new JsonLdCredentialFormatService(),
            new DataIntegrityCredentialFormatService(),
            new AnonCredsCredentialFormatService(),
          ],
        }),
      ],
    }),
    dids: new DidsModule({
      registrars: [new KeyDidRegistrar()],
      resolvers: [new KeyDidResolver(), new WebDidResolver(), new IndyVdrSovDidResolver(), new IndyVdrIndyDidResolver()],
    }),
    connections: new ConnectionsModule({
      autoAcceptConnections: true
    }),
    pushNotificationsFcm: new PushNotificationsFcmModule(),
    questionAnswer: new QuestionAnswerModule()

  }

  // configure mediator or endpoints
  if (withMediation) {
    delete agentConfig['endpoints']
  } else {
    delete modules['mediationRecipient']
  }

  // A new instance of an agent is created here
  const agent = new Agent({
    config: agentConfig,
    dependencies: agentDependencies,
    modules: modules
  })

  // Register a simple `WebSocket` outbound transport
  agent.registerOutboundTransport(new WsOutboundTransport())

  // Register a simple `Http` outbound transport
  agent.registerOutboundTransport(new HttpOutboundTransport())

  if (withMediation) {
    // wait for medation to be configured
    let timeout = config.verified_timeout_seconds * 1000

    const TimeDelay = new Promise((resolve, reject) => {
      setTimeout(resolve, timeout, false)
    })

    var def = deferred()

    var onConnectedMediation = async (event) => {
      let mediatorConnection = null
      let interval = 100; 
      for (let i = 0; i < (timeout - interval); i++)
      {
        // OutboundWebSocketOpenedEvent occurs before mediation is finalized, so we want to check
        // for the default mediation connection until it is not null or we hit a timeout
        // we sleep a small amount between requests just to be kind to our CPU. 
        await new Promise(r => setTimeout(r, interval))
        mediatorConnection = await agent.mediationRecipient.findDefaultMediatorConnection()
        if (mediatorConnection != null) {
          break;
        }
      }
      if (event.payload.connectionId === mediatorConnection?.id) {
        def.resolve(true)
        // we no longer need to listen to the event
        agent.events.off(
          TransportEventTypes.OutboundWebSocketOpenedEvent,
          onConnectedMediation
        )
      }
    }

    agent.events.on(
      TransportEventTypes.OutboundWebSocketOpenedEvent,
      onConnectedMediation
    )

    // Initialize the agent
    await agent.initialize()

    // wait for ws to be configured
    let value = await Promise.race([TimeDelay, def.promise])

    if (!value) {
      // we no longer need to listen to the event in case of failure
      agent.events.off(
        TransportEventTypes.OutboundWebSocketOpenedEvent,
        onConnectedMediation
      )
      throw 'Mediator timeout!'
    }
  } else {
    agent.registerInboundTransport(
      new HttpInboundTransport({ port: port })
    )
    await agent.initialize()
  }

  return [agent, agentConfig]
}

const pingMediator = async (agent) => {
  // Find mediator

  // wait for the ping
  let timeout = config.verified_timeout_seconds * 1000

  const TimeDelay = new Promise((resolve, reject) => {
    setTimeout(resolve, timeout, false)
  })

  var def = deferred()

  var onPingResponse = async (event) => {
    const mediatorConnection =
      await agent.mediationRecipient.findDefaultMediatorConnection()
    if (event.payload.connectionRecord.id === mediatorConnection?.id) {
      // we no longer need to listen to the event
      agent.events.off(
        TrustPingEventTypes.TrustPingResponseReceivedEvent,
        onPingResponse
      )

      def.resolve(true)
    }
  }

  agent.events.on(
    TrustPingEventTypes.TrustPingResponseReceivedEvent,
    onPingResponse
  )

  let mediatorConnection =
    await agent.mediationRecipient.findDefaultMediatorConnection()

  if (mediatorConnection) {
    //await agent.connections.acceptResponse(mediatorConnection.id)
    await agent.connections.sendPing(mediatorConnection.id, {})
  }

  // wait for ping repsonse
  let value = await Promise.race([TimeDelay, def.promise])

  if (!value) {
    // we no longer need to listen to the event in case of failure
    agent.events.off(
      TrustPingEventTypes.TrustPingResponseReceivedEvent,
      onPingResponse
    )
    throw 'Mediator timeout!'
  }
}

let deleteOobRecordById = async (agent, id) => {
  await agent.oob.deleteById(id);
};

let receiveInvitation = async (agent, invitationUrl) => {
  // wait for the connection
  let timeout = config.verified_timeout_seconds * 1000
  const TimeDelay = new Promise((resolve, reject) => {
    setTimeout(resolve, timeout, false)
  })

  var def = deferred()

  var onConnection = async (event) => {
    {
      let payload = event.payload
      if (
        payload.connectionRecord.state === DidExchangeState.Completed
      ) {
        // the connection is now ready for usage in other protocols!
        // console.log(`Connection for out-of-band id ${payload.connectionRecord.outOfBandId} completed`)
        // Custom business logic can be included here
        // In this example we can send a basic message to the connection, but
        // anything is possible

        agent.events.off(
          ConnectionEventTypes.ConnectionStateChanged,
          onConnection
        )

        def.resolve(true)
      }
    }
  }

  agent.events.on(
    ConnectionEventTypes.ConnectionStateChanged,
    onConnection
  )

  const { outOfBandRecord } = await agent.oob.receiveInvitationFromUrl(
    invitationUrl
  )

  // wait for connection
  let value = await Promise.race([TimeDelay, def.promise])

  if (!value) {
    // we no longer need to listen to the event in case of failure
    agent.events.off(
      ConnectionEventTypes.ConnectionStateChanged,
      onConnection
    )
    throw 'Connection timeout!'
  }

  return outOfBandRecord
}

let receiveInvitationConnectionDid = async (agent, invitationUrl) => {
  let timeout = config.verified_timeout_seconds * 1000
  const TimeDelay = new Promise((resolve, reject) => {
    setTimeout(resolve, timeout, false)
  })

  var def = deferred()

  var onConnection = async (event) => {
    {
      let payload = event.payload
      if (
        payload.connectionRecord.state === DidExchangeState.Completed
      ) {
        agent.events.off(
          ConnectionEventTypes.ConnectionStateChanged,
          onConnection
        )

        def.resolve(true)
      }
    }
  }

  agent.events.on(
    ConnectionEventTypes.ConnectionStateChanged,
    onConnection
  )

  let legacyConnectionDid = undefined;
  let connectionId = undefined;
  let oobRecordId = undefined;
  try {
    // LO: need connection record, not OOB record since we need the connection DID
    const { outOfBandRecord, connectionRecord } = await agent.oob.receiveInvitationFromUrl(
      invitationUrl
    )
    const strRes = JSON.stringify(connectionRecord)
    connectionId = connectionRecord.id;
    oobRecordId = outOfBandRecord.id;

    // LO: retrieve the legacy DID. IAS controller needs that to issue against
    // This code adapted from https://github.com/bcgov/bc-wallet-mobile/blob/main/app/src/helpers/BCIDHelper.ts
    const legacyDidKey = '_internal/legacyDid' // TODO:(from BC Wallet code) Waiting for AFJ export of this.
    const didRepository = agent.dependencyManager.resolve(DidRepository)  
    const dids = await didRepository.getAll(agent.context)
    const didRecord = dids.filter((d) => d.did === connectionRecord?.did).pop()
    legacyConnectionDid = didRecord.metadata.get(legacyDidKey)!.unqualifiedDid
  } catch (error) {
    process.stderr.write('******** ERROR'+ '\n' + error + '\n')
  }

  // wait for connection
  let value = await Promise.race([TimeDelay, def.promise])

  if (!value) {
    // we no longer need to listen to the event in case of failure
    agent.events.off(
      ConnectionEventTypes.ConnectionStateChanged,
      onConnection
    )
    throw 'Connection timeout!'
  }

  return { did: legacyConnectionDid, connectionId: connectionId, oobRecordId: oobRecordId}
}

let receiveCredential = async (agent) => {
  // wait for the ping
  let timeout = config.verified_timeout_seconds * 1000

  const TimeDelay = new Promise((resolve, reject) => {
    setTimeout(resolve, timeout, false)
  })

  var def = deferred()

  let onCredential = async (event) => {
    let payload = event.payload

    switch (payload.credentialRecord.state) {
      case CredentialState.OfferReceived:
        //console.log('received a credential')
        // custom logic here
        await agent.credentials.acceptOffer({
          credentialRecordId: payload.credentialRecord.id,
        })
        break
      case CredentialState.CredentialReceived:
        //console.log(`Credential for credential id ${payload.credentialRecord.id} is accepted`)
        // For demo purposes we exit the program here.

        agent.events.off(
          CredentialEventTypes.CredentialStateChanged,
          onCredential
        )

        def.resolve(true)
        break
    }
  }

  agent.events.on(
    CredentialEventTypes.CredentialStateChanged,
    onCredential
  )

  // Nothing for us to do

  // wait for credential
  let value = await Promise.race([TimeDelay, def.promise])

  if (!value) {
    // we no longer need to listen to the event in case of failure
    agent.events.off(
      CredentialEventTypes.CredentialStateChanged,
      onCredential
    )
    throw 'Credential timeout!'
  }
}

let presentationExchange = async (agent) => {
  // wait for the ping
  let timeout = config.verified_timeout_seconds * 1000

  const TimeDelay = new Promise((resolve, reject) => {
    setTimeout(resolve, timeout, false)
  })

  var def = deferred()

  let onRequest = async (event) => {
    let payload = event.payload

    switch (payload.proofRecord.state) {
      case ProofState.RequestReceived:
        const requestedCredentials =
          await agent.proofs.selectCredentialsForRequest({
            proofRecordId: payload.proofRecord.id,
            // config: {
            //   filterByPresentationPreview: true,
            // },
          })
        await agent.proofs.acceptRequest({
          proofRecordId: payload.proofRecord.id,
          proofFormats: requestedCredentials.proofFormats,
        })
        agent.events.off(ProofEventTypes.ProofStateChanged, onRequest)
        def.resolve(true)
        break
    }
  }

  agent.events.on(ProofEventTypes.ProofStateChanged, onRequest)

  // Wait for presentation
  let value = await Promise.race([TimeDelay, def.promise])

  if (!value) {
    // No longer need to listen to the event in case of failure
    agent.events.off(ProofEventTypes.ProofStateChanged, onRequest)
    throw 'Presentation timeout!'
  }
}

let receiveMessage = async (agent) => {
  // wait for the ping
  let timeout = config.verified_timeout_seconds * 1000

  const TimeDelay = new Promise((resolve, reject) => {
    setTimeout(resolve, timeout, false)
  })

  var def = deferred()

  let onMessage = async (event) => {
    let payload = event.payload

    //        console.error(payload)

    agent.events.off(
      BasicMessageEventTypes.BasicMessageStateChanged,
      onMessage
    )

    def.resolve(true)
  }

  agent.events.on(
    BasicMessageEventTypes.BasicMessageStateChanged,
    onMessage
  )

  // Nothing for us to do

  // wait for credential
  let value = await Promise.race([TimeDelay, def.promise])

  if (!value) {
    // we no longer need to listen to the event in case of failure
    agent.events.off(
      BasicMessageEventTypes.BasicMessageStateChanged,
      onMessage
    )
    throw 'Message timeout!'
  }
}

let getDefaultHolderDidKeyDocument = async (agent) => {
  try {
    let defaultDidRecord: DidRecord | null
    const didRepository = await agent.dependencyManager.resolve(DidRepository)

    defaultDidRecord = await didRepository.findSingleByQuery(agent.context, {
      isDefault: true,
    })

    if (!defaultDidRecord) {
      const did = await agent.dids.create({
        method: 'key',
        options: {
          keyType: KeyType.Ed25519,
        },
      })

      const [didRecord] = await agent.dids.getCreatedDids({
        did: did.didState.did,
        method: 'key',
      })

      didRecord.setTag('isDefault', true)

      await didRepository.update(agent.context, didRecord)
      defaultDidRecord = didRecord
    }

    const resolvedDidDocument = await agent.dids.resolveDidDocument(defaultDidRecord.did)
    // console.log('This is resolved did document::::', JSON.stringify(resolvedDidDocument, null, 2))
    return resolvedDidDocument
  } catch (error) {
    // eslint-disable-next-line no-console
    console.log('Error did create', error)
  }
}

var readline = require('readline')

var rl = readline.createInterface(process.stdin, null)

var agent = null
var agentConfig = null

rl.setPrompt('')
rl.prompt(false)

const handleError = async (e) => {
  process.stdout.write(JSON.stringify({ error: 1, result: e }) + '\n')
}

rl.on('line', async (line) => {
  try {
    var command = JSON.parse(line)

    if (command['cmd'] == 'start') {
      [agent, agentConfig] = await initializeAgent(
        command['withMediation'],
        command['port'],
        command['agentConfig']
      )
      // if (command["agentConfig"] === null || !command["agentConfig"]) {
      //   [agent, agentConfig] = await initializeAgent(
      //     command["withMediation"],
      //     command["port"]
      //   );
      // } else {
      //   [agent, agentConfig] = await initializeAgent();
      // }
      // process.stdout.write(
      //   JSON.stringify({ error: 0, result: "Initialized agent..." }) + "\n"
      // );
      process.stdout.write(
        JSON.stringify({ error: 0, result: agentConfig }) + '\n'
      )
    } else if (command['cmd'] == 'ping_mediator') {
      await pingMediator(agent)
      process.stdout.write(
        JSON.stringify({ error: 0, result: 'Ping Mediator' }) + '\n'
      )
    } else if (command['cmd'] == 'deleteOobRecordById') {
      await deleteOobRecordById(agent, command['id'])

      process.stdout.write(
        JSON.stringify({ error: 0, result: 'Delete OOB Record' }) + '\n'
      )
    } else if (command['cmd'] == 'createHolderDIDKey') {
      let didResult = await getDefaultHolderDidKeyDocument(agent)
      process.stdout.write(
        JSON.stringify({ error: 0, did: didResult,result: 'Created did:key for holder' }) + '\n'
      )
    } else if (command['cmd'] == 'receiveInvitation') {
      let connection = await receiveInvitation(agent, command['invitationUrl'])

      process.stdout.write(
        JSON.stringify({
          error: 0,
          result: 'Receive Connection',
          connection: connection,
        }) + '\n'
      )
    } else if (command['cmd'] == 'receiveInvitationConnectionDid') {
      let connection = await receiveInvitationConnectionDid(agent, command['invitationUrl'])

      process.stdout.write(
        JSON.stringify({
          error: 0,
          result: 'Receive Invitation Connection',
          connection: connection,
        }) + '\n'
      )
    } else if (command['cmd'] == 'receiveCredential') {
      await receiveCredential(agent)

      process.stdout.write(
        JSON.stringify({ error: 0, result: 'Receive Credential' }) + '\n'
      )
    } else if (command['cmd'] == 'presentationExchange') {
      await presentationExchange(agent)

      process.stdout.write(
        JSON.stringify({ error: 0, result: 'Presentation Exchange' }) + '\n'
      )
    } else if (command['cmd'] == 'receiveMessage') {
      await receiveMessage(agent)

      process.stdout.write(
        JSON.stringify({ error: 0, result: 'Receive Message' }) + '\n'
      )
    } else if (command['cmd'] == 'shutdown') {
      process.stdout.write(
        JSON.stringify({ error: 0, result: 'Shutting down agent' }) + '\n'
      )
      rl.close()
      await agent.shutdown()
      process.exit(1)
    } else {
      handleError('Invalid command')
    }
  } catch (e) {
    if (e.name === 'JSONDecodeError') {
      process.stdout.write(
        JSON.stringify({ error: 0, result: 'JSONDecodeError received' }) + '\n'
      )
    }
    handleError(e)
  }
})

process.once('SIGTERM', function (code) {
  process.stderr.write('SIGTERM received...' + '\n')
  process.exit(1)
})
