import pytest 


@pytest.mark.asyncio
async def test_protected_task_create(client):
    
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
    
    login_response = await client.post("/api/v1/users/login", data=login_payload)
    
    assert login_response.status_code == 200
    
    data = login_response.json()
    
    token = data["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    
    task_payload = {
        "title": "sample task 2",
        "description": "this is a task created to check the task workflow",
        "complexity": "light",
        "priority": 1,
        "payload": {"data":"here you got some more sample data"}
    }
    
    protected_response = await client.post(
        "/api/v1/tasks",
        json=task_payload,
        headers=headers
    )
    
    assert protected_response.status_code == 202