#!/usr/bin/env python
import json 
import requests
import warnings
import requests
import requests
import salt.client
import urllib3
requests.packages.urllib3.disable_warnings()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

caller = salt.client.Caller()
pillardata = caller.function('pillar.items')

username = pillardata['env']['login']
password = pillardata['env']['password']
cluster_ip = pillardata['env']['clusterip']

def main():
 
  base_url = ("https://%s:9440/PrismGateway/services/rest/v2.0/" % (cluster_ip))
  s = requests.Session()
  s.auth = (username, password)
  s.headers.update({'Content-Type': 'application/json; charset=utf-8'})

  data = s.get(base_url + 'vms', verify=False).json()

  for e in data["entities"]:
      print e["name"]
  
if __name__ == "__main__":
  main()
