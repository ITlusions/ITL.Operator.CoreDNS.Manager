import os
import logging
import kubernetes.client
from base.corefile_builder import build_coredns_corefile

# Get ConfigMap name and namespace from environment variables
configmap_name = os.getenv('COREDNS_CONFIGMAP_NAME', 'coredns_custom')
configmap_namespace = os.getenv('COREDNS_CONFIGMAP_NAMESPACE', 'kube-system')

group = os.getenv('DNSZONE_CRD_GROUP', 'itlusions.io')
version = os.getenv('DNSZONE_CRD_VERSION', 'v1')
plural = os.getenv('DNSZONE_CRD_PLURAL', 'dnszones')

def list_all_dnszones():
    crd_api = kubernetes.client.CustomObjectsApi()
    all_zones = []
    try:
        zones = crd_api.list_cluster_custom_object(
            group=group,
            version=version,
            plural=plural,
        )
        all_zones.extend(zones.get('items', []))
    except kubernetes.client.exceptions.ApiException as e:
        logging.error(f"Error listing DNSZones: {e}")
    return all_zones

def update_coredns_configmap(zones):
    corefile = build_coredns_corefile(zones)

    configmap = kubernetes.client.V1ConfigMap(
        metadata=kubernetes.client.V1ObjectMeta(name=configmap_name, namespace=configmap_namespace),
        data={"Corefile": corefile}
    )
    try:
        core_v1_api = kubernetes.client.CoreV1Api()
        core_v1_api.patch_namespaced_config_map(configmap_name, configmap_namespace, configmap)
        logging.info(f"Patched ConfigMap {configmap_name} in {configmap_namespace}")
    except kubernetes.client.exceptions.ApiException as e:
        if e.status == 404:
            core_v1_api.create_namespaced_config_map(configmap_namespace, configmap)
            logging.info(f"Created ConfigMap {configmap_name} in {configmap_namespace}")
        else:
            logging.error(f"Failed to update ConfigMap: {e}")
            raise
