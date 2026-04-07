import docker
import random
import string
from datetime import datetime

# Initialize Docker cient
client = docker.from_env()
# Helper Functions
def generate_password(length=12):
    chars = string.ascii_letters + string.digits + "!@#$%^&*()"
    return ''.join(random.choice(chars) for _ in range(length))

def generate_instance_id(length=6):
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))

# Deploy PostgreSQL container
def deploy_postgres(user_id, instance_name=None, port=None):
    instance_id = generate_instance_id()
    container_name = f"pg_{user_id}_{instance_id}"

    # Credentials
    db_name = f"db_{user_id}_{instance_id}"
    username = f"user_{user_id}_{instance_id}"
    password = generate_password()

    # Random port if not provided
    if port is None:
        port = random.randint(5400, 6500)

    # Volume for persistence
    volume_name = f"{container_name}_data"

    # Create volume
    try:
        client.volumes.create(name=volume_name)
    except docker.errors.APIError:
        pass  # volume might already exist

    # Run container
    container = client.containers.run(
        image="postgres:15",
        name=container_name,
        environment={
            "POSTGRES_DB": db_name,
            "POSTGRES_USER": username,
            "POSTGRES_PASSWORD": password
        },
        ports={"5432/tcp": port},
        volumes={volume_name: {"bind": "/var/lib/postgresql/data", "mode": "rw"}},
        detach=True,
    )

    # Return info
    return {
        "instance_id": instance_id,
        "container_id": container.id,
        "host": "localhost",
        "port": port,
        "database": db_name,
        "username": username,
        "password": password,
        "status": "running",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

# Stop container
def stop_postgres(container_id):
    try:
        container = client.containers.get(container_id)
        container.stop()
        return {"container_id": container_id, "status": "stopped", "message": "Container stopped successfully"}
    except docker.errors.NotFound:
        return {"container_id": container_id, "status": "deleted", "message": "Container not found"}

# Delete container
def delete_postgres(container_id, remove_volume=False):
    try:
        container = client.containers.get(container_id)
        container_name = container.name
        container.stop()
        container.remove()
        # Optionally remove associated volume
        if remove_volume:
            volume_name = f"{container_name}_data"
            vol = client.volumes.get(volume_name)
            vol.remove()
        return {"container_id": container_id, "status": "deleted", "message": "Container deleted successfully"}
    except docker.errors.NotFound:
        return {"container_id": container_id, "status": "deleted", "message": "Container not found"}

# Get connection info
def get_connection_info(container_id):
    try:
        container = client.containers.get(container_id)
        env = container.attrs['Config']['Env']
        env_dict = {e.split("=")[0]: e.split("=")[1] for e in env}
        port = container.attrs['NetworkSettings']['Ports']['5432/tcp'][0]['HostPort']
        return {
            "container_id": container_id,
            "host": "localhost",
            "port": int(port),
            "database": env_dict.get("POSTGRES_DB"),
            "username": env_dict.get("POSTGRES_USER"),
            "password": env_dict.get("POSTGRES_PASSWORD"),
            "status": container.status,
            "created_at": container.attrs['Created'],
            "updated_at": container.attrs['State']['StartedAt']
        }
    except docker.errors.NotFound:
        return {"container_id": container_id, "status": "deleted", "message": "Container not found"}