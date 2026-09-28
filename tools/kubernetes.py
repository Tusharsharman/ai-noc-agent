import subprocess


def run_kubectl(args):
    """
    Execute a kubectl command in read-only mode.
    """

    command = ["kubectl"] + args

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=15
    )

    if result.returncode != 0:
        raise RuntimeError(
            result.stderr.strip()
        )

    return result.stdout.strip()


def get_pods(namespace="default"):
    """
    Get pod status from Kubernetes.
    """

    return run_kubectl([
        "get",
        "pods",
        "-n",
        namespace,
        "-o",
        "wide"
    ])


def get_deployments(namespace="default"):
    """
    Get deployment status from Kubernetes.
    """

    return run_kubectl([
        "get",
        "deployments",
        "-n",
        namespace
    ])


def get_pod_restarts(namespace="default"):
    """
    Get pod restart information.
    """

    return run_kubectl([
        "get",
        "pods",
        "-n",
        namespace,
        "-o",
        "custom-columns="
        "NAME:.metadata.name,"
        "STATUS:.status.phase,"
        "RESTARTS:.status.containerStatuses[0].restartCount"
    ])


def get_pod_logs(
    pod_name,
    namespace="default",
    lines=50
):
    """
    Get recent logs from a Kubernetes pod.
    """

    return run_kubectl([
        "logs",
        pod_name,
        "-n",
        namespace,
        "--tail",
        str(lines)
    ])


def get_pod_description(
    pod_name,
    namespace="default"
):
    """
    Get detailed pod information including
    Kubernetes events.
    """

    return run_kubectl([
        "describe",
        "pod",
        pod_name,
        "-n",
        namespace
    ])


def get_pod_events(
    pod_name,
    namespace="default"
):
    """
    Get Kubernetes events for a specific pod.
    """

    return run_kubectl([
        "get",
        "events",
        "-n",
        namespace,
        "--field-selector",
        f"involvedObject.name={pod_name}",
        "--sort-by=.lastTimestamp"
    ])


if __name__ == "__main__":

    namespace = "noc-demo"

    print("\n================================")
    print("KUBERNETES PODS")
    print("================================")

    print(get_pods(namespace))

    print("\n================================")
    print("KUBERNETES DEPLOYMENTS")
    print("================================")

    print(get_deployments(namespace))

    print("\n================================")
    print("POD RESTARTS")
    print("================================")

    print(get_pod_restarts(namespace))

    print("\n================================")
    print("BROKEN POD DESCRIPTION")
    print("================================")

    try:
        print(
            get_pod_description(
                "noc-broken-pod",
                namespace
            )
        )

    except Exception as exc:
        print("Unable to describe pod:")
        print(exc)

    print("\n================================")
    print("BROKEN POD EVENTS")
    print("================================")

    try:
        print(
            get_pod_events(
                "noc-broken-pod",
                namespace
            )
        )

    except Exception as exc:
        print("Unable to get pod events:")
        print(exc)
