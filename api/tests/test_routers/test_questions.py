import pytest
import requests

# Define global headers with x-api-key
API_KEY = "8df7c3a5a2c6ead085fa26b63c7d6ff41cd118e20790440e7395efddc8ce6af0"
HEADERS = {"x-api-key": API_KEY}

BASE_URL = "http://localhost:8000"  # Change to your API's base URL

EXISTING_QUESTION_ID = 546


# Test GET /api/questions
@pytest.mark.parametrize(
    "params,expected_status",
    [
        ("?skip=0&limit=10", 200),
        ("?reaction=like", 200),
        ("?model_id=1", 200),
        ("?conversation_id=1", 200),
        ("?date_from=2024-01-01T00:00:00&date_to=2025-01-01T00:00:00", 200),
        ("?limit=-10", 200),  # uses default limit
    ],
)
def test_get_questions(params, expected_status):
    response = requests.get(f"{BASE_URL}/api/questions{params}", headers=HEADERS)
    assert response.status_code == expected_status


# Test POST /api/questions
@pytest.mark.parametrize(
    "payload,expected_status",
    [
        ({"text": "What is FastAPI?", "type": "text", "answer_type": "text", "stream": False}, 200),
        ({"text": "What is FastAPI?", "type": "text", "answer_type": "text", "stream": True}, 200),
        ({"type": "text", "answer_type": "text"}, 422),  # Missing required text or files
    ],
)
def test_create_question(payload, expected_status):
    response = requests.post(f"{BASE_URL}/api/questions", json=payload, headers=HEADERS)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    "payload,expected_status_code,expected_audio_file",
    [
        (
                {"text": "What is FastAPI? Give a short answer", "type": "text", "answer_type": "text", "stream": False,
                 "answer_format": "text"},
                200,
                False
        ),
        (
                {"text": "What is FastAPI? Give a short answer", "type": "text", "answer_type": "text", "stream": False,
                 "answer_format": "audio"},
                200,
                True
        ),
        # More scenarios, such as invalid response_format
        (
                {"text": "What is FastAPI? Give a short answer", "type": "text", "answer_type": "text", "stream": False,
                 "answer_format": "unsupported"},
                422,  # Or whatever you expect for invalid format
                None
        ),
    ],
)
def test_response_format(payload, expected_status_code, expected_audio_file):
    response = requests.post(f"{BASE_URL}/api/questions", json=payload, headers=HEADERS)
    assert response.status_code == expected_status_code

    if response.status_code == 200:
        data = response.json()
        question = data["question"]

        assert len(question["answer"]) > 0

        if expected_audio_file is not None:
            if expected_audio_file:
                assert len(question["audio_file"]) > 0
            else:
                assert not question["audio_file"]


# Test GET /api/questions/{item_id}
@pytest.mark.parametrize(
    "item_id,expected_status",
    [
        (EXISTING_QUESTION_ID, 200),
        (9999, 404),  # Non-existent question
    ],
)
def test_get_question(item_id, expected_status):
    response = requests.get(f"{BASE_URL}/api/questions/{item_id}", headers=HEADERS)
    assert response.status_code == expected_status


# Test POST /api/questions/{item_id}/like
@pytest.mark.parametrize(
    "item_id,expected_status",
    [
        (EXISTING_QUESTION_ID, 200),
        (9999, 404),  # Non-existent question
    ],
)
def test_like_question(item_id, expected_status):
    response = requests.post(f"{BASE_URL}/api/questions/{item_id}/like", headers=HEADERS)
    assert response.status_code == expected_status


# Test POST /api/questions/{item_id}/dislike
@pytest.mark.parametrize(
    "item_id,expected_status",
    [
        (EXISTING_QUESTION_ID, 200),
        (9999, 404),  # Non-existent question
    ],
)
def test_dislike_question(item_id, expected_status):
    response = requests.post(f"{BASE_URL}/api/questions/{item_id}/dislike", headers=HEADERS)
    assert response.status_code == expected_status


# Test edge cases for POST /api/questions
@pytest.mark.parametrize(
    "payload,expected_status",
    [
        ({"text": "", "files": None}, 422),  # Both text and files are missing
        ({"text": "Valid question", "files": []}, 200),  # Valid text without files
    ],
)
def test_create_question_edge_cases(payload, expected_status):
    response = requests.post(f"{BASE_URL}/api/questions", json=payload, headers=HEADERS)
    assert response.status_code == expected_status


# Test invalid inputs for endpoints
@pytest.mark.parametrize(
    "item_id,expected_status",
    [
        ("invalid_id", 422),  # Non-integer ID
        (-1, 404),  # Negative ID (unlikely to exist)
    ],
)
def test_invalid_question_inputs(item_id, expected_status):
    response = requests.get(f"{BASE_URL}/api/questions/{item_id}", headers=HEADERS)
    assert response.status_code == expected_status
