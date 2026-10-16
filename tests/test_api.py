from app.api.main import ask, health
from app.api.schemas import AskRequest
from app.db.seed import seed


def test_health_and_ask():
    seed()
    assert health()["status"] == "ok"
    response = ask(AskRequest(question="Compare South revenue in Q2 and Q3"))
    assert response["verified_facts"]
