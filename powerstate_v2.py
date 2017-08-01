#!/usr/bin/env python
import json 
import warnings
import errno
import os
import requests
import shutil
import traceback
import urllib
import uuid
import time
import sys
import urllib3
requests.packages.urllib3.disable_warnings()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

## usage: python  powerstate_v2.py <vmname> <ON|OFF>

vm_name = sys.argv[1]
powerstate = sys.argv[2]

cluster_ip = "cluster.nutanix.local"
base_url = ("https://%s:9440/PrismGateway/services/rest/v2.0/" % (cluster_ip))
username = "admin"
password = "nx2Tech666!"

class RestApiClient():

  def __init__(self, cluster_ip, username, password):
    self.cluster_ip = cluster_ip
    self.username = username
    self.password = password
    self.base_pg_url = base_url
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
    return uuid[0]


  def _strip_empty_fields(self, proto_dict):
    def strip_dict(d):
      if type(d) is dict:
        return dict((k, strip_dict(v))\
                    for k,v in d.iteritems() if v and strip_dict(v))
      if type(d) is list:
        return [strip_dict(v) for v in d if v and strip_dict(v)]
      else:
        return d
    return strip_dict(proto_dict)


  def construct_vm_power_proto(self, vm_uuid):
    return {"transition": powerstate}


  def poll_task(self, task_uuid):
    url = base_url+"tasks/poll"

    specs = []
    specs.append(task_uuid)
    uuidSpec = {}
    uuidSpec["completed_tasks"] = specs

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


  def set_power_state(self, vm_uuid):
    cloneSpec = self.construct_vm_power_proto(vm_uuid)
    url = base_url + "vms/"+str(vm_uuid)+"/set_power_state/"

    print ("TASK START TIME", time.strftime("%H:%M:%S"))
    r = self.session.post(url, data=json.dumps(cloneSpec))
    if r.status_code != 201:
      raise Exception("POST %s: %s" % (url, r.status_code))

    task_uuid = r.json()["task_uuid"]
    self.poll_task(task_uuid)
    print ("TASK END TIME", time.strftime("%H:%M:%S"))


def main():
  c = RestApiClient(cluster_ip, username, password)
  vm_uuid = c.resolve_vm_uuid(vm_name)
  c.set_power_state(vm_uuid)


if __name__ == "__main__":
  main()
