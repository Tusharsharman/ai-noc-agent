# Kubernetes ImagePullBackOff Runbook

## Purpose

This runbook provides read-only diagnostic guidance
for Kubernetes pods experiencing ImagePullBackOff
or ErrImagePull.

## Symptoms

Common symptoms include:

- Pod status shows ImagePullBackOff
- Pod status shows ErrImagePull
- Kubernetes events show image pull failures
- Kubernetes events may show "manifest not found"
- Container may remain in Pending state

## Diagnostic Steps

### 1. Check Pod Status

Check the affected pod status:

```bash
kubectl get pod <pod-name> -n <namespace>
