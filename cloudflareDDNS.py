#!/usr/bin/env python3
"""
This code is largely from
https://raw.githubusercontent.com/cloudflare/python-cloudflare/master/examples/example_update_dynamic_dns.py
"""

import os
import sys
import re
import json
import requests

import CloudFlare

def do_dns_update(cf, zone_name, zone_id, dns_name, ip_address, ip_address_type):
    try:
        params = {'name':dns_name, 'match':'all', 'type':ip_address_type}
        dns_records = cf.zones.dns_records.get(zone_id, params=params)
    except CloudFlare.exceptions.CloudFlareAPIError as e:
        exit('/zones/dns_records %s - %d %s - api call failed' % (dns_name, e, e))

    updated = False
    unchanged = True

    # update the record - unless it's already correct
    for dns_record in dns_records:
        old_ip_address = dns_record['content']
        old_ip_address_type = dns_record['type']

        if ip_address_type != old_ip_address_type:
            continue

        if ip_address == old_ip_address:
            updated = True
            continue

        # Yes, we need to update this record - we know it's the same address type

        dns_record_id = dns_record['id']
        dns_record = {
            'name':dns_name,
            'type':ip_address_type,
            'content':ip_address,
            'proxied':True
        }
        try:
            dns_record = cf.zones.dns_records.put(zone_id, dns_record_id, data=dns_record)
        except CloudFlare.exceptions.CloudFlareAPIError as e:
            exit('/zones.dns_records.put %s - %d %s - api call failed' % (dns_name, e, e))
        print('good')
        unchanged = False
        updated = True

    if updated:
        if unchanged:
            print('nochg')
        return

    # no exsiting dns record to update - so create dns record
    dns_record = {
        'name':dns_name,
        'type':ip_address_type,
        'content':ip_address
    }
    try:
        dns_record = cf.zones.dns_records.post(zone_id, data=dns_record)
    except CloudFlare.exceptions.CloudFlareAPIError as e:
        exit('/zones.dns_records.post %s - %d %s - api call failed' % (dns_name, e, e))
    print('good')

if __name__ == '__main__':
    try:
        email = sys.argv[1]
        api_key = sys.argv[2]
        dns_name = sys.argv[3]
        ip_address = sys.argv[4]
    except IndexError:
        # Synology gives the parameters in this particular order.
        exit('usage: cloudflareDDNS.py <username> <api_key> <hostname> <ip_address>')

    host_name, zone_name = dns_name.split('.', 1)
    ip_address_type = 'AAAA' if ':' in ip_address else 'A'

    cf = CloudFlare.CloudFlare(email=email, token=api_key)

    # grab the zone identifier
    try:
        params = {'name':zone_name}
        zones = cf.zones.get(params=params)
    except CloudFlare.exceptions.CloudFlareAPIError as e:
        print('badauth')
        exit()
    except Exception as e:
        exit('/zones.get - %s - api call failed' % (e))

    if len(zones) == 0:
        print('nohost')
        exit()

    if len(zones) != 1:
        exit('/zones.get - %s - api call returned %d items' % (zone_name, len(zones)))

    zone = zones[0]
    do_dns_update(cf, zone['name'], zone['id'], dns_name, ip_address, ip_address_type)
    exit(0)
