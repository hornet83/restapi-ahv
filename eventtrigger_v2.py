#!/bin/env python
import salt.config
import salt.utils.event
import salt.client
import sys
import time
import json
import sys
import warnings
import requests
import urllib3
requests.packages.urllib3.disable_warnings()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

local = salt.client.LocalClient()
caller = salt.client.Caller()
pillardata = caller.function('pillar.items')

event_trigger = sys.argv[1]
env = sys.argv[2]

opts = salt.config.client_config('/etc/salt/master')
event = salt.utils.event.get_event(
        'master',
        sock_dir=opts['sock_dir'],
        transport=opts['transport'],
        opts=opts)

for minion in pillardata[env].iteritems():
   while True:
      data = event.get_event(tag=event_trigger)
      if data is None:
         continue
      else:
         data = local.cmd('saltmaster*', 'mine.get', [data['id'], 'network.ip_addrs'])
         print data
         break
