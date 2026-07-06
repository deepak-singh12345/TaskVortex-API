import pytest 


@pytest.mark.asyncio
async def test_signup_success(client):
    payload = {
        "name": "alex",
        "email": "alex@gmail.com",
        "password": "alexPassword123"
    }
    
    response = await client.post(
        "/api/v1/users/signup",
        json=payload
    )
    
    assert response.status_code == 201
    
@pytest.mark.asyncio
async def test_multiple_signup_with_same_email(client):
    payload = {
        "name": "alex",
        "email": "alex@gmail.com",
        "password": "alexPassword123"
    }
    
    first_response = await client.post(
        "/api/v1/users/signup",
        json=payload
    )
    
    assert first_response.status_code == 201
    
    second_response = await client.post(
        "/api/v1/users/signup",
        json=payload
    )
    
    assert second_response.status_code == 400 
    assert second_response.json()["detail"] == "User already exists"
    

@pytest.mark.asyncio
async def test_successful_login(client):
    
    user_payload = {
        "name": "alex",
        "email": "alex@gmail.com",
        "password": "alexPassword123"
    }
    
    signup_response = await client.post(
        "/api/v1/users/signup",
        json=user_payload
    )
    
    assert signup_response.status_code == 201 
    
    login_payload = {
        "username": user_payload["email"],
        "password": user_payload["password"],
    }
    
    response = await client.post("/api/v1/users/login", data=login_payload)
    
    assert response.status_code == 200
    
    data = response.json()
    assert "access_token" in data 
    assert data["token_type"] == "bearer"
    

@pytest.mark.asyncio
async def test_login_with_wrong_password(client):
    
    user_payload = {
        "name": "alex",
        "email": "alex@gmail.com",
        "password": "alexPassword123"
    }
    
    signup_response = await client.post(
        "/api/v1/users/signup",
        json=user_payload
    )
    
    assert signup_response.status_code == 201 
    
    login_payload = {
        "username": user_payload["email"],
        "password": "wrong_password",
    }
    
    response = await client.post("/api/v1/users/login", data=login_payload)
    
    assert response.status_code == 401
    
    data = response.json()
    assert data["detail"] == "Invalid Credentials"
    

@pytest.mark.asyncio
async def test_login_with_unknown_user(client):
    
    login_payload = {
        "username": "unknownuser@gmail.com",
        "password": "wrong_password",
    }
    
    response = await client.post("/api/v1/users/login", data=login_payload)
    
    assert response.status_code == 401
    
    data = response.json()
    assert data["detail"] == "Invalid Credentials"
    