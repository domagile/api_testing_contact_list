import pytest
import requests
from http import HTTPStatus

from conftest import create_headers, contact_data_2


def test_add_contact(base_url, contact_data_1, register_user):
    user_data, token = register_user

    response = requests.post(f"{base_url}/contacts", json=contact_data_1, headers=create_headers(token))
    assert response.status_code == HTTPStatus.CREATED, f"Error [add contact]: {response.status_code}"

    actual_user_data = response.json()
    check_user_data(actual_user_data, contact_data_1, user_data.get("_id"), response.text)


def check_user_data(actual_user_data, expected_user_data, user_id, response_text):
    assert "_id" in actual_user_data, f"Missing id: {response_text}"
    assert actual_user_data["firstName"] == expected_user_data["firstName"], "Error: firstName does not match"
    assert actual_user_data["lastName"] == expected_user_data["lastName"], "Error: lastName does not match"
    assert actual_user_data["birthdate"] == expected_user_data["birthdate"], "Error: birthdate does not match"
    assert actual_user_data["email"] == expected_user_data["email"], "Error: email does not match"
    assert actual_user_data["phone"] == expected_user_data["phone"], "Error: phone does not match"
    assert actual_user_data["street1"] == expected_user_data["street1"], "Error: street1 does not match"
    assert actual_user_data["street2"] == expected_user_data["street2"], "Error: street2 does not match"
    assert actual_user_data["city"] == expected_user_data["city"], "Error: city does not match"
    assert actual_user_data["stateProvince"] == expected_user_data["stateProvince"], "Error: stateProvince does not match"
    assert actual_user_data["postalCode"] == expected_user_data["postalCode"], "Error: postalCode does not match"
    assert actual_user_data["country"] == expected_user_data["country"], "Error: country does not match"
    assert actual_user_data["owner"] == user_id, "Error: owner does not match"
    assert "__v" in actual_user_data, f"Missing version: {response_text}"


#todo remove duplication of contact creation and check
def test_get_contact_list(base_url, contact_data_1, contact_data_2, contact_data_3, register_user):
    user_data, token = register_user
    response = requests.post(f"{base_url}/contacts", json=contact_data_1, headers=create_headers(token))
    assert response.status_code == HTTPStatus.CREATED, f"Error [add contact]: {response.status_code}"
    expected_contact_1_id = response.json().get("_id")
    print(f"Expected contact 1 id: {expected_contact_1_id}")

    response = requests.post(f"{base_url}/contacts", json=contact_data_2, headers=create_headers(token))
    assert response.status_code == HTTPStatus.CREATED, f"Error [add contact]: {response.status_code}"
    expected_contact_2_id = response.json().get("_id")
    print(f"Expected contact 2 id: {expected_contact_2_id}")

    response = requests.post(f"{base_url}/contacts", json=contact_data_3, headers=create_headers(token))
    assert response.status_code == HTTPStatus.CREATED, f"Error [add contact]: {response.status_code}"
    expected_contact_3_id = response.json().get("_id")
    print(f"Expected contact 3 id: {expected_contact_3_id}")

    contact_list_response = requests.get(f"{base_url}/contacts", headers=create_headers(token))
    assert contact_list_response.status_code == HTTPStatus.OK, f"Error [get contacts list]: {contact_list_response.text}"
    print(f"Contact list response: {contact_list_response.json()}")

    actual_contact_1 = next((contact for contact in contact_list_response.json() if contact.get("_id") == expected_contact_1_id), None)
    assert actual_contact_1 is not None, "Contact is not found"

    owner = actual_contact_1.get("owner")
    user_id = user_data.get("_id")
    assert owner == user_id, "Incorrect owner"
    compare_contacts(actual_contact_1, contact_data_1)

    actual_contact_2 = next((contact for contact in contact_list_response.json() if contact.get("_id") == expected_contact_2_id), None)
    assert actual_contact_2 is not None, "Contact is not found"

    owner = actual_contact_2.get("owner")
    user_id = user_data.get("_id")
    assert owner == user_id
    compare_contacts(actual_contact_2, contact_data_2)

    actual_contact_3 = next((contact for contact in contact_list_response.json() if contact.get("_id") == expected_contact_3_id), None)
    assert actual_contact_3 is not None, "Contact is not found"

    owner = actual_contact_3.get("owner")
    user_id = user_data.get("_id")
    assert owner == user_id
    compare_contacts(actual_contact_3, contact_data_3)

#todo move duplicate code to method
def test_get_contact(base_url, contact_data_1, contact_data_2, contact_data_3, register_user):
    _, token = register_user
    response = requests.post(f"{base_url}/contacts", json=contact_data_1, headers=create_headers(token))
    assert response.status_code == HTTPStatus.CREATED, f"Error [add contact]: {response.status_code}"
    response = requests.post(f"{base_url}/contacts", json=contact_data_2, headers=create_headers(token))
    assert response.status_code == HTTPStatus.CREATED, f"Error [add contact]: {response.status_code}"
    contact_2_id = response.json().get("_id")
    response = requests.post(f"{base_url}/contacts", json=contact_data_3, headers=create_headers(token))
    assert response.status_code == HTTPStatus.CREATED, f"Error [add contact]: {response.status_code}"

    response = requests.get(f"{base_url}/contacts/{contact_2_id}", headers=create_headers(token))
    assert response.status_code == HTTPStatus.OK, f"Error [get contact]: {response.text}"
    actual_contact_2 = response.json()
    compare_contacts(actual_contact_2, contact_data_2)

def test_update_contact_put(base_url, contact_data_1, contact_data_2, register_user):
    _, token = register_user
    response = requests.post(f"{base_url}/contacts", json=contact_data_1, headers=create_headers(token))
    assert response.status_code == HTTPStatus.CREATED, f"Error [add contact]: {response.status_code}"
    response = requests.post(f"{base_url}/contacts", json=contact_data_1, headers=create_headers(token))
    assert response.status_code == HTTPStatus.CREATED, f"Error [add contact]: {response.status_code}"
    contact_id = response.json().get("_id")

    response = requests.put(f"{base_url}/contacts/{contact_id}", json=contact_data_2, headers=create_headers(token))
    assert response.status_code == HTTPStatus.OK, f"Error [update contact put]: {response.text}"
    actual_contact_data = response.json()
    compare_contacts(actual_contact_data, contact_data_2)

def test_update_contact_patch(base_url, contact_data_1, register_user):
    _, token = register_user
    response = requests.post(f"{base_url}/contacts", json=contact_data_1, headers=create_headers(token))
    assert response.status_code == HTTPStatus.CREATED, f"Error [add contact]: {response.status_code}"
    response = requests.post(f"{base_url}/contacts", json=contact_data_1, headers=create_headers(token))
    assert response.status_code == HTTPStatus.CREATED, f"Error [add contact]: {response.status_code}"
    contact_id = response.json().get("_id")

    updated_field_json = {"firstName": "Anna"}
    response = requests.patch(f"{base_url}/contacts/{contact_id}", json=updated_field_json, headers=create_headers(token))
    assert response.status_code == HTTPStatus.OK, f"Error [update contact patch]: {response.text}"
    actual_contact_data = response.json()
    assert actual_contact_data["firstName"] == updated_field_json["firstName"], "Error: firstName was not updated"

def test_delete_contact_(base_url, contact_data_1, register_user):
    _, token = register_user
    response = requests.post(f"{base_url}/contacts", json=contact_data_1, headers=create_headers(token))
    assert response.status_code == HTTPStatus.CREATED, f"Error [add contact]: {response.status_code}"
    contact_id = response.json().get("_id")

    response = requests.delete(f"{base_url}/contacts/{contact_id}", headers=create_headers(token))
    assert response.status_code == HTTPStatus.OK, f"Error [delete contact]: {response.status_code}"
    response = requests.get(f"{base_url}/contacts/{contact_id}", headers=create_headers(token))
    assert response.status_code == HTTPStatus.NOT_FOUND, f"Contact should not be found"


@pytest.mark.parametrize("contact_data, expected_status, error_message_part", [

    # Missing required fields
    ({"firstName": "John", "lastName": "", "dateOfBirth": "", "email": "", "password": ""}, HTTPStatus.BAD_REQUEST,
     "Contact validation failed: lastName: Path `lastName` is required., email: Email is invalid"),
    ({"firstName": "", "lastName": "Doe", "dateOfBirth": "1990-05-05", "email": "testsmail@test.com", "password": "ValidPass123!"},
     HTTPStatus.BAD_REQUEST, "Contact validation failed: firstName: Path `firstName` is required."),
    ({"firstName": "John", "lastName": "", "dateOfBirth": "1990-05-05", "email": "testsmail@test.com", "password": "ValidPass123!"},
     HTTPStatus.BAD_REQUEST, "Contact validation failed: lastName: Path `lastName` is required."),

    # Invalid emails
    ({"firstName": "John", "lastName": "Doe", "email": "testsmail@test,com", "password": "ValidPass123!"},
     HTTPStatus.BAD_REQUEST, "Contact validation failed: email: Email is invalid"),
    ({"firstName": "John", "lastName": "Doe", "email": "testsmailtest.com", "password": "ValidPass123!"},
     HTTPStatus.BAD_REQUEST, "Contact validation failed: email: Email is invalid"),

    # Invalid phone
    ({"firstName": "John", "lastName": "Doe", "birthdate": "1990-05-05", "email": "testsmail@test.com",
      "phone": "12-45-7890"}, HTTPStatus.BAD_REQUEST, "Contact validation failed: phone: Phone number is invalid"),
    ({"firstName": "John", "lastName": "Doe", "birthdate": "1990-05-05", "email": "testsmail@test.com",
      "phone": "12345678911112"}, HTTPStatus.BAD_REQUEST, "Contact validation failed: phone: Phone number is invalid"),

    # Date of birth validation
    ({"firstName": "John", "lastName": "Doe", "birthdate": "2022-13-32", "email": "testsmail@test.com",
      "password": "ValidPass123!"}, HTTPStatus.BAD_REQUEST, "Contact validation failed: birthdate: Birthdate is invalid"),

    # Invalid postal code:
    ({"firstName": "John", "lastName": "Doe", "birthdate": "1990-05-05", "email": "testsmail@test.com",
      "phone": "8005555555", "city": "Anytown", "postalCode": "123-450"}, HTTPStatus.BAD_REQUEST, "Contact validation failed: postalCode: Postal code is invalid"),
    ({"firstName": "John", "lastName": "Doe", "birthdate": "1990-05-05", "email": "testsmail@test.com",
      "phone": "8005555555", "city": "Anytown", "postalCode": "123 450"}, HTTPStatus.BAD_REQUEST, "Contact validation failed: postalCode: Postal code is invalid"),
    ({"firstName": "John", "lastName": "Doe", "birthdate": "1990-05-05", "email": "testsmail@test.com",
      "phone": "8005555555", "city": "Anytown", "postalCode": "UYGJLJ"}, HTTPStatus.BAD_REQUEST,
     "Contact validation failed: postalCode: Postal code is invalid"),

    # XSS attacks and SQL injections
    # Validation for XSS injections is missing
    #({"firstName": "<svg onload=alert()>", "lastName": "Doe", "email": "testsmail@test.comm", "password": "ValidPass123!"}, HTTPStatus.BAD_REQUEST, "Contact validation failed: firstName: Path `firstName` (`<script>alert('XSS')</script>`) is longer than the maximum allowed length (20)."),
    #({"firstName": "John", "lastName": "' OR 1=1 --", "email": "testsmail@test.com", "password": "ValidPass123!"}, HTTPStatus.BAD_REQUEST, "Contact validation failed: lastName: Path `lastName` (`'; DROP TABLE users; --`) is longer than the maximum allowed length (20)."),
    #({"firstName": "John", "lastName": "Doe", "email": "<svg onload=alert()>", "password": "ValidPass123!"}, HTTPStatus.BAD_REQUEST, "Contact validation failed: email: Email is invalid"),
    ])
def test_add_contact_negative(base_url, register_user, contact_data, expected_status, error_message_part):
    _, token = register_user
    response = requests.post(f"{base_url}/contacts", json=contact_data, headers=create_headers(token))
    assert response.status_code == HTTPStatus.BAD_REQUEST, f"Error [add contact]: {response.status_code}"
    actual_error_message = response.json().get("message")
    print(f"Message [{actual_error_message}]")
    assert error_message_part in actual_error_message, f"Not found expected [{error_message_part}]: {response.text}"


def test_update_contact_with_invalid_id_put(base_url, contact_data_1, register_user):
    _, token = register_user

    contact_id = "67b0647f2*a3be800134e8888"
    response = requests.put(f"{base_url}/contacts/{contact_id}", json=contact_data_1, headers=create_headers(token))
    assert response.status_code == HTTPStatus.BAD_REQUEST, f"Error [update contact put]: {response.text}"

def test_update_contact_with_invalid_id_patch(base_url, contact_data_1, register_user):
    _, token = register_user

    contact_id = "67b0647f2*a3be800134e888"
    updated_field_json = {"firstName": "Anna"}
    response = requests.patch(f"{base_url}/contacts/{contact_id}", json=updated_field_json, headers=create_headers(token))
    assert response.status_code == HTTPStatus.BAD_REQUEST, f"Error [update contact patch]: {response.text}"

def compare_contacts(actual_data, expected_data):
    assert actual_data["firstName"] == expected_data["firstName"], "Error: firstName does not match"
    assert actual_data["lastName"] == expected_data["lastName"], "Error: lastName does not match"
    assert actual_data["birthdate"] == expected_data["birthdate"], "Error: birthdate does not match"
    assert actual_data["email"] == expected_data["email"], "Error: email does not match"
    assert actual_data["phone"] == expected_data["phone"], "Error: phone does not match"
    assert actual_data["street1"] == expected_data["street1"], "Error: street1 does not match"
    assert actual_data["street2"] == expected_data["street2"], "Error: street2 does not match"
    assert actual_data["city"] == expected_data["city"], "Error: city does not match"
    assert actual_data["stateProvince"] == expected_data["stateProvince"], "Error: stateProvince does not match"
    assert actual_data["postalCode"] == expected_data["postalCode"], "Error: postalCode does not match"
    assert actual_data["country"] == expected_data["country"], "Error: country does not match"
