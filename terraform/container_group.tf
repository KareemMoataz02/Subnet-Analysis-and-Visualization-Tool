// container_group.tf

// Lookup ACR registry, including admin credentials
// The data source "azurerm_container_registry" exposes login_server, admin_username, and admin_password

data "azurerm_container_registry" "acr" {
  name                = var.acr_name
  resource_group_name = azurerm_resource_group.rg.name
}

// Container Group definition with ACR admin credentials for image pull
resource "azurerm_container_group" "aci" {
  name                = "subnet-analyzer-group"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  os_type             = "Linux"
  ip_address_type     = "Public"
  restart_policy      = "OnFailure"

  image_registry_credential {
    server   = data.azurerm_container_registry.acr.login_server
    username = data.azurerm_container_registry.acr.admin_username
    password = data.azurerm_container_registry.acr.admin_password
  }

  container {
    name   = var.image_name
    image  = "${data.azurerm_container_registry.acr.login_server}/${var.image_name}:latest"
    cpu    = "0.5"
    memory = "1.5"

    // Mount Azure File share for report outputs
    volume {
      name                 = "reports-volume"
      share_name           = azurerm_storage_share.reports.name
      storage_account_name = azurerm_storage_account.sa.name
      storage_account_key  = data.azurerm_storage_account.sa.primary_access_key
      mount_path           = "/mnt/reports"
    }

    // Startup commands to process and visualize subnets
    commands = [
      "/bin/bash", "-lc",
      join(" && ", [
        "cp /app/ip_data.xlsx /mnt/reports/ip_data.xlsx",
        "python subnet_analyzer.py --input /mnt/reports/ip_data.xlsx --output /mnt/reports/subnet_report.csv",
        # copy the Markdown report
        "cp report.md /mnt/reports/report.md",
        # generate the plot into /app (current behavior)
        "python visualize.py --input /mnt/reports/subnet_report.csv --output network_plot.png",
        # then copy the PNG into the share
        "cp network_plot.png /mnt/reports/network_plot.png"
      ])
    ]

    ports {
      port     = 80
      protocol = "TCP"
    }
  }

  tags = {
    environment = "dev"
    project     = "subnet-analyzer"
  }
}
