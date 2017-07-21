import salt.config
import salt.loader

__opts__ = salt.config.minion_config('/etc/salt/minion')
__grains__ = salt.loader.grains(__opts__)
__pillar__ = salt.loader.pillars(__opts__)
print __grains__['id']
print __pillar__
