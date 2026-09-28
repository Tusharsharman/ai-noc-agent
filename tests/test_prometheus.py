from tools.prometheus import query_prometheus


result = query_prometheus(
    "app_cpu_usage_percent"
)

print(result)