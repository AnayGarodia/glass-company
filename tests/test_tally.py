from unittest import mock
from ops import tally

FAKE = {
    "questions": [
        {"id": "q1", "title": "Email"},
        {"id": "q2", "title": "Who is this for?"},
    ],
    "submissions": [{
        "id": "sub1",
        "submittedAt": "2026-07-30T13:00:00Z",
        "responses": [
            {"questionId": "q1", "answer": "maya@example.com"},
            {"questionId": "q2", "answer": "My wife Maya"},
        ]}],
}


def test_fetch_intakes_normalizes():
    with mock.patch.object(tally, "_get", return_value=FAKE):
        intakes = tally.fetch_intakes("key", "form123")
    assert intakes == [{
        "submission_id": "sub1",
        "submitted_at": "2026-07-30T13:00:00Z",
        "fields": {"Email": "maya@example.com", "Who is this for?": "My wife Maya"},
    }]


def test_answer_shapes():
    data = {
        "questions": [{"id": "q1", "title": "Words"}],
        "submissions": [{"id": "s", "submittedAt": "t", "responses": [
            {"questionId": "q1", "answer": {"value": "nested"}},
        ]}, {"id": "s2", "submittedAt": "t2", "responses": [
            {"questionId": "q1", "answer": ["a", "b"]},
        ]}, {"id": "s3", "submittedAt": "t3", "responses": [
            {"questionId": "q1", "answer": None},
        ]}],
    }
    with mock.patch.object(tally, "_get", return_value=data):
        intakes = tally.fetch_intakes("k", "f")
    assert intakes[0]["fields"] == {"Words": "nested"}
    assert intakes[1]["fields"] == {"Words": "a, b"}
    assert intakes[2]["fields"] == {"Words": ""}
