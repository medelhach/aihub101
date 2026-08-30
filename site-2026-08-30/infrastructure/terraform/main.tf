terraform {
  required_version = ">= 1.6.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }
}

provider "azurerm" {
  features {}
}

variable "prefix" {
  type    = string
  default = "aihub"
}

variable "location" {
  type    = string
  default = "westeurope"
}

variable "postgres_admin_login" {
  type    = string
  default = "aihubadmin"
}

variable "postgres_admin_password" {
  type      = string
  sensitive = true
}

variable "content_cycle_secret" {
  type      = string
  sensitive = true
}

resource "azurerm_resource_group" "hub" {
  name     = "${var.prefix}-rg"
  location = var.location
}

resource "azurerm_log_analytics_workspace" "hub" {
  name                = "${var.prefix}-logs"
  location            = azurerm_resource_group.hub.location
  resource_group_name = azurerm_resource_group.hub.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
}

resource "azurerm_application_insights" "hub" {
  name                = "${var.prefix}-insights"
  location            = azurerm_resource_group.hub.location
  resource_group_name = azurerm_resource_group.hub.name
  application_type    = "web"
  workspace_id        = azurerm_log_analytics_workspace.hub.id
}

resource "azurerm_container_registry" "hub" {
  name                = replace("${var.prefix}acr", "-", "")
  resource_group_name = azurerm_resource_group.hub.name
  location            = azurerm_resource_group.hub.location
  sku                 = "Basic"
  admin_enabled       = false
}

resource "azurerm_key_vault" "hub" {
  name                       = "${var.prefix}-kv"
  location                   = azurerm_resource_group.hub.location
  resource_group_name        = azurerm_resource_group.hub.name
  tenant_id                  = data.azurerm_client_config.current.tenant_id
  sku_name                   = "standard"
  purge_protection_enabled   = true
  soft_delete_retention_days = 7
}

data "azurerm_client_config" "current" {}

resource "azurerm_postgresql_flexible_server" "hub" {
  name                   = "${var.prefix}-pg"
  resource_group_name    = azurerm_resource_group.hub.name
  location               = azurerm_resource_group.hub.location
  version                = "16"
  administrator_login    = var.postgres_admin_login
  administrator_password = var.postgres_admin_password
  sku_name               = "B_Standard_B1ms"
  storage_mb             = 32768
  zone                   = "1"
}

resource "azurerm_postgresql_flexible_server_database" "hub" {
  name      = "ai_hub"
  server_id = azurerm_postgresql_flexible_server.hub.id
  charset   = "UTF8"
  collation = "en_US.utf8"
}

resource "azurerm_service_plan" "hub" {
  name                = "${var.prefix}-plan"
  resource_group_name = azurerm_resource_group.hub.name
  location            = azurerm_resource_group.hub.location
  os_type             = "Linux"
  sku_name            = "B1"
}

resource "azurerm_linux_web_app" "api" {
  name                = "${var.prefix}-api"
  resource_group_name = azurerm_resource_group.hub.name
  location            = azurerm_service_plan.hub.location
  service_plan_id     = azurerm_service_plan.hub.id
  https_only          = true

  identity {
    type = "SystemAssigned"
  }

  site_config {
    always_on = true
    application_stack {
      docker_image_name   = "${azurerm_container_registry.hub.login_server}/aihub-api:latest"
      docker_registry_url = "https://${azurerm_container_registry.hub.login_server}"
    }
    health_check_path = "/api/v1/health/ready"
  }

  app_settings = {
    APP_ENV                         = "production"
    APP_DEBUG                       = "false"
    WEBSITES_PORT                   = "8000"
    CONTENT_CYCLE_SECRET            = var.content_cycle_secret
    APPLICATIONINSIGHTS_CONNECTION_STRING = azurerm_application_insights.hub.connection_string
  }
}

resource "azurerm_linux_web_app" "web" {
  name                = "${var.prefix}-web"
  resource_group_name = azurerm_resource_group.hub.name
  location            = azurerm_service_plan.hub.location
  service_plan_id     = azurerm_service_plan.hub.id
  https_only          = true

  identity {
    type = "SystemAssigned"
  }

  site_config {
    always_on = true
    application_stack {
      docker_image_name   = "${azurerm_container_registry.hub.login_server}/aihub-web:latest"
      docker_registry_url = "https://${azurerm_container_registry.hub.login_server}"
    }
    health_check_path = "/"
  }

  app_settings = {
    NODE_ENV                         = "production"
    WEBSITES_PORT                    = "3000"
    NEXT_PUBLIC_API_URL              = "https://${azurerm_linux_web_app.api.default_hostname}/api/v1"
    INTERNAL_API_URL                 = "https://${azurerm_linux_web_app.api.default_hostname}/api/v1"
    APPLICATIONINSIGHTS_CONNECTION_STRING = azurerm_application_insights.hub.connection_string
  }
}

resource "azurerm_service_plan" "functions" {
  name                = "${var.prefix}-func-plan"
  resource_group_name = azurerm_resource_group.hub.name
  location            = azurerm_resource_group.hub.location
  os_type             = "Linux"
  sku_name            = "Y1"
}

resource "azurerm_storage_account" "functions" {
  name                     = substr(replace("${var.prefix}funcsa", "-", ""), 0, 24)
  resource_group_name      = azurerm_resource_group.hub.name
  location                 = azurerm_resource_group.hub.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  min_tls_version          = "TLS1_2"
}

resource "azurerm_linux_function_app" "cycle" {
  name                = "${var.prefix}-cycle"
  resource_group_name = azurerm_resource_group.hub.name
  location            = azurerm_resource_group.hub.location
  service_plan_id     = azurerm_service_plan.functions.id
  storage_account_name       = azurerm_storage_account.functions.name
  storage_account_access_key = azurerm_storage_account.functions.primary_access_key
  https_only          = true

  identity {
    type = "SystemAssigned"
  }

  site_config {
    application_stack {
      python_version = "3.12"
    }
  }

  app_settings = {
    FUNCTIONS_WORKER_RUNTIME = "python"
    API_BASE_URL             = "https://${azurerm_linux_web_app.api.default_hostname}/api/v1"
    CONTENT_CYCLE_SECRET     = var.content_cycle_secret
  }
}

output "web_url" {
  value = "https://${azurerm_linux_web_app.web.default_hostname}"
}

output "api_url" {
  value = "https://${azurerm_linux_web_app.api.default_hostname}"
}
