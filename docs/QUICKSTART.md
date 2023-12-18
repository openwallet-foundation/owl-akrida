# Quick Start Guide

The quick start guide will help you use a local docker-compose file to start Locust, a mediator, and an Aca-Py instance. This guide will help you setup and configure the local environment and run Locust easily.

While this is a quick start guide to familiarize yourself with Locust testing for Aries based protocols, this project is not designed to manage or maintain any Aries environment, but to apply a load to it. 

## Setting up the environment

Copy the sample.demo.env file to .env

The start the demo docker-compose by running the following command.

`docker-compose -f docker-compose.demo.yml up`

The next step is to find the invitation to the mediator by running the following command.

`docker-compose -f docker-compose.demo.yml logs mediator`

You should see something like the following

```
aries-akrida-mediator-1  | Invitation URL (Connections protocol):
aries-akrida-mediator-1  | http://mediator:3000?c_i=eyJAdHlwZSI6ICJkaWQ6c292OkJ6Q2JzTlloTXJqSGlxWkRUVUFTSGc7c3BlYy9jb25uZWN0aW9ucy8xLjAvaW52aXRhdGlvbiIsICJAaWQiOiAiY2E2ZGNkNjEtNmRmZC00Zjk3LTg5MzktZDRlMThkNGRjYzI5IiwgInJlY2lwaWVudEtleXMiOiBbIjhzaWY5YTVTazR4QzFCYnhxYnNZZVJnTGN2WFNqZFF4UjFldnpKMjloQk1mIl0sICJsYWJlbCI6ICJNZWRpYXRvciAoQWRtaW4pIiwgInNlcnZpY2VFbmRwb2ludCI6ICJodHRwOi8vbWVkaWF0b3I6MzAwMCJ9
```

Copy the invitation URL into the .env file. Example:

```
MEDIATION_URL=http://mediator:3000?c_i=eyJAdHlwZSI6ICJkaWQ6c292OkJ6Q2JzTlloTXJqSGlxWkRUVUFTSGc7c3BlYy9jb25uZWN0aW9ucy8xLjAvaW52aXRhdGlvbiIsICJAaWQiOiAiY2E2ZGNkNjEtNmRmZC00Zjk3LTg5MzktZDRlMThkNGRjYzI5IiwgInJlY2lwaWVudEtleXMiOiBbIjhzaWY5YTVTazR4QzFCYnhxYnNZZVJnTGN2WFNqZFF4UjFldnpKMjloQk1mIl0sICJsYWJlbCI6ICJNZWRpYXRvciAoQWRtaW4pIiwgInNlcnZpY2VFbmRwb2ludCI6ICJodHRwOi8vbWVkaWF0b3I6MzAwMCJ9
```

Now we will need to restart the services for the .env file to update the Locust environment. Doing a simple docker-compose restart will not reload the .env file. We can CTRL-C the up command and run up again, or we can call the following to restart the services. When calling the docker-compose down, do not include the -v flag, as this will remove the volumes with the issuer and mediator settings.

```
docker-compose -f docker-compose.demo.yml down
docker-compose -f docker-compose.demo.yml up
```

We can now go to http://localhost:8089/ and start Locust with 1 agent. The default load configuration is the locustMediatorPing. This will send a DIDComm ping through the mediator agent back to the Locust AFJ agent.

### ACA-Py Agent Configuration

#### Anchoring and Setting DID

To run different tests, we will need to setup the issuer. To do this we can visit the swagger API at http://localhost:8150/api/doc.

In order to be able to have this ACA-Py agent be able to issue credentials to our simulated clients, we need to set it up for success. To do this, we will have to navigate to the ACA-Py Admin UI. 

Welcome to the ACA-Py Admin UI! There are a lot of API calls here, but we're only interested in a select few. Let's scroll down all the way to the section titled `wallet`. 

Within the `wallet` section, click on the $\color{green}{post}$ method  $\color{green}{/wallet/did/create}$. This should have the dropdown section extend downwards. Click on the box titled `Try it out`. Click on the blue $\color{blue}{Execute}$ button. This will generate you a DID and a verkey. 

In a separate tab in your browser, navigate to where you can anchor DIDs to the ledger you chose. For Indicio, this is our [self serve site](https://selfserve.indiciotech.io/). If you're using this [Indicio's self serve site], make sure you have selected Indicio's *TestNet*. Then, paste the DID and Verkey. (Notice, in the responses, there are two DIDs and Verkey pairs. There's the top (real) one and the bottom (example) one. We want the top pair.) After pasting, click the orange `Submit` button. (It's recommended not to close this tab yet or, if you do close this tab, save the DID.)

After submitting, return back to the ACA-Py admin UI. Scroll up to the section titled `ledger`. Under the $\color{blue}{get}$ request, click on the $\color{blue}{/ledger/taa}$ dropdown. We will need to accept the transaction author agreement, for the Indicio ledger (or whatever ledger you are using), in order to be able to successfully associate our DID with this issuer. Under this dropdown, click the `Try it out` box. Click the blue $\color{blue}{Execute}$ button.

This will return a rather large response. Copy everything in the `"text"` value; that is, for example... `"Indicio Transaction Author Agreement \n\nVersion... \n\n""`. Make sure to include the beginning `"` and ending `"`. 

Then, right below this dropdown menu, click the following $\color{green}{post}$ method with $\color{green}{ledger/taa/accept}$. Click on the `Try it out` button. 

Within the `body` section, replace the `"string"` bit corresponding to `"text"` with the bit you copied just before. Under `"mechanism"`, replace that corresponding `"string"` with `"on_file"` (unless told otherwise). Under `"version"`, replace that corresponding `"string"` with `"1.0"`. Thus, if you've done everything right, the JSON body box should look something like:

```
{
  "mechanism": "on_file",
  "text": "Indicio Transaction Author Agreement \n\n...under its own legislation.  \n\n",
  "version": "1.0"
}
```
where, of course, the text string above is much much longer. If everything looks right, click the blue $\color{blue}{Execute}$ button. 

Awesome! Now we should be able to assign our current public DID. We can do that by returning back to the `wallet` section, going under the $\color{green}{post}$ method titled $\color{green}{/wallet/did/public}$ and clicking it. Click on the `Try it out` button. After clicking on `Try it out`, paste the DID you anchored earlier into the `DID of interest` box. Then click the blue $\color{blue}{Execute}$ button. 

You've now successfully anchored that DID to the ledger and successfully associated that DID with this ACA-Py agent! 

#### Creating a Schema

Now let's create a schema, so we can issue some credentials. For this bit, we're going to stick with a super simple credential. However, after going through this process, you're more than welcome to modify the bits to whatever type of credential you're looking for. 

Under the same ACA-Py Admin UI, let's head to the section titled `schema`. Click on the $\color{green}{post}$ method titled $\color{green}{/schemas}$ and, again, click on the `Try it out` box. We're just going to use the default schema, as we're just interested in a small, simple credential, but you're welcome to change this (just note you'll need to propagate these changes elsewhere in the `.envs` and code, accordingly). Click the blue $\color{blue}{Execute}$ button. Like before when we copied the DID, copy the `schema_id` from the response. You will want to save this somewhere (will be used in the locust section too). 

*Note: If you get an error during this step saying that you need a public DID, go follow the previous instructions again (or, alternatively, analyze your process --- something may be going wrong when anchoring your DID).*

#### Creating a Credential Definition

Now that we have a schema created, let's scroll up to the section titled `credential-defintiion`. Click on the $\color{green}{post}$ method titled $\color{green}{/credential-definitions}$ and, again, click on the `Try it out` button. Modify the `body` JSON values so it looks like
```
{
  "schema_id": "pasteSchemaIDHere",
  "support_revocation": false,
  "tag": "default"
}
```
where `pasteSchemaIDHere` is the `schema_id` you just copied in the previous step. We will not be concerning ourselves with revocation at the moment but, certainly, we can in the future. If you've confirmed your JSON body value follows a similar format, click the blue $\color{blue}{Execute}$ button. Again, as you copied the DID and `schema_id` from before, copy this top `credential_definition_id`. Once again, we will be using this later, so make sure to save it some place safe. 

### Acapy Issuer based loads

We will add both the schema and credential definitions to our .env file. 

```
CRED_DEF=XWnDacoq8JZ7HyghGTjYw2:3:CL:24536:default
LEDGER=indicio # or candy or whichever ledger is your preference
CRED_ATTR='[{"mime-type": "text/plain","name": "score","value": "test"}]'
SCHEMA=XWnDacoq8JZ7HyghGTjYw2:2:prefs:1.0
VERIFIED_TIMEOUT_SECONDS=20 # seconds for verified: true
```

We can the select on of the other load tests, such as the locustMediatorIssue.py test, which will test issue credential to the Locust AFJ agent. 

To do this will will comment out the locustMediatorPing.py and select

```
WITH_MEDIATION = True 
#LOCUST_FILES=locustMediatorPing.py
#LOCUST_FILES=locustMediatorMsg.py
LOCUST_FILES=locustMediatorIssue.py
#LOCUST_FILES=locustMediatorPresentProof.py
```

We can now restart the docker-compose services and run the load test.

Now we will need to restart the services for the .env file to update the Locust environment. Doing a simple docker-compose restart will not reload the .env file. We can CTRL-C the up command and run up again, or we can call the following to restart the services. When calling the docker-compose down, do not include the -v flag, as this will remove the volumes with the issuer and mediator settings.

```
docker-compose -f docker-compose.demo.yml down
docker-compose -f docker-compose.demo.yml up
```

## Performance Testing Basics

Basic Performance Testing involves the following steps

### Identify the test environment

"Identify the Test Environment. Identify the physical test environment and the production environment as well as the tools and resources available to the test team. The physical environment includes hardware, software, and network configurations. Having a thorough understanding of the entire test environment at the outset enables more efficient test design and planning and helps you identify testing challenges early in the project. In some situations, this process must be revisited periodically throughout the project's life cycle." - [Wikipedia](https://en.wikipedia.org/wiki/Software_performance_testing)

First, it is important to identify the different aspects of the system that need to be tested. This will typically involve an Issuer Agent, a Verifier Agent, a Mediator Agent, and one or more Controllers that manage the agents. It is important that you identify the different pieces of software you wish to load test in your environment. You may have additional systems that you wish to load test that existing out side of the scope of the Aries Akrida project, which may require additional tools to load test. Locust may provide useful in load testing environments which the Aries Akrida project is not designed to load test.

Second, it is important to identify the various environments that you wish to load test. There may be development, staging, production, or even a new environment dedicated to load testing. Each of these environments may have different configurations that need to be considered during load testing. Firewalls, load balancers, network limitations, etc. It is recommend that when load testing, you test an environment that is as similar to the production environment as possible. By testing an environment that is production, or similar to, you can have confidence in the numbers generated by your load testing.

Third, it is important to identify the tools and resources available to the test team. Tools may include the load testing tools, monitoring tools, debugging tools, logging tools, and configuration tools. Resources may include the testing hardware, production hardware, and staff members.

It is important to have tools that help load test your environment. The Aries Akrida project provides load testing tools for DIDComm based protocols, but you may need additional load testing tools for your environment to test other features.

Monitoring tools may be helpful in identifying bottlenecks in your test environment. It is important to monitor the different aspects of your systems during testing to identify potential bottlenecks. Common bottlenecks include CPU, Memory, Disk, and Network based bottlenecks.

To monitor CPU usage, tools such as top, htop, Nagios, Zabbix or a cloud specific tool may be helpful here.

To monitor Memory usage, tools such as free, top, htop, Nagios, Zabbix or a cloud specific tool may be helpful here.

To monitor Disk usage, tools such as iostat, iotop, Nagios, Zabbix or a cloud specific tool may be helpful here.

To monitor Network usage, tools such as iftop, ethtool, Nagios, Zabbix, Cacti, SNMP, or a cloud specific tool may be helpful here.

The list of tools here is not an exhaustive list, but merely an idea of various tools that oculd be used to monitor you environment during load testing.

Forth, it can be helpful to diagram the configuration of the environment being tested to understand the configuration of the systems that are going to be load testing. Understanding the configuration of the environment may ease the diagnosis of bottlenecks. For example, if you understand that you have a 10mbit network link between the Aries Akrida test agents and the system you are testing, you may be able to identify the network being the bottleneck when the 10mbit interface is saturated.

### Identify Performance Acceptance Criteria

"Identify Performance Acceptance Criteria. Identify the response time, throughput, and resource-use goals and constraints. In general, response time is a user concern, throughput is a business concern, and resource use is a system concern. Additionally, identify project success criteria that may not be captured by those goals and constraints; for example, using performance tests to evaluate which combination of configuration settings will result in the most desirable performance characteristics."  - [Wikipedia](https://en.wikipedia.org/wiki/Software_performance_testing)

Understanding the performance acceptance criteria is crucial to the success of your project. These are often business based requirements, such as verifying 100,000 individuals for an event within 1 hour. Understanding your requirements will provide guidance what load tests to run, and if the environment meets the requirements.

### Plan and Design Tests

"Plan and Design Tests. Identify key scenarios, determine variability among representative users and how to simulate that variability, define test data, and establish metrics to be collected. Consolidate this information into one or more models of system usage to implemented, executed, and analyzed." - [Wikipedia](https://en.wikipedia.org/wiki/Software_performance_testing)

Planning and designing the tests may change based upon the particular goal of the load test. For example, load testing ot meet a particular business requirement may involve testing the entire system, including the issuer, verifier, mediator agent, and various controllers. In other cases, the goal may be to test a particular agent, such as the mediator agent, to determine the individual behavior of a single system.

Testing an individual agent separate form other agents, while not determining overall system performance, may help identify bottlenecks in your individual environment. An example of this is load testing the mediator agent separately from the rest of the environment may provide insight into the maximum load that your mediator agent can service. By understanding the limitation of the individual systems, it may be easier to identify the overall bottleneck in the system. If the mediator can only handle x number of messages, but you are trying to issue more credentials than the number of messages the mediator agent can handle, then you are able to establish that the mediator will be a bottleneck in your environment.

### Configure the Test Environment

"Configure the Test Environment. Prepare the test environment, tools, and resources necessary to execute each strategy, as features and components become available for test. Ensure that the test environment is instrumented for resource monitoring as necessary." - [Wikipedia](https://en.wikipedia.org/wiki/Software_performance_testing)

### Implement the Test Design

"Implement the Test Design. Develop the performance tests in accordance with the test design." - [Wikipedia](https://en.wikipedia.org/wiki/Software_performance_testing)

While Aries Akrida provides some sample performance tests, you may need to write your own performance tests to meet the requirements of your particular load test.

### Execute the Test

"Execute the Test. Run and monitor your tests. Validate the tests, test data, and results collection. Execute validated tests for analysis while monitoring the test and the test environment." - [Wikipedia](https://en.wikipedia.org/wiki/Software_performance_testing)

### Analyze Results, Tune, and Retest

"Analyze Results, Tune, and Retest. Analyze, consolidate, and share results data. Make a tuning change and retest. Compare the results of both tests. Each improvement made will return smaller improvement than the previous improvement. When do you stop? When you reach a CPU bottleneck, the choices then are either improve the code or add more CPU." - [Wikipedia](https://en.wikipedia.org/wiki/Software_performance_testing)

After each load test, it is important to analyze the data provided by the load test. An example, is looking the CPU usage of an Aca-Py Agent. Aca-Py is Python based, and so it is mostly limited to a single CPU. In top or htop, we often seen the Aca-Py process using up or around 130% CPU usage, or about 1 and a third CPU cores. Once that limit is reached, the individual Aca-Py agent cannot scale further, and would require a clustered environment.

If it is unclear where the bottleneck is, it may be helpful to test the individual components of the system. In some cases, it may be surprising to find that the network is the bottleneck, or the disk IO is the bottleneck. Not all systems provide a clear indication of when a particular resource has reached a bottleneck. For example, in some cloud environments, it may be unclear the number of packets per second that a network interface can handle. If a bottleneck is unclear, testing individual services or components may provide insight as to where the bottleneck actually is.

Aries Locust is designed to run with or without a mediator agent to assist in testing individual components. While the load test requests per second may not provide detailed numbers of the capability of an individual component, it may help you analyze the particular agents CPU, memory, disk IO, and network abilities. An example of this is your overall test may be designed to monitor the number of credentials issued per minute, but the load test of the mediator agent may only provide the number of messages sent per second. While the load test for the mediator agent doesn't provide insight into how many credentials could be issued per second, the test may provide details of the maximum CPU, memory, disk IO, or network usage the mediator can handle. This result can be compared to a test that includes multiple systems such as an issuer and mediator agent. If the performance of the mediator in the multiple system test is less than in the single agent test, it can be determined that mediator is not the likely source of the bottleneck. However, if the mediator agent's performance is the same, it may be determined that the mediator is the source of the bottleneck in the multi agent test.
