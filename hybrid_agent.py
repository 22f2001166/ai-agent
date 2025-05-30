from vectorstore import load_vector_index
from llm import query_llm
from db import query_sql
from access_control import enforce_rbac, enforce_geo


def handle_query(user_input, role, region):
    vs = load_vector_index()
    user_input_lower = user_input.lower()

    import re

    def format_answer(text):
        lines = text.strip().splitlines()
        formatted_lines = []

        for line in lines:
            # Format numbered steps
            if re.match(r"^\d+\.\s", line):
                formatted_lines.append(f"**{line}**")
            # Format sub-bullets with dashes
            elif re.match(r"^\s*-\s", line):
                formatted_lines.append(f"{line}")
            # Format section headers (optional heuristic)
            elif ":" in line and not line.strip().startswith("-"):
                parts = line.split(":", 1)
                formatted_lines.append(f"**{parts[0].strip()}**:{parts[1]}")
            else:
                formatted_lines.append(line)

        return "\n".join(formatted_lines)

    def handle_doc_query():
        docs = vs.similarity_search(user_input)
        context = "\n\n".join([doc.page_content for doc in docs[:2]])
        prompt = f"Use the context below to answer the question:\n{context}\n\nQuestion: {user_input}"
        raw_answer = query_llm(prompt)
        formatted_answer = format_answer(raw_answer)
        return {"type": "doc", "answer": formatted_answer}

    try:
        # 1. Total sales (all / region-based)
        if "total sales" in user_input_lower or "sales amount" in user_input_lower:
            if "southeast" in user_input_lower:
                sql = "SELECT SUM(Sales) AS total_sales FROM inventory WHERE `Order Region` = 'Southeast Asia'"
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
        if "no-mover" in user_input_lower and "total value" in user_input_lower:
            sql = """
                SELECT
                    SUM(`Order Item Product Price` * `Order Item Quantity`) AS total_value_no_mover
                FROM inventory
                WHERE julianday('now') - julianday(`order date (DateOrders)`) > 365
            """
            sql = enforce_geo(sql, region)
            sql = enforce_rbac(sql, role)
            return {"type": "data", "data": query_sql(sql)}

        # 6. Average time between order and shipping date by country
        if "average time" in user_input_lower and "shipping date" in user_input_lower:
            sql = """
                SELECT 
                `Order Country`,
                AVG(
                    julianday(
                    substr(`shipping date (DateOrders)`, instr(`shipping date (DateOrders)`, '/') + 4, 4) || '-' ||
                    printf('%02d', CAST(substr(`shipping date (DateOrders)`, 1, instr(`shipping date (DateOrders)`, '/') - 1) AS INTEGER)) || '-' ||
                    printf('%02d', CAST(substr(`shipping date (DateOrders)`, instr(`shipping date (DateOrders)`, '/') + 1, instr(substr(`shipping date (DateOrders)`, instr(`shipping date (DateOrders)`, '/') + 1), '/') - 1) AS INTEGER)) || ' ' ||
                    substr(`shipping date (DateOrders)`, instr(`shipping date (DateOrders)`, ' ') + 1) ||
                    printf(':%02d', 0)
                    ) - 
                    julianday(
                    substr(`order date (DateOrders)`, instr(`order date (DateOrders)`, '/') + 4, 4) || '-' ||
                    printf('%02d', CAST(substr(`order date (DateOrders)`, 1, instr(`order date (DateOrders)`, '/') - 1) AS INTEGER)) || '-' ||
                    printf('%02d', CAST(substr(`order date (DateOrders)`, instr(`order date (DateOrders)`, '/') + 1, instr(substr(`order date (DateOrders)`, instr(`order date (DateOrders)`, '/') + 1), '/') - 1) AS INTEGER)) || ' ' ||
                    substr(`order date (DateOrders)`, instr(`order date (DateOrders)`, ' ') + 1) ||
                    printf(':%02d', 0)
                    )
                ) AS avg_days
                FROM inventory
                GROUP BY `Order Country`;
            """
            sql = enforce_geo(sql, region)
            sql = enforce_rbac(sql, role)
            return {"type": "data", "data": query_sql(sql)}

        # 7. Declining sales in past 3 quarters (simplified)
        if "declining sales" in user_input_lower:
            sql = """
                SELECT 
                    `Category Name`, 
                    SUM(Sales) AS total_sales,
                    strftime('%Y', `order date (DateOrders)`) || '-Q' || 
                    (CAST((CAST(strftime('%m', `order date (DateOrders)`) AS INTEGER) - 1) / 3 AS INTEGER) + 1) AS quarter
                FROM inventory
                GROUP BY `Category Name`, quarter
                ORDER BY `Category Name`, quarter;
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
