import base64
from unittest import mock
from ops import emailer


def test_send_delivery_builds_payload(tmp_path):
    pdf = tmp_path / "x.pdf"
    pdf.write_bytes(b"%PDF-fake")
    with mock.patch.object(emailer, "_post",
                           return_value={"message_id": "msg_1"}) as p:
        mid = emailer.send_delivery("key", "a@b.com", "Your crossword",
                                    "<p>hi</p>", pdf_path=str(pdf))
    assert mid == "msg_1"
    path, payload = p.call_args.args[1], p.call_args.args[2]
    assert path == f"/inboxes/{emailer.INBOX}/messages/send"
    assert payload["to"] == "a@b.com"
    assert "run autonomously by an AI" in payload["html"]
    att = payload["attachments"][0]
    assert att["filename"] == "x.pdf"
    assert att["content_type"] == "application/pdf"
    assert base64.b64decode(att["content"]) == b"%PDF-fake"


def test_send_without_attachment():
    with mock.patch.object(emailer, "_post",
                           return_value={"message_id": "m"}) as p:
        emailer.send_delivery("key", "a@b.com", "s", "<p>x</p>")
    assert "attachments" not in p.call_args.args[2]


def test_fetch_inbound():
    with mock.patch.object(emailer, "_get",
                           return_value={"count": 1, "messages": [{"message_id": "m1"}]}):
        msgs = emailer.fetch_inbound("key")
    assert msgs == [{"message_id": "m1"}]


def test_sender_email_extracts_bare_address():
    assert emailer.sender_email({"from": "Jane Doe <jane@example.com>"}) == "jane@example.com"
    assert emailer.sender_email({"from": "AgentMail <glasscomany@agentmail.to>"}) == "glasscomany@agentmail.to"


def test_sender_email_handles_bare_address_already():
    assert emailer.sender_email({"from": "plain@example.com"}) == "plain@example.com"


def test_sender_email_is_case_insensitive():
    assert emailer.sender_email({"from": "Jane <Jane@Example.COM>"}) == "jane@example.com"
