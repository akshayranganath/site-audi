# README #

This project is to create a site-audit tool for accessing Akamai related details. 

As part of Phase 1, we are targeting only [Propert Manager (PAPI)](https://developer.akamai.com/api/luna/papi/overview.html).

### Usage ###

- In your ~/.edgerc file setup the credentials under the name __papi__
- Ensure you have python 3.x. 
- As a pre-installation step, please add the libraries that are required.
```bash
pip install -r requirements.txt
```

To run the reports, simple issue this command:
```bash
python3 aggregator.py
```

Depending on the number of configurations you have, this report can take at least 30 minutes to execute. Assume that it'll need about an hour - so ensure that your machine does not sleep during the time to help complete the execution of the script.

### Output ###
When this program is run, it will create a folder within the current directory under the name "Account_Name-Timestamp". Within this folder, following files will be created:

|File Name| Purpose|
|---------|--------|
| account.csv | High level account overview. It will list the account name and the groups associated with the account. |
| cpcodes.csv | A list of all the CP Codes by account and group id will be listed in this file. It will also list the products associated with the CP Codes |
| edgehostnames.csv| List of all edge host names associated with this account |
| hostnames.csv | This file pulls all the host names listed within the configurations. It will also list if the domain is CNAMED to Akamai and compare with the CNAME listed in the configuration |
| origins.csv | This file will list all the unique origin names defined within the configurations. It will also segregate as *Customer origin* or *GTM Origin* |
| properties.csv | This file will list all the properties associated with the account. For each property, it will list the following details: Property name, Current version in prod and staging, latest version and first version details. Finally, it lists all the behaviors seen in the config. |


## GTM Report
Within this script base is a code to generate a report about your GTM usage as well. To use this, simple issue a command as follows:

```bash
python3 gtm_report.py
```

The reports will be within a folder called _gtm_.