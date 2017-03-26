import requests, json

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
    else:
      print('saw another site')

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
print("Client ID string is: " + clientIdstr)

#else:
#       print('apparently did not authenticate: ' + resp.text)

#
# lets get our security group ID
#

heads={"ClientID": clientIdstr, "Content-Type": "application/json" }
resp = requests.post(_url('/dcaportal/api/bsmsearch/mySecurityGroups'),'',headers=heads)

if resp.status_code != 200:
    # This means something went wrong.
    raise ApiError('GET /tasks/ {}'.format(resp.status_code))

print(resp.text)


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
