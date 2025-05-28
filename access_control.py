# def enforce_rbac(sql: str, role: str) -> str:
#     if "profit" in sql and role != "Finance":
#         raise PermissionError("Insufficient role permission.")
#     return sql


def enforce_rbac(sql_query, role):
    if role == "Finance":
        allowed_tables = ["finance", "pnl", "costs", "inventory"]
    elif role == "Planning":
        allowed_tables = ["inventory", "logistics", "forecasting"]
    elif role == "Operations Manager":
        allowed_tables = ["inventory", "logistics", "suppliers"]
    else:
        allowed_tables = []

    for table in allowed_tables:
        if table in sql_query.lower():
            return sql_query
    raise PermissionError("Access denied: Your role is not authorized for this data.")


def enforce_geo(sql: str, region: str) -> str:
    if "Southwest" in sql and region != "India":
        raise PermissionError("Restricted by geographic access.")
    return sql
