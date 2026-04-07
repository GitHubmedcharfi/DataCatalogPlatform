from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime

# Enum for instance status
class InstanceStatus(str, Enum):
    running = "running"
    stopped = "stopped"
    deleted = "deleted"

# Deploy PostgreSQL
class DeployRequest(BaseModel):
    instance_name: str | None = Field(None, description="Optional user-friendly name for this instance")

class DeployResponse(BaseModel):
    instance_id: str = Field(..., description="Unique identifier of the PostgreSQL instance")
    container_id: str = Field(..., description="Docker container ID of the PostgreSQL instance")
    host: str = Field(..., description="Hostname or IP of the PostgreSQL instance")
    port: int = Field(..., description="Port exposed by the PostgreSQL container")
    database: str = Field(..., description="Database name for the user")
    username: str = Field(..., description="Username for PostgreSQL")
    password: str = Field(..., description="Password for PostgreSQL")
    status: InstanceStatus = Field(..., description="Status of the PostgreSQL instance")
    max_instances: int = Field(..., description="Maximum instances allowed per user")
    current_instances: int = Field(..., description="Number of instances currently deployed by the user")
    created_at: datetime = Field(..., description="Timestamp of instance creation")
    updated_at: datetime = Field(..., description="Timestamp of last update")

# Stop PostgreSQL
class StopRequest(BaseModel):
    instance_id: str = Field(..., description="Unique identifier of the PostgreSQL instance to stop")

class StopResponse(BaseModel):
    instance_id: str = Field(..., description="Unique identifier of the stopped PostgreSQL instance")
    status: InstanceStatus = Field(..., description="Status after stop operation")
    message: str = Field(..., description="Result message of the stop operation")

# Delete PostgreSQL
class DeleteRequest(BaseModel):
    instance_id: str = Field(..., description="Unique identifier of the PostgreSQL instance to delete")
    force_delete: bool = Field(False, description="If True, delete persistent volume as well")

class DeleteResponse(BaseModel):
    instance_id: str = Field(..., description="Unique identifier of the deleted PostgreSQL instance")
    status: InstanceStatus = Field(..., description="Status after delete operation")
    message: str = Field(..., description="Result message of the delete operation")

# Connection Info
class ConnectionInfoRequest(BaseModel):
    user_id: str = Field(..., description="Identifier of the user requesting connection info")
    instance_id: str = Field(..., description="Unique identifier of the PostgreSQL instance")

class ConnectionInfoResponse(BaseModel):
    instance_id: str = Field(..., description="Unique identifier of the PostgreSQL instance")
    host: str = Field(..., description="Hostname or IP of the PostgreSQL instance")
    port: int = Field(..., description="Port exposed by the PostgreSQL container")
    database: str = Field(..., description="Database name for the user")
    username: str = Field(..., description="Username for PostgreSQL")
    password: str = Field(..., description="Password for PostgreSQL")
    status: InstanceStatus = Field(..., description="Status of the PostgreSQL instance")
    created_at: datetime = Field(..., description="Timestamp of instance creation")
    updated_at: datetime = Field(..., description="Timestamp of last update")