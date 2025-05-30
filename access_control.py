def enforce_rbac(sql: str, role: str) -> str:
    if "profit" in sql and role != "Finance":
        raise PermissionError("Insufficient role permission.")
    if "top 10" in sql and role != "Finance":
        raise PermissionError("Insufficient role permission.")
    if "slow-moving inventory" in sql and role != "Planner":
        raise PermissionError("Insufficient role permission.")
    if "key performance indicators" in sql and role != "Planner":
        raise PermissionError("Insufficient role permission.")
    if "shipping mode" in sql and role != "Manager":
        raise PermissionError("Insufficient role permission.")
    if "policy" in sql and role != "Manager":
        raise PermissionError("Insufficient role permission.")
    return sql


def enforce_geo(sql: str, region: str) -> str:
    if "Southeast Asia" in sql and region != "Global":
        raise PermissionError("Restricted by geographic access.")
    if "by country" in sql and region != "Global":
        raise PermissionError("Restricted by geographic access.")
    if "region" in sql and region != "Global":
        raise PermissionError("Restricted by geographic access.")
    return sql
