import pytest
import requests
import random

BASE_URL = "https://thinking-tester-contact-list.herokuapp.com"

@pytest.fixture(scope="session")
def base_url():
    return BASE_URL

def generate_unique_email():
    return f"user_{random.random()}@test.com"

@pytest.fixture(scope="function")
def create_user_data():
    return {
        "firstName": "FirstName",
        "lastName": "LastName",
        #todo: add comment why
        "email": generate_unique_email(),
        "password": "123Password*"
    }

@pytest.fixture(scope="function")
def register_user(base_url, create_user_data):
    response = requests.post(f"{base_url}/users", json=create_user_data)

    user_data = response.json().get("user")

    token = response.json().get("token")
    user_id = user_data.get("_id")

    print(f"create user response: {response.json()}")
    print(f"user_id: {user_id}")
    print(f"token: {token}")

    #todo replace token on headers from tests
    yield user_data, token

    headers = create_headers(token)
    response = requests.delete(f"{base_url}/users/me", headers=headers)


@pytest.fixture(scope="function")
def register_user_with_logout(register_user, base_url):
    user_data, token = register_user
    requests.post(f"{base_url}/users/logout", json=user_data)
    return user_data


def create_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}

def delete_user(token, base_url):
    response = requests.delete(f"{base_url}/users/me", headers=create_headers(token))


@pytest.fixture(scope="function")
def contact_data_1():
    return {
        "firstName": "John",
        "lastName": "Doe",
        "birthdate": "1970-01-01",
        "email": "testsmail@test.com",
        "phone": "8005555555",
        "street1": "1 Main St.",
        "street2": "Apartment A",
        "city": "Anytown",
        "stateProvince": "KS",
        "postalCode": "12345",
        "country": "USA"
    }


@pytest.fixture(scope="function")
def contact_data_2():
    return {
        "firstName": "Amy",
        "lastName": "Miller",
        "birthdate": "1992-02-02",
        "email": "amiller@test.com",
        "phone": "8005554242",
        "street1": "13 School St.",
        "street2": "Apt. 5",
        "city": "Washington",
        "stateProvince": "QC",
        "postalCode": "A1A1A1",
        "country": "Canada"
    }

@pytest.fixture(scope="function")
def contact_data_3():
    return {
        "firstName": "name3",
        "lastName": "lastName3",
        "birthdate": "1993-03-03",
        "email": "email3@test.com",
        "phone": "8005554243",
        "street1": "3 School St.",
        "street2": "Apt. 3",
        "city": "City 3",
        "stateProvince": "state 3",
        "postalCode": "A1A1A3",
        "country": "Country 3"
    }
