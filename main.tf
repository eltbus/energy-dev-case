terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 2.13.0"
    }
  }
}

provider "docker" {}

resource "docker_image" "postgres" {
  name         = "postgres:latest"
  keep_locally = false
}

resource "docker_container" "db" {
  image = "postgres:latest"
  name  = "db"
  env   = ["POSTGRES_USER=${var.username}", "POSTGRES_PASSWORD=${var.password}", "POSTGRES_DB=${var.dbname}"]
  ports {
    internal = 5432
    external = 5432
  }
}

resource "docker_container" "api" {
  image = "myapi:latest"
  name  = "api"
  env   = ["POSTGRES_USER=${var.username}", "POSTGRES_PASSWORD=${var.password}", "POSTGRES_DB=${var.dbname}"]
  ports {
    internal = 8000
    external = 8000
  }
  depends_on = [
    docker_container.db
  ]
}
