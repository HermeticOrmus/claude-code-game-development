# Kan Extension 3: GitOps and Continuous Deployment Patterns

## Overview

This third Kan extension advances from cloud-native infrastructure to sophisticated GitOps workflows and continuous deployment patterns, implementing advanced deployment strategies, progressive delivery, and policy-as-code governance.

## Mathematical Foundation

### Kan Extension with Adjunction

```
    C ⊣ D
    ↓   ↓
    E → F

    Lan ⊣ Ran
```

Where:
- **C**: Source control state
- **D**: Deployed infrastructure state
- **E**: GitOps workflows
- **F**: Runtime environments
- **Lan ⊣ Ran**: Adjoint pair of Kan extensions for bidirectional synchronization

## Advanced GitOps Patterns

### 1. Multi-Environment GitOps Architecture

```yaml
# gitops-structure/environments/production/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

namespace: production

resources:
  - ../../base
  - ingress.yaml
  - secrets-sealed.yaml

patchesStrategicMerge:
  - deployment-patch.yaml
  - service-patch.yaml

configMapGenerator:
  - name: app-config
    behavior: merge
    literals:
      - environment=production
      - log_level=info
      - feature_flags=stable

images:
  - name: myapp
    newTag: v2.1.0

replicas:
  - name: myapp-deployment
    count: 10

transformers:
  - labels.yaml
  - annotations.yaml

---
# gitops-structure/environments/production/deployment-patch.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp-deployment
spec:
  template:
    spec:
      containers:
      - name: app
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        env:
        - name: DATABASE_POOL_SIZE
          value: "50"
        - name: CACHE_TTL
          value: "3600"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 60
          periodSeconds: 10
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 5
          successThreshold: 1
```

### 2. Progressive Delivery with Flagger

```yaml
# progressive-delivery/canary-deployment.yaml
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: myapp
  namespace: production
spec:
  # Target deployment
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: myapp

  # Progressive delivery strategy
  progressDeadlineSeconds: 600

  # Service configuration
  service:
    port: 80
    targetPort: 8080
    gateways:
    - public-gateway.istio-system.svc.cluster.local
    hosts:
    - app.example.com
    trafficPolicy:
      tls:
        mode: ISTIO_MUTUAL

  # Canary analysis configuration
  analysis:
    # Schedule interval for metrics analysis
    interval: 1m

    # Number of iterations before promotion
    iterations: 10

    # Max traffic percentage routed to canary
    maxWeight: 50

    # Canary increment step percentage
    stepWeight: 5

    # Threshold for rolling back the canary
    threshold: 5

    # Metrics for canary analysis
    metrics:
    - name: request-success-rate
      templateRef:
        name: request-success-rate
        namespace: istio-system
      thresholdRange:
        min: 99
      interval: 1m

    - name: request-duration
      templateRef:
        name: request-duration
        namespace: istio-system
      thresholdRange:
        max: 500
      interval: 1m

    - name: error-rate
      templateRef:
        name: error-rate
        namespace: istio-system
      thresholdRange:
        max: 1
      interval: 1m

    # Webhooks for integration
    webhooks:
    - name: acceptance-test
      url: http://flagger-loadtester/
      timeout: 30s
      metadata:
        type: bash
        cmd: "curl -sS http://myapp-canary:80/health | grep -q 'healthy'"

    - name: load-test
      url: http://flagger-loadtester/
      timeout: 60s
      metadata:
        type: cmd
        cmd: "hey -z 1m -q 10 -c 2 http://myapp-canary.production:80/"

    - name: smoke-test
      url: http://flagger-loadtester/
      timeout: 60s
      metadata:
        type: helmv3
        cmd: "test myapp --namespace production"

    # Alerts configuration
    alerts:
    - name: "Canary promotion"
      severity: info
      providerRef:
        name: slack
        namespace: flagger-system

---
# Metric templates for Flagger
apiVersion: flagger.app/v1beta1
kind: MetricTemplate
metadata:
  name: request-success-rate
  namespace: istio-system
spec:
  provider: prometheus
  query: |
    sum(
      rate(
        istio_request_duration_milliseconds_count{
          reporter="destination",
          destination_workload="{{target}}",
          response_code!~"5..",
          namespace="{{namespace}}"
        }[{{interval}}]
      )
    ) /
    sum(
      rate(
        istio_request_duration_milliseconds_count{
          reporter="destination",
          destination_workload="{{target}}",
          namespace="{{namespace}}"
        }[{{interval}}]
      )
    ) * 100

---
apiVersion: flagger.app/v1beta1
kind: MetricTemplate
metadata:
  name: request-duration
  namespace: istio-system
spec:
  provider: prometheus
  query: |
    histogram_quantile(0.99,
      sum(
        rate(
          istio_request_duration_milliseconds_bucket{
            reporter="destination",
            destination_workload="{{target}}",
            namespace="{{namespace}}"
          }[{{interval}}]
        )
      ) by (le)
    )

---
apiVersion: flagger.app/v1beta1
kind: AlertProvider
metadata:
  name: slack
  namespace: flagger-system
spec:
  type: slack
  secretRef:
    name: slack-webhook
  channel: deployments
```

### 3. Policy-as-Code with OPA

```yaml
# policy-as-code/gatekeeper-policies.yaml
apiVersion: templates.gatekeeper.sh/v1beta1
kind: ConstraintTemplate
metadata:
  name: k8srequiredsecuritycontrols
spec:
  crd:
    spec:
      names:
        kind: K8sRequiredSecurityControls
      validation:
        openAPIV3Schema:
          type: object
          properties:
            allowedCapabilities:
              type: array
              items:
                type: string
            requiredDropCapabilities:
              type: array
              items:
                type: string
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8srequiredsecuritycontrols

        violation[{"msg": msg}] {
          container := input.review.object.spec.containers[_]
          not container.securityContext.runAsNonRoot
          msg := sprintf("Container %v must run as non-root user", [container.name])
        }

        violation[{"msg": msg}] {
          container := input.review.object.spec.containers[_]
          not container.securityContext.readOnlyRootFilesystem
          msg := sprintf("Container %v must have read-only root filesystem", [container.name])
        }

        violation[{"msg": msg}] {
          container := input.review.object.spec.containers[_]
          not container.securityContext.allowPrivilegeEscalation == false
          msg := sprintf("Container %v must not allow privilege escalation", [container.name])
        }

        violation[{"msg": msg}] {
          container := input.review.object.spec.containers[_]
          has_disallowed_capabilities(container)
          msg := sprintf("Container %v has disallowed capabilities", [container.name])
        }

        has_disallowed_capabilities(container) {
          container.securityContext.capabilities.add[_] == "SYS_ADMIN"
        }

        has_disallowed_capabilities(container) {
          container.securityContext.capabilities.add[_] == "NET_ADMIN"
        }

---
apiVersion: v1
kind: ConfigMap
metadata:
  name: deployment-policies
  namespace: opa-system
data:
  deployment_policies.rego: |
    package deployment

    default allow = false

    # Allow deployments only during business hours
    allow {
      current_hour := time.clock(time.now_ns())[0]
      current_hour >= 9
      current_hour <= 17
      day_of_week := time.weekday(time.now_ns())
      day_of_week != "Saturday"
      day_of_week != "Sunday"
    }

    # Require approval for production deployments
    allow {
      input.namespace == "production"
      input.annotations["approved-by"] != ""
      input.annotations["approval-ticket"] != ""
    }

    # Auto-approve development deployments
    allow {
      input.namespace == "development"
    }

    # Enforce image signing
    deny[msg] {
      input.spec.template.spec.containers[_].image
      not image_signed(input.spec.template.spec.containers[_].image)
      msg := "Container image must be signed"
    }

    image_signed(image) {
      # Check if image has signature in registry
      response := http.send({
        "method": "GET",
        "url": sprintf("https://registry.example.com/v2/%v/signatures", [image]),
        "headers": {"Authorization": "Bearer " + env.REGISTRY_TOKEN}
      })
      response.status_code == 200
    }
```

### 4. GitOps CI/CD Pipeline

```yaml
# .github/workflows/gitops-pipeline.yml
name: GitOps Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Setup tools
      run: |
        # Install required tools
        curl -s "https://raw.githubusercontent.com/kubernetes-sigs/kustomize/master/hack/install_kustomize.sh" | bash
        sudo mv kustomize /usr/local/bin/

        # Install kubeconform for validation
        curl -L https://github.com/yannh/kubeconform/releases/latest/download/kubeconform-linux-amd64.tar.gz | tar xz
        sudo mv kubeconform /usr/local/bin/

        # Install OPA for policy validation
        curl -L -o opa https://openpolicyagent.org/downloads/latest/opa_linux_amd64
        chmod +x opa
        sudo mv opa /usr/local/bin/

    - name: Validate Kubernetes manifests
      run: |
        # Generate manifests
        kustomize build environments/production > production-manifests.yaml

        # Validate schema
        kubeconform -summary -output json production-manifests.yaml

    - name: Policy validation
      run: |
        # Validate against OPA policies
        opa eval -d policies/ -i production-manifests.yaml "data.deployment.allow"

    - name: Security scanning
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'config'
        scan-ref: '.'
        format: 'sarif'
        output: 'trivy-results.sarif'

    - name: Upload scan results
      uses: github/codeql-action/upload-sarif@v2
      with:
        sarif_file: 'trivy-results.sarif'

  build:
    needs: validate
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
      id-token: write

    steps:
    - uses: actions/checkout@v3

    - name: Setup Docker Buildx
      uses: docker/setup-buildx-action@v2

    - name: Log in to Container Registry
      uses: docker/login-action@v2
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}

    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v4
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=semver,pattern={{version}}
          type=semver,pattern={{major}}.{{minor}}
          type=sha,prefix={{branch}}-

    - name: Build and push image
      uses: docker/build-push-action@v4
      with:
        context: .
        platforms: linux/amd64,linux/arm64
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max

    - name: Generate SBOM
      uses: anchore/sbom-action@v0
      with:
        image: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ steps.meta.outputs.version }}
        format: spdx-json
        output-file: sbom.spdx.json

    - name: Sign container image
      run: |
        # Install cosign
        curl -LO https://github.com/sigstore/cosign/releases/latest/download/cosign-linux-amd64
        chmod +x cosign-linux-amd64
        sudo mv cosign-linux-amd64 /usr/local/bin/cosign

        # Sign image
        cosign sign --yes ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ steps.meta.outputs.version }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
    - uses: actions/checkout@v3
      with:
        token: ${{ secrets.GITHUB_TOKEN }}

    - name: Update manifests
      run: |
        # Install yq for YAML manipulation
        sudo wget -qO /usr/local/bin/yq https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64
        sudo chmod +x /usr/local/bin/yq

        # Update image tag in kustomization
        cd environments/staging
        yq e '.images[0].newTag = "${{ steps.meta.outputs.version }}"' -i kustomization.yaml

        # Commit changes
        git config user.name github-actions
        git config user.email github-actions@github.com
        git add .
        git commit -m "Update staging to ${{ steps.meta.outputs.version }}"
        git push

    - name: Create deployment PR
      uses: peter-evans/create-pull-request@v5
      with:
        token: ${{ secrets.GITHUB_TOKEN }}
        commit-message: Deploy ${{ steps.meta.outputs.version }} to production
        title: '[Deployment] Release ${{ steps.meta.outputs.version }}'
        body: |
          ## Deployment Summary

          **Version**: ${{ steps.meta.outputs.version }}
          **Commit**: ${{ github.sha }}
          **Author**: ${{ github.actor }}

          ### Changes
          ${{ steps.changelog.outputs.changelog }}

          ### Deployment Checklist
          - [ ] All tests passing
          - [ ] Security scan complete
          - [ ] Performance baseline met
          - [ ] Documentation updated
          - [ ] Rollback plan prepared
        branch: deploy/${{ steps.meta.outputs.version }}
        base: main

    - name: Trigger ArgoCD sync
      run: |
        # Sync ArgoCD application
        curl -X POST https://argocd.example.com/api/v1/applications/myapp/sync \
          -H "Authorization: Bearer ${{ secrets.ARGOCD_TOKEN }}" \
          -H "Content-Type: application/json" \
          -d '{
            "revision": "${{ github.sha }}",
            "prune": true,
            "dryRun": false,
            "strategy": {
              "hook": {
                "force": false
              }
            }
          }'

  verify:
    needs: deploy
    runs-on: ubuntu-latest
    steps:
    - name: Run smoke tests
      run: |
        # Wait for deployment
        sleep 60

        # Run smoke tests
        for endpoint in health ready metrics; do
          response=$(curl -sS -o /dev/null -w "%{http_code}" https://staging.example.com/${endpoint})
          if [ $response -ne 200 ]; then
            echo "Smoke test failed for /${endpoint}"
            exit 1
          fi
        done

    - name: Run integration tests
      run: |
        # Run comprehensive integration tests
        npm install -g newman
        newman run integration-tests.postman_collection.json \
          --environment staging.postman_environment.json \
          --reporters cli,json \
          --reporter-json-export integration-results.json

    - name: Performance testing
      run: |
        # Run performance tests with k6
        curl https://github.com/grafana/k6/releases/download/v0.47.0/k6-v0.47.0-linux-amd64.tar.gz -L | tar xz
        ./k6 run performance-test.js \
          --out cloud \
          --duration 5m \
          --vus 100
```

### 5. Advanced Rollback Mechanisms

```python
# rollback_manager.py
import kubernetes
from kubernetes import client, config
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import hashlib

class RollbackManager:
    def __init__(self, namespace: str):
        config.load_incluster_config()
        self.namespace = namespace
        self.apps_v1 = client.AppsV1Api()
        self.core_v1 = client.CoreV1Api()
        self.custom_api = client.CustomObjectsApi()

    def create_snapshot(self, deployment_name: str) -> str:
        """Create a snapshot of current deployment state"""
        deployment = self.apps_v1.read_namespaced_deployment(
            name=deployment_name,
            namespace=self.namespace
        )

        snapshot = {
            'timestamp': datetime.now().isoformat(),
            'deployment': deployment.to_dict(),
            'config_maps': self._get_related_configmaps(deployment),
            'secrets': self._get_related_secrets(deployment),
            'services': self._get_related_services(deployment),
            'metrics': self._capture_current_metrics(deployment_name)
        }

        # Store snapshot
        snapshot_id = hashlib.sha256(
            json.dumps(snapshot, default=str).encode()
        ).hexdigest()[:8]

        config_map = client.V1ConfigMap(
            metadata=client.V1ObjectMeta(
                name=f"snapshot-{deployment_name}-{snapshot_id}",
                namespace=self.namespace,
                labels={'type': 'deployment-snapshot', 'deployment': deployment_name}
            ),
            data={'snapshot': json.dumps(snapshot, default=str)}
        )

        self.core_v1.create_namespaced_config_map(
            namespace=self.namespace,
            body=config_map
        )

        return snapshot_id

    def automated_rollback(self, deployment_name: str,
                         error_threshold: float = 0.05,
                         latency_threshold: int = 1000) -> bool:
        """Automatically rollback if metrics exceed thresholds"""
        current_metrics = self._capture_current_metrics(deployment_name)

        if (current_metrics['error_rate'] > error_threshold or
            current_metrics['p99_latency'] > latency_threshold):

            print(f"Threshold exceeded, initiating rollback for {deployment_name}")

            # Get previous revision
            deployment = self.apps_v1.read_namespaced_deployment(
                name=deployment_name,
                namespace=self.namespace
            )

            # Check rollout history
            replicasets = self.apps_v1.list_namespaced_replica_set(
                namespace=self.namespace,
                label_selector=f"app={deployment_name}"
            )

            # Sort by revision number
            sorted_rs = sorted(
                replicasets.items,
                key=lambda rs: int(rs.metadata.annotations.get(
                    'deployment.kubernetes.io/revision', '0'
                )),
                reverse=True
            )

            if len(sorted_rs) > 1:
                # Rollback to previous revision
                previous_rs = sorted_rs[1]

                deployment.spec.template = previous_rs.spec.template

                self.apps_v1.patch_namespaced_deployment(
                    name=deployment_name,
                    namespace=self.namespace,
                    body=deployment
                )

                # Create rollback event
                self._create_rollback_event(deployment_name,
                                           f"Automated rollback: error_rate={current_metrics['error_rate']}, "
                                           f"p99_latency={current_metrics['p99_latency']}")

                return True

        return False

    def canary_rollback(self, canary_name: str) -> bool:
        """Rollback canary deployment"""
        try:
            # Get Flagger canary resource
            canary = self.custom_api.get_namespaced_custom_object(
                group="flagger.app",
                version="v1beta1",
                namespace=self.namespace,
                plural="canaries",
                name=canary_name
            )

            # Trigger rollback
            canary['spec']['skipAnalysis'] = True

            self.custom_api.patch_namespaced_custom_object(
                group="flagger.app",
                version="v1beta1",
                namespace=self.namespace,
                plural="canaries",
                name=canary_name,
                body=canary
            )

            # Reset canary
            canary['spec']['skipAnalysis'] = False
            canary['spec']['service']['weight'] = 0

            self.custom_api.patch_namespaced_custom_object(
                group="flagger.app",
                version="v1beta1",
                namespace=self.namespace,
                plural="canaries",
                name=canary_name,
                body=canary
            )

            return True

        except Exception as e:
            print(f"Failed to rollback canary: {e}")
            return False

    def time_based_rollback(self, deployment_name: str,
                           revision_timestamp: str) -> bool:
        """Rollback to a specific point in time"""
        target_time = datetime.fromisoformat(revision_timestamp)

        # List all snapshots
        snapshots = self.core_v1.list_namespaced_config_map(
            namespace=self.namespace,
            label_selector=f"type=deployment-snapshot,deployment={deployment_name}"
        )

        # Find closest snapshot to target time
        closest_snapshot = None
        min_diff = timedelta.max

        for snapshot_cm in snapshots.items:
            snapshot_data = json.loads(snapshot_cm.data['snapshot'])
            snapshot_time = datetime.fromisoformat(snapshot_data['timestamp'])

            if snapshot_time <= target_time:
                diff = target_time - snapshot_time
                if diff < min_diff:
                    min_diff = diff
                    closest_snapshot = snapshot_data

        if closest_snapshot:
            # Restore deployment from snapshot
            deployment_dict = closest_snapshot['deployment']

            # Clean metadata
            deployment_dict['metadata'].pop('resourceVersion', None)
            deployment_dict['metadata'].pop('uid', None)

            deployment = client.V1Deployment(**deployment_dict)

            self.apps_v1.patch_namespaced_deployment(
                name=deployment_name,
                namespace=self.namespace,
                body=deployment
            )

            # Restore config maps
            for cm_dict in closest_snapshot['config_maps']:
                cm_dict['metadata'].pop('resourceVersion', None)
                cm_dict['metadata'].pop('uid', None)

                config_map = client.V1ConfigMap(**cm_dict)
                self.core_v1.patch_namespaced_config_map(
                    name=config_map.metadata.name,
                    namespace=self.namespace,
                    body=config_map
                )

            return True

        return False

    def _capture_current_metrics(self, deployment_name: str) -> Dict:
        """Capture current deployment metrics"""
        # This would integrate with Prometheus
        # Simplified example
        return {
            'error_rate': 0.01,
            'p99_latency': 500,
            'request_rate': 1000,
            'cpu_usage': 0.6,
            'memory_usage': 0.7
        }

    def _create_rollback_event(self, deployment_name: str, reason: str):
        """Create Kubernetes event for rollback"""
        event = client.V1Event(
            metadata=client.V1ObjectMeta(
                name=f"rollback-{deployment_name}-{datetime.now().timestamp()}",
                namespace=self.namespace
            ),
            involved_object=client.V1ObjectReference(
                api_version="apps/v1",
                kind="Deployment",
                name=deployment_name,
                namespace=self.namespace
            ),
            reason="Rollback",
            message=reason,
            type="Warning",
            first_timestamp=datetime.now(),
            last_timestamp=datetime.now(),
            count=1
        )

        self.core_v1.create_namespaced_event(
            namespace=self.namespace,
            body=event
        )
```

## Categorical Extensions

### GitOps Functor Category

```haskell
-- GitOps transformation functors
data GitOpsF a = GitOpsF {
    source :: GitRepository,
    target :: KubernetesCluster,
    transform :: a -> IO a,
    policy :: PolicySet
}

-- Functor instance for GitOps
instance Functor GitOpsF where
    fmap f (GitOpsF src tgt trans pol) =
        GitOpsF src tgt (trans . f) pol

-- Natural transformation for environment promotion
promote :: GitOpsF Development -> GitOpsF Production
promote (GitOpsF src _ trans pol) =
    GitOpsF src prodCluster enhancedTransform strictPolicy
  where
    enhancedTransform = addProductionControls . trans
    strictPolicy = pol <> productionPolicies
```

### Deployment Monad with Rollback

```haskell
-- Deployment monad with automatic rollback
newtype Deployment a = Deployment {
    runDeployment :: DeploymentEnv -> IO (Either DeploymentError a, DeploymentState)
}

-- MonadRollback class
class Monad m => MonadRollback m where
    checkpoint :: m ()
    rollback :: m ()
    withRollback :: m a -> m a

instance MonadRollback Deployment where
    checkpoint = Deployment $ \env -> do
        state <- captureState env
        return (Right (), state)

    rollback = Deployment $ \env -> do
        prevState <- getPreviousState env
        restoreState prevState
        return (Right (), prevState)

    withRollback action = do
        checkpoint
        result <- action `catchError` \e -> do
            rollback
            throwError e
        return result
```

## Implementation Examples

### Complete GitOps Setup

```bash
#!/bin/bash
# setup-gitops.sh

# Install Flux
flux install --namespace=flux-system

# Bootstrap Git repository
flux bootstrap github \
  --owner=${GITHUB_OWNER} \
  --repository=${GITHUB_REPO} \
  --branch=main \
  --path=./clusters/production \
  --personal

# Install Flagger for progressive delivery
kubectl apply -f https://raw.githubusercontent.com/fluxcd/flagger/main/artifacts/flagger/crd.yaml
helm repo add flagger https://flagger.app
helm install flagger flagger/flagger \
  --namespace=istio-system \
  --set meshProvider=istio \
  --set metricsServer=http://prometheus:9090

# Install OPA Gatekeeper for policy enforcement
kubectl apply -f https://raw.githubusercontent.com/open-policy-agent/gatekeeper/release-3.14/deploy/gatekeeper.yaml

# Setup Sealed Secrets for secret management
kubectl apply -f https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.23.0/controller.yaml

# Configure image automation
flux create image repository myapp \
  --image=ghcr.io/myorg/myapp \
  --interval=1m

flux create image policy myapp \
  --image-ref=myapp \
  --select-semver=">1.0.0" \
  --filter-regex='^main-[a-f0-9]+'

flux create image update myapp \
  --git-repo-ref=flux-system \
  --git-repo-path="./clusters/production" \
  --checkout-branch=main \
  --push-branch=main \
  --author-name=flux \
  --author-email=flux@example.com \
  --commit-template="{{range .Updated.Images}}{{println .}}{{end}}"

# Setup monitoring for GitOps
kubectl apply -f - <<EOF
apiVersion: v1
kind: ServiceMonitor
metadata:
  name: flux-system
  namespace: flux-system
spec:
  selector:
    matchLabels:
      app: flux
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics
EOF

echo "GitOps setup complete!"
```

## Conclusion

This third Kan extension provides comprehensive GitOps and continuous deployment patterns that build upon cloud-native infrastructure to deliver sophisticated deployment automation, progressive delivery, and policy governance. The categorical structure with adjunctions ensures bidirectional synchronization between Git and runtime states while maintaining mathematical rigor in deployment transformations.