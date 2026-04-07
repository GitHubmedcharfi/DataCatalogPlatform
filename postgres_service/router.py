from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict
from datetime import datetime
from postgres_service import docker_utils, schemas
from auth.auth_utils import get_current_user 

router = APIRouter(
    prefix="/postgres",
    tags=["PostgreSQL"]
)

USER_INSTANCES: Dict[str, list] = {}

# Max instances per user 
MAX_INSTANCES = 5

# Deploy PostgreSQL
@router.post("/deploy", response_model=schemas.DeployResponse)
def deploy_postgres(
    request: schemas.DeployRequest,
    current_user=Depends(get_current_user)
):
    user_id = current_user["user_id"]

    # Enforce max instances
    instances = USER_INSTANCES.get(user_id, [])
    if len(instances) >= MAX_INSTANCES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum instances reached ({MAX_INSTANCES})"
        )

    # Deploy new container
    info = docker_utils.deploy_postgres(user_id, instance_name=request.instance_name)

    # Track instance
    instances.append(info)
    USER_INSTANCES[user_id] = instances

    # Return response
    return schemas.DeployResponse(
        instance_id=info["instance_id"],
        container_id=info["container_id"],
        host=info["host"],
        port=info["port"],
        database=info["database"],
        username=info["username"],
        password=info["password"],
        status=info["status"],
        max_instances=MAX_INSTANCES,
        current_instances=len(instances),
        created_at=info["created_at"],
        updated_at=info["updated_at"]
    )

# Stop PostgreSQL
@router.post("/stop", response_model=schemas.StopResponse)
def stop_postgres(
    request: schemas.StopRequest,
    current_user=Depends(get_current_user)
):
    user_id = current_user["user_id"]
    instances = USER_INSTANCES.get(user_id, [])

    instance = next((i for i in instances if i["instance_id"] == request.instance_id), None)
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")

    result = docker_utils.stop_postgres(instance["container_id"])
    instance["status"] = result["status"]
    instance["updated_at"] = datetime.utcnow()

    return schemas.StopResponse(
        instance_id=instance["instance_id"],
        status=instance["status"],
        message=result["message"]
    )

# Delete PostgreSQL
@router.post("/delete", response_model=schemas.DeleteResponse)
def delete_postgres(
    request: schemas.DeleteRequest,
    current_user=Depends(get_current_user)
):
    user_id = current_user["user_id"]
    instances = USER_INSTANCES.get(user_id, [])

    instance = next((i for i in instances if i["instance_id"] == request.instance_id), None)
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")
    result = docker_utils.delete_postgres(instance["container_id"], remove_volume=request.force_delete)
    instances.remove(instance)
    return schemas.DeleteResponse(
        instance_id=instance["instance_id"],
        status=result["status"],
        message=result["message"]
    )
# Get Connection Info
@router.get("/connection-info", response_model=schemas.ConnectionInfoResponse)
def get_connection_info(
    user_id: str,
    instance_id: str,
    current_user=Depends(get_current_user)
):
    if user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Unauthorized")

    instances = USER_INSTANCES.get(user_id, [])
    instance = next((i for i in instances if i["instance_id"] == instance_id), None)
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")

    info = docker_utils.get_connection_info(instance["container_id"])
    return schemas.ConnectionInfoResponse(
        instance_id=instance_id,
        host=info.get("host"),
        port=info.get("port"),
        database=info.get("database"),
        username=info.get("username"),
        password=info.get("password"),
        status=info.get("status"),
        created_at=datetime.fromisoformat(info.get("created_at").replace("Z", "+00:00")),
        updated_at=datetime.fromisoformat(info.get("updated_at").replace("Z", "+00:00"))
    )