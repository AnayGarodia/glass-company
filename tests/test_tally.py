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


def _page(n, has_more):
    """One page of Tally's real response shape: 50 submissions, newest first."""
    return {
        "page": n,
        "limit": 50,
        "hasMore": has_more,
        "questions": [{"id": "q1", "title": "Email"}],
        "submissions": [{
            "id": f"p{n}s{i}",
            "submittedAt": f"2026-08-0{n}T00:00:{i:02d}Z",
            "responses": [{"questionId": "q1", "answer": f"p{n}s{i}@example.com"}],
        } for i in range(50)],
    }


def test_fetch_intakes_follows_pagination():
    pages = [_page(1, True), _page(2, True), _page(3, False)]
    with mock.patch.object(tally, "_get", side_effect=pages) as g:
        intakes = tally.fetch_intakes("k", "f")
    assert len(intakes) == 150, "a backlog past page 1 must not fall off silently"
    assert [c.args[1] for c in g.call_args_list] == [
        "/forms/f/submissions?page=1",
        "/forms/f/submissions?page=2",
        "/forms/f/submissions?page=3",
    ]
    # The oldest submission is the one a single-page read would have lost.
    assert intakes[-1]["submission_id"] == "p3s49"


def test_fetch_intakes_stops_when_no_more():
    with mock.patch.object(tally, "_get", side_effect=[_page(1, False)]) as g:
        intakes = tally.fetch_intakes("k", "f")
    assert len(intakes) == 50
    assert g.call_count == 1


def test_fetch_intakes_refuses_to_truncate_silently():
    """A form that never stops paginating must fail loudly, not return a slice."""
    with mock.patch.object(tally, "_get", return_value=_page(1, True)):
        try:
            tally.fetch_intakes("k", "f")
        except RuntimeError as e:
            assert "truncated" in str(e)
        else:
            raise AssertionError("expected RuntimeError")
