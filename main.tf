terraform {
  required_providers {
    docker = {
      source = "kreuzwerker/docker"
    }
  }
}


provider "docker" {
  host = "tcp://10.48.168.169:2736/"
}


resource "docker_container" "aci-events-handler" {
  image = "aci-events"
  name  = "aci-events-handler"
  restart = "always"
}
