#!/usr/bin/env python
import json 
import requests
import warnings
import requests
import requests
import urllib3
requests.packages.urllib3.disable_warnings()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def main():
 
  base_url = "https://cluster.nutanix.local:9440/PrismGateway/services/rest/v2.0/"
  s = requests.Session()
  s.auth = ('admin', 'nx2Tech666!')
  s.headers.update({'Content-Type': 'application/json; charset=utf-8'})

  data = s.get(base_url + 'vms', verify=False).json()

  for e in data["entities"]:
      print e["name"]
  
if __name__ == "__main__":
  main()
