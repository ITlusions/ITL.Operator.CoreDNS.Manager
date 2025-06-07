import kopf
from base import load_k8s_config
from k8s_client import list_all_dnszones, update_coredns_configmap

import logging
import os

load_k8s_config()

configmap_name = os.getenv('COREDNS_CONFIGMAP_NAME', 'coredns_custom')
configmap_namespace = os.getenv('COREDNS_CONFIGMAP_NAMESPACE', 'kube-system')

group = os.getenv('DNSZONE_CRD_GROUP', 'itlusions.io')
version = os.getenv('DNSZONE_CRD_VERSION', 'v1')
plural = os.getenv('DNSZONE_CRD_PLURAL', 'dnszones')


@kopf.on.startup()
def configure(settings: kopf.OperatorSettings, **_):
    settings.posting.level = logging.INFO
    logging.info("Starting DNSZone operator")

@kopf.on.event(group, version, plural)
def on_dnszone_event(event, **kwargs):
    obj = event.get('object', {})
    name = obj.get('metadata', {}).get('name')
    ns = obj.get('metadata', {}).get('namespace')
    event_type = event.get('type')
    logging.info(f"Event {event_type} on DNSZone {ns}/{name}")

    zones = list_all_dnszones(group=group, version=version, plural=plural)
    update_coredns_configmap(zones, configmap_name=configmap_name, configmap_namespace=configmap_namespace)
