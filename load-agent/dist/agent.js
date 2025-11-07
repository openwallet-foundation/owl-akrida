"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const anoncreds_1 = require("@credo-ts/anoncreds");
const indy_vdr_1 = require("@credo-ts/indy-vdr");
const askar_1 = require("@credo-ts/askar");
const core_1 = require("@credo-ts/core");
const anoncreds_nodejs_1 = require("@hyperledger/anoncreds-nodejs");
const aries_askar_nodejs_1 = require("@hyperledger/aries-askar-nodejs");
const indy_vdr_nodejs_1 = require("@hyperledger/indy-vdr-nodejs");
const node_1 = require("@credo-ts/node");
var config = require('./config.js');
var deferred = require('deferred');
var process = require('process');
var readline = require('readline');
/*
  Remap all logging to stderr
*/
class ConsoleError extends core_1.ConsoleLogger {
    constructor(...args) {
        super(...args);
        // Map our log levels to console levels
        this.consoleLogMap = {
            [core_1.LogLevel.test]: 'error',
            [core_1.LogLevel.trace]: 'error',
            [core_1.LogLevel.debug]: 'error',
            [core_1.LogLevel.info]: 'error',
            [core_1.LogLevel.warn]: 'error',
            [core_1.LogLevel.error]: 'error',
            [core_1.LogLevel.fatal]: 'error',
        };
    }
}
const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
function generateString(length) {
    let result = '';
    const charactersLength = characters.length;
    for (let i = 0; i < length; i++) {
        result += characters.charAt(Math.floor(Math.random() * charactersLength));
    }
    return result;
}
const initializeAgent = async (withMediation, port, agentConfig = null) => {
    // Simple agent configuration. This sets some basic fields like the wallet
    // configuration and the label. It also sets the mediator invitation url,
    // because this is most likely required in a mobile environment.
    try {
        let mediation_url = config.mediation_url;
        let endpoints = ['http://' + config.agent_ip + ':' + port];
        const logLevel = parseInt(process.env.AGENT_LOGGING_LEVEL) || core_1.LogLevel.off;
        process.stderr.write('Agent Log Level: ' + parseInt(process.env.AGENT_LOGGING_LEVEL) + '\n');
        if (!agentConfig || agentConfig === null || agentConfig.length === 0) {
            agentConfig = {
                label: generateString(14),
                walletConfig: {
                    id: generateString(32),
                    key: generateString(32),
                },
                autoAcceptConnections: true,
                endpoints: endpoints,
                mediation_url: mediation_url,
                autoAcceptInvitation: true,
                logger: new ConsoleError(logLevel),
                didCommMimeType: core_1.DidCommMimeType.V1,
                storage: {
                    type: 'sqlite',
                    config: { memory: true }, // ephemeral
                },
            };
        }
        const legacyIndyCredentialFormat = new anoncreds_1.LegacyIndyCredentialFormatService();
        const legacyIndyProofFormat = new anoncreds_1.LegacyIndyProofFormatService();
        const anonCredsCredentialFormatService = new anoncreds_1.AnonCredsCredentialFormatService();
        const anonCredsProofFormatService = new anoncreds_1.AnonCredsProofFormatService();
        let modules = {
            indyVdr: new indy_vdr_1.IndyVdrModule({
                indyVdr: indy_vdr_nodejs_1.indyVdr,
                networks: [config.ledger]
            }),
            askar: new askar_1.AskarModule({
                ariesAskar: aries_askar_nodejs_1.ariesAskar,
            }),
            // mediator: new MediatorModule({
            //   autoAcceptMediationRequests: true,
            // }),
            mediationRecipient: new core_1.MediationRecipientModule({
                mediatorInvitationUrl: mediation_url,
                mediatorPickupStrategy: core_1.MediatorPickupStrategy.Implicit,
            }),
            anoncreds: new anoncreds_1.AnonCredsModule({
                registries: [new indy_vdr_1.IndyVdrAnonCredsRegistry()],
                anoncreds: anoncreds_nodejs_1.anoncreds
            }),
            connections: new core_1.ConnectionsModule({
                autoAcceptConnections: true,
            }),
            proofs: new core_1.ProofsModule({
                proofProtocols: [
                    new anoncreds_1.V1ProofProtocol({
                        indyProofFormat: legacyIndyProofFormat,
                    }),
                    new core_1.V2ProofProtocol({
                        proofFormats: [legacyIndyProofFormat, anonCredsProofFormatService],
                    }),
                ],
            }),
            credentials: new core_1.CredentialsModule({
                credentialProtocols: [
                    new anoncreds_1.V1CredentialProtocol({
                        indyCredentialFormat: legacyIndyCredentialFormat,
                    }),
                    new core_1.V2CredentialProtocol({
                        credentialFormats: [legacyIndyCredentialFormat, anonCredsCredentialFormatService],
                    }),
                ],
            }),
            dids: new core_1.DidsModule({
                registrars: [new indy_vdr_1.IndyVdrIndyDidRegistrar(), new core_1.KeyDidRegistrar()],
                resolvers: [new indy_vdr_1.IndyVdrIndyDidResolver(), new core_1.KeyDidResolver(), new core_1.WebDidResolver()],
            }),
        };
        // configure mediator or endpoints
        if (withMediation) {
            delete agentConfig['endpoints'];
        }
        else {
            delete modules['mediationRecipient'];
        }
        // A new instance of an agent is created here
        const agent = new core_1.Agent({
            config: agentConfig,
            dependencies: node_1.agentDependencies,
            modules: modules
        });
        const wsTransport = new core_1.WsOutboundTransport();
        const httpTransport = new core_1.HttpOutboundTransport();
        // Register a simple `WebSocket` outbound transport
        agent.registerOutboundTransport(wsTransport);
        // Register a simple `Http` outbound transport
        agent.registerOutboundTransport(httpTransport);
        if (withMediation) {
            // wait for mediation to be configured
            let timeout = config.verified_timeout_seconds * 1000;
            const TimeDelay = new Promise((resolve, reject) => {
                setTimeout(resolve, timeout, false);
            });
            var def = deferred();
            var onConnectedMediation = async (event) => {
                let mediatorConnection = null;
                let interval = 100;
                for (let i = 0; i < (timeout - interval); i++) {
                    // OutboundWebSocketOpenedEvent occurs before mediation is finalized, so we want to check
                    // for the default mediation connection until it is not null or we hit a timeout
                    // we sleep a small amount between requests just to be kind to our CPU. 
                    await new Promise(r => setTimeout(r, interval));
                    mediatorConnection = await agent.mediationRecipient.findDefaultMediatorConnection();
                    if (mediatorConnection != null) {
                        break;
                    }
                }
                if (event.payload.connectionId === mediatorConnection?.id) {
                    def.resolve(true);
                    // we no longer need to listen to the event
                    agent.events.off(core_1.TransportEventTypes.OutboundWebSocketOpenedEvent, onConnectedMediation);
                }
            };
            agent.events.on(core_1.TransportEventTypes.OutboundWebSocketOpenedEvent, onConnectedMediation);
            // Initialize the agent
            await agent.initialize();
            if (config.pickup_strategy === 'pickupv2-live') {
                process.stderr.write('Pickup strategy: pickupv2-live');
                await agent.mediationRecipient.initiateMessagePickup(undefined, core_1.MediatorPickupStrategy.PickUpV2LiveMode);
            }
            // wait for ws to be configured
            let value = await Promise.race([TimeDelay, def.promise]);
            if (!value) {
                // we no longer need to listen to the event in case of failure
                agent.events.off(core_1.TransportEventTypes.OutboundWebSocketOpenedEvent, onConnectedMediation);
                throw 'Mediator timeout!';
            }
        }
        else {
            const httpInbound = new node_1.HttpInboundTransport({ port: port });
            agent.registerInboundTransport(httpInbound);
            await agent.initialize();
        }
        return [agent, agentConfig];
    }
    catch (error) {
        process.stderr.write('******** ERROR Error at initialize agent' + '\n' + error + '\n');
    }
};
const pingMediator = async (agent) => {
    // Find mediator
    // wait for the ping
    let timeout = config.verified_timeout_seconds * 1000;
    const TimeDelay = new Promise((resolve, reject) => {
        setTimeout(resolve, timeout, false);
    });
    var def = deferred();
    var onPingResponse = async (event) => {
        const mediatorConnection = await agent.mediationRecipient.findDefaultMediatorConnection();
        if (event.payload.connectionRecord.id === mediatorConnection?.id) {
            // we no longer need to listen to the event
            agent.events.off(core_1.TrustPingEventTypes.TrustPingResponseReceivedEvent, onPingResponse);
            def.resolve(true);
        }
    };
    agent.events.on(core_1.TrustPingEventTypes.TrustPingResponseReceivedEvent, onPingResponse);
    let mediatorConnection = await agent.mediationRecipient.findDefaultMediatorConnection();
    if (mediatorConnection) {
        //await agent.connections.acceptResponse(mediatorConnection.id)
        await agent.connections.sendPing(mediatorConnection.id, {});
    }
    // wait for ping response
    let value = await Promise.race([TimeDelay, def.promise]);
    if (!value) {
        // we no longer need to listen to the event in case of failure
        agent.events.off(core_1.TrustPingEventTypes.TrustPingResponseReceivedEvent, onPingResponse);
        throw 'Mediator timeout!';
    }
};
let deleteOobRecordById = async (agent, id) => {
    await agent.oob.deleteById(id);
};
let receiveInvitation = async (agent, invitationUrl) => {
    // wait for the connection
    let timeout = config.verified_timeout_seconds * 1000;
    const TimeDelay = new Promise((resolve, reject) => {
        setTimeout(resolve, timeout, false);
    });
    var def = deferred();
    var onConnection = async (event) => {
        {
            let payload = event.payload;
            if (payload.connectionRecord.state === core_1.DidExchangeState.Completed) {
                // the connection is now ready for usage in other protocols!
                // console.log(`Connection for out-of-band id ${payload.connectionRecord.outOfBandId} completed`)
                // Custom business logic can be included here
                // In this example we can send a basic message to the connection, but
                // anything is possible
                agent.events.off(core_1.ConnectionEventTypes.ConnectionStateChanged, onConnection);
                def.resolve(true);
            }
        }
    };
    agent.events.on(core_1.ConnectionEventTypes.ConnectionStateChanged, onConnection);
    const { outOfBandRecord } = await agent.oob.receiveInvitationFromUrl(invitationUrl);
    // wait for connection
    let value = await Promise.race([TimeDelay, def.promise]);
    if (!value) {
        // we no longer need to listen to the event in case of failure
        agent.events.off(core_1.ConnectionEventTypes.ConnectionStateChanged, onConnection);
        throw 'Connection timeout!';
    }
    return outOfBandRecord;
};
let receiveInvitationConnectionDid = async (agent, invitationUrl) => {
    let timeout = config.verified_timeout_seconds * 1000;
    const TimeDelay = new Promise((resolve, reject) => {
        setTimeout(resolve, timeout, false);
    });
    var def = deferred();
    var onConnection = async (event) => {
        {
            let payload = event.payload;
            if (payload.connectionRecord.state === core_1.DidExchangeState.Completed) {
                agent.events.off(core_1.ConnectionEventTypes.ConnectionStateChanged, onConnection);
                def.resolve(true);
            }
        }
    };
    agent.events.on(core_1.ConnectionEventTypes.ConnectionStateChanged, onConnection);
    let legacyConnectionDid = undefined;
    let connectionId = undefined;
    let oobRecordId = undefined;
    try {
        // LO: need connection record, not OOB record since we need the connection DID
        const { outOfBandRecord, connectionRecord } = await agent.oob.receiveInvitationFromUrl(invitationUrl);
        const strRes = JSON.stringify(connectionRecord);
        connectionId = connectionRecord.id;
        oobRecordId = outOfBandRecord.id;
        // LO: retrieve the legacy DID. IAS controller needs that to issue against
        // This code adapted from https://github.com/bcgov/bc-wallet-mobile/blob/main/app/src/helpers/BCIDHelper.ts
        const legacyDidKey = '_internal/legacyDid'; // TODO:(from BC Wallet code) Waiting for AFJ export of this.
        const didRepository = agent.dependencyManager.resolve(core_1.DidRepository);
        const dids = await didRepository.getAll(agent.context);
        const didRecord = dids.filter((d) => d.did === connectionRecord?.did).pop();
        legacyConnectionDid = didRecord.metadata.get(legacyDidKey).unqualifiedDid;
    }
    catch (error) {
        process.stderr.write('******** ERROR' + '\n' + error + '\n');
    }
    // wait for connection
    let value = await Promise.race([TimeDelay, def.promise]);
    if (!value) {
        // we no longer need to listen to the event in case of failure
        agent.events.off(core_1.ConnectionEventTypes.ConnectionStateChanged, onConnection);
        throw 'Connection timeout!';
    }
    return { did: legacyConnectionDid, connectionId: connectionId, oobRecordId: oobRecordId };
};
let receiveCredential = async (agent) => {
    // wait for the ping
    let timeout = config.verified_timeout_seconds * 1000;
    const TimeDelay = new Promise((resolve, reject) => {
        setTimeout(resolve, timeout, false);
    });
    var def = deferred();
    let onCredential = async (event) => {
        let payload = event.payload;
        switch (payload.credentialRecord.state) {
            case core_1.CredentialState.OfferReceived:
                // custom logic here
                await agent.credentials.acceptOffer({
                    credentialRecordId: payload.credentialRecord.id,
                });
                break;
            case core_1.CredentialState.CredentialReceived:
                // For demo purposes we exit the program here.
                agent.events.off(core_1.CredentialEventTypes.CredentialStateChanged, onCredential);
                def.resolve(true);
                break;
        }
    };
    agent.events.on(core_1.CredentialEventTypes.CredentialStateChanged, onCredential);
    // Nothing for us to do
    // wait for credential
    let value = await Promise.race([TimeDelay, def.promise]);
    if (!value) {
        // we no longer need to listen to the event in case of failure
        agent.events.off(core_1.CredentialEventTypes.CredentialStateChanged, onCredential);
        throw 'Credential timeout!';
    }
};
let presentationExchange = async (agent) => {
    // wait for the ping
    let timeout = config.verified_timeout_seconds * 1000;
    const TimeDelay = new Promise((resolve, reject) => {
        setTimeout(resolve, timeout, false);
    });
    var def = deferred();
    let onRequest = async (event) => {
        let payload = event.payload;
        switch (payload.proofRecord.state) {
            case core_1.ProofState.RequestReceived:
                const requestedCredentials = await agent.proofs.selectCredentialsForRequest({
                    proofRecordId: payload.proofRecord.id,
                    // config: {
                    //   filterByPresentationPreview: true,
                    // },
                });
                await agent.proofs.acceptRequest({
                    proofRecordId: payload.proofRecord.id,
                    proofFormats: requestedCredentials.proofFormats,
                });
                agent.events.off(core_1.ProofEventTypes.ProofStateChanged, onRequest);
                def.resolve(true);
                break;
        }
    };
    agent.events.on(core_1.ProofEventTypes.ProofStateChanged, onRequest);
    // Wait for presentation
    let value = await Promise.race([TimeDelay, def.promise]);
    if (!value) {
        // No longer need to listen to the event in case of failure
        agent.events.off(core_1.ProofEventTypes.ProofStateChanged, onRequest);
        throw 'Presentation timeout!';
    }
};
let receiveMessage = async (agent) => {
    // wait for the ping
    let timeout = config.verified_timeout_seconds * 1000;
    const TimeDelay = new Promise((resolve, reject) => {
        setTimeout(resolve, timeout, false);
    });
    var def = deferred();
    let onMessage = async (event) => {
        let payload = event.payload;
        //        console.error(payload)
        agent.events.off(core_1.BasicMessageEventTypes.BasicMessageStateChanged, onMessage);
        def.resolve(true);
    };
    agent.events.on(core_1.BasicMessageEventTypes.BasicMessageStateChanged, onMessage);
    // Nothing for us to do
    // wait for credential
    let value = await Promise.race([TimeDelay, def.promise]);
    if (!value) {
        // we no longer need to listen to the event in case of failure
        agent.events.off(core_1.BasicMessageEventTypes.BasicMessageStateChanged, onMessage);
        throw 'Message timeout!';
    }
};
// var readline = require('readline')
var rl = readline.createInterface(process.stdin, null);
var agent = null;
var agentConfig = null;
rl.setPrompt('');
rl.prompt(false);
const handleError = async (e) => {
    process.stdout.write(JSON.stringify({ error: 1, result: e }) + '\n');
};
rl.on('line', async (line) => {
    try {
        var command = JSON.parse(line);
        // console.log('command: ',command);
        if (command['cmd'] == 'start') {
            [agent, agentConfig] = await initializeAgent(command['withMediation'], command['port'], command['agentConfig']);
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
            process.stdout.write(JSON.stringify({ error: 0, result: agentConfig }) + '\n');
        }
        else if (command['cmd'] == 'ping_mediator') {
            await pingMediator(agent);
            process.stdout.write(JSON.stringify({ error: 0, result: 'Ping Mediator' }) + '\n');
        }
        else if (command['cmd'] == 'deleteOobRecordById') {
            await deleteOobRecordById(agent, command['id']);
            process.stdout.write(JSON.stringify({ error: 0, result: 'Delete OOB Record' }) + '\n');
        }
        else if (command['cmd'] == 'receiveInvitation') {
            let connection = await receiveInvitation(agent, command['invitationUrl']);
            process.stdout.write(JSON.stringify({
                error: 0,
                result: 'Receive Connection',
                connection: connection,
            }) + '\n');
        }
        else if (command['cmd'] == 'receiveInvitationConnectionDid') {
            let connection = await receiveInvitationConnectionDid(agent, command['invitationUrl']);
            process.stdout.write(JSON.stringify({
                error: 0,
                result: 'Receive Invitation Connection',
                connection: connection,
            }) + '\n');
        }
        else if (command['cmd'] == 'receiveCredential') {
            await receiveCredential(agent);
            process.stdout.write(JSON.stringify({ error: 0, result: 'Receive Credential' }) + '\n');
        }
        else if (command['cmd'] == 'presentationExchange') {
            await presentationExchange(agent);
            process.stdout.write(JSON.stringify({ error: 0, result: 'Presentation Exchange' }) + '\n');
        }
        else if (command['cmd'] == 'receiveMessage') {
            await receiveMessage(agent);
            process.stdout.write(JSON.stringify({ error: 0, result: 'Receive Message' }) + '\n');
        }
        else if (command['cmd'] == 'shutdown') {
            process.stdout.write(JSON.stringify({ error: 0, result: 'Shutting down agent' }) + '\n');
            rl.close();
            await agent.shutdown();
            process.exit(1);
        }
        else {
            handleError('Invalid command');
        }
    }
    catch (e) {
        if (e.name === 'JSONDecodeError') {
            process.stdout.write(JSON.stringify({ error: 0, result: 'JSONDecodeError received' }) + '\n');
        }
        handleError(e);
    }
});
process.once('SIGTERM', function (code) {
    process.stderr.write('SIGTERM received...' + '\n');
    process.exit(1);
});
