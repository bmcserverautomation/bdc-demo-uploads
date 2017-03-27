# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import requests, json, pprint

def _url(path):
        return 'http://mobility01-btd.trybmc.com/' + path

#
# Let's get the GUID of the site.
#

resp = requests.post(_url('/dcaportal/api/login/sites'))

if resp.status_code != 200:
    # This means something went wrong.
    raise ApiError('GET /tasks/ {}'.format(resp.status_code))

j = resp.json();

for object in j['results']['objects']:
    siteType = (object[1]['emType'])
    if siteType == 'BSA':
      print('Found a BSA site')
      junk, siteguid = object[0].split("/")
      print(siteguid)
    else: print('saw another site') 
#
# Got the GUID, time to login and get a clientId
#

heads={"content-type": "application/json" }
loginStr = '{ "authenticationMethod": "SRP", "username": "BLAdmin", "password": "password", "siteGuids": ["' + siteguid + '"] }'
resp = requests.post(_url('/dcaportal/api/login'),headers=heads,data=loginStr)

if resp.status_code != 200:
    # This means something went wrong.
    raise ApiError('GET /tasks/ {}'.format(resp.status_code))

j = resp.json()


#if j['isAuthenticated'] == 'True':
#       print('successfully authenticated' + j['clientId']) 

clientIdstr=j['clientId']
jsession,junk,junk=resp.headers['Set-Cookie'].split(';')
#print("Client ID string is: " + clientIdstr)

#
# lets get our security group ID
#


heads={'clientId': clientIdstr, 'Content-Type': 'application/json', 'Cookie': jsession }
#print('Sending Headers: ')
#print(heads)

resp = requests.post(_url('/dcaportal/api/bsmsearch/mySecurityGroups'),headers=heads)


if resp.status_code != 200:
    # This means something went wrong.
    raise ApiError('GET /tasks/ {}'.format(resp.status_code))

j = resp.json()

# {"errorCode":null,"taskId":"42"}


#if j['errorCode'] != 'None':
#    # This means something went wrong.
#    #raise ApiError('GET /tasks/ {}'.format(resp.text))
#    print('Something went wrong: ')
#    print(j['errorCode'])
#    exit()


taskId=j['taskId']
print('Next taskID: ')
print(j['taskId'])

# 
# Get Data from /api/bsmsearch/mySecurityGroups
#

print (heads)

urlPath = '/dcaportal/api/bsmsearch/results?taskId=' + taskId
resp = requests.get(_url(urlPath),headers=heads)

j = resp.json()
taskId=j['taskId']
print('Next taskID: ')
print(j['taskId'])

#
# This will eventually extract the GUID for the particular Security group.  FIXME
#
#for object in j['searchResult']['objects']:
#  if j['searchResult']['objects']['emRoleName'] == 'BLAdmins':
#    print('Found BLAdmins: ')
#    print object.title()
#  print object

secGroupGuid='3ae0f8b5-7077-11e6-80fa-005056021034'


#
# Let's pull the list of vulnerability scans: first generate the data set
#

print ("Let's pull the list of vulnerability scans")

vulnScanReq = {
 "pageSize": 50,
 "pageNumber": 1,
 "sortedColumns": [{
  "columnName": "importedDate",
  "ascending": "false"
 }],
 "filters": []
}

resp = requests.post(_url('/dcaportal/api/vulnerability/listAllScans'),headers=heads,data=vulnScanReq)

# print (resp.text)
# j = resp.json()

# taskId=j['taskId']
# print('Next taskID: ')
# print(j['taskId'])

#
# Now retrieve the data set 
#

resultsUrl = '/dcaportal/api/bsmsearch/results?taskId=' + taskId

resp = requests.get(_url(resultsUrl),headers=heads,data=None)
# j = resp.json()

# taskId=j['taskId']
# print('Next taskID: ')
# print(j['taskId'])

#
# At this point, we should parse the list of vulnerability scans and 
#   identify our preferred, in this case, a Qualys scan run in the Demo env.
# FIXME
#
vulnScanGuid='c44f5d6e-f482-11e6-ac32-005056021003'


#
# Now we need a list of assets
#
assetListReq = {
 "pageSize": 200,
 "pageNumber": 1,
 "sortedColumns": [{
  "columnName": "dns",
  "ascending": "true"
 }],
 "parameters": {
  "securityGroup": "3ae0f8b5-7077-11e6-80fa-005056021034"
 },
 "filters": []
}

reqUrl = '/dcaportal/api/vulnerability/assetSearch'

resp = requests.get(_url(reqUrl),headers=heads,data=assetListReq)
# j = resp.json()

#taskId=j['taskId']
#print('Next taskID: ')
#print(j['taskId'])

#
# Now retrieve the data set 
#

#resultsUrl = '/dcaportal/api/action/results?taskId=' + taskId

#resp = requests.get(_url(resultsUrl),headers=heads,data=None)
#j = resp.json()

#print('Next taskID: ')
#print(j['taskId'])

#
# We now need to retrieve a list of mapped vulnerabilities for the remediation operation
#

assetSearchReq = {
 "pageSize": 200,
 "pageNumber": 1,
 "sortedColumns": [{
  "columnName": "emTargetName",
  "ascending": "true"
 }, {
  "columnName": "vulnerabilityName",
  "ascending": "true"
 }],
 "parameters": {
  "securityGroup": "3ae0f8b5-7077-11e6-80fa-005056021034",
  "applyLicensedFilter": "true"
 },
 "filters": [{
  "name": "emTargetName",
  "value": "bao"
 }, {
  "name": "scanIds",
  "value": "scan/1484323137.36245"
  }]
}

resp = requests.get(_url('/dcaportal/api/dashboard/vulScanData'),headers=heads,data=None)
j = resp.json()

taskId=j['taskId']
print('Next taskID: ')
print(j['taskId'])

resultsUrl = '/dcaportal/api/action/results?taskId=' + taskId

resp = requests.get(_url(resultsUrl),headers=heads,data=None)
j = resp.json()

taskId=j['taskId']
print('Next taskID: ')
print(j['taskId'])






#{
#  "name": "vulnerabilityName",
#  "value": "91041"
# },

# "filters": [{
#  "name": "emTargetName",
#  "value": "bao"
# }, {
#  "name": "vulnerabilityName",
#  "value": "Microsoft Windows HTTP.sys Remote Code Execution Vulnerability (MS15-034)",
# }, {
#  "name": "scanIds",
#  "value": "scan/1484323137.36245"
#


#
# This is what the assset search responds with:
#
#assetSearchResp 
#{
#"errorCode": null,
#"taskId": null,
#"cancelled": false,
#"completed": true,
#"results": {
#"roots": [
#  "dcaportal.VulnerabilityScanHolder/6bc741b3-12e9-11e7-92e0-005056021003"
#],
#"objects": [
#  [
#  "dcaportal.VulnerabilityScanHolder/6bc741b3-12e9-11e7-92e0-005056021003",
#  {
#"severity": 5,
#"emType": "BSA",
#"emTargetType": null,
#"scannedDate": "January 13, 2017 3:58:57 PM GMT",
#"osPlatform": "x86_64",
#"scanIds": [],
#"osVendor": "Microsoft",
#"osVersion": "2008 R2",
#"lastApprovalRequestedDate": null,
#"includedCVEs": [
#  "CVE-2015-1635"
#],
#"emTargetExternalID": "/id/SystemObject/Server/5ffe37bf-50ec-40d5-b739-e8d3040190a5",
#"lastJobRunEndDate": null,
#"assetIP": "192.168.100.9",
#"creationDate": null,
#"modificationDate": "February 16, 2017 8:02:07 PM GMT",
#"vulnerabilityID": "91041",
#"assetDNS": "bao",
#"OS": "Windows",
#"vulnerabilityName": "Microsoft Windows HTTP.sys Remote Code Execution Vulnerability (MS15-034)",
#"lastMappedDate": "February 16, 2017 8:02:07 PM GMT",
#"importedDate": "February 16, 2017 8:01:56 PM GMT",
#"name": null,
#"description": null,
#"emTargetName": "bao",
#"isLicensed": true,
#"lastApprovalReceivedDate": null,
#"closedAge": null,
#"osRelease": "6.1",
#"assetGroupNames": [],
#"lastJobRunStartDate": null,
#"lastOperationCreatedDate": null,
#"status": "TARGET_MAPPED",
#"exclusionStatusBySG": [],
#"remediationBySG": [
#  "dcaportal.VulnerabilityRemediation/6bc741b4-12e9-11e7-92e0-005056021003"
#],
#}
#],,
#  [
#  "dcaportal.VulnerabilityRemediation/6bc741b4-12e9-11e7-92e0-005056021003",
#  {
#"emType": "BSA",
#"isConditionalMapping": false,
#"name": null,
#"description": null,
#"creationDate": "February 16, 2017 8:02:16 PM GMT",
#"modificationDate": null,
#"securityGroupId": "3ae0f8b5-7077-11e6-80fa-005056021034",
#"mappingStatus": "MANUAL_MAPPED",
#"securityGroup": "dcaportal.DCAPortalSecurityGroup/3ae0f8b5-7077-11e6-80fa-005056021034",
#"remediationByCondition": [
#  "dcaportal.VulnerabilityRemediationByCondition/6bc741b6-12e9-11e7-92e0-005056021003"
#],
#}
#],,
#  [
#  "dcaportal.DCAPortalSecurityGroup/3ae0f8b5-7077-11e6-80fa-005056021034",
#  {
#"owner": null,
#"defaultJobURI": null,
#"name": null,
#"description": null,
#"emRoleExternalID": null,
#"defaultDepotPath": null,
#"creationDate": null,
#"modificationDate": null,
#"defaultJobPath": null,
#"defaultDepotURI": null,
#"emRoleName": null
#}
#],,
#  [
#  "dcaportal.VulnerabilityRemediationByCondition/6bc741b6-12e9-11e7-92e0-005056021003",
#  {
#"optionalUris": [],
#"name": "Remediation Script Linux",
#"description": null,
#"path": "Depot/Portal Operations",
#"remediationContentType": "NSHSCRIPT",
#"creationDate": "February 16, 2017 8:02:16 PM GMT",
#"isAndCondition": false,
#"modificationDate": null,
#"remediationContentUri": "/id/SystemObject/Depot Object/NSH Script/da4bffdb-d64f-421b-865f-a19bf795a019",
#"cvesFixed": [],
#"conditions": [],
#}
#],
#],
#}
#}
#








# assetID dns name "scan host"
# targetID name "Name (2nd col)
# vuln ID: vulnerability ID, 2nd col on vulns page
# device type list, full URI for device, GUID of target ID

createOperationJson = {
 "isValidateOnly": false,
 "operationPrefix": "Vuln-Remed-Op-",
 "createOperationRequests": [{
  "allowOverrideTargets": false,
  "componentTypeList": [],
  "contentType": "NSHSCRIPT",
  "description": "Automatically generated remediation job",
  "deviceTypeList": ["<Device type list retrieved from /dcaportal/api/dashboard/vulScanData>"],
  "distributionPoint": null,
  "isExecuteNow": true,
  "jobGroupURI": "<Job Group USI retrieved from /dcaportal/api/browse/submit",
  "name": "Version4",
  "notifications": [],
  "operationSubType": null,
  "operationType": "NSH_SCRIPT",
  "originalName": "SK_createfolder",
  "remContentURIList": ["<list retrieved from /dcaportal/api/dashboard/vulScanData>"],
  "remediationInfo": {},
  "schedules": [],
  "securityGroup": "3ae0f8b5-7077-11e6-80fa-005056021034",
  "sharedFolderLocation": null,
  "vatsList": [{
   "assetId": "<Asset ID>",
   "targetId": "",
   "vulnerabilityId": "<VUlnerability ID>"
  }],
  "nshParameters": {
   "rootURIs": ["roots from /dcaportal/api/search/nsh_parameters"],
   "objects": [
    ["dcaportal.ElementManagerNSHScriptJobParameter/<GUID from dcaportal/api/search/nsh_parameters ", {
     "creationDate": null,
     "description": "",
     "modificationDate": null,
     "name": "<Parameter Name from dcaportal/api/search/nsh_parameters",
     "modelClass": null,
     "value": "tt",
     "isSkipFlag": false,
     "isReadOnly": false,
     "isSkipValue": false,
     "isAcceptValue": true,
     "isValueRequired": false,
     "isFlagRequired": false,
     "parameterID": 1,
     "externalID": null,
     "nshScriptParameterURI": "<externalID of parameter from dcaportal/api/search/nsh_parameters",
     "commandArgument": ""
    }]
   ]
  }
 }]
}

#e0f8b5-7077-11e6-80fa-005056021034

#
# vulnerability scans list
#
#      [
#        "dcaportal.VulnerabilityScan/c44f5d6e-f482-11e6-ac32-005056021003",
#        {
#          "scanDuration": null,
#          "name": "BDC BTD Scan - 20170113",
#          "reportType": null,
#          "description": "1637 records of 1637  were successfully imported.",
#          "scannedDate": "January 13, 2017 3:58:57 PM GMT",
#          "scanHost": "appliance not set",
#          "actualTargetsScanned": null,
#          "totalTargetsToBeScanned": null,
#          "recordStatus": "AVAILABLE",
#          "creationDate": "February 16, 2017 8:01:57 PM GMT",
#          "modificationDate": null,
#          "importedDate": "February 16, 2017 8:01:56 PM GMT",
#          "externalID": "scan/1484323137.36245",
#          "importedFileName": "Scan_Results_20170113_scan_1484323137_36245.xml",
#          "scannedBy": null,
#          "importedBy": "dcaportal.DCAPortalUser/3b0cc3af-7077-11e6-80fa-005056021034",
#          "product": "dcaportal.VulnerabilityProduct/3b34e522-7077-11e6-80fa-005056021034"
#        }
#      ],
#

#
# SecurityGroups
#
#[u'dcaportal.DCAPortalSite/37d4f133-7077-11e6-80fa-005056021034',
#              [u'dcaportal.DCAPortalSecurityGroup/3ae0f8b5-7077-11e6-80fa-005056021034',
#               {u'assetGroups': [],
#                u'authorizations': [u'dcaportal.DCAPortalAuthorization/3ae51769-7077-11e6-80fa-005056021034',
#                                    u'dcaportal.DCAPortalAuthorization/3ae53e7c-7077-11e6-80fa-005056021034',
#                                    u'dcaportal.DCAPortalAuthorization/3ae51767-7077-11e6-80fa-005056021034',
#                                    u'dcaportal.DCAPortalAuthorization/3ae51768-7077-11e6-80fa-005056021034',
#                                    u'dcaportal.DCAPortalAuthorization/3ae5176a-7077-11e6-80fa-005056021034',
#                                    u'dcaportal.DCAPortalAuthorization/3ae51766-7077-11e6-80fa-005056021034',
#                                    u'dcaportal.DCAPortalAuthorization/3ae5176b-7077-11e6-80fa-005056021034',
#                                    u'dcaportal.DCAPortalAuthorization/3ae53e7e-7077-11e6-80fa-005056021034',
#                                    u'dcaportal.DCAPortalAuthorization/3ae53e7d-7077-11e6-80fa-005056021034'],
#                u'creationDate': u'September 1, 2016 7:06:47 PM GMT',
#                u'defaultDepotPath': u'/Depot/Portal Operations',
#                u'defaultDepotURI': u'/id/SystemObject/Static Group/Abstract Depot Group/Depot Group/88d6654d-9eb8-483f-8ed2-a23bd378baa5',
#                u'defaultJobPath': u'/Jobs/Portal Operations',
#                u'defaultJobURI': u'/id/SystemObject/Static Group/Job Group/b48fdd1d-311a-4b3d-bc0a-51eab4af4bea',
#                u'deployTemplates': [],
#                u'description': u'Portal Administrator: BLAdmins',
#                u'emRoleExternalID': None,
#                u'emRoleName': u'BLAdmins',
#                u'modificationDate': u'September 30, 2016 11:10:51 PM GMT',
#                u'name': u'BLAdmins',
#                u'owner': None,
#                u'site': u'dcaportal.DCAPortalSite/37d4f133-7077-11e6-80fa-005056021034'}],


#pprint.pprint(j)
#pprint.pprint(j['searchResult'])

exit()


#
# let's get a list of the scans available
#

#heads={"content-type": "application/json", "ClientID": clientIdstr }
#body='{ "pageSize": 50, "pageNumber": 1, "sortedColumns": [{ "columnName": "importedDate", "ascending": false }], "filters": [] }'
#resp = requests.post(_url('/dcaportal/api/vulnerability/listAllScans'),headers=heads,data=body)





#
#  {'errorCode': None, 'taskId': None, 'results': 
#        {
#                'roots': ['dcaportal.DCAPortalSite/31a4a268-710f-11e6-9c18-005056021034', 'dcaportal.DCAPortalSite/37d4f133-7077-11e6-80fa-005056021034'], 
#                'objects': [
#                        ['dcaportal.DCAPortalSite/37d4f133-7077-11e6-80fa-005056021034', 
#                            {'isDashboardEnabled': None, 
#                                'name': 'bl-appserver', 
#                                'description': None, 
#                                'buildVersion': None, 
#                                'serverHost': 'bl-app', 
#                                'protocol': None, 
#                                'defaultDepotURI': None, 
#                                'isPrimarySite': True, 
#                                'defaultJobPath': None, 
#                                'port': None, 
#                                'emSiteAdminRoleName': None, 
#                                'externalID': None, 
#                                'creationDate': None, 
#                                'modificationDate': None, 
#                                'defaultJobURI': None, 
#                                'dashboardPort': None, 
#                                'defaultDepotPath': None, 
#                                'fileViewerViewableFileExtensions': None, 
#                                'defaultExportPath': None, 
#                                'emType': 'BSA'}
#                       ], 
#                       ['dcaportal.DCAPortalSite/31a4a268-710f-11e6-9c18-005056021034', {'isDashboardEnabled': None, 'name': 'bna', 'description': None, 'buildVersion': None, 'serverHost': 'bna', 'protocol': None, 'defaultDepotURI': None, 'isPrimarySite': True, 'defaultJobPath': None, 'port': None, 'emSiteAdminRoleName': None, 'externalID': None, 'creationDate': None, 'modificationDate': None, 'defaultJobURI': None, 'dashboardPort': None, 'defaultDepotPath': None, 'fileViewerViewableFileExtensions': None, 'defaultExportPath': None, 'emType': 'BNA'}]]}}
#
