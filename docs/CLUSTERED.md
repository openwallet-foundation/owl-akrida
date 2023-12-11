# Load Agent using Locust

Locust is an open source load testing tool. Locust allows defining user behaviour with Python code, and swarming your system with millions of simultaneous users.

For more information about why [Locust](https://locust.io/) was chosen, or the design document, please see [here](https://github.com/Indicio-tech/aries-akrida/blob/main/docs/DESIGN.md). 

Before proceeding, please make sure you have a billing account set up on your cloud provider and that you will have permissions to create and deploy VM instances and other architectures.

## Review of Non-Clustered Work

*Please complete the [non-clustered] section (NONCLUSTERED.md) before attempting to proceed with the instructions for spinning the load testing framework in a *clustered* environment.*

Due to the nature of AWS security groups, we have changed some things to the non-clustered portion of the environment (namely,  how to access ACA-Py). 

For each of the VMs you created in the non-clustered portion of the environment, it is recommended to update everything. (Including recloning the repository, moving everything out, etc.) This also includes updating the `.env` files with their updated counterparts. Namely, the ACA-Py `.env` file. This file will now include a key, which you will need to input / authorize yourself before using ACA-Py. (See the `sample.env`)

To help get your environment up and running, here is a helpful [checklist](CHECKLIST.md).

## Clustered Environment

In order to spin up the clustered environment for load testing, we will break this up into three steps: 
1. Creating a "master" and a "worker" VM, 
2. Creating a load balancer for the ACA-Py Agents (for both the frontend and backend). 
3. Creating load balancer for the Locust workers (as in (1)).

Once again, before proceeding with the following instructions, please (a) update your current non-clustered environment up to date and (b) ensure everything still works. 

Getting the environment back to working again is often not a trivial step (IPs change especially, which can cause havoc). In fact, throughout this document, it will be vital to check that your environment currently works (like baby steps) along the way, so you know that you're on the right track. In order to better easily get the non-clustered environment up and running, we have created a [checklist document](CHECKLIST.md) in order to better do so. (It's crucial, when creating an image of the ACA-Py agent, that everything is up-to-date as can be (especially with new ACA-Py releases).)

### "Master" and "Worker" Nodes

Please only proceed with the following section after ensuring your [non-clustered environment](NONCLUSTERED.md) is working. 

Notice, in our current [non-clustered environment](NONCLUSTERED.md), we only have one VM representing Locust. We will soon change this, delegating one controller node as what Locust calls [the "master node"](https://docs.locust.io/en/stable/running-distributed.html) and the majority of the work spread out amongst what Locust calls ["worker" nodes](https://docs.locust.io/en/stable/running-distributed.html). 

In order to do this, we will need to clone the current state of our current Locust node. 

### Duplicating Locust VMs

#### Some Minor Time-Saving Details

Of course, first, we will want to create an image of our current machine state of Locust. *However*, in order to save time later, it's better to address (a) hanging docker issues (see [non-clustered.md](NONCLUSTERED.md)) and (b) ensuring the docker image you will be using is already cached (so you don't have to build it from scratch every time). 

*(We will proceed with the assumption that you have already gotten your non-clustered environment up and running.)*

In order to solve the hanging docker issues, SSH into the Locust VM and copy and paste these commands:

(Down your `Locust` VM, if you haven't already, with `sudo docker-compose -f docker-compose.yml down -v`)

```
sudo pkill -9 -f docker
sudo systemctl disable docker docker.socket
sudo rm -rf /var/lib/docker
sudo systemctl start docker
# If needed: sudo systemctl restart docker
```

From here, we'll want to build our image (but not up it). More specifically, since we'll be upping images for our worker VMs, we'll want to build it via
```
sudo docker-compose -f worker.docker-compose.yml build
````

After this is done building, we can clone this VM.

#### AMI - Amazon Machine Image

In order to copy our current *working* state of our Locust worker, we will want to create an Amazon Machine Image (AMI) of it to use within our future auto scaling group. 

Log in to AWS. After logging in, press the menu bar dropdown on the left-hand side. Head to `Instances > Instances`. Click on the `Instance ID` of your Locust VM. Then, in the top dropdown menu, click on `Actions > Image and templates > Create image`. 

This should open up a new window, asking you to create an Amazon Machine Image from this Locust VM. For the image ID, enter something conveying that this will be your `Locust Worker AMI`. If desired, put in a helpful description. Under `Tags`, if you would like, add the tag with the `Key` of `type` and with the `Value` of `Perf` (this is for filtering resources VMs later on, if you would like). Click on `Create image`. 

After pressing `Create image`, you will likely get a green notification saying: 

*Currently creating AMI ami-some-string from instance i-some-other-string. Check that the AMI status is 'Available' before deleting the instance or carrying out other actions related to this AMI.*

It might now take a few moments to create this machine image. 

*(This would be a good time to also create a machine image [that you will need later] for your [ACA-Py agent](###Abstracting-Away-ACA-Py-Agents). (See below). Once you are done creating this second image, this first image may be done (or, at least, closer to being done).)*

#### Instantiating Worker Node

Now, we'll want to launch our worker node. Click on the orange `Launch Instances > Launch Instances`. This will send you the page in order to be able to create a VM. 

##### Names and tags

Give this first VM an appropriate name. We will go in order as above and, thus, give this first VM the very creative name of `Worker Locust VM`. 

##### Application and OS Images (Amazon Machine Image)

Under `Application and OS Images (Amazon Machine Image)`, navigate to the `My AMIs` section. If it's not selected already, select `Owned by me`. Under the `Amazon Machine Image (AMI)` dropdown, select the AMI you created above (for the Locust VM). Recall, we called ours `Locust Worker AMI`.  

##### Instance type

Under `Instance Type`, click on the box below `Instance Type` (it should be set to `t2.micro` by default). Choose the one that best suits your needs. Since these workers will need quite a bit of resources to spin up users, it's recommended not to choose something small (we'll be going with `t3.large` or `t3.xlarge` to get things working here).

##### Key pair (login)

Click on the box under `Key pair name` navigate to the key pair you have previously created for this project. For us, since our previously extremly creative name of our key pair was `performance`, we'll click on this. 

##### Network Settings

1. Under `Firewall (security groups)`, click the `Select existing security group` box. 
2. Click on the box under `Common security groups`. Select the previous security group you created for this project (in our case, `performance-testing`). 

*(For this worker Locust VM, since we are essentially "copying" the settings we gave our original Locust VM, your disk size settings should have been saved from the original VM. There should be nothing to change for this part. (If you haven't changed this already though, it would be surprising if you haven't already run into errors...))*

##### Launch instance

Finally, scroll to the bottom of the page and press the orange `Launch instance button`. 

#### Launching Master and Worker Nodes

Once your new worker Locust VM spins up, SSH into both the `master` and `worker` VMs. Within both of these VMs, enter `cd aries-akrida/` and then `vim .env`.  

For both of these VMs, replace the `AGENT_IP` variable, within both `.env`s with the external IP of your `worker` [or new] Locust VM (for both of these VMs). Save and quit by doing `:wq`. 

With this, we should be good to up everything. 

##### Upping Everything

In the `master` VM, run

```
sudo docker-compose down -v

# If needed: sudo systemctl restart docker
# Then try again

sudo docker-compose -f master.docker-compose.yml build
sudo docker-compose -f master.docker-compose.yml up -d
```

Then, in the `worker` VM, enter

```
sudo docker-compose down -v # likely unnecessary

# If needed: sudo systemctl restart docker
# Then try again

sudo docker-compose -f worker.docker-compose.yml build
sudo docker-compose -f worker.docker-compose.yml up -d
```

Once everything spins up, the Locust browser will be available on `http://{EXTERNAL_IP_OF_LOCUST_MASTER_VM}:8089`. However, before we can execute the tests, we'll need to take care of some firewall rules. 


##### Firewall Rules

For now, as before, add these firewall rules

1. Allow the worker node to be able to access Locust (`8089-8090`)
    * Type: `Custom TCP`
    * Port Range: `8089-8090`
    * Source: `Custom`
        * `Worker Locust Exteral IP` / 32
    * Description: `Worker can access Locust`
2. Allow the worker node to be able to access ACA-Py (`8150-8151`)
    * Type: `Custom TCP`
    * Port Range: `8150-8151`
    * Source: `Custom`
        * `Worker Locust Exteral IP` / 32
    * Description: `Worker can access ACA-Py `

After adding these firewall rules, we should be good to go to run one of the tests. Since these steps required your non-clustered enviroment working before spinning up the worker node, please see our [checklist](CHECKLIST.md) if you missed something there (likely, updating firewall rules). Otherwise, for additional help, please see our [debugging section](DEBUGGING.md). 

### Abstracting Away ACA-Py Agents

Next we will begin abstracting away each of our components, so that we can scale up our environment. We will begin by putting more abstract versions of our ACA-Py agents into an auto scaling group, behind a load balancer. 

#### AMI - Amazon Machine Image

In order to copy our current *working* state of our ACA-Py Agent, we will want to create an Amazon Machine Image (AMI) of it to use within our future auto scaling group. 

Log in to AWS. After logging in, press the menu bar dropdown on the left-hand side. Head to `Instances > Instances`. Click on the `Instance ID` of your ACA-Py Agent VM. In the top dropdown menus, click on `Actions > Image and templates > Create image`. 

This should open up a new window, asking you to create an Amazon Machine Image from this Locust VM. For the image ID, enter something conveying that this will be your `ACA-Py Agent VM`. If desired, put in a helpful description. Under `Tags`, if you would like, add the tag with the `Key` of `type` and with the `Value` of `Perf` (this is for filtering resources VMs later on, if you would like). Click on `Create image`. 

After pressing `Create image`, you will likely get a green notification saying: 

*Currently creating AMI ami-some-string from instance i-some-other-string. Check that the AMI status is 'Available' before deleting the instance or carrying out other actions related to this AMI.*

It might now take a few moments to create this machine image. 

#### Launch Template

After creating the AMI of the ACA-Py instances, we will now create a launch template to tell our auto scaling group how we would like to create and handle our instances. 

In order to create a launch template, press the menu bar dropdown on the left-hand side. Head to `Instances > Launch Templates`. Once AWS have navigated you to the`Launch Templates` page, press the orange `Create launch template button`. 

Give your ACA-Py launch template a meaningful name (consider, for example, `ACAPyAgent`). Put in a meaningful description as well. 

Under the box titled `Application and OS Images (Amazon Machine Image)`, click on the tab `My AMIs`, and then click on the select option `Owned by me`. From here, you should be able to click the drop down (below `Amazon Machine Image (AMI)`) and select the Amazon Machine Image that you created in the previous step. 

Under the box titled `Instance type`, choose a `c7i.large` (or `c6i.large` or `t3.small`), as designated by our cost savings sheet (or whatever works best for you). 

Under the box titled `Key pair (login)`, click on the dropbox under `Key pair name`. Select the key pair you've been using throughout this project. 

Under the box titled `Network settings`, under `Firewall (security groups)`, click `Select existing security group`. Click the dropdown box under `Security groups` and select the security group you've been working with throughout this project. 

Under the box titled `Advanced details`, click on the arrow next to the text (`Advanced Details`). Clicking this arrow should open up this box. Scroll down to the bottom, until you reach `User data - optional`. Within this box, paste in the below start up script, pasting in the relevant values from below from your current `.env` of your already existing ACA-Py agent. It is okay to leave the `ISSUER` variable empty for now (we will want to change this later). 

Start up script:

```
#!/bin/bash
sudo pkill -9 -f docker
sudo systemctl disable docker docker.socket
sudo rm -rf /var/lib/docker
sudo systemctl start docker
sudo systemctl restart docker

cd /home/ubuntu
cat << EOF > .env
# (Transport load balancer)
ISSUER= # Leave this blank for now
ACAPY_ADMIN_API_KEY=# Your API Key from earlier (.env)
DATABASE=# Internal IP of DATABASE from earlier (.env)
EXPOSED_PORT=80 # 8151 non-clustered; 80 clustered
ACAPY_GENESIS_URL=# Genesis URL from earlier (.env)
ACCOUNT=# Your ACCOUNT from earlier (.env)
PASSWORD=# Your PASSWORD from earlier (.env)
ADMIN_ACCOUNT=# Your password from earlier (.env)
ADMIN_PASSWORD=# Your password from earlier (.env)
EOF
sudo docker-compose build
sudo docker-compose up -d
```

After copying, pasting, and modifying this start up script into the `User data - optional` field, click on the orange `Create launch template` button. 

From here, we can start building out our two load balancers.

## Load Balancer

Now, we'll want to create a load balancer both for the frontend of ACA-Py (the admin UI) as well as the backend. We'll start with creating the front end.

In order to create a launch template, press the menu bar dropdown on the left-hand side. Head to `Load Balancing > Load Balancers`. Click on the orange `Create load balancer` button. 
 
AWS should then ask you which type of load balancer you would like to create. Please press the `Create` button under `Application Load Balancer`. 

### ACA-Py Frontend

From here, give the load balancer a unique, meaningful name. We went with `acapy-admin-lb`. Make sure the `Scheme` is `Internet-facing` and the `IP address type` is `IPv4`. 

Under the box `Network mapping`, choose the zones you would like this load balancer to balance traffic between. We selected all of them for wider availability. In the case of load testing, choosing more focused zones is probably recommended; on the other hand, by choosing more focused zones, it is very likely that AWS may in the future impose certain quotas for machine types or other limitations. 

Under the box `Security groups`, select the dropdown and choose the security group you've been working with throughout this project. 

Under `Listeners and routing`, under `Default action`, there should be a `Select a target group` dropdown. Instead of selecting a target group, press on the blue `Create target group`. 

#### (Frontend) Target Group

For the following portions, if an option is not specified, assume the default version given to you by AWS. 
* Under `Choose a target type`, choose `Instances`. 
* Under `Target group name`, give the target group a meaningful name. We went with `Performance-ACAPy-Admin`. 
* Under `Protocol: Port`, select `HTTP` for the left dropdown box and `8150` for the port (the right input box). Recall, the port `8150` was the one used to access the ACA-Py Admin UI. 
* Under `IP Address Type`, select `IPv4`.
* Under the box `Health checks`, select `HTTP` for the `Health check protocol`. 
* Under `Health check path`, type in `/status/live`. This is the endpoint that will be curled, by AWS, to ensure that our ACA-Py instances are "healthy".
* Under `Advanced health check settings` (these are more recommendations than strict guidelines), 
    * set the `healthy threshold` to `2` successes,
    * set the `unhealthy threshold` to `2` failures,
    * set the `timeout` to `10` seconds,
    * set the `interval` to `12` seconds,
    * and set the `Success codes` to `200`. 
* Under `Tags - optional`, if you would like, add the tag with the `Key` of `type` and with the `Value` of `Perf` (this is for filtering running VMs later on, if you would like). 

After all of this has been entered, you should be good to go and press the orange `Next` button. 

AWS should then take you to the next page, something with the title `Register targets`. Skip past all of this and press the orange `Create target group` button. 

If all was successful, AWS should then say that the target group was successfully created. 

### ACA-Py Frontend (cont.) 

Return to the load balancer tab, where we were creating the load balancer for the frontend for ACA-Py. Now, under that same `Select a target group` dropdown that we were looking at earlier, press the refresh button to the right of this box. Then, try clicking this same dropdown again, and click the target group (for the frontend) that you just created. Under `Port` (to the left of the dropdown box), type in `8080`.

(Optional) Under `Load balancer tags`, if you would like, add the tag with the `Key` of `type` and with the `Value` of `Perf`. 

Scroll down to the bottom and click the orange `Create load balancer` button. 

Now we'll create our second load balancer for the backend for ACA-Py. 

### ACA-Py Backend

For the backend load balancer, follow all of the steps from [above](##Load-Balancer). 

Create another target group, but this time for the backend. Set the port to `8151` this time. Set the `Health check path` to just `/`. 

When returning back to the load balancer for the backend (after creating the target group), make sure to set the `Listerners and routing` `Port` to `80`. 

Then, create the load balancer. 

Now we'll want to create our auto scaling groups that now point to the DNS names given to these load balancers. 

## Auto Scaling Group

In order to create an auto scaling group for the ACA-Py VMs, press the menu bar dropdown on the left-hand side. Head to `Auto Scaling > Auto Scaling Groups`. Click on the orange `Create Auto Scaling group` button. 

Under `Auto Scaling group name`, give this auto scaling group an appropriate name. We used `Performance - ACA-Py Instances`. 

Under `Launch Template`, click the dropdown and select the launch template you created from before. Click the orange `Next` button. 

AWS should then take you to a page titled `Choose instance launch options`. Under the `Network` box, choose the same `Availability Zones and subnets` as you did when creating the load balancers. Click the orange `Next` button. 

AWS should then take you to a page titled `Configure advanced options - optional`. 

Under the box titled `Load balancing`, select `Attach to an existing load balancer`. 

Under `Existing load balancer target groups`, click the dropdown and select ***both*** the frontend *target group* and backend *target group* that you created in the previous steps. 

Under `Health checks > Additional health check types - optional`, select `Turn on Elastic Load Balancing health checks`. 

Under `Additional settings > Monitoring`, select `Enable group metrics collection within CloudWatch`. Under `Default instance warmup`, select `Enable default instance warmup`, and set the default to `300` seconds. Click the orange `Next` button.

From here, AWS should take you to a page titled `Configure group size and scaling - optional`. 

Since we have yet to update our launch template with the DNS name of our issuer, let us currently set the `Desired capacity` to `0` (we will change this later). 

Under the box titled `Scaling`, also set the `Min desired capacity` to `0`. 

Under `Automatic scaling - optional`, choose your preference of scaling (either automatic (`Target tracking scaling policy`) or manual (`No scaling policies`)). For the sake of this work, we will be scaling our instances manually, so we will select `No scaling policies`; however, it is generally recommended to do `Target tracking scaling policy`, especially if you do not know how many ACA-Py instances you will need. (The only word of caution is that this might be potentially problematic if, say, AWS spins up ACA-Py agents and accidentally directs traffics to these VMs [agents] before they are ready and are not quite up and ready to go yet.). 

Under the box titled `Instance maintenance policy - new`, choose a replacement behavior that best meets your needs. For cost saving purposes, we will choose `Terminate and launch`. 

After selecting the above option, click the orange `Next` button. 

At this point, if you would like, you can add notifications, from AWS, based on scaling changes. Otherwise, click the orange `Next` button.

Next, if you would like, you can associate a tag to this auto scaling group. As before, we will add the tag with the `Key` of `type` and with the `Value` of `Perf` (we will also choose to select to `Tag new instances` with this tag). Click on the orange `Next` button.

AWS will then take you to a page to review all of your changes. Review all of these. Once you are confident everything is correct, click the orange `Create auto scaling group` button. 

### Connecting All the Pieces

#### Grab Load Balancer DNS Name

Press the menu bar dropdown on the left-hand side. Head to `Load Balancing > Load Balancers`. Look for your ACA-Py backend / transport load balancer. Select it by clicking on its name. 

From here, copy the DNS name of this backend load balancer by copying the DNS name under `DNS name` (either highlight and copy or press the squares copy button).

#### Point ACA-Py Agents to the Load Balancer

From here, let's put this DNS name into action. Let us return to our launch templates. Recall, to get launch templates, press the menu bar dropdown on the left-hand side. Head to `Instances > Launch Templates`. Once AWS have navigated you to the`Launch Templates` page, look for the launch template you created for your ACA-Py instance. Click on the respective `Launch Template ID` for that launch template.

*(Note: This section is also useful to review if you've made any mistakes in your launch template. This would be the methodology to use if you want to fix any mistakes or add anything new to the launch template and then launch those instances with the new fixes.)*

Once the launch template opens up, click on the `Actions` dropdown in the top right. Click `Modify template (Create new version)`. 

Once the launch template opens up in the editing menu, scroll all the way down to the box labeled `Advanced Details`. Scroll down to the `User data - optional` input field. 

Put the DNS name of the backend / transport load balancer you copied in the previous step in as the `ISSUER` variable (under where it says `# transport load balancer`). After putting this in, press the orange `Create template version`. 

So we've saved our changes to AWS, where this launch template is now pointing to this backend DNS name, but now we need to tell AWS to use this updated version (rather than our first version). 

Head back to the launch templates (if you're not there already). You can get back here by pressing the menu bar dropdown on the left-hand side and heading to `Instances > Launch Templates`. Click on the `Launch Template ID` of your ACA-Py launch template. From there, click on the `Actions` dropdown and select `Set default version`.

Once the box `Set default version` comes up, under `Template version` select the highest number that comes up under this dropdown (this will correspond with the most recent changes). For example, if you've only made this one change, then likely `2` will be the highest number here. After selecting the highest number, press the orange `Set as default version` button. 

*(This concludes the section on how to make and propagate changes to your launch template.)*

Then, if we head back to our auto scaling group (`Auto Scaling > Auto Scaling Groups`, pressing on the respective name of the ACA-Py auto scaling group, we can head to the box titled `Group details`, press the `Edit` button, and change the `Desired capacity` to `1` and the `Min desired capacity` to `1`. Press the orange `Update` button.

Amazing! This auto scaling group will soon spin up ACA-Py agent VMs matching our launch template shortly. 

Before we can access the admin UI though, to ensure things are working, we need to allow (a) ourselves access to these VMs as well as (b) our Locust components. 

## ACA-Py Firewall Rules

For this portion, for the sake of cleanliness, we recommend creating a new security group, specifically for your load balancers. 

Navigate to the security group section of AWS, by pressing the menu bar dropdown on the left-hand side and heading to `Network & Security > Security Groups`. Click on the orange button `Create security group`. 

### Creating Load Balancer Security Group

Give the security group an appropriate name, for example `Performance-ACA-Py-Load-Balancer-Security-Group`. 

For the `Description` (required by AWS), put something appropriate, like `Security group for ACA-Py Load Balancers (Frontend and Backend)`. 

Under `Inbound rules`, add the following `Inbound rules`: 
1. Allow yourself access to the ACA-Py frontend load balancer (`8080`)
    * Type: `Custom TCP`
    * Port Range: `8080`
    * Source: `My IP`
    * Description: `Front - I can access ACA-Py admin LB (8080)`
2. Allow yourself access to the ACA-Py backend load balancer (`80`)
    * Type: `Custom TCP`
    * Port Range: `80`
    * Source: `My IP`
    * Description: `Back - I can access ACA-Py transport LB (80)`
3. Allow everyone *(AKA external facing portion of the performance testing security group)* access to the ACA-Py Admin UI (`8080`)
*(Notice, the firewall rules are necessary to communicate with ACA-Py over the internet; thus, we are protecting ACA-Py with our API Key. If AWS had an externally-facing persistent IP we could attach to an inbound rule, we would. However, we do not know of a way to do this at this time. If there is another way to create this firewall rule (handling the dynamic external IPs of the ACA-Py VMs behind the auto scaling group and load balancer), please let us know by submitting an issue or PR to this repo.)*
    * Type: `Custom TCP`
    * Port Range: `8080`
    * Source: `Anywhere-IPv4`
        * `0.0.0.0/0`
    * Description: `All can access ACA-Py on 8080` 
4. Allow everyone access to ACA-Py transport (`80`)
*(Notice, the firewall rules are necessary, and we are protecting ACA-Py with our API Key. However, if there is another way to create this firewall rule (handling the dynamic external IPs of the ACA-Py VMs behind the auto scaling group and load balancer), please let us know by submitting an issue or PR to this repo.)*
    * Type: `Custom TCP`
    * Port Range: `80`
    * Source: `Anywhere-IPv4`
        * `0.0.0.0/0`
    * Description: `All can access ACA-Py on 80` 

Under `Tags - optional`, if you would like, add the tag with the `Key` of `type` and with the `Value` of `Perf`.

Click on the orange `Create security group` button.

After creating this security group, we'll want to go reflect this within our newly created load balancers. You can get to load balancers by pressing the menu dropdown on the left-hand side and heading to `Load Balancing > Load Balancers`. Click on the name of the frontend or admin load balancer. Press the `Actions` dropdown button and select `Edit security groups`. 

Under `Security groups`, select the dropdown and select the newly created security group you just created for our load balancers. (Recall, we called ours `Performance-ACA-Py-Load-Balancer-Security-Group`). Ensure, then, that this load balancer is a part of both (a) your original performance testing security group that you created (for the non-clustered portion of this project) as well as (b) this newly created security group. Click on the orange `Save changes` button.

**Repeat the above steps for the transport load balancer, using the aforementioned security group.**

### Firewall Rules for Performance Testing Security Group

Before modifying firewall rules to your original (most used) performance testing group, we'll need some information: namely, what format the internal IPs of your VMs take. For this, we'll need to gather this information from your (a) pre-existing VMs and (b) VMs you just created behind your auto scaling group

#### Information Gathering

##### Pre-existing VMs

To gather the internal or private IP of the VMs within your non-clustered environment, press the menu bar dropdown on the left-hand side and head to `Instances > Instances`. Click on the Instance ID of one of the respective VMs you have been using for the non-clustered environment. Observe and take note of the first two blocks [first five digits] of the respective internal IP address. So, for example, if the internal IP is `172.31.12.123`, take note of the `172.31` portion. 

##### VMs Behind Auto Scaling Group

To gather the internal or private IP of the VMs within your auto scaling group, press the menu bar dropdown on the left-hand side and head to `Auto Scaling > Auto Scaling Groups`. Click on the respective name of the auto scaling group for your ACA-Py instances. On the top, click on the tab titled `Instanced management` (to the right of `Details` by a couple of tabs). From there, click on the respective ID of any of the VMs that are up within this group. Observe its private IP address again and take note of it. So, for example, if the internal IP is `172.32.12.123`, take note of the `172.32` portion. 

#### Firewall Rules

Return to AWS' security group page by pressing the menu bar dropdown on the left-hand side and heading to `Network & Security > Security Groups`. Click on the respective `Security group ID` of the performance testing group you have been using (for the non-clustered portion). 

Under `Inbound Rules`, click on the box `Edit Inbound Rules`. Add the following inbound rules:

1. Allow internal traffic for the holder database (`5432`)
    * Type: `Custom TCP`
    * Port Range: `5432`
    * Source: `Custom`
        * `172.31.0.0/16, 172.32.0.0/16`
            * *This portion will be of the forms of the internal IPs you recorded, where, for example the first `172.31.0.0/16` can be replaced with the respective two first bits you recorded and the second `172.31.0.0/16` can be replaced with the respective two second bits you recorded.*
    * Description: `Internal traffic can access the holder database`
2. Allow internal traffic to access the redis-host (database) (`6379`)
    * Type: `Custom TCP`
    * Port Range: `6379`
    * Source: `Custom`
        * `172.31.0.0/16, 172.32.0.0/16`
            * *Same as above.*
    * Description: `Internal traffic can access the redis host (database)`
3. (Own mediator) Allow internal traffic to access mediator on cloud (`3000`)
    * Type: `Custom TCP`
    * Port Range: `3000`
    * Source: `Custom`
        * `172.31.0.0/16, 172.32.0.0/16`
            * Same as above.
    * Description: `Internal traffic can access mediator on cloud (here)`
4. (Revocation) Allow internal traffic to access tails server (`6543`)
    * Type: `Custom TCP`
    * Port Range: `6543`
    * Source: `Custom`
        * `172.31.0.0/16, 172.32.0.0/16`
            * *Same as above.*
    * Description: `Internal traffic can access the tails server, makes revocation possible`
5. Allow the ACA-Py Admin LB access to the performance security group on `8150`
    * Type: `Custom TCP`
    * Port Range: `8150`
    * Source: `Custom`
        * *ACA-Py Load Balancer Security Group*
    * Description: `Front - Admin LB can access performance SG on 8150`
6. Allow the ACA-Py Transport LB access to the performance security group on `8151`
    * Type: `Custom TCP`
    * Port Range: `8151`
    * Source: `Custom`
        * *ACA-Py Load Balancer Security Group*
    * Description: `Back - Transport LB can access performance SG on 8151`

Press the orange `Save rules` button.

#### Verifying We Can Access ACA-Py Via the Browser

We'll want to see now if we've successfully done everything. In order to test this, we'll want to test whether or not we can access ACA-Py via the admin UI. 

In order to do this, we'll need the DNS name from our load balancer. To grab this again, press the menu dropdown on the left-hand side and head to `Load Balancing > Load Balancers`. Click on the name of the ACA-Py frontend / ACA-Py admin UI load balancer. Copy the `DNS name` again, as from before. Suppose, for example, this `DNS name` is `acapy-admin-lb.amazonaws.com` (although, yours will come with some specific information after it). Paste this into the browser, and then tack on `:8080/api/doc`. So, for example, if we use our example from above, it would look like we are accessing the link `acapy-admin-lb.amazonaws.com:8080/api/doc`. 

If you're able to access this page, congrats! You've done it! You should now be able to authenticate yourself (just to double-check) in the browser. Since, from before, you should have already anchored your DID, schema, and credential definition from before, this information should be stored in your database VM (so you shouldn't have to do these steps over again). 

However, to ensure that you are only using the ACA-Py VMs from your auto scaling group, we'll want to shut off that single remaining ACA-Py Agent VM. 

##### Spin Down Single ACA-Py Issuer VM

To be fully dependent on the ACA-Py VMs behind the auto scaling group, we'll want to delete or shut down the last standalone ACA-Py VM.

Press the menu bar dropdown on the left-hand side and head to `Instances > Instances`. Click on the respective checkmark box next to your stand alone ACA-Py Agent VM. Click the dropdown `Instance state`, and press (your choice) either `Stop instance` (to spin down) or `Terminate instance` (to delete entirely (recall, you have the launch template, so it shouldn't be that difficult to respin up a separate instance if you would like)). 

Now we should be fully dependent on our ACA-Py instances behind the load balancers and auto scaling group!

##### Verifying Everything Works

Now, before we go pasting our new `ISSUER_URL` into the environment of our Locust master and worker nodes, let's make sure our ACA-Py agent is set up properly. The below section will introduce a useful "sanity check" to ensure your ACA-Py Agent is up and running as it should.

###### Sanity Check

1. **Head to the ACA-Py Admin UI** 
    This is `acapy-admin-lb.amazonaws.com:8080/api/doc` in this instance.
2. **Create a connection invitation.**
To form a connection, head to your admin API. Authorize yourself if needed. Then, head down to the sections `connections` and head to the post method `/connections/create-invitation`. Click on the box `Try it out` and, within the body, modify the input box such that
```
{
    metadata: {}
}
```
is the only thing within the box. Click on the blue `Execute` button. Within the (top) response box, copy the **`invitation_url`**. 
3. **Create a connection invitation.** 
* Does the beginning of the invitation look correct? 
    * (Non-Clustered) Does it match the external IP of ACA-Py? Or 
    * (Clustered) Does it match the transport (backend) DNS name?
* Does the end port look correct? 
    * (Non-Clustered) Does it end in `8151`? 
    * (Clustered) Does it end in `80`?
5. Access the `invitation_url` via the browser.
    a. *Do you get an invitation?* *Can you access it?* If not, investigate firewall rules.
    b. If clustering, check load balancer target group and port mapping settings.
    
If you're able to access all of these steps with ease, you should be all good to move on. Go to your `master` and `worker` agent VMs. Verify all of the `.env` information is up to date, as above, and that the `ISSUER_URL` now successfully points to your ACA-Py Admin UI. With our example from before, this would take the form of 
```
ISSUER_URL=http://acapy-admin-lb.amazonaws.com:8080
```
for us. (Don't forget to update `ISSUER_HEADER`, with the API Key, if you haven't already. This shouldn't change though, if you have done it already.)

After ensuring all of the remaining environment variables are correct (for *both* the `master` and `worker` VM) (`MASTER_HOST`, `AGENT_IP`, `SCHEMA`, `CRED_DEF`, `ISSUER_HEADER`, and `LOCUST_FILES`), go ahead and down, build, and up everything. Within the `master` VM, 

```
sudo docker-compose -f master.docker-compose.yml down -v
sudo docker-compose -f master.docker-compose.yml build 
sudo docker-compose -f master.docker-compose.yml up -d
```

Do the same thing with the `worker` VM, except replacing `master.docker-compose.yml` with `worker.docker-compose.yml`.

If the `master` VM throws an error about (a) (1) docker not being up or (2) docker is not responsive at all (you are not seing any output), try our "hanging" docker commands from before:

```
sudo pkill -9 -f docker
sudo systemctl disable docker docker.socket 
sudo rm -rf /var/lib/docker
sudo systemctl start docker
# If needed: sudo systemctl restart docker
```

Additionally, if within the failures of Locust (after running the test), it appears that Locust is grabbing the wrong `ISSUER_URL`, try downing, building, and upping again, but, for the build command, use
```
sudo docker-compose -f master.docker-compose.yml build --no-cache
```
for the `master` VM, and the analogous command for the `worker` VM by replacing `master.docker-compose.yml` with `worker.docker-compose.yml`. 

For any other problems, please message us or see our [DEBUGGING.md](DEBUGGING.md). 

If you do run into trouble, it is recommended to (a) SSH into one of the ACA-Py Agents behind the auto scaling group and then (b) run `sudo docker-compose logs`. This will give you logs to sift through to try and determine what the problem might be. 

At this point, once you get things working, this would be a great place to take a break and step away for a bit, before tackling the next load balancer!

## Locust Workers

Now that we've abstracted away one of our components (the ACA-Py agents), it's now time we abstract away our Locust workers!

### Launch Template

Recall, from the first part of this document, we used an Amazon Machine Image to copy the state of our Locust `master` in order to launch our Locust `worker`. We will now use this Amazon Machine Image in order to create a launch template for the Locust worker. 

In order to create a launch template, press the menu bar dropdown on the left-hand side. Head to `Instances > Launch Templates`. Once AWS have navigated you to the`Launch Templates` page, press the orange `Create launch template button`. 

Give your Locust worker launch template a meaningful name (consider, for example, `LocustWorker`). Put in a meaningful description as well. 

Under the box titled `Application and OS Images (Amazon Machine Image)`, click on the tab `My AMIs`, and then click on the select option `Owned by me`. From here, you should be able to click the drop down (below `Amazon Machine Image (AMI)`) and select the Amazon Machine Image that you created for the Locust worker. 

Under the box titled `Instance type`, choose a `t3.xlarge`. (We will want something large, as we'll need resources in order to spin up resources.)

Under the box titled `Key pair (login)`, click on the dropdown under `Key pair name`. Select the key pair you've been using throughout this project. 

Under the box titled `Network settings`, under `Firewall (security groups)`, click `Select existing security group`. Click the dropdown box under `Security groups` and select the security group you've been working with throughout this project. 

Under the box titled `Advanced details`, click on the arrow next to the text (`Advanced Details`) to open up this box. Scroll down to the bottom, until you reach `User data - optional`. Within this box, paste in the below start up script, pasting in the relevant values from below from your current `.env` of your already existing Locust `worker` VM.

Start up script:

```
#!/bin/bash
sudo pkill -9 -f docker
sudo systemctl disable docker docker.socket 
sudo rm -rf /var/lib/docker
sudo systemctl start docker

cd /home/ubuntu/aries-akrida
cat << EOF > .env
# Copy the below variables from your currently up
# and running Locust worker VM
MEDIATION_URL= # In .env
MASTER_HOST= # INTERNAL IP of Locust Master VM
MASTER_PORT=8089

# Period an agent will wait before running another ping
LOCUST_MIN_WAIT=1
LOCUST_MAX_WAIT=10
ISSUER_URL= # In .env (should point to load balancer (:8080))

# Update the X-API-Key with your ACAPY_ADMIN_API_KEY from your ACA-Py Agent VM
ISSUER_HEADERS={"Authorization":"Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ3YWxsZXRfaWQiOiIwOWY5ZDAwNC02OTM0LTQyZDYtOGI4NC1jZTY4YmViYzRjYTUiLCJpYXQiOjE2NzY4NDExMTB9.pDQPjiYEAoDJf3044zbsHrSjijgS-yC8t-9ZiuC08x8","X-API-Key": "Insert ACAPY_ADMIN_API_KEY Here"}

CRED_DEF= # In .env (have to update each time)
LEDGER=indicio
SCHEMA= # In .env (have to update each time)
CRED_ATTR='[{"mime-type": "text/plain","name": "score","value":"test"}]'
VERIFIED_TIMEOUT_SECONDS=20
WITH_MEDIATION=True

# LEDGER=candy
LOCUST_FILES=locustMediatorPresentProofExisting.py
# Increase the END_PORT if you want to run a lot of agents in parallel
START_PORT=10000
END_PORT=10500

MESSAGE_TO_SEND="Lorem ipsum dolor sit amet consectetur, adipiscing elit nisi aptent rutrum varius, class non nullam etiam. Ac purus donec morbi litora vivamus nec semper suscipit vehicula, aliquet parturient leo mollis in mauris quis nisi tincidunt, sociis accumsan senectus pellentesque erat cras sociosqu phasellus augue, posuere ligula scelerisque tempus dapibus enim torquent facilisi. Imperdiet gravida justo conubia congue senectus porta vivamus netus rhoncus nec, mauris tristique semper feugiat natoque nunc nibh montes dapibus proin, egestas luctus sollicitudin maecenas malesuada pharetra eleifend nam ultrices. Iaculis fringilla penatibus dictumst varius enim elementum justo senectus, pretium mauris cum vel tempor gravida lacinia auctor a, cursus sed euismod scelerisque vivamus netus aenean. Montes iaculis dui platea blandit mattis nec urna, diam ridiculus augue tellus vivamus justo nulla, auctor hendrerit aenean arcu venenatis tristique feugiat, odio pellentesque purus nascetur netus fringilla. S."

EOF

# Grabs einternal IP of particular VM, puts in .env
export TOKEN=`curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600"`
export INTERNAL_IP=`curl -H "X-aws-ec2-metadata-token: $TOKEN" -v http://169.254.169.254/latest/meta-data/local-ipv4`
echo "AGENT_IP=${INTERNAL_IP}" >> .env

sudo docker-compose down -v && sudo docker-compose -f worker.docker-compose.yml build && sudo docker-compose -f worker.docker-compose.yml up -d
```

After copying, pasting, and modifying this start up script into the `User data - optional` field, click on the orange `Create launch template` button. 

#### 

*(Note above that we have now changed the `MASTER_HOST` to point internally rather than externally.)*

From here, we can start building out our load balancer.

### Worker Load Balancer

In order to create a load balancer, press the menu bar dropdown on the left-hand side. Head to `Load Balancing > Load Balancers`. Click on the orange `Create load balancer` button. 
 
AWS should then ask you which type of load balancer you would like to create. Please press the `Create` button under `Application Load Balancer`. 

From here, give the load balancer a unique, meaningful name. We went with `locust-worker-lb`. Make sure the `Scheme` is `Internet-facing` and the `IP address type` is `IPv4`. 

Under the box `Network mapping`, choose the zones you would like this load balancer to balance traffic between. We selected all of them for wider availability. In the case of load testing, choosing more focused zones is probably recommended; on the other hand, by choosing more focused zones, it is very likely that AWS may in the future impose certain quotas for machine types or other limitations. 

Under the box `Security groups`, select the dropdown and choose the security group you've been working with throughout this project. Also choose the security group you recently just created for the ACA-Py load balancers.

Under `Listeners and routing`, under `Default action`, there should be a `Select a target group` dropdown. Press on blue text `Create target group`. 

#### Locust Worker Target Group

For the following portions, if an option is not specified, assume the default version given to you by AWS. 
* Under `Choose a target type`, choose `Instances`. 
* Under `Target group name`, give the target group a meaningful name. We went with `Performance-Locust-Workers`. 
* Under `Protocol: Port`, select `HTTP` for the left dropdown box and `8089` for the port (the right input box). 
* Under `IP Address Type`, select `IPv4`.
* Under the box `Health checks`, select `HTTP` for the `Health check protocol`. 
* Under `Health check path`, type in `/`. 
* Under `Advanced health check settings` (these are more recommendations than strict guidelines), 
    * set the `healthy threshold` to `2` successes,
    * set the `unhealthy threshold` to `2` failures,
    * set the `timeout` to `10` seconds,
    * set the `interval` to `12` seconds,
    * and set the `Success codes` to `200`. 
* Under `Tags - optional`, if you would like, add the tag with the `Key` of `type` and with the `Value` of Perf` (this is for filtering running VMs later on, if you would like). 

After all of this has been entered, press the orange `Next` button. 

AWS should then take you to the next page, something with the title `Register targets`. Skip past all of this and press the orange `Create target group` button. 

If all was successful, AWS should then say that the target group was successfully created. 

### Worker Load Balancer (cont.)

Now return back to the load balancer tab, where we were creating the load balancer for the Locust workers. Under that same `Select a target group` dropdown that we were looking at earlier, press the refresh button to the right of this box. Then, try clicking this same dropdown again, and click the target group (for the frontend) that you just created. Under `Port` (to the left of the dropdown box), type in `8080`.

(Optional) Under `Load balancer tags`, if you would like, add the tag with the `Key` of `type` and with the `Value` of `Perf`. 

Scroll down to the bottom and click the orange `Create load balancer` button. 

Congrats! Now we have a load balancer for the Locust workers. Now we just need to back an auto scaling group behind it. 

### Worker Auto Scaling Group

In order to create an auto scaling group for the Locust `worker` VMs, press the menu bar dropdown on the left-hand side. Head to `Auto Scaling > Auto Scaling Groups`. Click on the orange `Create Auto Scaling group` button.  

Under `Auto Scaling group name`, give this auto scaling group an appropriate name. We used `Performance - Locust Workers`. 

Under `Launch Template`, click the dropdown and select the launch template you created from before. Click the orange `Next` button. 

AWS should then take you to a page titled `Choose instance launch options`. Under the `Network` box, choose the same `Availability Zones and subnets` as you did when creating the load balancers. Click the orange `Next` button. 

AWS should then take you to a page titled `Configure advanced options - optional`. 

Under the box titled `Load balancing`, select `Attach to an existing load balancer`. 

Under `Existing load balancer target groups`, click the below dropdown and select *both* the frontend load balancer and backend load balancer that you created in the previous steps. 

Under `Health checks > Additional health check types - optional`, select `Turn on Elastic Load Balancing health checks`. 

Under `Additional settings`, under `Monitoring`, select `Enable group metrics collection within CloudWatch`. Under `Default instance warmup`, select `Enable default instance warmup`, and set the default to `3600` seconds. Click the orange `Next` button. 

*(Yes. 3600 seconds. It's better to be generous with this auto scaling group, especially if you're doing the "hanging" docker commands, as it will have to build the images from scratch. Once you get everything up and running (and demonstrate that, in fact, you don't need these "hanging" docker commands for your image), then it is recommended to rude this time.)*

From here, AWS should take you to a page titled `Configure group size and scaling - optional`. 

Since we have yet to update our launch template with the DNS name of our issuer, let us currently set the `Desired capacity` to `0` (we will change this later). 

Under the box titled `Scaling`, also set the `Min desired capacity` to `0`. 

Under `Automatic scaling - optional`, choose your preference of scaling (either automatic (`Target tracking scaling policy`) or manual (`No scaling policies`)). For the sake of this work, we will be scaling our instances manually, so we will select `No scaling policies`; however, it is generally recommended to select `Target tracking scaling policy`, especially if you do not know how many Locust worker instances you will need. 

Under the box titled `Instance maintenance policy - new`, choose a replacement behavior that best meets your needs. For cost saving purposes, we will choose `Terminate and launch`. 

After selecting the above option, click the orange `Next` button. 

At this point, if you would like, you can add notifications from AWS, based on scaling changes. Otherwise, click the orange `Next` button.

Next, if you would like, you can associate a tag to this auto scaling group. As before, we will add the tag with the `Key` of `type` and with the `Value` of `Perf` (we will also choose to select to `Tag new instances` with this tag). Click on the orange `Next` button.

AWS will then take you to a page to review all of your changes. Review all of these. Then, once you are confident everything is correct, click the orange `Create auto scaling group` button. 

Now, let's connect our pieces together. 

### Connecting All the Pieces

##### Grab Locust Worker Load Balancer DNS Name

In order to be able to point our Locust `master` to our collection of Locust `workers`, we'll need to grab the DNS name from the Locust `worker` load balancer. 

Press the menu bar dropdown on the left-hand side. Head to `Load Balancing > Load Balancers`. Look for your Locust `worker` load balancer. Select it by clicking on its name. 

From here, copy the `DNS name` of this Locust `worker` load balancer by copying the DNS name under `DNS name` (either highlight and copy or press the squares copy button). For example, we'll assume ours takes the form of something like `locust-worker.amazonaws.com` (although, yours will probaby have some more specific information within here). 

Now, we'll want to use this within the Locust `master`.

##### Point Locust Master to the Locust Worker Load Balancer

SSH into your Locust `worker` VM and open up your `.env` file of the `aries-akrida` repo. 

Within this `.env` file, you'll want to change the `AGENT_IP` variable to point to this DNS name you just copied, such that
```
AGENT_IP=locust-worker.amazonaws.com
```
for example. Save by typing `:wq`. Of course, in order for this to take effect, you'll have to allow more inbound firewall rules. 

#### Firewall Rules

##### Load Balancer Security Group

Now we'll go and modify firewall rules to our new load balancer security group (the most recently created security group we created while constructing our ACA-Py load balancers). 

Return to AWS' security group page by pressing the menu bar dropdown on the left-hand side and heading to `Network & Security > Security Groups`. Click on the respective `Security group ID` for this load balancer security group. 

Under `Inbound Rules`, click on the box `Edit Inbound Rules`. Add the following inbound rules:

1. Allow the (old) performance testing security group to talk to Locust (`8089-8090`)
    * Type: `Custom TCP`
    * Port Range: `8089-8090`
    * Source: `Custom`
        * Performance Testing Security Group
    * Description: `Performance security group can talk to Locust (8089-8090)`

Press the orange `Save rules` button.

##### (Old) Performance Testing Security Group

Now we'll go and modify firewall rules to your original (most used) performance testing security group. Return to AWS' security group page by pressing the menu bar dropdown on the left-hand side and heading to `Network & Security > Security Groups`. Click on the respective `Security group ID` of the performance testing group you have been using (for the non-clustered portion). 

Under `Inbound Rules`, click on the box `Edit Inbound Rules`. Add the following inbound rules:

1. Allow all of the load balancers the ability to access Locust
    * Type: `Custom TCP`
    * Port Range: `8089-8090`
    * Source: `Custom`
        * ACA-Py Load Balancer Security Group
    * Description: `LBs can access Locust`

Press the orange `Save rules` button.

# Verification

##### Spin Down Single ACA-Py Issuer VM

Now, in order to be fully dependent on the Locust worker VMs behind the auto scaling group, we'll want to delete or shut down the last standalone Locust worker VM. 

Press the menu bar dropdown on the left-hand side and head to `Instances > Instances`. Click on the respective checkmark box next to your stand alone Locust `worker` VM. Click the dropdown `Instance state`, and press (your choice) either `Stop instance` (to spin down) or `Terminate instance` (to delete entirely (recall, you have the launch template, so it shouldn't be that difficult to respin up a separate instance if you would like)). 

Now we should be fully dependent on our Locust `worker` instances behind the load balancers and auto scaling group!

##### Verifying Everything Works

Now, everything should (hopefully) be all good to go. Once again, please double check all of your environment variables from before. 

First of all, since we set the VMs behind our auto scaling group to spin up 0, let's change this and spin up our first worker. 

As before, on the left-hand side of your screen, press the menu dropdown button and navigate to `Auto Scaling > Auto Scaling Groups`. From there, click on the respective name of the auto scaling group with your Locust `workers`. 

On the `Group details` box, click on `Edit`. Set the `Desired capacity` to `1` and the `Min desired capacity` to `1`. Press the orange `Update` button. This should shortly spin up a Locust `worker`. 

From here, let's focus our attention on our `master` VM. Within the `master` VM, run

```
sudo docker-compose -f master.docker-compose.yml down -v
sudo docker-compose -f master.docker-compose.yml build
sudo docker-compose -f master.docker-compose.yml up -d
```

If the `master` VM throw an error about (a) (1) docker not being up or (2) docker is not responsive at all (you are not seing any output), try our "hanging" docker commands from before:

```
sudo pkill -9 -f docker
sudo systemctl disable docker docker.socket 
sudo rm -rf /var/lib/docker
sudo systemctl start 
# If needed: sudo systemctl restart docker
```

If, on the top right of your screen, you never see the amount of workers increase (from 0 to 1), try downing, building, and upping again, but, for the build command, use
```
sudo docker-compose -f master.docker-compose.yml build --no-cache
```

For any other problems, please see our [DEBUGGING.md](DEBUGGING.md) or leave us an issue within this repo. 

If you do run into trouble, it is recommended to SSH into either (1) one of the locust workers behind the auto scaling group or (2) the Locust master and run `sudo docker-compose logs`. This will give you logs to sift through to try and determine what the problem might be. (The locust workers might be a bit more unstable as, if you SSH into them but they can't connect to the host, they might terminate themselves and spin up another VM, as the auto scaling group might deem this lack of connection to the `master` host as "unhealthy".)

At this point, once you get things working, congrats! Everything should be completed at this time. Once again, before executing large scale load testing, please make sure you have permission to target the respective endpoints. If you're encountering failures, please see our [DEBUGGING.md](DEBUGGING.md). Further, if you're wanting to find bottlenecks within your system please see [BOTTLENECKS.md](BOTTLENECKS.md). Congrats! 


