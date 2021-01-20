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
  env = ["WEBEX_TOKEN=OTkxNjdiOWMtZDU0OC00ZDk5LWIzNWYtNzg3ODQwYjQwMTlkMmY3N2I4YTMtMDIw_PF84_1eb65fdf-9643-417f-9974-ad72cae0e10f", "WEBEX_ROOMID=Y2lzY29zcGFyazovL3VzL1JPT00vNThhYjU4NDAtMzk2MC0xMWViLTkxNzQtOTllMWQxYzMzOWY0", "APIC_IP=10.48.168.221", "TENANT=mgmt", "APIC_USER=admin", "APIC_PWD=ins3965!"]
  restart = "always"
}
