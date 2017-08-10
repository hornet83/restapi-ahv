#!/usr/bin/env python
import time
import json
import warnings
import sys
import requests
import salt.client
import urllib3
requests.packages.urllib3.disable_warnings()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

## usage: python deletevm_v2.py <vm_name>

caller = salt.client.Caller()
pillardata = caller.function('pillar.items')

username = pillardata['env']['login']
password = pillardata['env']['password']
cluster_ip = pillardata['env']['clusterip']
base_url = ("https://%s:9440/PrismGateway/services/rest/v2.0/" % (cluster_ip))
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


  def poll_task(self, task_uuid):
    url = base_url+"tasks/poll"

    specs = []
    specs.append(task_uuid)
    uuidSpec = {}
    uuidSpec["completed_tasks"] = specs
    print uuidSpec

    while True:
      print("Polling task %s for completion" % (task_uuid,))
      r = self.session.post(url, data=json.dumps(uuidSpec))
      if r.status_code != 201:
        raise Exception("GET %s: %s" % (url, r.status_code))

      obj = r.json()
      for entry in obj['completed_tasks_info']:
        mr = entry['meta_response']['error_code']

      if mr is None:
        continue
      if mr is 0:
        break
      else:
        raise Exception("Task %s failed with error code: %s" %
            (task_uuid, mr))


  def resolve_vm_uuid(self, vm_name):
    url = base_url + "/vms/"
    r = self.session.get(url)

    if r.status_code != requests.codes.ok:
      raise Exception("GET %s: %s" % (url, r.status_code))

    obj = r.json()
    uuid = [x["uuid"] for x in obj["entities"] if x["name"] == vm_name]
    uuidentry = uuid[0]
    return uuidentry


  def delete_vm(self, vm_uuid, vm_name):
    url = base_url + "vms/"+str(vm_uuid)+"/?delete_snapshots=true"

    print ("STARTING DELETE OF " + vm_name, time.strftime("%H:%M:%S"))

    r = self.session.delete(url)
    if r.status_code != 201:
      raise Exception("POST %s: %s" % (url, r.status_code))

    task_uuid = r.json()["task_uuid"]
    self.poll_task(task_uuid)
    print ("DELETED " + vm_name, time.strftime("%H:%M:%S"))


def main():
  ## get vm uuid from vm name
  c = RestApiClient(cluster_ip, username, password)
  vm_uuid = c.resolve_vm_uuid(vm_name)
  c.delete_vm(vm_uuid, vm_name)

if __name__ == "__main__":
  main()
