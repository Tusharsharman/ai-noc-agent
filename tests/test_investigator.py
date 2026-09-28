from agent.investigator import get_current_health


health = get_current_health()

print("\n===== NOC HEALTH =====")

print(
    f"CPU: {health['cpu']}%"
)

print(
    f"Memory: {health['memory']}%"
)

print(
    f"Incident Mode: {health['incident_mode']}"
)