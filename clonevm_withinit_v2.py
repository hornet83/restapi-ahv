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
import re
import urllib3
requests.packages.urllib3.disable_warnings()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

vm_name = sys.argv[1]
clonename = sys.argv[2]
numvcpus = sys.argv[3]
numvcpucores = sys.argv[4]
memory_mb = sys.argv[5]
ip_address = sys.argv[6]

if re.search('oracle', vm_name):
  cloud_init = ("/srv/cloudinit/oracle")
else:
  cloud_init = ("/srv/cloudinit/appserver")

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
    uuidentry = uuid[0]
    return uuidentry


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


  def construct_vm_clone_proto(self, vm_uuid):
    vm_clone_proto = {
         "numvcpus": numvcpus,
         "num_cores_per_vcpu": numvcpucores,
         "name": clonename,
         "memory_mb": memory_mb,
    }
    specs = []
    name = vm_clone_proto["name"]
    print("Creating Clone of VM %s" %vm_clone_proto["name"])
    specs.append(self._strip_empty_fields(vm_clone_proto))

    with open(cloud_init, 'r') as f:
      data=f.read()

    data = data.replace('ipaddress', ip_address)
    data = data.replace('servername', clonename)

    print data

    vm_cust = {
         "userdata":("""%s""" % (data))
    }

    return {"spec_list": specs, "vm_customization_config": vm_cust}


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


  def create_clones(self, vm_uuid):
    cloneSpec = self.construct_vm_clone_proto(vm_uuid)
    url = base_url + "vms/"+str(vm_uuid)+"/clone"

    print ("CLONE START TIME", time.strftime("%H:%M:%S"))
    r = self.session.post(url, data=json.dumps(cloneSpec))
    if r.status_code != 201:
      raise Exception("POST %s: %s" % (url, r.status_code))

    task_uuid = r.json()["task_uuid"]
    self.poll_task(task_uuid)
    print ("CLONE END TIME", time.strftime("%H:%M:%S"))


def main():
  ## get vm uuid from vm name
  c = RestApiClient(cluster_ip, username, password)
  vm_uuid = c.resolve_vm_uuid(vm_name)
  c.create_clones(vm_uuid)

if __name__ == "__main__":
  main()
