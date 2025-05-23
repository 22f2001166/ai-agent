from vectorstore import load_vector_index
from llm import query_llm
from db import query_sql
from access_control import enforce_rbac, enforce_geo


def handle_query(user_input, role, region):
    vs = load_vector_index()
    user_input_lower = user_input.lower()

    try:
        # 1. Sales aggregation queries
        if "total sales" in user_input_lower or "sales amount" in user_input_lower:
            if "southwest" in user_input_lower:
                sql = "SELECT SUM(Sales) AS total_sales FROM inventory WHERE `Order Region` = 'Southwest'"
                sql = enforce_geo(sql, region)
                sql = enforce_rbac(sql, role)
                data = query_sql(sql)
                return {"type": "data", "data": data}
            elif (
                "by region" in user_input_lower
                or "distribution of orders" in user_input_lower
            ):
                sql = "SELECT `Order Region`, SUM(Sales) AS total_sales FROM inventory GROUP BY `Order Region`"
                sql = enforce_geo(sql, region)
                sql = enforce_rbac(sql, role)
                data = query_sql(sql)
                return {"type": "data", "data": data}
            else:
                sql = "SELECT SUM(Sales) AS total_sales FROM inventory"
                sql = enforce_geo(sql, region)
                sql = enforce_rbac(sql, role)
                data = query_sql(sql)
                return {"type": "data", "data": data}

        # 2. Customer related queries (top customers by order value)
        elif "top 10 customers" in user_input_lower:
            sql = """
                SELECT `Customer Id`, `Customer Fname`, `Customer Lname`, SUM(Sales) AS total_sales
                FROM inventory
                GROUP BY `Customer Id`
                ORDER BY total_sales DESC
                LIMIT 10
            """
            sql = enforce_geo(sql, region)
            sql = enforce_rbac(sql, role)
            data = query_sql(sql)
            return {"type": "data", "data": data}

        # 3. Inventory item classifications: no-mover, slow-moving, obsolete
        elif (
            "no-mover" in user_input_lower
            or "slow-moving inventory" in user_input_lower
        ):
            # Try a more targeted similarity search
            search_terms = "slow-moving inventory policy definition"
            docs = vs.similarity_search(search_terms)
            context = "\n\n".join([doc.page_content for doc in docs[:2]])
            prompt = f"Based on the following company policy context:\n{context}\n\nAnswer this: {user_input}"
            definition = query_llm(prompt)

            # Assign SQL based on detected keywords or default thresholds
            if "180 days" in definition or "no-mover" in user_input_lower:
                sql = "SELECT * FROM inventory WHERE `Days for shipping (real)` >= 180"
            elif "90 days" in definition or "slow-moving" in user_input_lower:
                sql = "SELECT * FROM inventory WHERE `Days for shipping (real)` BETWEEN 90 AND 179"
            else:
                # Default fallback for slow-moving if no threshold found
                if "slow-moving" in user_input_lower:
                    sql = "SELECT * FROM inventory WHERE `Days for shipping (real)` BETWEEN 90 AND 179"
                else:
                    sql = None

            if sql:
                sql = enforce_geo(sql, region)
                sql = enforce_rbac(sql, role)
                data = query_sql(sql)
                return {"type": "hybrid", "definition": definition, "data": data}

            # fallback if no suitable SQL
            answer = query_llm(
                f"Use the context below to answer:\n{context}\n\nQuestion: {user_input}"
            )
            return {"type": "doc", "answer": answer}

        # 4. Supplier qualification, ethical sourcing, performance KPIs
        elif any(
            k in user_input_lower
            for k in [
                "supplier",
                "ethical sourcing",
                "supplier selection",
                "supplier code of conduct",
                "supplier performance",
            ]
        ):
            docs = vs.similarity_search(user_input)
            context = "\n\n".join([doc.page_content for doc in docs[:2]])
            prompt = f"Use the context below to answer the question:\n{context}\n\nQuestion: {user_input}"
            answer = query_llm(prompt)
            return {"type": "doc", "answer": answer}

        # 5. Logistics, sustainability, returns, reverse logistics policies
        elif any(
            k in user_input_lower
            for k in [
                "logistics",
                "environmental sustainability",
                "returns",
                "reverse logistics",
            ]
        ):
            docs = vs.similarity_search(user_input)
            context = "\n\n".join([doc.page_content for doc in docs[:2]])
            prompt = f"Use the context below to answer the question:\n{context}\n\nQuestion: {user_input}"
            answer = query_llm(prompt)
            return {"type": "doc", "answer": answer}

        # 6. Product performance, profit margins, quality returns
        elif any(
            k in user_input_lower
            for k in [
                "profit margin",
                "quality-related returns",
                "product quality assurance",
            ]
        ):
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
                data = query_sql(sql)
                return {"type": "data", "data": data}
            else:
                docs = vs.similarity_search(user_input)
                context = "\n\n".join([doc.page_content for doc in docs[:2]])
                prompt = f"Use the context below to answer the question:\n{context}\n\nQuestion: {user_input}"
                answer = query_llm(prompt)
                return {"type": "doc", "answer": answer}

        # 7. Shipping mode and delivery performance
        elif any(
            k in user_input_lower
            for k in [
                "shipping mode",
                "on-time deliveries",
                "shipping modes",
                "delivery status",
            ]
        ):
            if "lowest rate of on-time deliveries" in user_input_lower:
                sql = """
                    SELECT `Shipping Mode`, AVG(CASE WHEN `Delivery Status`='On Time' THEN 1 ELSE 0 END) AS on_time_rate
                    FROM inventory
                    GROUP BY `Shipping Mode`
                    ORDER BY on_time_rate ASC
                    LIMIT 1
                """
                sql = enforce_geo(sql, region)
                sql = enforce_rbac(sql, role)
                data = query_sql(sql)
                return {"type": "data", "data": data}
            else:
                docs = vs.similarity_search(user_input)
                context = "\n\n".join([doc.page_content for doc in docs[:2]])
                prompt = f"Use the context below to answer the question:\n{context}\n\nQuestion: {user_input}"
                answer = query_llm(prompt)
                return {"type": "doc", "answer": answer}

        # 8. Hazardous materials storage compliance
        elif (
            "hazardous materials" in user_input_lower
            or "hse policy" in user_input_lower
        ):
            docs = vs.similarity_search(user_input)
            context = "\n\n".join([doc.page_content for doc in docs[:2]])
            prompt = f"Use the context below to answer the question:\n{context}\n\nQuestion: {user_input}"
            answer = query_llm(prompt)
            return {"type": "doc", "answer": answer}

        # 9. Average time between order and shipping date by country
        elif (
            "average time" in user_input_lower
            and "order date" in user_input_lower
            and "shipping date" in user_input_lower
        ):
            sql = """
                SELECT `Order Country`,
                       AVG(julianday(`shipping date (DateOrders)`) - julianday(`order date (DateOrders)`)) AS avg_shipping_delay
                FROM inventory
                GROUP BY `Order Country`
            """
            sql = enforce_geo(sql, region)
            sql = enforce_rbac(sql, role)
            data = query_sql(sql)
            return {"type": "data", "data": data}

        # 10. Declining sales over past quarters
        elif (
            "declining sales" in user_input_lower
            or "past three quarters" in user_input_lower
        ):
            docs = vs.similarity_search(user_input)
            context = "\n\n".join([doc.page_content for doc in docs[:2]])
            prompt = f"Use the context below to answer the question:\n{context}\n\nQuestion: {user_input}"
            answer = query_llm(prompt)
            return {"type": "doc", "answer": answer}

        # Default fallback to vector search + LLM answer
        else:
            docs = vs.similarity_search(user_input)
            context = "\n\n".join([doc.page_content for doc in docs[:2]])
            prompt = f"Use the context below to answer the question:\n{context}\n\nQuestion: {user_input}"
            answer = query_llm(prompt)
            return {"type": "doc", "answer": answer}

    except PermissionError as e:
        return {"type": "error", "message": str(e)}
