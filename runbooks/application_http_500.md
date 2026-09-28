# Application HTTP 500 Runbook

## Purpose

This runbook provides read-only diagnostic guidance
for HTTP 500 application errors.

## Symptoms

Common symptoms include:

- HTTP 500 responses
- Increasing application error count
- Error logs containing application failures
- Increased error percentage

## Diagnostic Steps

### 1. Check Application Error Rate

Review the application's error metrics.

Determine:

- Recent error count
- Recent request count
- Error percentage
- Error trend

### 2. Review Application Logs

Inspect recent application error logs.

Look for:

- Exception messages
- Error types
- Failed endpoints
- Repeated failures
- Correlated timestamps

### 3. Check Request Patterns

Determine whether errors are:

- Isolated
- Endpoint-specific
- Increasing
- Affecting multiple endpoints

### 4. Check Application Health

Review:

- Application health endpoint
- Application metrics
- CPU utilization
- Memory utilization
- Request latency

### 5. Check Kubernetes Health

Review:

- Pod status
- Pod restarts
- Deployment status
- Kubernetes events

Determine whether Kubernetes issues occur
at the same time as the application errors.

## Important Interpretation

An HTTP 500 error confirms that the application
returned an internal server error.

It does not automatically identify the root cause.

The root cause should only be declared when the
available evidence establishes a causal relationship.

## Simulated Test Errors

If the error originates from the AI NOC demo
application's simulated error endpoint, clearly
identify the error as simulated test evidence.

Do not treat simulated errors as production failures.

## Safety Rules

The AI NOC Agent must not automatically:

- Restart the application
- Delete pods
- Modify application configuration
- Change infrastructure
- Scale deployments

Any remediation requires explicit human approval.

## Recommended Investigation Output

The AI NOC Agent should provide:

1. Confirmed observations
2. Error pattern
3. Possible contributing factors
4. Correlated infrastructure signals
5. Root cause status
6. Read-only diagnostic next steps
