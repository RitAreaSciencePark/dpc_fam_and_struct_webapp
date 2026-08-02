# Pending kdevel HTTPS activation

These files are review-only templates. They are deliberately outside the
active `k8s/overlays/kdevel` Kustomization and must not be applied yet.

Activation is blocked until the Kubernetes administrators confirm:

1. The CloudNativePG operator namespace and labels.
2. The approved cert-manager `ClusterIssuer` name.
3. The DNS target and approved hostname for the `nginx-devel` Ingress.

Before activation:

1. Replace every `REPLACE_WITH_...` value.
2. Add the confirmed NetworkPolicy to the kdevel overlay and wait for the
   CloudNativePG Cluster to report `Ready=True`.
3. Confirm that DNS resolves to the `nginx-devel` endpoint.
4. Add the Certificate, Ingress, and ConfigMap patch to the kdevel overlay.
5. Run client and server dry-runs before applying the overlay.
6. Wait for the Certificate to become Ready before enabling or testing HTTPS
   redirects.
7. Run the complete smoke test through the HTTPS hostname.

HSTS remains disabled for the initial HTTPS validation. Enable it only after
the hostname and certificate are stable.
