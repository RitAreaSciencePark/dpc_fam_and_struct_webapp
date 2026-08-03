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

The first kdevel deployment used:

- Zero web replicas
- Suspended data-loader Job
- Suspended migration Job

This prevented workloads from starting before PostgreSQL, biological data, images, and Secrets were ready.

After the data volume, database restore, migrations, and web image were validated, the kdevel overlay was promoted to one web replica. The data-loader and migration Jobs remain suspended in Git and are activated only for explicit one-time operations.

Never commit Kubernetes Secrets.

CloudNativePG creates the database Secret named:

`dpcexplorer-postgresql-app`

The Django Secret must be created directly in Kubernetes as:

`dpcexplorer-django`

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

The kdevel Ingress routes `dpcexplorer.areasciencepark.it` through
`nginx-public` to `dpcexplorer-web:8000`. It references the
administrator-provisioned `tls-cert` Secret. AREA administrators manage the
public DNS record and TLS Secret lifecycle; certificate renewal responsibility
must remain documented with them. Secret contents are never stored in Git.

## Manual kdevel web releases

Routine web releases use an explicit, reviewed image digest:

1. Let the `CI` workflow publish the web image from protected `main`.
2. Create a branch and replace only the web `digest` in
   `k8s/overlays/kdevel/kustomization.yaml`.
3. Open a pull request and merge it only after the required checks pass.
4. From the Actions page, run the `Deploy kdevel` workflow on `main`.
5. Complete any configured `kdevel` environment approval when prompted.
6. Confirm that the rollout and application smoke tests pass.

The workflow deploys only `deployment/dpcexplorer-web`. It always performs a
server-side dry run first, waits for the rollout, and restores the previous
image if the rollout fails. It does not modify PostgreSQL, biological data,
PVCs, Secrets, Jobs, Ingress, or TLS resources.

The `kdevel` GitHub environment requires:

- variable `KDEVEL_KUBE_CONTEXT`: the exact context name approved by the
  Kubernetes administrators
- secret `KDEVEL_KUBECONFIG_B64`: a base64-encoded kubeconfig for a dedicated,
  least-privilege deployment identity

Never use the mutable `main` image tag in Kubernetes and never store a personal
kubeconfig in GitHub. The committed sha256 digest is the release record.

## Pending security hardening

Review-only HTTPS ConfigMap and CloudNativePG NetworkPolicy templates are
stored in `k8s/pending/kdevel`. They are excluded from the active overlay and
must not be applied directly. The HTTPS patch is deferred until public DNS and
HTTPS smoke tests pass. The NetworkPolicy template is retained only for a
future administrator-approved namespace-restricted policy.
