from vectorstore import load_vector_index
from llm import query_llm
from db import query_sql
from access_control import enforce_rbac, enforce_geo


def handle_query(user_input, role, region):
    vs = load_vector_index()
    user_input_lower = user_input.lower()

    def handle_doc_query():
        docs = vs.similarity_search(user_input)
        context = "\n\n".join([doc.page_content for doc in docs[:2]])
        prompt = f"Use the context below to answer the question:\n{context}\n\nQuestion: {user_input}"
        answer = query_llm(prompt)
        return {"type": "doc", "answer": answer}

    try:
        # 1. Total sales (all / region-based)
        if "total sales" in user_input_lower or "sales amount" in user_input_lower:
            if "southwest" in user_input_lower:
                sql = "SELECT SUM(Sales) AS total_sales FROM inventory WHERE `Order Region` = 'Southwest'"
            else:
                sql = "SELECT SUM(Sales) AS total_sales FROM inventory"
            sql = enforce_geo(sql, region)
            sql = enforce_rbac(sql, role)
            return {"type": "data", "data": query_sql(sql)}

        # 2. Distribution by customer segment and region
        if (
            "distribution of orders" in user_input_lower
            and "segment" in user_input_lower
        ):
            sql = """
                SELECT `Customer Segment`, `Order Region`, COUNT(*) AS order_count
                FROM inventory
                GROUP BY `Customer Segment`, `Order Region`
            """
            sql = enforce_geo(sql, region)
            sql = enforce_rbac(sql, role)
            return {"type": "data", "data": query_sql(sql)}

        # 3. Top 10 customers by total order value
        if "top 10 customers" in user_input_lower:
            sql = """
                SELECT `Customer Id`, `Customer Fname`, `Customer Lname`, SUM(Sales) AS total_sales
                FROM inventory
                GROUP BY `Customer Id`
                ORDER BY total_sales DESC
                LIMIT 10
            """
            sql = enforce_geo(sql, region)
            sql = enforce_rbac(sql, role)
            return {"type": "data", "data": query_sql(sql)}

        # 4. Highest profit margin products
        if "highest profit margin" in user_input_lower:
            sql = """
                SELECT `Product Name`, MAX(`Order Item Profit Ratio`) AS max_profit_margin
                FROM inventory
                GROUP BY `Product Name`
                ORDER BY max_profit_margin DESC
                LIMIT 10
            """
            sql = enforce_geo(sql, region)
            sql = enforce_rbac(sql, role)
            return {"type": "data", "data": query_sql(sql)}

        # 5. Slow-moving / No-mover inventory
        if "slow-moving" in user_input_lower or "no-mover" in user_input_lower:
            search_terms = "inventory classification policy"
            docs = vs.similarity_search(search_terms)
            context = "\n\n".join([doc.page_content for doc in docs[:2]])
            prompt = f"Based on the following context:\n{context}\n\n{user_input}"
            definition = query_llm(prompt)
            if "180 days" in definition:
                sql = "SELECT * FROM inventory WHERE `Days for shipping (real)` >= 180"
            else:
                sql = "SELECT * FROM inventory WHERE `Days for shipping (real)` BETWEEN 90 AND 179"
            sql = enforce_geo(sql, region)
            sql = enforce_rbac(sql, role)
            return {"type": "hybrid", "definition": definition, "data": query_sql(sql)}

        # 6. Average time between order and shipping date by country
        if "average time" in user_input_lower and "shipping date" in user_input_lower:
            sql = """
                SELECT `Order Country`,
                       AVG(julianday(`shipping date (DateOrders)`) - julianday(`order date (DateOrders)`)) AS avg_days
                FROM inventory
                GROUP BY `Order Country`
            """
            sql = enforce_geo(sql, region)
            sql = enforce_rbac(sql, role)
            return {"type": "data", "data": query_sql(sql)}

        # 7. Declining sales in past 3 quarters (simplified)
        if "declining sales" in user_input_lower:
            sql = """
                SELECT `Product Category`, SUM(Sales) AS total_sales, strftime('%Y-Q%m', `order date (DateOrders)`) AS quarter
                FROM inventory
                GROUP BY `Product Category`, quarter
                ORDER BY `Product Category`, quarter
            """
            sql = enforce_geo(sql, region)
            sql = enforce_rbac(sql, role)
            return {"type": "data", "data": query_sql(sql)}

        # 8. On-time delivery analysis by shipping mode
        if "on-time deliveries" in user_input_lower:
            sql = """
                SELECT `Shipping Mode`, 
                       AVG(CASE WHEN `Delivery Status` = 'On Time' THEN 1 ELSE 0 END) AS on_time_rate
                FROM inventory
                GROUP BY `Shipping Mode`
                ORDER BY on_time_rate ASC
                LIMIT 1
            """
            sql = enforce_geo(sql, region)
            sql = enforce_rbac(sql, role)
            return {"type": "data", "data": query_sql(sql)}

        # 9. Product quality returns
        if "quality-related returns" in user_input_lower:
            return handle_doc_query()

        # 10. Supplier compliance, sourcing, KPIs
        if any(
            k in user_input_lower
            for k in ["supplier", "ethical", "code of conduct", "kpi"]
        ):
            return handle_doc_query()

        # 11. Logistics, returns, sustainability
        if any(
            k in user_input_lower for k in ["logistics", "sustainability", "returns"]
        ):
            return handle_doc_query()

        # 12. Hazardous material compliance
        if "hazardous materials" in user_input_lower:
            return handle_doc_query()

        # 13. Risk management threshold breaches
        if (
            "risk tolerance" in user_input_lower
            or "risk management" in user_input_lower
        ):
            return handle_doc_query()

        # Default to semantic search if no rule matched
        return handle_doc_query()

    except Exception as e:
        return {"type": "error", "message": str(e)}
