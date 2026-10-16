import uuid

from app.agents.query import understand
from app.core.security import screen_input
from app.tools.analytics import Fact, contribution_analysis, period_over_period
from app.tools.rag.retriever import retrieve
from app.tools.sql.executor import execute


def answer(question: str) -> dict:
    warnings = screen_input(question)
    trace_id = str(uuid.uuid4())
    if warnings:
        return {"question": question, "summary": "I can help with business analysis, but cannot follow instruction-like content.", "verified_facts": [], "hypotheses": [], "recommended_investigations": [], "charts": [], "citations": [], "warnings": warnings, "trace_id": trace_id, "trace": {"plan": []}}
    spec = understand(question)
    if spec.intent == "policy_question":
        passages = retrieve(question, spec.region)
        return _response(question, spec, [], [], passages, trace_id, ["rag"])
    region_filter = f"WHERE region = '{spec.region}'" if spec.region else ""
    sql = f"""SELECT CASE WHEN sale_date < '2026-07-01' THEN '2026-Q2' ELSE '2026-Q3' END AS period,
       region, product, ROUND(SUM(revenue), 2) AS revenue
       FROM v_sales_enriched {region_filter}
       GROUP BY period, region, product ORDER BY period, product"""
    frame, executed_sql = execute(sql)
    passages = retrieve(question, spec.region) if spec.intent == "root_cause" else []
    return _response(question, spec, frame, [executed_sql], passages, trace_id, ["sql", "analytics"] + (["rag"] if passages else []))


def _response(question, spec, frame, queries, passages, trace_id, plan):
    facts, charts = [], []
    if not frame.empty:
        totals = frame.groupby("period", as_index=False)["revenue"].sum()
        _delta, percent = period_over_period(totals)
        direction = "fell" if percent < 0 else "rose"
        facts.append(Fact("f1", f"Revenue {direction} {abs(percent):.1%} from Q2 to Q3.", percent, {"type": "sql", "query_id": "q1"}).as_dict())
        drivers = contribution_analysis(frame.groupby(["period", "product"], as_index=False)["revenue"].sum(), "product")
        if not drivers.empty:
            driver = drivers.iloc[0]
            facts.append(Fact("f2", f"{driver['product']} changed revenue by ${driver['delta']:,.0f}.", float(driver["delta"]), {"type": "sql", "query_id": "q1"}).as_dict())
            charts.append({"type": "bar", "title": "Revenue change by product", "data": drivers.to_dict(orient="records"), "x": "product", "y": "delta"})
    hypotheses = []
    for passage in passages:
        hypotheses.append({"statement": f"{passage.title} may help explain the observed result.", "confidence": "medium", "support": [{"type": "rag", "doc_id": passage.doc_id, "chunk_id": passage.chunk_id}], "needs_validation": True})
    summary = facts[0]["statement"] if facts else "Retrieved relevant business-document evidence."
    if hypotheses:
        summary += " Documents provide possible context; they are labeled as hypotheses until validated."
    return {"question": question, "interpretation": {"metric": spec.metric, "region": spec.region, "period": "2026-Q3", "baseline": "2026-Q2"}, "summary": summary, "verified_facts": facts, "hypotheses": hypotheses, "recommended_investigations": ["Compare post-campaign unit sales by product.", "Review competitor pricing and win/loss notes in South."], "charts": charts, "citations": [{"id": f"c{index}", "doc_id": p.doc_id, "page": p.page, "excerpt_ref": p.chunk_id, "excerpt": p.text} for index, p in enumerate(passages, 1)], "warnings": [], "trace_id": trace_id, "trace": {"plan": plan, "executed_sql": queries}}
