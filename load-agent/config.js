require("dotenv").config();

const CANdy = ``;

let ledger = {};

if (process.env.LEDGER == "bcovrin") {
  ledger = {
    genesisPath: "./networks/BCovrintest.txn",
    id: "BCovrinTest",
    indyNamespace: 'bcovrin:test',
    isProduction: false,
    connectOnStartup: true,
  };
} else if (process.env.LEDGER == "candy") {
  ledger = {
    genesisPath: "./networks/CANdy.txn",
    id: "CANdyDev",
    indyNamespace: 'candy:dev',
    isProduction: false,
    connectOnStartup: true,
  };
} else if (process.env.LEDGER == "indicio") {
  ledger = {
    genesisPath: "./networks/indicio-test.txn",
    id: "IndicioTest",
    indyNamespace: 'indicio:test',
    isProduction: false,
    connectOnStartup: true,
  };
}

exports.mediation_url = process.env.MEDIATION_URL;
exports.agent_ip = process.env.AGENT_IP;
exports.verified_timeout_seconds = (process.env.VERIFIED_TIMEOUT_SECONDS || 120)
exports.ledger = ledger;
