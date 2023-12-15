# Credential Customization

This short document is to help customize your environment to putting your own credentials into Locust. The default credential attributes we mainly work with are for a small one attribute credential. 

## Preliminary Information

In this example below, we will walk through the example of a credential with 
* a `created-date` of `22 Mar 23`, 
* a nice identifying `photo` (whose value we will fill in later), 
* a `given-name` of `Bob`, and 
* a `family-name` of `Builder`,
so, within our Locust `.env`, we will have
```
CRED_ATTR='[
    {"name": "created-date", "value": "22 Mar 23"},
    {"name": "photo", "value": "putPhotoHere"},
    {"name": "family-name", "value": "Builder"},
    {"name": "given-names", "value": "Bob"}
]'
```
Fill this portion out appropriately for your respective credential. (In order to ensure your environment works properly, it is recommended to put simple, short strings in at first (e.g. for images or unique IDs) and then, later, replace these short strings with their longer form after everything has been confirmed to work.

Using your respective `CRED_ATTR`, fill out the names of the attributes you will need. In this example, we would have
```
ATTRIBUTES=[
    "created-date",
    "photo",
    "family-name",
    "given-names"
]
```
With this information now recorded, we can now get started.

## ACA-Py Admin UI

Head to your ACA-Py Admin UI. 
* For your non-clustered environment, this is located at `{EXTERNAL_IP_OF_ACAPY_AGENT}:8150/api/doc`, where `{EXTERNAL_IP_OF_ACAPY_AGENT}` is the external IP of your ACA-Py agent.
* For your clustered environment, this is located at `{FRONTEND_ACAPY_LB_DNS}:8080/api/doc`, where `{FRONTEND_ACAPY_LB_DNS}` is the DNS name of your frontend ACA-Py load balancer.

#### Schema

Now let's create a schema, so we can issue some fun new credentials.

Under the ACA-Py Admin UI, let's head to the section titled `schema`. Click on the $\color{green}{post}$ method titled $\color{green}{/schemas}$ and, again, click on the `Try it out` box. Then, fill it out so

```
{
  "attributes": ATTRIBUTES,
  "schema_name": "nameOfSchema",
  "schema_version": "1.0"
}
```
where `ATTRIBUTES` is the list we created earlier (`[` and `]` included) and where `nameOfSchema` is an arbitrary string for the respective name of the schema you're creating. So, for example, this might look like
```
{
  "attributes": [
    "created-date",
    "photo",
    "family-name",
    "given-names"
    ],
  "schema_name": "example_credential",
  "schema_version": "1.0"
}
```

Then, click the blue $\color{blue}{Execute}$ button. Copy the `schema_id` from the response (the top box). You will want to save this somewhere (as we'll reuse this within the locust section). 

*Note: If you get an error during this step saying that you need a public DID, go follow the instructions for anchoring your did within [NONCLUSTERED.md](NONCLUSTERED.md).*

#### Credential Definition

Now that we have a schema created, let's scroll up to the section titled `credential-definition`. Click on the $\color{green}{post}$ method titled $\color{green}{/credential-definitions}$ and, again, click on the `Try it out` button. Modify the `body` JSON values so it looks like
```
{
  "schema_id": "pasteSchemaIDHere",
  "support_revocation": false,
  "tag": "default"
}
```
where `pasteSchemaIDHere` is the `schema_id` you just copied in the previous step. If you would like this credential to be revocable (make sure, within your `docker-compose.yml`, you have a tails service), try
```
{
  "revocation_registry_size": 1000,
  "schema_id": "pasteSchemaIDHere",
  "support_revocation": true,
  "tag": "default"
}
```
instead for the body input box. If you've confirmed your JSON body value follows a similar format (either the non-revocable or revocable format), click the blue $\color{blue}{Execute}$ button. Again, as you copied the DID and `schema_id` from before, copy this top `credential_definition_id`. Once again, we will be using this later, so make sure to save it some place safe. 

Awesome! Now we're ready to move onto locust.

## Locust

Simply put, within the Locust `.env`, update the `CRED_ATTR`, `SCHEMA`, and `CRED_DEF` variables, respectively, as we have done previously. 
* For your non-clustered environment, with a single Locust VM, just update the single `.env`.
* For your non-clustered Locust environment, with a Locust `master` and `worker` VM, update both `.env`'s. 
* For your clustered environment, update the `.env` of your Locust `master` VM. For the Locust `worker` VM, 
    1. update the launch template, 
    2. set the default version of the launch template, 
    3. spin down the auto scaling group for the Locust `workers`, and 
    4. spin back up the auto scaling group. 
    If you need help with steps 1-4, please see [CLUSTERED.md](CLUSTERED.md).

From here, we should be good to go, if you have already populated the `.env`. To proceed, just type in
```
# If needed:
# sudo docker-compose down -v
# sudo pkill -9 -f docker
# sudo systemctl disable docker docker.socket 
# sudo rm -rf /var/lib/docker
# sudo systemctl start docker
# If needed: sudo systemctl restart docker

sudo docker-compose build
sudo docker-compose up
# If .env doesn't update, try: sudo docker-compose build --no-cache
```
Once everything spins up, the locust browser will be available on `http://{EXTERNAL_IP_OF_LOCUST_MASTER_VM}:8089`. Go ahead and give things a whirl with `1` total user spawning at a rate of `1` per second. It might take a moment to go through all of the scenarios but, if things are successful, then you've successfully spun up the environment!

If everything works successfully, now would be a good time to spin down the environment and begin putting in any long strings that you originally left out of your `CRED_ATTR` variable. In order to send photos, (1) find the respective photo, (2) use a base64 encoder so you can send it through a credential (this can be googled), and (3) paste the base64 encoded value as the value for the respective photo keys within your `CRED_ATTR`. Then, try downing, building, and upping again!