#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright Tristan Le Guern (@tleguern) <tleguern at bouledef.eu>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: proxmox_domain_info
short_description: Retrieve information about one or more Proxmox VE domains
version_added: 1.3.0
description:
  - Retrieve information about one or more Proxmox VE domains.
attributes:
  action_group:
    version_added: 9.0.0
options:
  domain:
    description:
      - Restrict results to a specific authentication realm.
    aliases: ['realm', 'name']
    type: str
author: Tristan Le Guern (@tleguern)
extends_documentation_fragment:
  - community.general.proxmox.actiongroup_proxmox
  - community.general.proxmox.documentation
  - community.general.attributes
  - community.general.attributes.info_module
'''


EXAMPLES = '''
- name: List existing domains
  community.general.proxmox_domain_info:
    api_host: helldorado
    api_user: root@pam
    api_password: "{{ password | default(omit) }}"
    api_token_id: "{{ token_id | default(omit) }}"
    api_token_secret: "{{ token_secret | default(omit) }}"
  register: proxmox_domains

- name: Retrieve information about the pve domain
  community.general.proxmox_domain_info:
    api_host: helldorado
    api_user: root@pam
    api_password: "{{ password | default(omit) }}"
    api_token_id: "{{ token_id | default(omit) }}"
    api_token_secret: "{{ token_secret | default(omit) }}"
    domain: pve
  register: proxmox_domain_pve
'''


RETURN = '''
proxmox_domains:
    description: List of authentication domains.
    returned: always, but can be empty
    type: list
    elements: dict
    contains:
      comment:
        description: Short description of the realm.
        returned: on success
        type: str
      realm:
        description: Realm name.
        returned: on success
        type: str
      type:
        description: Realm type.
        returned: on success
        type: str
      digest:
        description: Realm hash.
        returned: on success, can be absent
        type: str
'''


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.proxmox import (
    proxmox_auth_argument_spec, ProxmoxAnsible)


class ProxmoxDomainInfoAnsible(ProxmoxAnsible):
    def get_domain(self, realm):
        try:
            domain = self.proxmox_api.access.domains.get(realm)
        except Exception:
            self.module.fail_json(msg="Domain '%s' does not exist" % realm)
        domain['realm'] = realm
        return domain

    def get_domains(self):
        domains = self.proxmox_api.access.domains.get()
        return domains


def proxmox_domain_info_argument_spec():
    return dict(
        domain=dict(type='str', aliases=['realm', 'name']),
    )


def main():
    module_args = proxmox_auth_argument_spec()
    domain_info_args = proxmox_domain_info_argument_spec()
    module_args.update(domain_info_args)

    module = AnsibleModule(
        argument_spec=module_args,
        required_together=[('api_token_id', 'api_token_secret')],
        supports_check_mode=True
    )
    result = dict(
        changed=False
    )

    proxmox = ProxmoxDomainInfoAnsible(module)
    domain = module.params['domain']

    if domain:
        domains = [proxmox.get_domain(realm=domain)]
    else:
        domains = proxmox.get_domains()
    result['proxmox_domains'] = domains

    module.exit_json(**result)


if __name__ == '__main__':
    main()
