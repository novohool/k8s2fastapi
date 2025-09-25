from fastapi import FastAPI, Request
from k8s_data import K8SData
from auth import authenticate_and_authorize,authenticate_token_only
import uvicorn

app = FastAPI(title="K8s Data API")

k8s_client = K8SData()

@app.get("/auth")
def auth_check(request: Request):
    user_info = authenticate_token_only(request)
    return {
        "authenticated": True,
        "user": {
            "username": user_info["username"],
            "uid": user_info.get("uid"),
            "groups": user_info.get("groups", [])
        },
        "message": "Authentication successful"
    }

@app.get("/nodes")
def get_nodes(request: Request):
    authenticate_and_authorize(request)
    return k8s_client.get_node_to_json()

@app.get("/containers")
def get_containers(request: Request):
    authenticate_and_authorize(request)
    return k8s_client.get_all_container_configs()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)