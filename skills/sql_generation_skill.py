from skills.chroma_rag_skill import retrieve_context_chroma
from agent.sql_agent import generate_sql
from agent.qc_agent import validate_sql
from agent.analyst_agent import analyze_result
from tools.db_tool import run_query


def answer_with_generated_sql(user_question: str):
    """
    Full AI workflow:
    User question -> ChromaDB RAG -> LLM SQL generation -> QC -> DB query -> Analyst answer.
    """
    rag_context = retrieve_context_chroma(user_question)

    try:
        sql = generate_sql(user_question, rag_context)
    except Exception as e:
        return {
            "success": False,
            "sql": "",
            "qc_message": f"SQL generation error: {e}",
            "dataframe": None,
            "analysis": "I could not generate SQL for this question.",
            "rag_context": rag_context
        }

    is_valid, qc_message = validate_sql(sql)

    if not is_valid:
        return {
            "success": False,
            "sql": sql,
            "qc_message": qc_message,
            "dataframe": None,
            "analysis": "The generated SQL did not pass safety checks.",
            "rag_context": rag_context
        }

    try:
        df = run_query(sql)

        if df.empty:
            result_markdown = "No rows returned."
        else:
            result_markdown = df.head(50).to_markdown(index=False)

        analysis = analyze_result(
            user_question=user_question,
            sql=sql,
            result_markdown=result_markdown,
            rag_context=rag_context
        )

        return {
            "success": True,
            "sql": sql,
            "qc_message": qc_message,
            "dataframe": df,
            "analysis": analysis,
            "rag_context": rag_context
        }

    except Exception as e:
        return {
            "success": False,
            "sql": sql,
            "qc_message": f"SQL execution error: {e}",
            "dataframe": None,
            "analysis": "The SQL query could not be executed.",
            "rag_context": rag_context
        }
