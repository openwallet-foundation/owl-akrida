# Running Aries Akrida

Before starting any load testing you **SHOULD** gain written permission that includes the time, method and various systems that you wish to load test. You **MUST NOT** load test any system that you do **NOT** have permission to test.

For high concurrency testing, it is useful to run Locust on a VM where you can easily add more resources for bigger tests. Please read [docs/VM.md](./VM.md)

## Running Locally

Use the [Quick Start](./QUICKSTART.md) guide to run locally.

### DevContainer

This project contains a vscode devContainer to provide a consistent platform for running the load tests and/or mediator in a virtual environment.

Prerequisites:
- VSCode with the Dev Containers plugin installed.

To use it, open the project in VSCode and you should be prompted to `Reopen in Container`.  Click `Reopen in Container`.  Once the container has built and started you will be able to access a workspace terminal in the container where you'll be able to run your commands.  You can then follow the remainder of these steps from within the container.

ToDo:
- Enhance the dev container to automate the setup of the load testing environment.

### Local Setup Instructions

## Running load tests
```
# Clone this repo
git clone URL aries-akirda
cd aries-akirda

# Copy the sample.env to .env and edit it according to your needs -- at least the MEDIATION URL
cp sample.env .env

# If you are running a local Mediator using the root `docker-compose.yml` file, then start it first and copy/paste the Mediation invitation URL
# MEDIATION_URL=<insert your mediation invitation url here>

# Each successive ping on an AFJ agent will be sent in a random interval between these two parameters (in seconds)
# Lower these to send more pings
# LOCUST_MIN_WAIT=60 min time between pings
# LOCUST_MAX_WAIT=120 max time between pings

# Some tests require the issuer or verifier to talk directly to AFJ. A port and IP address are required for this. The ports and IP address must be available for the Issuer or Verifier to contact for the tests to work correctly. In the case that the test is using a mediator, the IP and address don't need to be publicly available, but they still need to be allocated for code simplification.

# AGENT_IP=172.16.49.18

# A port range is required since each AFJ agent requires its own port. The ports are in a pool and are acquired from the pool as needed. If the process runs out of ports during operation, it will hang causes locust to freeze. Allocating at least one IP address per locust user is required. All the ports are mapped in Docker, so the more ports that are mapped, the longer it will take to start the docker environment.
# The more ports you allocate, the longer to start and stop the Locust

# START_PORT=10000
# END_PORT=12000

# More than one locust file can be specified at a time. Each locust User will be assigned to run one test. After the tests are defined, other locust commands could be added to the end of the LOCUST_FILES parameter.
# For mediator testing use just the "locustMediatorPing.py" as notes in the sample.env
# LOCUST_FILES=locustMediatorPing.py,locustIssue.py # Specifies which tests to run
# LOCUST_FILES=locustMediatorPing.py --master -P 8090

# The Issuer URL and HEADERS required to use the issuer
# Not needed for Mediator testing with pings
# ISSUER_URL=http://172.16.49.18:8150
# ISSUER_HEADERS={"Authorization":"Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ3YWxsZXRfaWQiOiIwOWY5ZDAwNC02OTM0LTQyZDYtOGI4NC1jZTY4YmViYzRjYTUiLCJpYXQiOjE2NzY4NDExMTB9.pDQPjiYEAoDJf3044zbsHrSjijgS-yC8t-9ZiuC08x8"}

# The cred def, credential attributes, and schema used for issuer load testing.
# Not needed for Mediator testing with pings
# CRED_DEF=MjCTo55s4x1UWy2W2spuU2:3:CL:131358:default
# CRED_ATTR='[{"mime-type": "text/plain","name": "score","value": "test"}]'
# SCHEMA=MjCTo55s4x1UWy2W2spuU2:2:prefs:1.0

# The ledger to use for issuance and verification. Additional networks can be added to config.js
# Not needed for Mediator testing with pings
# LEDGER=candy

docker-compose build
docker-compose up

# open web browser to localhost:8089
# Use the interface to start and stop tests, review results
```

### User Startup

When starting up the Users for tests, the Aries Framework Javascript(AFJ) agents used for the Locust client may take more CPU than when running the test. Since the startup cost can be more expensive, you may either need a larger machine to onboard Users faster, or slow down the onboarding rate.

Typically symptoms of starting agents to quickly is getting an timeout error on startup.

Depending upon the test and the Minimum and Maximum wait times configured for the test, the number of Users you can run on a single Locust machine may vary. It is recommend to monitor CPU, memory utilization, and network usage in your environment so that you can tune the load test machine(s) appropriately.

## Issuer configuration

Accept TAA

Register DID

Register Schema

{
  "attributes": [
    "score"
  ],
  "schema_name": "prefs",
  "schema_version": "1.0"
}

Register Cred Def

Add Cred Def and Schema to env

## Load Test Notes

The start rate for clients, when to high will, will cause the mediator to be overloaded.
Starting at new clients of 0.4 for every second is a good starting point.

Since the load testing uses AFJ for the clients, it may require more resources to run the
load environment than other Locust based load testing frameworks.

## Multi machine load test

Multiple locust nodes can be run to distribute the load testing. In the case of running
multiple nodes, you need to ensure each node has the environment variables set.

The master node will need to have a port opened to listen to incoming workers.

```
locust --master -P 8090
locust --worker
locust --worker  --master-host 10.128.15.214
```

## System requirements

* An IP address and ports accessible to the Issuer or Verifier if running tests without a mediator
* Each AFJ agent requires approximately 52 - 100 MB of ram. So a 32 GB machine should be able to run approximately 550 Users assuming 4 GB of OS overhead.
* CPU usage will vary depending upon LOCUST_X_TIME and load test being run

### Memory Usage

Memory usage is more complicated than looking at top and using the RSS value.

Looking at the process status in linux we can see the following
```
cat /proc/15041/status

Name:   node
Umask:  0022
State:  S (sleeping)
Tgid:   15041
Ngid:   0
Pid:    15041
PPid:   14769
TracerPid:      0
Uid:    0       0       0       0
Gid:    0       0       0       0
FDSize: 64
Groups:  
NStgid: 15041   178
NSpid:  15041   178
NSpgid: 14769   1
NSsid:  14769   1
VmPeak: 12090960 kB
VmSize: 12023888 kB
VmLck:         0 kB
VmPin:         0 kB
VmHWM:    225704 kB
VmRSS:    100892 kB
RssAnon:           49280 kB
RssFile:           51612 kB
RssShmem:              0 kB
VmData:   173944 kB
VmStk:       132 kB
VmExe:     78112 kB
VmLib:     16852 kB
VmPTE:      2760 kB
VmSwap:        0 kB
HugetlbPages:          0 kB
CoreDumping:    0
THP_enabled:    1
Threads:        19
SigQ:   0/63948
SigPnd: 0000000000000000
ShdPnd: 0000000000000000
SigBlk: 0000000000000000
SigIgn: 0000000001001000
SigCgt: 0000000188004602
CapInh: 00000000a80425fb
CapPrm: 00000000a80425fb
CapEff: 00000000a80425fb
CapBnd: 00000000a80425fb
CapAmb: 0000000000000000
NoNewPrivs:     0
Seccomp:        2
Seccomp_filters:        1
Speculation_Store_Bypass:       thread force mitigated
Cpus_allowed:   f
Cpus_allowed_list:      0-3
Mems_allowed:   00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000001
Mems_allowed_list:      0
voluntary_ctxt_switches:        1162
nonvoluntary_ctxt_switches:     644
```

Focusing on memory usage

```
RssAnon:           49280 kB
RssFile:           51612 kB
```

It can be seen that the process uses a unique 49280 kB, but since the RssFile can be shared between processes, only one copy of 51612 kB needs to reside in memory. This results in each process using around ~50 MB of ram with an additional ~50 MB shared with all the processes.



## Using Wallet type as Askar-Anoncreds instead of Askar

*  Delete old containers
* In issuer.yml (instance-configs/acapy-agent/configs/issuer.yml) and change  
the wallet type  -->> wallet-type: askar-anoncreds
* change the wallet name ,  wallet-name: issuer or any new name
* In IssuerAgent , in acapy.py file ,
  def issue_credential_ver2_0(self, connection_id):
                headers = json.loads(os.getenv("ISSUER_HEADERS"))
                headers["Content-Type"] = "application/json"
                
                issuer_did = os.getenv("CRED_DEF").split(":")[0]
                schema_parts = os.getenv("SCHEMA").split(":")
                payload = {
                        "auto_remove": True,
                        "comment": "Performance Issuance",
                        "connection_id": connection_id,
                        "credential_preview": {
                        "@type": "issue-credential/2.0/credential-preview",
                        "attributes": json.loads(os.getenv("CRED_ATTR")),
                        },
                        "filter": {
                        "indy": {
                                "cred_def_id": os.getenv("CRED_DEF"),
                                "schema_id": os.getenv("SCHEMA"),
                                "schema_name": schema_parts[2],
                                "schema_version": schema_parts[3]
                        }
                        },
                        "trace": True,
                }
                r = requests.post(
                        os.getenv("ISSUER_URL") + "/issue-credential-2.0/send",
                        json=payload,
                        headers=headers
                )
                
                if r.status_code != 200:
                        raise Exception(r.content)

                r = r.json()
                return {
                        "connection_id": r["connection_id"], 
                        "cred_ex_id": r["cred_ex_id"]
                }




* Note : Dont use IssuerDId and schema_issuer_did  in Json 

* Build the container image
* create a wallet and add to the ledger.
* make the wallet type public 
* create schema and cred -def
* Make the container image down
* update the .env file with the cred def and schema details

* build up the container images again 
* run the test with aries askar-anoncred wallet
