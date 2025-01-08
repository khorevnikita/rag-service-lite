import pytest
import requests

# Define global headers with x-api-key
API_KEY = "b10094088c44d70cec75ab289ca8ad7dfef8ce38a10b6844ebb55765ca751fb5"
HEADERS = {"x-api-key": API_KEY}

BASE_URL = "http://localhost:8000"  # Change to your API's base URL

ACCOUNT_ID = 19
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
