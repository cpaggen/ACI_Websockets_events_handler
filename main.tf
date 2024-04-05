terraform {
  required_providers {
    docker = {
      source = "kreuzwerker/docker"
    }
  }
}


provider "docker" {
  host = "tcp://localhost:2736/"
}


resource "docker_container" "aci-events-handler" {
  image = "acieventscicd:gitlab"
  name  = "aci-events-handler"
  env   = ["WEBEX_TOKEN=...", "WEBEX_ROOMID=...", "APIC_IP=10.48.168.221", "TENANT=newDemoTenant4", "APIC_USER=admin", "APIC_PWD=..."]

  restart = "always"
}
