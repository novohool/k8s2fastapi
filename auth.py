from fastapi import Request, HTTPException, status
from kubernetes import client
import logging

logger = logging.getLogger(__name__)

def authenticate_token_only(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header"
        )

    token = auth_header.split(" ", 1)[1]

    try:
        tr = client.AuthenticationV1Api().create_token_review(
            body=client.V1TokenReview(spec=client.V1TokenReviewSpec(token=token))
        )
    except Exception as e:
        logger.error(f"TokenReview failed: {e}")
        raise HTTPException(status_code=500, detail="Authentication service error")

    if not tr.status or not tr.status.authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=tr.status.error if tr.status else "Invalid token"
        )

    user = tr.status.user
    return {
        "username": user.username,
        "uid": user.uid,
        "groups": user.groups or []
    }

def authenticate_and_authorize(request: Request):
    user_info = authenticate_token_only(request)
    username = user_info["username"]
    groups = user_info["groups"]

    sar_spec = client.V1SubjectAccessReviewSpec(
        user=username,
        groups=groups,
        non_resource_attributes=client.V1NonResourceAttributes(
            path=request.url.path,
            verb=request.method.lower()
        )
    )

    sar_body = client.V1SubjectAccessReview(spec=sar_spec)

    try:
        sar = client.AuthorizationV1Api().create_subject_access_review(body=sar_body)
    except Exception as e:
        logger.error(f"SubjectAccessReview failed: {e}")
        raise HTTPException(status_code=500, detail="Authorization service error")

    if not sar.status or not sar.status.allowed:
        reason = sar.status.reason if sar.status else "Access denied"
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=reason
        )