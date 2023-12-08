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