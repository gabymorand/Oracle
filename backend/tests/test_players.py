def test_create_player(client):
    response = client.post("/api/v1/players", json={"summoner_name": "Faker", "role": "mid"})
    assert response.status_code == 201
    data = response.json()
    assert data["summoner_name"] == "Faker"
    assert data["role"] == "mid"
    assert "id" in data


def test_list_players(client):
    client.post("/api/v1/players", json={"summoner_name": "Faker", "role": "mid"})
    client.post("/api/v1/players", json={"summoner_name": "Zeus", "role": "top"})

    response = client.get("/api/v1/players")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_get_player(client):
    create_response = client.post("/api/v1/players", json={"summoner_name": "Faker", "role": "mid"})
    player_id = create_response.json()["id"]

    response = client.get(f"/api/v1/players/{player_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["summoner_name"] == "Faker"


def test_update_player(client):
    create_response = client.post("/api/v1/players", json={"summoner_name": "Faker", "role": "mid"})
    player_id = create_response.json()["id"]

    response = client.patch(f"/api/v1/players/{player_id}", json={"summoner_name": "Faker T1"})
    assert response.status_code == 200
    data = response.json()
    assert data["summoner_name"] == "Faker T1"


def test_delete_player(client):
    create_response = client.post("/api/v1/players", json={"summoner_name": "Faker", "role": "mid"})
    player_id = create_response.json()["id"]

    response = client.delete(f"/api/v1/players/{player_id}")
    assert response.status_code == 204

    get_response = client.get(f"/api/v1/players/{player_id}")
    assert get_response.status_code == 404
