'''
// Good luck with this code. Do praise if its good.
// And dont curse if its bad :)
Author: Vreddhi Bhat and Bhavin Dutia
Contact: vbhat@akamai.com and bdutia@akamai.com
'''

import json


__all__=['Originpapitools']

class Originpapitools(object):
    """All basic operations that can be performed using PAPI """

    final_response = "NULL" #This variable holds the SUCCESS or FAILURE reason
    headers = {
        "Content-Type": "application/json"
    }

    access_hostname = "mandatory"
    property_name = "optional"
    version = "optional"
    notes = "optional"
    emails = "optional"
    groupId = "optional"
    contractId = "optional"
    propertyId = "optional"

    def __init__(self, access_hostname, property_name = "optional", \
                version = "optional",notes = "optional", emails = "optional", \
                groupId = "optional", contractId = "optional", propertyId = "optional"):
        self.access_hostname = access_hostname
        self.property_name = property_name
        self.version = version
        self.notes = notes
        self.emails = emails
        self.groupId = groupId
        self.contractId = contractId
        self.propertyId = propertyId

    def populateDetailsInMemory(self,session):
        """
        Function to populate mapping of properties and its ID

        Parameters
        -----------
        session : <string>
            An EdgeGrid Auth akamai session object

        Returns
        -------
        mappedResponse : mappedResponse
            (mappedResponse) Object with all details
        """
        groupsInfo = self.getGroups(session)
        if groupsInfo.status_code == 200:
            propertyDetailsMap = []
            for everyGroup in groupsInfo.json()['groups']['items']:
                if 'contractIds' in everyGroup:
                    for everyContractId in everyGroup['contractIds']:
                        url = 'https://' + self.access_hostname + '/papi/v0/properties/?contractId=' + everyContractId +'&groupId=' + everyGroup['groupId']
                        propertiesResponse = session.get(url)
                        #print(json.dumps(propertiesResponse.json()))
                        if 'properties' in propertiesResponse.json():
                            for everyProperty in propertiesResponse.json()['properties']['items']:
                                propertyInformation = {}
                                propertyInformation['propertyName'] = everyProperty['propertyName']
                                propertyInformation['propertyId'] = everyProperty['propertyId']
                                propertyInformation['groupId'] = everyProperty['groupId']
                                propertyInformation['contractId'] = everyProperty['contractId']
                                propertyInformation['latestVersion'] = everyProperty['latestVersion']
                                propertyInformation['stagingVersion'] = everyProperty['stagingVersion']
                                propertyInformation['productionVersion'] = everyProperty['productionVersion']
                                propertyDetailsMap.append(propertyInformation)
        #print(json.dumps(propertyDetailsMap))
        return propertyDetailsMap


    def getGroups(self,session):
        """
        Function to fetch all the groups under the contract

        Parameters
        ----------
        session : <string>
            An EdgeGrid Auth akamai session object

        Returns
        -------
        groupResponse : groupResponse
            (groupResponse) Object with all response details.
        """

        groupUrl = 'https://' + self.access_hostname + '/papi/v0/groups/'
        groupResponse = session.get(groupUrl)
        if groupResponse.status_code == 200:
            self.final_response = "SUCCESS"
        else:
            self.final_response = "FAILURE"
        return groupResponse


    def getPropertyRulesfromPropertyId(self,session,propertyId,version,contractId,groupId):
        """
        Function to download rules from a property

        Parameters
        ----------
        session : <string>
            An EdgeGrid Auth akamai session object
        property_name: <string>
            Property or configuration name
        version : <int>
            Property orconfiguration version number

        Returns
        -------
        rulesResponse : rulesResponse
            (rulesResponse) Object with all response details.
        """

        rulesUrl = 'https://' + self.access_hostname  + '/papi/v0/properties/' + propertyId +'/versions/'+str(version)+'/rules/?contractId='+ contractId +'&groupId='+ groupId
        rulesResponse = session.get(rulesUrl)
        if rulesResponse.status_code == 200:
            self.final_response = "SUCCESS"
        else:
            self.final_response = rulesResponse.json()
            print(json.dumps(rulesResponse.json()))
        return rulesResponse