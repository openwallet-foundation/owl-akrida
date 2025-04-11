require("dotenv").config();
const fs = require('fs');
const CANdy = ``;
let ledger = {};
const ReadGenesisTransactions = (networks) => {
  try {
    const fileContents = fs.readFileSync(networks, 'utf-8');
    const genesisTransactions = fileContents;
    return genesisTransactions
  } catch (error) {
    process.stderr.write('******** Error at ReadingGenesisTransactions'+ '\n' +error+ '\n')
  }
}
if (process.env.LEDGER == "bcovrin") {
  ledger = {
    genesisTransactions: ReadGenesisTransactions("./networks/BCovrintest.txn"),
    id: "BCovrinTest",
    indyNamespace: 'bcovrin:test',
    isProduction: false,
    connectOnStartup: true,
  };
} else if (process.env.LEDGER == "candy") {
  ledger = {
    genesisTransactions: ReadGenesisTransactions("./networks/CANdy.txn"),
    id: "CANdyDev",
    indyNamespace: 'did:indy:candy:dev',
    isProduction: false,
    connectOnStartup: true,
  };
} else if (process.env.LEDGER == "indicio") {
  ledger = {
    genesisTransactions: ReadGenesisTransactions("./networks/indicio-test.txn"),
    id: "IndicioTest",
    indyNamespace: 'did:indy:indicio:test',
    isProduction: false,
    connectOnStartup: true,
  };
}
exports.mediation_url = process.env.MEDIATION_URL;
exports.agent_ip = process.env.AGENT_IP;
exports.verified_timeout_seconds = (process.env.VERIFIED_TIMEOUT_SECONDS || 120)
exports.ledger = ledger;