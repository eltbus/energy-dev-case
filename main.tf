terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "3.0.1"
    }
  }
}

provider "docker" {}

resource "docker_network" "private_network" {
  name   = "my_network"
  driver = "bridge"
}

resource "docker_image" "postgres" {
  name = "postgres:latest"
}

resource "docker_volume" "db_data" {
  name = "db_data"
}

resource "docker_container" "db" {
  name  = "db"
  image = docker_image.postgres.image_id
  env   = ["POSTGRES_USER=${var.username}", "POSTGRES_PASSWORD=${var.password}", "POSTGRES_DB=${var.dbname}"]
  healthcheck {
    test     = ["CMD", "pg_isready", "-d", "${var.dbname}", "-U", "${var.username}"]
    timeout  = "30s"
    interval = "10s"
    retries  = 3
  }
  networks_advanced {
    name = docker_network.private_network.name
  }
  ports {
    internal = 5432
    external = 5432
  }
  volumes {
    host_path = "${abspath(path.root)}/data/db"
    container_path = "/var/lib/postgresql/data"
  }
}

resource "docker_container" "api" {
  name  = "api"
  image = "myapi"
  env   = ["POSTGRES_USER=${var.username}", "POSTGRES_PASSWORD=${var.password}", "POSTGRES_DB=${var.dbname}", "POSTGRES_HOST=${docker_container.db.name}"]
  ports {
    internal = 8000
    external = 8000
  }
  networks_advanced {
    name = docker_network.private_network.name
  }
  depends_on = [
    docker_container.db
  ]
}
