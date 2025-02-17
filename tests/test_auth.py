import pytest
import requests
from http import HTTPStatus

from conftest import delete_user, create_headers

def test_register_user(base_url, create_user_data):
    response = requests.post(f"{base_url}/users", json=create_user_data)
    assert response.status_code == HTTPStatus.CREATED, f"Error register user: {response.text}"

    actual_user_data = response.json().get("user")

    check_user_data(actual_user_data, create_user_data, response.text)
    token = response.json().get("token")
    assert token, f"Token is missing in response: {token}"

    delete_user(token, base_url)

def test_get_user_info(base_url, register_user):
    expected_used_data, token = register_user
    response = requests.get(f"{base_url}/users/me", headers = create_headers(token))

    assert response.status_code == HTTPStatus.OK, "Error: Unable to get user info"

    actual_user_data = response.json()
    check_user_data(actual_user_data, expected_used_data, response.text)


def check_user_data(actual_user_data, expected_user_data, response_text):
    assert "_id" in actual_user_data, f"Missing id: {response_text}"
    assert actual_user_data["email"] == expected_user_data["email"], "Error: email does not match"
    assert actual_user_data["firstName"] == expected_user_data["firstName"], "Error: firstName does not match"
    assert actual_user_data["lastName"] == expected_user_data["lastName"], "Error: lastName does not match"
    assert "__v" in actual_user_data, f"Missing version: {response_text}"

def test_update_user_email(base_url, register_user):
    expected_used_data, token = register_user
    new_email = "111dom@gmail.com"
    update_data = {"email": new_email}

    response = requests.patch(f"{base_url}/users/me", json=update_data, headers=create_headers(token))
    assert response.status_code == HTTPStatus.OK, f"Email update error: {response.text}"
    actual_user_data = response.json()
    assert actual_user_data["email"] == new_email, "Error: email does not match"
    assert actual_user_data["firstName"] == expected_used_data["firstName"], "Error: firstName does not match"
    assert actual_user_data["lastName"] == expected_used_data["lastName"], "Error: lastName does not match"


def test_delete_user(base_url, create_user_data):
    response = requests.post(f"{base_url}/users", json=create_user_data)
    assert response.status_code == HTTPStatus.CREATED, f"Registration error: {response.text}"

    token = response.json().get("token")
    headers = create_headers(token)

    response = requests.delete(f"{base_url}/users/me", headers = headers)
    assert response.status_code == HTTPStatus.OK, "Error: Unable to delete user"

    response_after_delete = requests.get(f"{base_url}/users/me", headers=headers)
    assert response_after_delete.status_code == HTTPStatus.UNAUTHORIZED,  "Error: User data is still accessible after deletion"


def test_login_existing_user(register_user_with_logout, base_url, create_user_data):
    response = requests.post(f"{base_url}/users/login", json=create_user_data)
    assert response.status_code == HTTPStatus.OK, f"Login error: {response.status_code}"

    token = response.json().get("token")
    assert token, "Error: Token missing from response"

def test_logout(base_url, register_user, create_user_data):
    user_data, token = register_user
    response = requests.post(f"{base_url}/users/logout", headers=create_headers(token))

    assert response.status_code == HTTPStatus.OK, f"Logout error: {response.status_code}"

    # we log in again because "delete_user" needs authentication to execute
    response = requests.post(f"{base_url}/users/login", json=create_user_data)
    assert response.status_code == HTTPStatus.OK, "Error: Unable to log in after logout"
    token = response.json().get("token")
    delete_user(token, base_url)

def test_registration_duplicate_email(register_user, base_url, create_user_data):
    user_data, _ = register_user
    response = requests.post(f"{base_url}/users", json=create_user_data)
    actual_error_message = response.json().get("message")
    assert response.status_code == HTTPStatus.BAD_REQUEST, f"Error: A user with this email has registered again!: {response.text}"
    assert "Email address is already in use" == actual_error_message, f"Unexpected error message: {actual_error_message}"

@pytest.mark.parametrize("user_data, expected_status, error_message_part", [
        # Missing required fields
        ({"firstName": "", "lastName": "", "email": "", "password": ""}, HTTPStatus.BAD_REQUEST, "User validation failed: firstName: Path `firstName` is required., lastName: Path `lastName` is required., email: Email is invalid, password: Path `password` is required"),
        ({"firstName": "", "lastName": "Doe", "email": "testemail@test.com", "password": "ValidPass123!"}, HTTPStatus.BAD_REQUEST, "User validation failed: firstName"),
        ({"firstName": "John", "lastName": "", "email": "testemail@test.com", "password": "ValidPass123!"}, HTTPStatus.BAD_REQUEST, "User validation failed: lastName"),
        ({"firstName": "John", "lastName": "Doe", "email": "", "password": "ValidPass123!"}, HTTPStatus.BAD_REQUEST, "User validation failed: email: Email is invalid"),
        ({"firstName": "John", "lastName": "Doe", "email": "testemail@test.com", "password": ""}, HTTPStatus.BAD_REQUEST, "User validation failed: password: Path `password` is required."),

        # Invalid emails and password
        ({"firstName": "John", "lastName": "Doe", "email": "testemail@test,com", "password": "ValidPass123!"}, HTTPStatus.BAD_REQUEST, "User validation failed: email: Email is invalid"),
        ({"firstName": "John", "lastName": "Doe", "email": "testemail@test.", "password": "ValidPass123!"}, HTTPStatus.BAD_REQUEST, "User validation failed: email: Email is invalid"),
        ({"firstName": "John", "lastName": "Doe", "email": "john.doe@example", "password": "ValidPass123!"}, HTTPStatus.BAD_REQUEST, "User validation failed: email: Email is invalid"),
        ({"firstName": "Test", "lastName": "User", "email": "user@example.com", "password": " 	"}, HTTPStatus.BAD_REQUEST, "User validation failed: password: Path `password` is required."),

        # XSS attacks and SQL injections
        #todo add generation e-mail
        # Validation for XSS injections is missing, but after the first failure, the test fails with an error about an existing email.
        #({"firstName": "<svg onload=alert()>", "lastName": "Doe", "email": "testema45@test.com", "password": "ValidPass123!"}, HTTPStatus.BAD_REQUEST, "XSS in firstName"),
        #({"firstName": "John", "lastName": "' OR 1=1 --", "email": "testemail@test.com", "password": "ValidPass123!"}, HTTPStatus.BAD_REQUEST, "SQL injection in lastName"),
        #({"firstName": "John", "lastName": "Doe", "email": "<script>alert('XSS')</script>@example.com", "password": "ValidPass123!"}, HTTPStatus.BAD_REQUEST, "XSS in email"),
        #({"firstName": "John", "lastName": "Doe", "email": "testemail@test.com", "password": "' OR '1'='1"}, HTTPStatus.BAD_REQUEST, "SQL injection in password"),

        # Values too long
        ({"firstName": "A" * 256, "lastName": "B" * 256, "email": "testemail@test.com", "password": "ValidPass123"}, HTTPStatus.BAD_REQUEST, "User validation failed: firstName: Path `firstName`"),
        ({"firstName": "John", "lastName": "Doe", "email": "testemail@test.com", "password": "short"}, HTTPStatus.BAD_REQUEST, "User validation failed: password: Path `password` (`short`) is shorter than the minimum allowed length (7)."),
        ({"firstName": "John", "lastName": "Doe", "email": "testemail@test.com", "password": "aa" * 256}, HTTPStatus.BAD_REQUEST, "User validation failed: password: Path `password`"),
        ])
def test_register_user_negative_cases(base_url, user_data, expected_status, error_message_part):
    response = requests.post(f"{base_url}/users", json=user_data)
    assert response.status_code == expected_status, f"Error: unexpected status code {response.status_code} for check [{error_message_part}]- {response.text}"
    actual_error_message = response.json().get("message")
    print(f"Message [{actual_error_message}]")
    assert error_message_part in actual_error_message, f"Not found expected [{error_message_part}]: {response.text}"


@pytest.mark.parametrize("user_data, expected_status, description", [
    # Missing required fields
    ({"email": "", "password": ""}, HTTPStatus.UNAUTHORIZED, "All fields are missing"),
    ({"email": "testemail@test.com", "password": "ValidPass123!"}, HTTPStatus.UNAUTHORIZED, "Email is missing"),
    ({"email": "testemail@test.com", "password": "password123"}, HTTPStatus.UNAUTHORIZED, "Password is missing"),

    # Invalid emails
    ({"email": "testemailtest.com", "password": "password123"}, HTTPStatus.UNAUTHORIZED, "Invalid email"),
    ({"email": "testemail@test.", "password": "password123"}, HTTPStatus.UNAUTHORIZED, "Incomplete email"),
    ({"email": "john.doe@example", "password": "ValidPass123!"}, HTTPStatus.UNAUTHORIZED, "Missing domain extension in email"),

    # Not registered user
    ({"email": "testnewemail@test.com", "password": "123456789123456789"}, HTTPStatus.UNAUTHORIZED, "Unregistered use"),

    # XSS attacks and SQL injections
    ({"email": "<script>alert('XSS')</script>@example.com", "password": "ValidPass123!"}, HTTPStatus.UNAUTHORIZED, "XSS in email"),
    ({"email": "testemail@test.com", "password": "<script>alert('XSS')</script>"}, HTTPStatus.UNAUTHORIZED, "XSS in password"),
    ({"email": "testemail@test.com", "password": "' OR '1'='1"}, HTTPStatus.UNAUTHORIZED, "SQL injection in password"),
    ({"email": "'; DROP TABLE users; --", "password": "ValidPass123!"}, HTTPStatus.UNAUTHORIZED, "SQL injection in email"),
])
def test_login_user_negative_cases(base_url, user_data, expected_status, description):
    response = requests.post(f"{base_url}/users/login", json=user_data)
    assert response.status_code == expected_status, f"Error: {description}"







