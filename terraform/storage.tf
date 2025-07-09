# Storage Account (for both remote state and file share)
resource "azurerm_storage_account" "sa" {
  name                     = var.sa_name
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

# File Share for reports
resource "azurerm_storage_share" "reports" {
  name                 = "reports"
  storage_account_name = azurerm_storage_account.sa.name
  quota                = 1
}

# Fetch Storage Account Key (primary_access_key)
data "azurerm_storage_account" "sa" {
  name                = azurerm_storage_account.sa.name
  resource_group_name = azurerm_resource_group.rg.name
}
