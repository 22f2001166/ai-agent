def enforce_rbac(sql: str, role: str) -> str:
    if "profit" in sql and role != "Finance":
        raise PermissionError("Insufficient role permission.")
    return sql


def enforce_geo(sql: str, region: str) -> str:
    if "Southwest" in sql and region != "India":
        raise PermissionError("Restricted by geographic access.")
    return sql
