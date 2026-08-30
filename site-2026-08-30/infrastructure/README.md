# Azure hosting

This environment deploys the Hub as two **Azure App Service** Linux Web Apps
(Next.js and FastAPI containers), **Azure Database for PostgreSQL Flexible Server**,
and an **Azure Function** timer that calls `POST /api/v1/operations/content-cycle`.

App Service is the right default: independent scale for web and API, deployment slots,
managed identity, and health probes. PostgreSQL Flexible Server is the system of record.
Functions handle the 15-minute ingestion schedule without keeping a worker process on the
API instances. Optional **Azure OpenAI** rewrites briefs into original reporter copy.

## Apply

```bash
cd infrastructure/terraform
terraform init
terraform plan -var="prefix=aihub" -var="location=westeurope"
terraform apply
```

Store `content_cycle_secret` and database credentials in Key Vault. Point both App Services
at the Key Vault references. Run `alembic upgrade head` as a startup command on the API app.

The Function uses a timer (`0 */15 * * * *`) and the cycle secret header.
