# Simple Checklist

This document is a simple step-by-step instructional document in how to get your locust non-clustered environment quickly up and running again. 

## Non-Clustered

1. Database
    - [ ] Remove data
    ```
    sudo rm -rf redis-data/ redis.conf/ holder-db/
    ```
    - [ ] Down `sudo docker-compose down -v`
    - [ ] Pull up to date
    ```
    # Remove everything currently in your working directory
    # (do NOT do rm -rf *)
    git@github.com:hyperledger/aries-akrida.git
    cd instance-configs/database
    mv * ../../../
    cd ../../../
    rm -rf aries-akrida/
    ```
    - [ ] Ensure `.env` looks correct (should not have changed)
        - Friendly reminder of `vim` commands:
            - `vim .env` to enter the file
            - Press `i` to enter `insert` mode
            - Press `esc` (Escape) to exit `insert` mode
            - Type in `:w` to save changes (have to be out of insert mode)
            - Type in `:q` to exit (have to be out of insert mode)
            - Type in `:wq` to save and exit
    - [ ] Build `sudo docker-compose build`
    - [ ] Up `sudo docker-compose up -d`
2. ACA-Py Agent
    - [ ] Down `sudo docker-compose down -v` (shouldn't need to)
    - [ ] Pull up to date
    ```
    # Remove everything currently in your working directory
    # (do NOT do rm -rf *)
    git@github.com:hyperledger/aries-akrida.git
    cd instance-configs/acapy-agent
    mv * ../../../
    cd ../../../
    rm -rf aries-akrida/
    ```
    - [ ] Update `.env` file
        - [ ] Update `ISSUER` var to the external IP of the ACA-Py agent
            - If, for example, `ISSUER=123.45.67.899`, (a) `vim .env`, (b) type in `:%s/123.45.67.899/{new_external_ip}`
        - [ ] Update API Key (if first time)
            - [ ] `.env`
            ```
            ACAPY_ADMIN_API_KEY="insertYourAPIKeyHere"
            ```
    - [ ] Build `sudo docker-compose build`
    - [ ] Up `sudo docker-compose up -d`
    - [ ] Update firewall rules 
        - [ ] You can access ACA-Py (your IP)
            - Allow yourself access to ports `8150-8151`
                * Type: `Custom TCP`
                * Port Range: `8150-8151`
                * Source: `My IP`
    - [ ] Verify ACA-Py comes up in the browser at `{EXTERNAL_IP}:8150/api/doc`
    - [ ] Verify your API key, in your `.env`, "unlocks" ACA-Py (authenticate yourself)
        - At the top of the ACA-Py Admin UI, there should be a green box called `Authorize`. Click on this, then paste in your `ACAPY_ADMIN_API_KEY` within this box.
    - [ ] Verify your transport port (sanity check)
        - Within the ACA-Py Admin UI, head to the `connection` section. Find the green `POST` method with `/connections/create-invitation`. Click on it. Then press `Try it out`. 
        - Within the body, have the input field only have
        ```
        {"metadata": {}}
        ```
        - Press `Execute`. 
        - Ensure the `Response` [the top box]
            - is of type `200` (AKA you do not receive an Unauthorized error)
        - For the `invitation_url`, 
            - Does the `invitation_url` contain the external IP of ACA-Py?
                - If not, review ACA-Py `.env`.
            - Does the end port of the `invitation_url` end in `8151`?
                - If not, review ACA-Py `.env`
            - Can you access the `invitation_url` via your browser?
                - If not, review firewall rules.
    - [ ] Anchor DID ([see ACA-Py-Agent-Configuration within NONCLUSTERED.md](NONCLUSTERED.md###ACA-Py-Agent-Configuration)) 
        - If needed, here's Indicio's Self Serve site: https://selfserve.indiciotech.io/
        - If the input field for the body box is not already empty, go ahead and make it match just `{}`.
    - [ ] Create Schema
    - [ ] Create Credential Definition
3. Locust Worker
    - [ ] `cd aries-akrida/`
    - [ ] Down `sudo docker-compose down -v` (shouldn't need to)
        - If the docker daemon isn't running, give it a friendly kick with
        ```
        sudo systemctl restart docker
        # Optional (additional) commands if the above doesn't work
        sudo pkill -9 -f docker
        sudo systemctl disable docker docker.socket 
        # Optional: sudo rm -rf /var/lib/docker
        sudo systemctl start docker
        # If needed again: sudo systemctl restart docker
        ```
        - Pro tip: Maybe only have a modest amount of ports open (e.g. like `10000-10500`)
        
    - [ ] Pull up to date
    ```
    # Remove everything currently in your working directory
    # (do NOT do rm -rf *)
    git@github.com:hyperledger/aries-akrida.git
    cd aries-akrida/
    git clone git@github.com:openwallet-foundation/agent-framework-javascript.git
    ```
    - [ ] Update `.env` file
        - [ ] `MASTER_HOST` to the external IP of the locust master
        - [ ] `AGENT_IP` to the external IP of the locust worker
            - If you don't have a `master` or `worker` VM yet, these two values are the same (your only Locust VM). 
        - [ ] `ISSUER_URL` to `http://{External_IP_ACA-Py_Agent}:8150`
        - [ ] `SCHEMA` as above
        - [ ] `CRED_DEF` as above
        - [ ] `LOCUST_FILES` to an arbitrary load testing script created (if you would like to change the scenario)
    - [ ] Ensure your mediator is up and running and ready to connect
        - [ ] Update any necessary firewall rules
    - [ ] Update `agent.ts` according to the pickup protocol version your mediator is using
        - Set to `V2` by default
        - If using implicit, search for the pickup protocol within agent.ts (line 106); comment out the `V2` line and uncomment the `Implicit` pickup strategy line, so
        ```
        // mediatorPickupStrategy: MediatorPickupStrategy.PickUpV2,
        mediatorPickupStrategy: MediatorPickupStrategy.Implicit, 
        ```
        - You can jump to this line by typing in `:106` or by searching for it by typing in`/mediatorPickupStrategy`
    - [ ] Build and Up
        - Just one locust VM
            - `sudo docker-compose build`
            - `sudo docker-compose up -d`
        - Master and worker nodes
            - Master:
                - `sudo docker-compose -f master.docker-compose.yml build`
                - `sudo docker-compose -f master.docker-compose.yml up -d`
            - Worker (do the same steps as above, too)
                - `sudo docker-compose -f worker.docker-compose.yml build`
                - `sudo docker-compose -f worker.docker-compose.yml up -d`
    - [ ] Update Firewall rules
        - Allow yourself access to `8089-8090`
            * Type: `Custom TCP`
            * Port Range: `8089-8090`
            * Source: `My Ip`
        - Allow Locust access to the ACA-Py Admin UI (`8150-8151`)
            * Type: `Custom TCP`
            * Port Range: `8150-8151`
            * Source: `Custom TCP`
                * `Locust Exteral IP` / 32
    - [ ] Ensure you can access locust via the web browser
        - `{MASTER_EXTERNAL_IP}:8089`

    Getting everything back up and running again is not trivial. If things are not coming up properly, try running `sudo docker-compose logs` in either (a) one of your locust VMs or (b) your ACA-Py agent. There might be some useful information as to what is going wrong there. If you're still stuck, please reach out for help!
    
    Extra: "Hanging Docker" Portion:
    ```
    # Restart docker
    sudo pkill -9 -f docker
    sudo systemctl disable docker docker.socket
    sudo rm -rf /var/lib/docker
    sudo systemctl start docker
    ```
    
4. (Optional) Mediator
    - [ ] Down `sudo docker-compose down -v` (shouldn't need to)
    - [ ] Pull up to date
    ```
    # Remove everything currently in your working directory
    # (do NOT do rm -rf *)
    git@github.com:hyperledger/aries-akrida.git
    cd aries-akrida/instance-configs/mediator
    mv * ../../../
    cd ../../../
    rm -rf aries-akrida/
    ```
    (`.env` file should largely stay the same)
    - [ ] Edit `docker-compose.yml`
*(You will need the DNS entry for the mediator and the arbitrary safe string used in the `.env` for the password.)*
        - [ ] Replace:
            - [ ] `insertDNSEntryHere.com` with the DNS name of your mediator (without the `http`)
            - [ ] `insertStringHere` with an arbitrary safe string (unquoted) you can remember
    - [ ] Update Firewall rules
        - [ ] 1. Allow locust to access this mediator on port `3000`
            * Type: `Custom TCP`
            * Port Range: `3000`
            * Source: `Custom TCP`
                * `Locust External IP` / 32
        - [ ] 2. Allow the mediator to be able to access itself with its external IP on port `3000`
            * Type: `Custom TCP`
            * Port Range: `3000`
            * Source: `Custom TCP`
                * `Mediator External IP` / 32
        - [ ] 3. Allow the mediator to be able to access locust on ports `8089-8090`
            * Type: `Custom TCP`
            * Port Range: `8089-8090`
            * Source: `Custom TCP`
                * `Mediator External IP` /32
        - [ ] 4. Allow the mediator to be able to access the ACA-Py agent on ports `8150-8151`
            * Type: `Custom TCP`
            * Port Range: `8150-8151`
            * Source: `Custom TCP`
                * `Mediator External IP` / 32
        - [ ] 5. Allow ACA-Py to be able to access the mediator VM on port `3000`
            * Type: `Custom TCP`
            * Port Range: `3000`
            * Source: `Custom TCP`
                * `ACA-Py External IP` / 32
    - [ ] Build and Up
    ```
    sudo docker build -f Dockerfile --no-cache -t indicio-tech/aries-mediator .
    sudo docker-compose up 
    ```
    - [ ] Put mediation URL into locust `.env`
    - [ ] Down, build, and up locust

## Clustered

1. Database
    - [ ] Remove data
    ```
    sudo rm -rf redis-data/ redis.conf/ holder-db/
    ```
    - [ ] Down `sudo docker-compose down -v`
    - [ ] If needed, pull up to date
    ```
    # Remove everything currently in your working directory
    # (do NOT do rm -rf *)
    git@github.com:hyperledger/aries-akrida.git
    cd instance-configs/database
    mv * ../../../
    cd ../../../
    rm -rf aries-akrida/
    ```
    - [ ] Ensure `.env` looks correct (should not have changed)
        - Friendly reminder of `vim` commands:
            - `vim .env` to enter the file
            - Press `i` to enter `insert` mode
            - Press `esc` (Escape) to exit `insert` mode
            - Type in `:w` to save changes (have to be out of insert mode)
            - Type in `:q` to exit (have to be out of insert mode)
            - Type in `:wq` to save and exit
    - [ ] Build `sudo docker-compose build`
    - [ ] Up `sudo docker-compose up -d`
2. ACA-Py Agent Autoscaling Group
    - If updating: 
        - [ ] Spin up single ACA-Py instance
        - [ ] Pull up to date
            ```
            # Remove everything currently in your working directory
            # (do NOT do rm -rf *)
            git@github.com:hyperledger/aries-akrida.git
            cd instance-configs/acapy-agent
            mv * ../../../
            cd ../../../
            rm -rf aries-akrida
            ```
        - [ ] Create new Amazon Machine Image (see [CLUSTERED.md](CLUSTERED.md))
        - [ ] Change AMI to newly created (above) AMI within ACA-Py Launch template (see [CLUSTERED.md](CLUSTERED.md))
        - [ ] Set default version of ACA-Py Launch template to new highest number (see [CLUSTERED.md](CLUSTERED.md))
    - [ ] Spin up at least one VM of your autoscaling group
        - `Auto Scaling > Auto Scaling Groups`
        - Click on ACA-Py Autoscaling Group
        - `Group Details > Edit`
            - `Desired Capacity` to at least `1`
            - `Min desired capacity` to at least `1`
    - [ ] Update firewall rules 
        *There are more firewall rules than these, but these should be the only rules that will change. For a list of all of the firewall rules, see [CLUSTERED.md](CLUSTERED.md).*
        - Load Balancing Security Group
            - Allow yourself access to the ACA-Py frontend load balancer (`8080`)
                * Type: `Custom TCP`
                * Port Range: `8080`
                * Source: `My IP`
                * Description: `Front - I can access ACA-Py admin LB (8080)`
            - Allow yourself access to the ACA-Py backend load balancer (`80`)
                * Type: `Custom TCP`
                * Port Range: `80`
                * Source: `My IP`
                * Description: `Back - I can access ACA-Py transport LB (80)`
    - [ ] Verify ACA-Py comes up in the browser at `{ACAPY_FRONTEND_LB_DNS}:8080/api/doc`
    - [ ] Verify your API key, in your `.env`, "unlocks" ACA-Py (authenticate yourself)
        - At the top of the ACA-Py Admin UI, there should be a green box called `Authorize`. Click on this, then paste in your `ACAPY_ADMIN_API_KEY` within this box.
    - [ ] Verify your transport port (sanity check)
        - Within the ACA-Py Admin UI, head to the `connection` section. Find the green `POST` method with `/connections/create-invitation`. Click on it. Then press `Try it out`. 
        - Within the body, have the input field only have
        ```
        {"metadata": {}}
        ```
        - Press `Execute`. 
        - Ensure the `Response` [the top box]
            - is of type `200` (AKA you do not receive an Unauthorized error)
        - For the `invitation_url`, 
            - Does the `invitation_url` contain the transport (backend) DNS name?
                - If not, review ACA-Py `.env`.
            - Does the end port of the `invitation_url` end in `80`?
                - If not, review ACA-Py `.env`
            - Can you access the `invitation_url` via your browser?
                - If not, review firewall rules.


    - [ ] Anchor DID ([see ACA-Py-Agent-Configuration within NONCLUSTERED.md](NONCLUSTERED.md###ACA-Py-Agent-Configuration)) 
        - If needed, here's Indicio's Self Serve site: https://selfserve.indiciotech.io/
        - If the input field for the body box is not already empty, go ahead and make it match just `{}`.
    - [ ] Create Schema
    - [ ] Create Credential Definition
3. Locust Master & Locust Worker Auto Scaling Group
*If you only clustered your ACA-Py agent, follow the Locust Worker section above [within the non-clustered portion]. **This section is only if you clustered your Locust workers**.*
    - For the Locust `workers`:
        - If updating:
            - [ ] Spin up single locust `worker` VM.
            - [ ] Pull up to date
                ```
                # Remove everything currently in your working directory
                # (do NOT do rm -rf *)
                git@github.com:hyperledger/aries-akrida.git
                cd aries-akrida/
                git clone git@github.com:openwallet-foundation/agent-framework-javascript.git
                ```
            - [ ] Update `agent.ts` according to the pickup protocol version your mediator is using
                - Set to `V2` by default
                - If using implicit, search for the pickup protocol within agent.ts (line 106); comment out the `V2` line and uncomment the `Implicit` pickup strategy line, so
                ```
                // mediatorPickupStrategy: MediatorPickupStrategy.PickUpV2,
                mediatorPickupStrategy: MediatorPickupStrategy.Implicit, 
                ```
                - You can jump to this line by typing in `:106` or by searching for it by typing in`/mediatorPickupStrategy`
            - [ ] Create new Amazon Machine Image (see [CLUSTERED.md](CLUSTERED.md))
            - [ ] Change AMI to newly created (above) AMI within Locust worker launch template (see [CLUSTERED.md](CLUSTERED.md))
            - [ ] Set default version of Locust worker Llaunch template to new highest number (see [CLUSTERED.md](CLUSTERED.md))
        - [ ] Spin up at least one VM of your autoscaling group
            - `Auto Scaling > Auto Scaling Groups`
            - Click on Locust Worker Autoscaling Group
            - `Group Details > Edit`
                - `Desired Capacity` to at least `1`
                - `Min desired capacity` to at least `1`
    - For the Locust `master` VM:
        - [ ] `cd aries-akrida/`
        - [ ] Down `sudo docker-compose down -v` (shouldn't need to)
            - If the docker daemon isn't running, give it a friendly kick with
            ```
            sudo systemctl restart docker
            # Optional (additional) commands if the above doesn't work
            sudo pkill -9 -f docker
            sudo systemctl disable docker docker.socket 
            # Optional: sudo rm -rf /var/lib/docker
            sudo systemctl start docker
            # If needed again: sudo systemctl restart docker
            ```
            - Pro tip: Maybe only have a modest amount of ports open (e.g. like `10000-10500`)

        - [ ] Pull up to date
        ```
        # Remove everything currently in your working directory
        # (do NOT do rm -rf *)
        git@github.com:hyperledger/aries-akrida.git
        cd aries-akrida/
        git clone git@github.com:openwallet-foundation/agent-framework-javascript.git
        ```
        - [ ] Update `.env` file
            - [ ] `MASTER_HOST` to the internal IP of the locust master
            - [ ] `AGENT_IP` to the DNS name of the worker load balancer
            - [ ] `ISSUER_URL` to `http://{FRONTEND_DNS_NAME_ACAPy_LOAD_BALANCER}:8150`
            - [ ] `SCHEMA` as above
            - [ ] `CRED_DEF` as above
            - [ ] `LOCUST_FILES` to an arbitrary load testing script created (if you would like to change the scenario)
        - [ ] Ensure your mediator is up and running and ready to connect
            - [ ] Update any necessary firewall rules
        - [ ] Update `agent.ts` according to the pickup protocol version your mediator is using
            - Set to `V2` by default
            - If using implicit, search for the pickup protocol within agent.ts (line 106); comment out the `V2` line and uncomment the `Implicit` pickup strategy line, so
            ```
            // mediatorPickupStrategy: MediatorPickupStrategy.PickUpV2,
            mediatorPickupStrategy: MediatorPickupStrategy.Implicit, 
            ```
            - You can jump to this line by typing in `:106` or by searching for it by typing in`/mediatorPickupStrategy`
        - [ ] Build and Up
            - `sudo docker-compose -f master.docker-compose.yml build`
            - `sudo docker-compose -f master.docker-compose.yml up -d`
        - [ ] Update firewall rules 
        *There are more firewall rules than these, but these should be the only rules that will change. For a list of all of the firewall rules, see [CLUSTERED.md](CLUSTERED.md).*
        - (Old) Performance Testing Security Group
            - Allow yourself access to `8089-8090`
                * Type: `Custom TCP`
                * Port Range: `8089-8090`
                * Source: `My Ip`
            - Allow Locust access to the ACA-Py Admin UI (`8150-8151`)
                * Type: `Custom TCP`
                * Port Range: `8150-8151`
                * Source: `Custom TCP`
                    * `Locust Exteral IP` / 32
        - [ ] Ensure you can access locust via the web browser
            - `{MASTER_EXTERNAL_IP}:8089`

    
    Extra: "Hanging Docker" Portion:
    ```
    # Restart docker
    sudo pkill -9 -f docker
    sudo systemctl disable docker docker.socket
    sudo rm -rf /var/lib/docker
    sudo systemctl start docker
    ```
    
4. (Optional) Mediator
    - [ ] Down `sudo docker-compose down -v` (shouldn't need to)
    - [ ] Pull up to date
    ```
    # Remove everything currently in your working directory
    # (do NOT do rm -rf *)
    git@github.com:hyperledger/aries-akrida.git
    cd aries-akrida/instance-configs/mediator
    mv * ../../../
    cd ../../../
    rm -rf aries-akrida/
    ```
    (`.env` file should largely stay the same)
    - [ ] Edit `docker-compose.yml`
*(You will need the DNS entry for the mediator and the arbitrary safe string used in the `.env` for the password.)*
        - [ ] Replace:
            - [ ] `insertDNSEntryHere.com` with the DNS name of your mediator (without the `http`)
            - [ ] `insertStringHere` with an arbitrary safe string (unquoted) you can remember
    - [ ] Update Firewall rules
        - [ ] 1. Allow locust to access this mediator on port `3000`
            * Type: `Custom TCP`
            * Port Range: `3000`
            * Source: `Custom TCP`
                * `Locust External IP` / 32
        - [ ] 2. Allow the mediator to be able to access itself with its external IP on port `3000`
            * Type: `Custom TCP`
            * Port Range: `3000`
            * Source: `Custom TCP`
                * `Mediator External IP` / 32
        - [ ] 3. Allow the mediator to be able to access locust on ports `8089-8090`
            * Type: `Custom TCP`
            * Port Range: `8089-8090`
            * Source: `Custom TCP`
                * `Mediator External IP` /32
        - [ ] 4. Allow the mediator to be able to access the ACA-Py agent on ports `8150-8151`
            * Type: `Custom TCP`
            * Port Range: `8150-8151`
            * Source: `Custom TCP`
                * `Mediator External IP` / 32
        - [ ] 5. Allow ACA-Py to be able to access the mediator VM on port `3000`
            * Type: `Custom TCP`
            * Port Range: `3000`
            * Source: `Custom TCP`
                * `ACA-Py External IP` / 32
    - [ ] Build and Up
    ```
    sudo docker build -f Dockerfile --no-cache -t indicio-tech/aries-mediator .
    sudo docker-compose up 
    ```
    - [ ] Put mediation URL into locust `.env`
    - [ ] Down, build, and up locust
