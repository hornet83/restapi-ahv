#!/usr/bin/env python
import json
import warnings
import sys
import requests
import urllib3
requests.packages.urllib3.disable_warnings()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

## usage: python getuuid_v2.py <vm_name>

username = "xxx"
password = "xxx"
cluster_ip = "cluster.nutanix.local"
base_url = "https://cluster.nutanix.local:9440/PrismGateway/services/rest/v2.0/"
vm_name = sys.argv[1]

class RestApiClient():

  def __init__(self, cluster_ip, username, password):
    self.cluster_ip = cluster_ip
    self.username = username
    self.password = password
    self.base_pg_url = ("https://%s:9440/PrismGateway/services/rest/v2.0" % (self.cluster_ip,))
    self.session = self.get_server_session(self.username, self.password)

  def get_server_session(self, username, password):
    session = requests.Session()
    session.auth = (username, password)
    session.verify = False
    session.headers.update(
        {'Content-Type': 'application/json; charset=utf-8'})
    return session

  def resolve_vm_uuid(self, vm_name):
    url = base_url + "/vms/"
    r = self.session.get(url)

    if r.status_code != requests.codes.ok:
      raise Exception("GET %s: %s" % (url, r.status_code))

    obj = r.json()
    uuid = [x["uuid"] for x in obj["entities"] if x["name"] == vm_name]
    uuidentry = uuid[0]
    return uuidentry


def main():
  ## get vm uuid from vm name
  c = RestApiClient(cluster_ip, username, password)
  vm_uuid = c.resolve_vm_uuid(vm_name)
  print vm_uuid

if __name__ == "__main__":
  main()
