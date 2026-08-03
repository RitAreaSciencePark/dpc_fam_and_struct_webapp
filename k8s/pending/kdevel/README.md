# Pending kdevel security hardening

These files are review-only templates. They are deliberately outside the
active `k8s/overlays/kdevel` Kustomization and must not be applied directly.

The public Ingress is active in `k8s/overlays/kdevel/ingress.yaml` and
references the administrator-provisioned `tls-cert` Secret. Public DNS and the
TLS Secret lifecycle are administrator-managed; renewal responsibility must be
confirmed with them.

The remaining templates are optional hardening steps:

- `https-configmap-patch.yaml` enables Django proxy-aware HTTPS redirects and
  secure cookies. Activate it only after public DNS and HTTPS smoke tests pass.
- `cnpg-operator-network-policy.template.yaml` is a reference for any future
  namespace-restricted policy. Use it only with administrator-confirmed
  CloudNativePG operator labels and namespace.

Before activating either template, run client and server dry-runs and confirm
that the web Deployment and CloudNativePG Cluster remain healthy.

HSTS remains disabled for the initial HTTPS validation. Enable it only after
the hostname and certificate are stable.
