# DNS Operator

This operator manages `DNSZone` CRDs cluster-wide and aggregates them into a single CoreDNS ConfigMap.

## Features
- Watches `DNSZone` CRDs across all namespaces.
- Generates CoreDNS Corefile with support for `A`, `CNAME`, `TXT`, and `SRV` records.
- Adds namespace comments to zones for clarity.
- Updates CoreDNS ConfigMap in the `kube-system` namespace.


## Deployment

### Prerequisites
1. **Kubernetes Cluster**: Ensure you have access to a running Kubernetes cluster.
2. **kubectl**: Install `kubectl` to interact with your cluster.
3. **CoreDNS**: Ensure CoreDNS is deployed in your cluster and is configured to use the ConfigMap managed by this operator.

### Steps to Deploy
1. **Apply the CustomResourceDefinition (CRD)**:
   Deploy the `DNSZone` CRD to your cluster:
   ```bash
   kubectl apply -f manifest/crd_dnszone.yaml
   ```

2. **Set Up RBAC**:
   Apply the RBAC configuration to grant the operator the necessary permissions:
   ```bash
   kubectl apply -f manifest/rbac.yaml
   ```

3. **Deploy the Operator**:
   Deploy the operator using the provided deployment manifest:
   ```bash
   kubectl apply -f manifest/deployment.yaml
   ```

4. **Verify Deployment**:
   Check that the operator is running:
   ```bash
   kubectl get pods -n kube-system
   ```



## Usage

### Create a DNSZone Resource
1. Define a `DNSZone` resource in a YAML file (e.g., `example-dnszone.yaml`):
   ```yaml
   apiVersion: itlusions.io/v1
   kind: DNSZone
   metadata:
     name: example-zone
     namespace: default
   spec:
     zone: example.com
     records:
       - type: A
         name: www
         value: 192.168.1.1
         ttl: 300
   ```

2. Apply the resource to your cluster:
   ```bash
   kubectl apply -f example-dnszone.yaml
   ```

### Verify CoreDNS ConfigMap
The operator will update the CoreDNS ConfigMap (`coredns_custom`) in the `kube-system` namespace. Verify the changes:
```bash
kubectl get configmap coredns_custom -n kube-system -o yaml
```

### Logs and Debugging
To monitor the operator's activity, check its logs:
```bash
kubectl logs -l app=dns-operator -n kube-system
```


## Environment Variables
The operator uses the following environment variables for configuration:

| Variable Name              | Default Value       | Description                                      |
|----------------------------|---------------------|--------------------------------------------------|
| `COREDNS_CONFIGMAP_NAME`   | `coredns_custom`    | Name of the CoreDNS ConfigMap to update.         |
| `COREDNS_CONFIGMAP_NAMESPACE` | `kube-system`   | Namespace of the CoreDNS ConfigMap.              |
| `DNSZONE_CRD_GROUP`        | `itlusions.io`      | API group of the `DNSZone` CRD.                 |
| `DNSZONE_CRD_VERSION`      | `v1`               | API version of the `DNSZone` CRD.               |
| `DNSZONE_CRD_PLURAL`       | `dnszones`         | Plural name of the `DNSZone` CRD.               |

---

## Development

### Run Locally
1. Install dependencies:
   ```bash
   pip install kopf kubernetes python-dotenv
   ```

2. Set environment variables:
   ```bash
   export COREDNS_CONFIGMAP_NAME=coredns_custom
   export COREDNS_CONFIGMAP_NAMESPACE=kube-system
   export DNSZONE_CRD_GROUP=itlusions.io
   export DNSZONE_CRD_VERSION=v1
   export DNSZONE_CRD_PLURAL=dnszones
   ```

3. Run the operator:
   ```bash
   kopf run src/operator/main.py
   ```

### Test Locally
- Apply the `DNSZone` CRD and create a sample resource as described in the **Usage** section.
- Monitor the logs to ensure the operator processes the events correctly.

## Uninstall
To remove the operator and its resources from your cluster:
```bash
kubectl delete -f deployment.yaml
kubectl delete -f rbac.yaml
kubectl delete -f crd_dnszone.yaml
```


## Notes
- Ensure that the CoreDNS deployment is configured to use the ConfigMap managed by this operator.
- The operator is designed to work with Kubernetes clusters where CoreDNS is the DNS provider.
