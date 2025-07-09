output "acr_login_server" {
  value       = azurerm_container_registry.acr.login_server
  description = "FQDN of your ACR, e.g. myregistry.azurecr.io"
}

output "container_group_id" {
  value       = azurerm_container_group.aci.id
  description = "Resource ID of the Azure Container Instance"
}
