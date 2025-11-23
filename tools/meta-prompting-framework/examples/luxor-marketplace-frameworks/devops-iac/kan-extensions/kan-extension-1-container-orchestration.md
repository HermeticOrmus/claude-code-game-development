# Kan Extension 1: Container Orchestration Patterns

## Overview

This first Kan extension focuses on advanced container orchestration patterns, extending the base framework with sophisticated container management strategies and service mesh capabilities.

## Mathematical Foundation

### Left Kan Extension

```
    C ---F---> D
    |         ^
  G |        / Lan_F G
    v       /
    E ----'
```

Where:
- **C**: Container configurations
- **D**: Orchestrated deployments
- **E**: Extended orchestration patterns
- **F**: Basic orchestration functor
- **G**: Pattern enhancement functor
- **Lan_F G**: Left Kan extension for pattern optimization

## Extended Orchestration Patterns

### 1. Multi-Stage Service Mesh

```yaml
# Istio service mesh configuration
apiVersion: install.istio.io/v1alpha1
kind: IstioOperator
metadata:
  name: production-mesh
spec:
  profile: production
  components:
    pilot:
      k8s:
        resources:
          requests:
            cpu: 1000m
            memory: 1024Mi
        hpaSpec:
          maxReplicas: 5
          minReplicas: 2
          metrics:
          - type: Resource
            resource:
              name: cpu
              target:
                type: Utilization
                averageUtilization: 60

    ingressGateways:
    - name: istio-ingressgateway
      enabled: true
      k8s:
        service:
          type: LoadBalancer
          ports:
          - port: 80
            targetPort: 8080
            name: http
          - port: 443
            targetPort: 8443
            name: https

  meshConfig:
    defaultConfig:
      proxyStatsMatcher:
        inclusionRegexps:
        - ".*outlier_detection.*"
        - ".*circuit_breakers.*"
        - ".*retry.*"
    accessLogFile: /dev/stdout
    defaultProviders:
      metrics:
      - prometheus
```

### 2. Advanced Container Scheduling

```yaml
# Pod scheduling with topology spread constraints
apiVersion: apps/v1
kind: Deployment
metadata:
  name: distributed-app
spec:
  replicas: 10
  template:
    spec:
      topologySpreadConstraints:
      - maxSkew: 1
        topologyKey: topology.kubernetes.io/zone
        whenUnsatisfiable: DoNotSchedule
        labelSelector:
          matchLabels:
            app: distributed-app
      - maxSkew: 1
        topologyKey: kubernetes.io/hostname
        whenUnsatisfiable: ScheduleAnyway
        labelSelector:
          matchLabels:
            app: distributed-app

      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - distributed-app
              topologyKey: kubernetes.io/hostname

        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
            - matchExpressions:
              - key: node-type
                operator: In
                values:
                - compute-optimized
                - memory-optimized
```

### 3. Container Runtime Security

```yaml
# Pod Security Policy with runtime protection
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: restricted-psp
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
    - ALL
  volumes:
    - 'configMap'
    - 'emptyDir'
    - 'projected'
    - 'secret'
    - 'downwardAPI'
    - 'persistentVolumeClaim'
  hostNetwork: false
  hostIPC: false
  hostPID: false
  runAsUser:
    rule: 'MustRunAsNonRoot'
  seLinux:
    rule: 'RunAsAny'
  supplementalGroups:
    rule: 'RunAsAny'
  fsGroup:
    rule: 'RunAsAny'
  readOnlyRootFilesystem: true
---
# Falco runtime security rules
- rule: Unexpected process in container
  desc: Detect processes that are not expected in container
  condition: >
    container and
    not container.image.repository in (trusted_repos) and
    proc.name not in (allowed_processes)
  output: >
    Unexpected process started in container
    (user=%user.name command=%proc.cmdline container=%container.name image=%container.image.repository)
  priority: WARNING

- rule: Container drift detected
  desc: Detect when container filesystem is modified
  condition: >
    container and
    evt.type in (open, openat) and
    evt.is_open_write=true and
    fd.typechar='f' and
    fd.num>=0 and
    container.image.repository != "" and
    not fd.name in (allowed_write_paths)
  output: >
    Container filesystem modified
    (user=%user.name command=%proc.cmdline file=%fd.name container=%container.name)
  priority: ERROR
```

### 4. Stateful Container Patterns

```yaml
# StatefulSet with persistent volumes
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: distributed-database
spec:
  serviceName: database-service
  replicas: 3
  selector:
    matchLabels:
      app: distributed-database
  template:
    metadata:
      labels:
        app: distributed-database
    spec:
      initContainers:
      - name: init-database
        image: database:init
        command:
        - bash
        - -c
        - |
          set -ex
          # Initialize replica set configuration
          if [[ $HOSTNAME =~ -0$ ]]; then
            # Primary node initialization
            /scripts/init-primary.sh
          else
            # Secondary node initialization
            /scripts/init-secondary.sh
          fi
        volumeMounts:
        - name: data
          mountPath: /var/lib/database
        - name: init-scripts
          mountPath: /scripts

      containers:
      - name: database
        image: database:v1.0.0
        ports:
        - containerPort: 5432
          name: database
        env:
        - name: REPLICATION_MODE
          value: "master-slave"
        - name: REPLICATION_USER
          valueFrom:
            secretKeyRef:
              name: database-secret
              key: replication-user
        volumeMounts:
        - name: data
          mountPath: /var/lib/database
        - name: config
          mountPath: /etc/database
        livenessProbe:
          exec:
            command:
            - /bin/sh
            - -c
            - pg_isready -U postgres
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          exec:
            command:
            - /bin/sh
            - -c
            - pg_isready -U postgres && psql -U postgres -c "SELECT 1"
          initialDelaySeconds: 5
          periodSeconds: 5

  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: fast-ssd
      resources:
        requests:
          storage: 100Gi
```

### 5. Sidecar Container Patterns

```yaml
# Deployment with multiple sidecar patterns
apiVersion: apps/v1
kind: Deployment
metadata:
  name: microservice-with-sidecars
spec:
  template:
    spec:
      containers:
      # Main application container
      - name: app
        image: myapp:v1.0.0
        ports:
        - containerPort: 8080
        volumeMounts:
        - name: logs
          mountPath: /var/log/app

      # Logging sidecar
      - name: log-forwarder
        image: fluentbit/fluent-bit:latest
        volumeMounts:
        - name: logs
          mountPath: /var/log/app
        - name: fluent-bit-config
          mountPath: /fluent-bit/etc/
        env:
        - name: FLUENT_ELASTICSEARCH_HOST
          value: "elasticsearch.logging.svc.cluster.local"

      # Proxy sidecar (Envoy)
      - name: envoy-proxy
        image: envoyproxy/envoy:v1.24.0
        ports:
        - containerPort: 9901
          name: admin
        - containerPort: 10000
          name: proxy
        volumeMounts:
        - name: envoy-config
          mountPath: /etc/envoy
        command:
        - /usr/local/bin/envoy
        - -c
        - /etc/envoy/envoy.yaml
        - --service-cluster
        - myapp
        - --service-node
        - ${POD_NAME}
        env:
        - name: POD_NAME
          valueFrom:
            fieldRef:
              fieldPath: metadata.name

      # Metrics sidecar
      - name: prometheus-exporter
        image: prom/node-exporter:latest
        ports:
        - containerPort: 9100
          name: metrics
        resources:
          requests:
            memory: "30Mi"
            cpu: "10m"

      volumes:
      - name: logs
        emptyDir: {}
      - name: fluent-bit-config
        configMap:
          name: fluent-bit-config
      - name: envoy-config
        configMap:
          name: envoy-config
```

## Categorical Extensions

### Container Composition Functor

```haskell
-- Container composition with categorical structure
data Container = Container {
    image :: Image,
    env :: Environment,
    volumes :: [Volume],
    ports :: [Port]
}

-- Functor for container transformation
instance Functor ContainerF where
    fmap :: (a -> b) -> ContainerF a -> ContainerF b
    fmap f (ContainerF img env vols ports meta) =
        ContainerF (f img) (fmap f env) (fmap f vols) (fmap f ports) (f meta)

-- Natural transformation for sidecar injection
sidecarInject :: Container -> CompositeContainer
sidecarInject mainContainer = CompositeContainer {
    containers = [mainContainer, loggingSidecar, proxySidecar],
    sharedVolumes = extractSharedVolumes mainContainer,
    networkPolicy = meshNetworkPolicy
}
```

### Service Mesh Category

```haskell
-- Service mesh as a monoidal category
data ServiceMesh = ServiceMesh {
    dataPlane :: [Proxy],
    controlPlane :: ControlPlane,
    policies :: [Policy]
}

-- Tensor product for service composition
(⊗) :: Service -> Service -> ServiceMesh
service1 ⊗ service2 = ServiceMesh {
    dataPlane = [createProxy service1, createProxy service2],
    controlPlane = unifiedControl [service1, service2],
    policies = mergePolicies (policies service1) (policies service2)
}

-- Identity service
identityService :: Service
identityService = PassthroughService
```

## Implementation Examples

### 1. Complete Container Orchestration Setup

```bash
#!/bin/bash
# setup-orchestration.sh

# Install Istio service mesh
curl -L https://istio.io/downloadIstio | sh -
cd istio-*
export PATH=$PWD/bin:$PATH
istioctl install --set profile=production -y

# Label namespace for sidecar injection
kubectl label namespace production istio-injection=enabled

# Deploy Falco for runtime security
helm repo add falcosecurity https://falcosecurity.github.io/charts
helm install falco falcosecurity/falco \
  --set falco.grpc.enabled=true \
  --set falco.grpcOutput.enabled=true

# Install OPA for policy enforcement
kubectl apply -f https://raw.githubusercontent.com/open-policy-agent/opa-gatekeeper/release-3.14/deploy/gatekeeper.yaml

# Deploy Prometheus and Grafana
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack

# Configure distributed tracing with Jaeger
kubectl create namespace observability
kubectl apply -n observability -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/master/deploy/crds/jaegertracing.io_jaegers_crd.yaml
kubectl apply -n observability -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/master/deploy/service_account.yaml
kubectl apply -n observability -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/master/deploy/role.yaml
kubectl apply -n observability -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/master/deploy/role_binding.yaml
kubectl apply -n observability -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/master/deploy/operator.yaml
```

### 2. Advanced Deployment Strategy

```python
# advanced_deployer.py
import kubernetes
from kubernetes import client, config
import time
from typing import List, Dict, Optional

class AdvancedDeployer:
    def __init__(self):
        config.load_incluster_config()
        self.apps_v1 = client.AppsV1Api()
        self.core_v1 = client.CoreV1Api()
        self.networking_v1 = client.NetworkingV1Api()

    def canary_deployment(self,
                         namespace: str,
                         deployment_name: str,
                         new_image: str,
                         canary_percentage: int = 10) -> bool:
        """
        Implement canary deployment with traffic splitting
        """
        try:
            # Get current deployment
            deployment = self.apps_v1.read_namespaced_deployment(
                name=deployment_name,
                namespace=namespace
            )

            # Create canary deployment
            canary_name = f"{deployment_name}-canary"
            canary_deployment = deployment
            canary_deployment.metadata.name = canary_name
            canary_deployment.spec.template.spec.containers[0].image = new_image

            # Calculate canary replicas
            total_replicas = deployment.spec.replicas
            canary_replicas = max(1, int(total_replicas * canary_percentage / 100))
            stable_replicas = total_replicas - canary_replicas

            # Update replica counts
            canary_deployment.spec.replicas = canary_replicas
            deployment.spec.replicas = stable_replicas

            # Deploy canary
            self.apps_v1.create_namespaced_deployment(
                namespace=namespace,
                body=canary_deployment
            )

            # Update stable deployment
            self.apps_v1.patch_namespaced_deployment(
                name=deployment_name,
                namespace=namespace,
                body=deployment
            )

            # Configure traffic splitting
            self._configure_traffic_split(
                namespace=namespace,
                stable_name=deployment_name,
                canary_name=canary_name,
                canary_weight=canary_percentage
            )

            # Monitor canary health
            if self._monitor_canary_health(namespace, canary_name):
                # Promote canary
                self._promote_canary(namespace, deployment_name, canary_name, new_image)
                return True
            else:
                # Rollback canary
                self._rollback_canary(namespace, deployment_name, canary_name)
                return False

        except Exception as e:
            print(f"Canary deployment failed: {e}")
            return False

    def blue_green_deployment(self,
                            namespace: str,
                            deployment_name: str,
                            new_image: str) -> bool:
        """
        Implement blue-green deployment
        """
        try:
            # Get current (blue) deployment
            blue_deployment = self.apps_v1.read_namespaced_deployment(
                name=f"{deployment_name}-blue",
                namespace=namespace
            )

            # Create green deployment
            green_deployment = blue_deployment
            green_deployment.metadata.name = f"{deployment_name}-green"
            green_deployment.spec.template.spec.containers[0].image = new_image
            green_deployment.spec.selector.match_labels["version"] = "green"
            green_deployment.spec.template.metadata.labels["version"] = "green"

            # Deploy green
            self.apps_v1.create_namespaced_deployment(
                namespace=namespace,
                body=green_deployment
            )

            # Wait for green to be ready
            self._wait_for_deployment_ready(namespace, f"{deployment_name}-green")

            # Run smoke tests
            if self._run_smoke_tests(namespace, f"{deployment_name}-green"):
                # Switch traffic to green
                self._switch_traffic(namespace, deployment_name, "green")

                # Monitor for issues
                time.sleep(300)  # 5 minutes monitoring period

                if self._check_deployment_health(namespace, f"{deployment_name}-green"):
                    # Delete blue deployment
                    self.apps_v1.delete_namespaced_deployment(
                        name=f"{deployment_name}-blue",
                        namespace=namespace
                    )
                    # Rename green to blue for next deployment
                    self._rename_deployment(
                        namespace,
                        f"{deployment_name}-green",
                        f"{deployment_name}-blue"
                    )
                    return True

            # Rollback to blue
            self._switch_traffic(namespace, deployment_name, "blue")
            self.apps_v1.delete_namespaced_deployment(
                name=f"{deployment_name}-green",
                namespace=namespace
            )
            return False

        except Exception as e:
            print(f"Blue-green deployment failed: {e}")
            return False

    def _configure_traffic_split(self,
                                namespace: str,
                                stable_name: str,
                                canary_name: str,
                                canary_weight: int):
        """
        Configure Istio VirtualService for traffic splitting
        """
        virtual_service = {
            "apiVersion": "networking.istio.io/v1beta1",
            "kind": "VirtualService",
            "metadata": {
                "name": f"{stable_name}-vs",
                "namespace": namespace
            },
            "spec": {
                "http": [{
                    "match": [{"headers": {"canary": {"exact": "true"}}}],
                    "route": [{
                        "destination": {
                            "host": canary_name,
                            "port": {"number": 80}
                        }
                    }]
                }, {
                    "route": [{
                        "destination": {
                            "host": stable_name,
                            "port": {"number": 80}
                        },
                        "weight": 100 - canary_weight
                    }, {
                        "destination": {
                            "host": canary_name,
                            "port": {"number": 80}
                        },
                        "weight": canary_weight
                    }]
                }]
            }
        }

        # Apply using kubernetes dynamic client
        api = client.ApiClient()
        utils.create_from_yaml(api, virtual_service)
```

## Performance Optimization

### Container Resource Tuning

```yaml
# Vertical Pod Autoscaler configuration
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: app-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: myapp
  updatePolicy:
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
    - containerName: app
      minAllowed:
        cpu: 100m
        memory: 128Mi
      maxAllowed:
        cpu: 2000m
        memory: 2Gi
      controlledResources: ["cpu", "memory"]
      controlledValues: RequestsAndLimits
```

## Security Hardening

### Container Image Scanning

```yaml
# Trivy security scanning in CI/CD
name: Security Scan

on:
  push:
    branches: [main]

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        image-ref: 'myregistry/myapp:${{ github.sha }}'
        format: 'sarif'
        output: 'trivy-results.sarif'
        severity: 'CRITICAL,HIGH'
        exit-code: '1'

    - name: Upload Trivy results to GitHub Security
      uses: github/codeql-action/upload-sarif@v2
      with:
        sarif_file: 'trivy-results.sarif'
```

## Conclusion

This first Kan extension provides advanced container orchestration patterns that extend the base framework with sophisticated scheduling, security, and deployment strategies. The categorical structure ensures composability and formal reasoning about container transformations, while practical implementations demonstrate real-world applicability.