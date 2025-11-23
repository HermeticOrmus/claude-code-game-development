# Kan Extension 2: Cloud-Native Infrastructure Patterns

## Overview

This second Kan extension builds upon container orchestration to provide comprehensive cloud-native infrastructure patterns, focusing on multi-cloud strategies, serverless architectures, and advanced Infrastructure as Code techniques.

## Mathematical Foundation

### Right Kan Extension

```
    C <---F--- D
    |         ^
  G |        / Ran_F G
    v       /
    E <----'
```

Where:
- **C**: Cloud resources
- **D**: Infrastructure patterns
- **E**: Extended cloud-native patterns
- **F**: Basic infrastructure functor
- **G**: Cloud-native enhancement functor
- **Ran_F G**: Right Kan extension for pattern synthesis

## Cloud-Native Infrastructure Patterns

### 1. Multi-Cloud Terraform Modules

```hcl
# modules/multi-cloud-kubernetes/main.tf
variable "cloud_provider" {
  description = "Cloud provider (aws, gcp, azure)"
  type        = string
}

variable "cluster_config" {
  description = "Cluster configuration"
  type = object({
    name               = string
    version           = string
    node_count        = number
    node_type         = string
    enable_autoscaling = bool
    min_nodes         = number
    max_nodes         = number
  })
}

# Provider-agnostic Kubernetes cluster
module "kubernetes_cluster" {
  source = "./${var.cloud_provider}"
  count  = var.cloud_provider != "" ? 1 : 0

  cluster_name    = var.cluster_config.name
  cluster_version = var.cluster_config.version
  node_config     = var.cluster_config
}

# AWS EKS Implementation
module "eks" {
  source  = "./aws"
  count   = var.cloud_provider == "aws" ? 1 : 0

  cluster_name    = var.cluster_config.name
  cluster_version = var.cluster_config.version

  vpc_id     = data.aws_vpc.main.id
  subnet_ids = data.aws_subnets.private.ids

  node_groups = {
    main = {
      desired_size = var.cluster_config.node_count
      min_size     = var.cluster_config.min_nodes
      max_size     = var.cluster_config.max_nodes

      instance_types = [var.cluster_config.node_type]

      update_config = {
        max_unavailable_percentage = 33
      }
    }
  }

  # IRSA (IAM Roles for Service Accounts)
  enable_irsa = true

  # Enable cluster addons
  cluster_addons = {
    coredns = {
      resolve_conflicts = "OVERWRITE"
    }
    kube-proxy = {}
    vpc-cni = {
      resolve_conflicts        = "OVERWRITE"
      service_account_role_arn = module.vpc_cni_irsa.iam_role_arn
    }
    ebs-csi-driver = {
      resolve_conflicts        = "OVERWRITE"
      service_account_role_arn = module.ebs_csi_irsa.iam_role_arn
    }
  }
}

# GKE Implementation
module "gke" {
  source  = "./gcp"
  count   = var.cloud_provider == "gcp" ? 1 : 0

  project_id     = var.gcp_project_id
  cluster_name   = var.cluster_config.name
  region         = var.gcp_region
  network        = data.google_compute_network.main.name
  subnetwork     = data.google_compute_subnetwork.private.name

  kubernetes_version = var.cluster_config.version

  node_pools = [{
    name               = "main-pool"
    machine_type       = var.cluster_config.node_type
    initial_node_count = var.cluster_config.node_count
    min_count         = var.cluster_config.min_nodes
    max_count         = var.cluster_config.max_nodes
    auto_repair       = true
    auto_upgrade      = true

    node_config = {
      preemptible     = false
      disk_size_gb    = 100
      disk_type       = "pd-ssd"
      service_account = google_service_account.kubernetes.email

      oauth_scopes = [
        "https://www.googleapis.com/auth/cloud-platform"
      ]

      labels = {
        environment = var.environment
      }

      metadata = {
        disable-legacy-endpoints = "true"
      }
    }
  }]

  # Enable Workload Identity
  workload_identity_config = {
    workload_pool = "${var.gcp_project_id}.svc.id.goog"
  }

  # Enable Binary Authorization
  binary_authorization = {
    evaluation_mode = "PROJECT_SINGLETON_POLICY_ENFORCE"
  }
}

# AKS Implementation
module "aks" {
  source = "./azure"
  count  = var.cloud_provider == "azure" ? 1 : 0

  resource_group_name = azurerm_resource_group.main.name
  location           = var.azure_region
  cluster_name       = var.cluster_config.name
  kubernetes_version = var.cluster_config.version

  default_node_pool = {
    name                = "default"
    node_count          = var.cluster_config.node_count
    vm_size            = var.cluster_config.node_type
    enable_auto_scaling = var.cluster_config.enable_autoscaling
    min_count          = var.cluster_config.min_nodes
    max_count          = var.cluster_config.max_nodes
    availability_zones  = ["1", "2", "3"]
  }

  # Azure AD integration
  azure_active_directory_role_based_access_control = {
    managed                = true
    azure_rbac_enabled     = true
    admin_group_object_ids = [data.azuread_group.aks_admins.object_id]
  }

  # Enable Azure Policy
  azure_policy_enabled = true

  # Network configuration
  network_profile = {
    network_plugin    = "azure"
    network_policy    = "calico"
    load_balancer_sku = "standard"
    outbound_type     = "loadBalancer"
  }
}

# Outputs
output "cluster_endpoint" {
  description = "Cluster API endpoint"
  value = coalesce(
    try(module.eks[0].cluster_endpoint, ""),
    try(module.gke[0].endpoint, ""),
    try(module.aks[0].cluster_fqdn, "")
  )
}

output "kubeconfig" {
  description = "Kubeconfig for cluster access"
  sensitive   = true
  value = coalesce(
    try(module.eks[0].kubeconfig, ""),
    try(module.gke[0].kubeconfig, ""),
    try(module.aks[0].kube_config_raw, "")
  )
}
```

### 2. Serverless Infrastructure Patterns

```hcl
# serverless-application/main.tf
module "serverless_api" {
  source = "./modules/serverless-api"

  api_name    = "${var.project}-api"
  environment = var.environment

  # Lambda functions
  functions = {
    auth = {
      runtime     = "nodejs18.x"
      handler     = "auth.handler"
      memory_size = 256
      timeout     = 10

      environment_variables = {
        JWT_SECRET = data.aws_secretsmanager_secret_version.jwt.secret_string
      }

      event_source_mapping = {
        type = "api_gateway"
        path = "/auth/*"
        method = "POST"
      }
    }

    user_service = {
      runtime     = "python3.11"
      handler     = "user_service.handler"
      memory_size = 512
      timeout     = 30

      environment_variables = {
        DATABASE_URL = module.rds.connection_string
      }

      layers = [
        module.lambda_layer_psycopg2.arn
      ]

      vpc_config = {
        subnet_ids         = module.vpc.private_subnet_ids
        security_group_ids = [module.security.lambda_sg_id]
      }

      event_source_mapping = {
        type = "api_gateway"
        path = "/users/*"
        method = "ANY"
      }
    }

    async_processor = {
      runtime     = "go1.x"
      handler     = "main"
      memory_size = 1024
      timeout     = 300

      environment_variables = {
        S3_BUCKET = module.s3.bucket_name
        SQS_QUEUE = module.sqs.queue_url
      }

      event_source_mapping = {
        type = "sqs"
        queue_arn = module.sqs.queue_arn
        batch_size = 10
      }
    }
  }

  # API Gateway configuration
  api_gateway_config = {
    type = "REST"

    stages = {
      dev = {
        throttle_burst_limit = 100
        throttle_rate_limit  = 50
      }
      prod = {
        throttle_burst_limit = 5000
        throttle_rate_limit  = 2000
      }
    }

    custom_domain = var.environment == "production" ? {
      domain_name     = "api.${var.domain_name}"
      certificate_arn = data.aws_acm_certificate.api.arn
    } : null
  }

  # Step Functions for orchestration
  step_functions = {
    data_pipeline = {
      definition = file("${path.module}/step-functions/data-pipeline.json")

      role_policy = {
        lambda_invoke = true
        s3_access     = ["${module.s3.bucket_arn}/*"]
        dynamodb_access = [module.dynamodb.table_arn]
      }
    }
  }
}

# DynamoDB for serverless data
module "dynamodb" {
  source = "./modules/dynamodb"

  tables = {
    users = {
      hash_key  = "user_id"
      range_key = "created_at"

      attributes = [
        { name = "user_id", type = "S" },
        { name = "created_at", type = "N" },
        { name = "email", type = "S" }
      ]

      global_secondary_indexes = [{
        name            = "email-index"
        hash_key        = "email"
        projection_type = "ALL"
      }]

      billing_mode = "PAY_PER_REQUEST"

      stream_enabled   = true
      stream_view_type = "NEW_AND_OLD_IMAGES"

      point_in_time_recovery = true

      server_side_encryption = {
        enabled = true
        kms_key_arn = module.kms.key_arn
      }
    }
  }
}

# EventBridge for event-driven architecture
module "eventbridge" {
  source = "./modules/eventbridge"

  bus_name = "${var.project}-events"

  rules = {
    user_created = {
      event_pattern = jsonencode({
        source      = ["user.service"]
        detail-type = ["User Created"]
      })

      targets = [
        {
          arn = module.serverless_api.functions["async_processor"].arn
        },
        {
          arn = module.sns.topic_arn
        }
      ]
    }

    scheduled_cleanup = {
      schedule_expression = "rate(1 hour)"

      targets = [{
        arn = module.serverless_api.functions["cleanup"].arn
        input = jsonencode({
          action = "cleanup_old_records"
        })
      }]
    }
  }
}
```

### 3. Service Mesh Infrastructure

```hcl
# service-mesh/main.tf
module "istio_infrastructure" {
  source = "./modules/istio"

  cluster_id = module.kubernetes.cluster_id

  # Istio configuration
  istio_config = {
    version = "1.19.0"
    profile = "production"

    components = {
      pilot = {
        resources = {
          requests = {
            cpu    = "1000m"
            memory = "1Gi"
          }
        }
        hpa = {
          enabled     = true
          min_replicas = 2
          max_replicas = 5
        }
      }

      ingress_gateway = {
        service_type = "LoadBalancer"

        service_annotations = {
          "service.beta.kubernetes.io/aws-load-balancer-type" = "nlb"
        }

        resources = {
          requests = {
            cpu    = "500m"
            memory = "512Mi"
          }
        }
      }
    }

    mesh_config = {
      access_log_file = "/dev/stdout"

      default_config = {
        proxy_stats_matcher = {
          inclusion_regexps = [
            ".*outlier_detection.*",
            ".*circuit_breakers.*",
            ".*retry.*"
          ]
        }
      }

      extension_providers = [{
        name = "prometheus"
        prometheus = {
          service = "prometheus.istio-system.svc.cluster.local"
          port    = 9090
        }
      }]
    }
  }

  # Virtual services
  virtual_services = {
    api = {
      hosts = ["api.example.com"]

      http_routes = [{
        match = [{
          uri = { prefix = "/v1" }
        }]

        route = [{
          destination = {
            host   = "api-v1"
            port   = 80
            weight = 90
          }
        }, {
          destination = {
            host   = "api-v2"
            port   = 80
            weight = 10
          }
        }]

        timeout = "30s"

        retry_policy = {
          attempts      = 3
          per_try_timeout = "10s"
          retry_on      = "5xx"
        }
      }]
    }
  }

  # Destination rules
  destination_rules = {
    api = {
      host = "api.production.svc.cluster.local"

      traffic_policy = {
        connection_pool = {
          tcp = {
            max_connections = 100
          }
          http = {
            http1_max_pending_requests = 100
            http2_max_requests        = 100
          }
        }

        outlier_detection = {
          consecutive_errors        = 5
          interval                 = "30s"
          base_ejection_time       = "30s"
          max_ejection_percent     = 50
          min_healthy_percent      = 30
          split_external_local_origin_errors = true
        }
      }

      subsets = [{
        name   = "v1"
        labels = { version = "v1" }
      }, {
        name   = "v2"
        labels = { version = "v2" }
      }]
    }
  }

  # Service entries for external services
  service_entries = {
    external_api = {
      hosts = ["api.external.com"]
      ports = [{
        number   = 443
        protocol = "HTTPS"
        name     = "https"
      }]
      location = "MESH_EXTERNAL"
    }
  }
}
```

### 4. Observability Infrastructure

```hcl
# observability/main.tf
module "observability_stack" {
  source = "./modules/observability"

  cluster_id = module.kubernetes.cluster_id
  namespace  = "observability"

  # Prometheus configuration
  prometheus = {
    retention_period = "30d"
    storage_size     = "100Gi"

    remote_write = [{
      url = "https://prometheus-prod-us-central1.grafana.net/api/prom/push"
      basic_auth = {
        username = data.aws_secretsmanager_secret_version.grafana.secret_string["username"]
        password = data.aws_secretsmanager_secret_version.grafana.secret_string["password"]
      }
    }]

    service_monitors = {
      apps = {
        selector = {
          match_labels = {
            prometheus = "enabled"
          }
        }
        namespace_selector = {
          any = true
        }
      }
    }

    rules = {
      alerts = {
        groups = [{
          name = "kubernetes"
          interval = "30s"
          rules = [
            {
              alert = "PodCrashLooping"
              expr  = "rate(kube_pod_container_status_restarts_total[15m]) > 0"
              for   = "5m"
              annotations = {
                summary = "Pod {{ $labels.namespace }}/{{ $labels.pod }} is crash looping"
              }
            },
            {
              alert = "HighMemoryUsage"
              expr  = "container_memory_usage_bytes / container_spec_memory_limit_bytes > 0.9"
              for   = "5m"
              annotations = {
                summary = "Container {{ $labels.container }} memory usage above 90%"
              }
            }
          ]
        }]
      }
    }
  }

  # Grafana configuration
  grafana = {
    admin_password = random_password.grafana_admin.result

    datasources = {
      prometheus = {
        type = "prometheus"
        url  = "http://prometheus-server.observability.svc.cluster.local"
      }

      loki = {
        type = "loki"
        url  = "http://loki.observability.svc.cluster.local:3100"
      }

      tempo = {
        type = "tempo"
        url  = "http://tempo.observability.svc.cluster.local:3100"
      }
    }

    dashboards = {
      kubernetes = {
        provider = "file"
        path     = "${path.module}/dashboards/kubernetes"
      }

      istio = {
        provider = "file"
        path     = "${path.module}/dashboards/istio"
      }
    }
  }

  # Loki for log aggregation
  loki = {
    storage = {
      type = "s3"
      s3 = {
        bucketname = module.s3_logs.bucket_name
        region     = var.aws_region
      }
    }

    schema_config = {
      configs = [{
        from = "2024-01-01"
        store = "boltdb-shipper"
        object_store = "s3"
        schema = "v11"
        index = {
          prefix = "loki_index_"
          period = "24h"
        }
      }]
    }
  }

  # Tempo for distributed tracing
  tempo = {
    storage = {
      trace = {
        backend = "s3"
        s3 = {
          bucket = module.s3_traces.bucket_name
          region = var.aws_region
        }
      }
    }

    receivers = {
      otlp = {
        protocols = {
          grpc = { enabled = true }
          http = { enabled = true }
        }
      }
      jaeger = {
        protocols = {
          thrift_compact = { enabled = true }
          grpc = { enabled = true }
        }
      }
    }
  }

  # Alertmanager configuration
  alertmanager = {
    config = {
      global = {
        smtp_smarthost = "smtp.gmail.com:587"
        smtp_from      = "alerts@example.com"
        smtp_auth_username = data.aws_secretsmanager_secret_version.smtp.secret_string["username"]
        smtp_auth_password = data.aws_secretsmanager_secret_version.smtp.secret_string["password"]
      }

      route = {
        group_by = ["alertname", "cluster", "service"]
        group_wait = "10s"
        group_interval = "10s"
        repeat_interval = "12h"
        receiver = "default"

        routes = [
          {
            match = { severity = "critical" }
            receiver = "pagerduty"
          },
          {
            match = { severity = "warning" }
            receiver = "slack"
          }
        ]
      }

      receivers = [
        {
          name = "default"
          email_configs = [{
            to = "devops@example.com"
          }]
        },
        {
          name = "pagerduty"
          pagerduty_configs = [{
            service_key = data.aws_secretsmanager_secret_version.pagerduty.secret_string
          }]
        },
        {
          name = "slack"
          slack_configs = [{
            api_url = data.aws_secretsmanager_secret_version.slack.secret_string
            channel = "#alerts"
          }]
        }
      ]
    }
  }
}
```

### 5. Cost Optimization Infrastructure

```python
# cost_optimizer.py
import boto3
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import json

class CloudCostOptimizer:
    def __init__(self, cloud_provider: str):
        self.cloud_provider = cloud_provider
        self.recommendations = []

        if cloud_provider == "aws":
            self.ce_client = boto3.client('ce')  # Cost Explorer
            self.ec2_client = boto3.client('ec2')
            self.rds_client = boto3.client('rds')
            self.compute_optimizer = boto3.client('compute-optimizer')

    def analyze_costs(self) -> Dict:
        """Analyze cloud costs and provide recommendations"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)

        # Get cost breakdown
        cost_data = self.ce_client.get_cost_and_usage(
            TimePeriod={
                'Start': start_date.isoformat(),
                'End': end_date.isoformat()
            },
            Granularity='DAILY',
            Metrics=['UnblendedCost', 'UsageQuantity'],
            GroupBy=[
                {'Type': 'DIMENSION', 'Key': 'SERVICE'},
                {'Type': 'DIMENSION', 'Key': 'USAGE_TYPE'}
            ]
        )

        # Analyze EC2 instances
        ec2_recommendations = self._analyze_ec2_instances()

        # Analyze RDS instances
        rds_recommendations = self._analyze_rds_instances()

        # Analyze unattached resources
        unattached_recommendations = self._find_unattached_resources()

        # Get Reserved Instance recommendations
        ri_recommendations = self._get_ri_recommendations()

        # Get Savings Plan recommendations
        sp_recommendations = self._get_savings_plan_recommendations()

        return {
            'total_monthly_cost': self._calculate_total_cost(cost_data),
            'potential_monthly_savings': self._calculate_potential_savings(),
            'recommendations': {
                'ec2': ec2_recommendations,
                'rds': rds_recommendations,
                'unattached': unattached_recommendations,
                'reserved_instances': ri_recommendations,
                'savings_plans': sp_recommendations
            }
        }

    def _analyze_ec2_instances(self) -> List[Dict]:
        """Analyze EC2 instances for optimization"""
        recommendations = []

        # Get all EC2 instances
        instances = self.ec2_client.describe_instances()

        for reservation in instances['Reservations']:
            for instance in reservation['Instances']:
                if instance['State']['Name'] == 'running':
                    instance_id = instance['InstanceId']

                    # Get CloudWatch metrics
                    cw = boto3.client('cloudwatch')

                    # Check CPU utilization
                    cpu_stats = cw.get_metric_statistics(
                        Namespace='AWS/EC2',
                        MetricName='CPUUtilization',
                        Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                        StartTime=datetime.now() - timedelta(days=7),
                        EndTime=datetime.now(),
                        Period=3600,
                        Statistics=['Average', 'Maximum']
                    )

                    if cpu_stats['Datapoints']:
                        avg_cpu = sum(d['Average'] for d in cpu_stats['Datapoints']) / len(cpu_stats['Datapoints'])

                        if avg_cpu < 10:
                            recommendations.append({
                                'resource_id': instance_id,
                                'current_type': instance['InstanceType'],
                                'recommendation': 'Terminate or downsize instance',
                                'reason': f'Average CPU utilization is {avg_cpu:.1f}%',
                                'potential_savings': self._estimate_instance_savings(instance)
                            })
                        elif avg_cpu < 40:
                            # Get rightsizing recommendation
                            optimizer_rec = self.compute_optimizer.get_ec2_instance_recommendations(
                                instanceArns=[f"arn:aws:ec2:{instance['Placement']['AvailabilityZone'][:-1]}:{instance['OwnerId']}:instance/{instance_id}"]
                            )

                            if optimizer_rec['instanceRecommendations']:
                                rec = optimizer_rec['instanceRecommendations'][0]
                                if rec['recommendationOptions']:
                                    best_option = rec['recommendationOptions'][0]
                                    recommendations.append({
                                        'resource_id': instance_id,
                                        'current_type': instance['InstanceType'],
                                        'recommended_type': best_option['instanceType'],
                                        'reason': f'Average CPU utilization is {avg_cpu:.1f}%',
                                        'potential_savings': best_option.get('estimatedMonthlySavings', {}).get('value', 0)
                                    })

        return recommendations

    def _find_unattached_resources(self) -> List[Dict]:
        """Find unattached resources that can be deleted"""
        recommendations = []

        # Find unattached EBS volumes
        volumes = self.ec2_client.describe_volumes(
            Filters=[{'Name': 'status', 'Values': ['available']}]
        )

        for volume in volumes['Volumes']:
            recommendations.append({
                'resource_type': 'EBS Volume',
                'resource_id': volume['VolumeId'],
                'size': f"{volume['Size']} GB",
                'recommendation': 'Delete unattached volume',
                'potential_savings': volume['Size'] * 0.10  # Approximate cost per GB
            })

        # Find unattached Elastic IPs
        eips = self.ec2_client.describe_addresses()

        for eip in eips['Addresses']:
            if 'InstanceId' not in eip:
                recommendations.append({
                    'resource_type': 'Elastic IP',
                    'resource_id': eip.get('AllocationId', eip.get('PublicIp')),
                    'recommendation': 'Release unattached Elastic IP',
                    'potential_savings': 3.65  # $0.005 per hour
                })

        return recommendations

    def implement_cost_savings(self, recommendations: Dict) -> Dict:
        """Automatically implement approved cost-saving measures"""
        implemented = {
            'actions_taken': [],
            'savings_achieved': 0
        }

        for category, recs in recommendations.items():
            for rec in recs:
                if rec.get('auto_implement', False):
                    try:
                        if category == 'unattached':
                            if rec['resource_type'] == 'EBS Volume':
                                self.ec2_client.delete_volume(VolumeId=rec['resource_id'])
                                implemented['actions_taken'].append(f"Deleted volume {rec['resource_id']}")
                                implemented['savings_achieved'] += rec['potential_savings']

                            elif rec['resource_type'] == 'Elastic IP':
                                self.ec2_client.release_address(AllocationId=rec['resource_id'])
                                implemented['actions_taken'].append(f"Released EIP {rec['resource_id']}")
                                implemented['savings_achieved'] += rec['potential_savings']

                        elif category == 'ec2' and rec.get('recommended_type'):
                            # Modify instance type (requires stop/start)
                            instance_id = rec['resource_id']
                            self.ec2_client.stop_instances(InstanceIds=[instance_id])

                            # Wait for instance to stop
                            waiter = self.ec2_client.get_waiter('instance_stopped')
                            waiter.wait(InstanceIds=[instance_id])

                            # Modify instance type
                            self.ec2_client.modify_instance_attribute(
                                InstanceId=instance_id,
                                InstanceType={'Value': rec['recommended_type']}
                            )

                            # Start instance
                            self.ec2_client.start_instances(InstanceIds=[instance_id])

                            implemented['actions_taken'].append(
                                f"Resized instance {instance_id} from {rec['current_type']} to {rec['recommended_type']}"
                            )
                            implemented['savings_achieved'] += rec['potential_savings']

                    except Exception as e:
                        print(f"Failed to implement recommendation: {e}")

        return implemented
```

## Categorical Extensions

### Cloud Resource Functor

```haskell
-- Cloud resource transformations
data CloudResource a = CloudResource {
    provider :: CloudProvider,
    resource :: a,
    metadata :: ResourceMetadata
}

-- Functor for cloud resource transformation
instance Functor CloudResource where
    fmap :: (a -> b) -> CloudResource a -> CloudResource b
    fmap f (CloudResource p r m) = CloudResource p (f r) m

-- Natural transformation between cloud providers
awsToGcp :: CloudResource AWS -> CloudResource GCP
awsToGcp (CloudResource _ res meta) = CloudResource GCP (translateResource res) meta
  where
    translateResource :: AWS -> GCP
    translateResource (EC2Instance spec) = GCEInstance (translateSpec spec)
    translateResource (S3Bucket config) = GCSBucket (translateConfig config)
```

### Infrastructure Monad

```haskell
-- Infrastructure monad for composing cloud resources
newtype Infrastructure a = Infrastructure {
    runInfrastructure :: CloudEnv -> IO (Either InfraError a, CloudEnv)
}

instance Monad Infrastructure where
    return :: a -> Infrastructure a
    return x = Infrastructure $ \env -> return (Right x, env)

    (>>=) :: Infrastructure a -> (a -> Infrastructure b) -> Infrastructure b
    m >>= k = Infrastructure $ \env -> do
        (result, env') <- runInfrastructure m env
        case result of
            Left err -> return (Left err, env')
            Right val -> runInfrastructure (k val) env'

-- Deploy composed infrastructure
deployInfrastructure :: Infrastructure () -> IO ()
deployInfrastructure infra = do
    env <- initializeCloudEnv
    (result, finalEnv) <- runInfrastructure infra env
    case result of
        Left err -> handleError err
        Right _ -> commitInfrastructure finalEnv
```

## Implementation Examples

### Complete Cloud-Native Setup

```bash
#!/bin/bash
# setup-cloud-native.sh

# Initialize Terraform
terraform init

# Deploy multi-cloud infrastructure
terraform plan -var="cloud_provider=aws" -out=tfplan
terraform apply tfplan

# Install service mesh
kubectl apply -f https://github.com/istio/istio/releases/download/1.19.0/istio-1.19.0.yaml

# Deploy observability stack
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install monitoring prometheus-community/kube-prometheus-stack \
  --namespace observability \
  --create-namespace \
  --values observability-values.yaml

# Configure GitOps
flux bootstrap github \
  --owner=$GITHUB_USER \
  --repository=$GITHUB_REPO \
  --branch=main \
  --path=./clusters/production \
  --personal

# Enable cost optimization
python3 cost_optimizer.py --analyze --implement
```

## Conclusion

This second Kan extension provides comprehensive cloud-native infrastructure patterns that build upon container orchestration to deliver multi-cloud capabilities, serverless architectures, and advanced observability. The categorical structure ensures mathematical rigor in infrastructure transformations while maintaining practical applicability across different cloud providers.