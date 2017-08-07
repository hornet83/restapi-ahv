#!/usr/bin/env python
import json
import warnings
import sys
import requests
import salt.client
import urllib3
requests.packages.urllib3.disable_warnings()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

## usage: python getipaddr_v2.py <vm_name> <vlan_name>

caller = salt.client.Caller()
pillardata = caller.function('pillar.items')

username = pillardata['env']['login']
password = pillardata['env']['password']
cluster_ip = pillardata['env']['clusterip']
base_url = ("https://%s:9440/PrismGateway/services/rest/v2.0/" % (cluster_ip))

vm_name = sys.argv[1]
vlan_name = sys.argv[2]

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


  def resolve_vlanid(self, vlan_name):
    url = base_url + "networks/"
    r = self.session.get(url)

    if r.status_code != requests.codes.ok:
      raise Exception("GET %s: %s" % (url, r.status_code))

    obj = r.json()
    id = [x["uuid"] for x in obj["entities"] if x["name"] == vlan_name]
    return id[0]


  def resolve_vm_uuid(self, vm_name):
    url = base_url + "/vms/"
    r = self.session.get(url)

    if r.status_code != requests.codes.ok:
      raise Exception("GET %s: %s" % (url, r.status_code))

    obj = r.json()
    uuid = [x["uuid"] for x in obj["entities"] if x["name"] == vm_name]
    return uuid[0]


  def get_vm_ipaddress(self, vm_uuid, vlanid):
    url = base_url + "networks/" + vlanid + "/addresses"
    r = self.session.get(url)

    if r.status_code != requests.codes.ok:
      raise Exception("GET %s: %s" % (url, r.status_code))

    obj = r.json()
    ip = [x["ip_address"] for x in obj["entities"] if x["entity_uuid"] == vm_uuid]
    return ip[0]


def main():
  ## get vm uuid from vm name
  c = RestApiClient(cluster_ip, username, password)
  vlanid = c.resolve_vlanid(vlan_name)
  vm_uuid = c.resolve_vm_uuid(vm_name)
  vm_ip = c.get_vm_ipaddress(vm_uuid, vlanid)
  print vm_ip


if __name__ == "__main__":
  main()
