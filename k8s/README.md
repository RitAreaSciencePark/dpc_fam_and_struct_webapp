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

Build and tag each image with the Git commit SHA, then pin the resulting
sha256 image digest in the environment overlay before deployment.

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

Private GHCR images are pulled using the Kubernetes Secret:

`dpcexplorer-ghcr-pull`

This Secret must use a token with only `read:packages`. Record its expiration
date and rotate it before it expires. Never store the token or Secret manifest
in Git.

## Planned deployment order

1. Publish both images using the Git commit SHA.
2. Pin both published sha256 digests in the kdevel overlay.
3. Create the read-only GHCR pull Secret directly in Kubernetes.
4. Create the Django Secret directly in Kubernetes.
5. Apply the safe kdevel overlay with zero web replicas and suspended Jobs.
6. Wait for CloudNativePG to become Ready.
7. Activate and verify the data-loader Job.
8. Restore the PostgreSQL database.
9. Activate and verify the migration Job.
10. Scale the web Deployment to one replica.
11. Run the complete smoke test through port-forwarding.

The Ingress is intentionally deferred until the preproduction hostname and TLS configuration are confirmed.
