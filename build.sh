terraform destroy -auto-approve
docker build -t aci-events .
terraform plan
terraform apply -auto-approve
docker ps -ql | xargs docker logs -f
