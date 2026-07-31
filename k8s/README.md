# DPCexplorer Kubernetes deployment

## Environments

- `k8s/base`: shared Kubernetes resources
- `k8s/overlays/kdevel`: preproduction configuration
- `k8s/overlays/kprod`: reserved for the later production milestone
- Namespace: `dpcdom`

## Images

- Web and migration:
  `ghcr.io/ritareasciencepark/dpc_fam_and_struct_webapp:<git-sha>`
- Data loader:
  `ghcr.io/ritareasciencepark/dpc_fam_and_struct_webapp-data-loader:<git-sha>`

Always replace the image placeholders with an immutable Git commit SHA before deployment.

## Safety

The initial kdevel overlay uses:

- Zero web replicas
- Suspended data-loader Job
- Suspended migration Job

This prevents workloads from starting before PostgreSQL, biological data, images, and Secrets are ready.

Never commit Kubernetes Secrets.

CloudNativePG creates the database Secret named:

`dpcexplorer-postgresql-app`

The Django Secret must be created directly in Kubernetes as:

`dpcexplorer-django`

## Planned deployment order

1. Publish both images with the Git commit SHA.
2. Replace both image placeholders in the kdevel overlay.
3. Create the Django Secret directly in Kubernetes.
4. Apply the kdevel overlay.
5. Wait for CloudNativePG to become Ready.
6. Activate and verify the data-loader Job.
7. Restore the PostgreSQL database.
8. Activate and verify the migration Job.
9. Scale the web Deployment to one replica.
10. Run the complete smoke test through port-forwarding.

The Ingress is intentionally deferred until the preproduction hostname and TLS configuration are confirmed.
