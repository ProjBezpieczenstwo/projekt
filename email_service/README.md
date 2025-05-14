## Email Service (`email_service`)

Repo: https://github.com/ProjBezpieczenstwo/email_service

Autorzy: Jakub Kucharek, Igor Osiakowski, Mateusz Ługowski, Mikołaj Lewandowski, Michał Kruczyński

### 1. Utwórz Azure Container App

- Resource group: Twój_RG  
- Location: Central Europe (Poland)  
- Container:
  - Registry: GitHub Container Registry (`ghcr.io`)  
  - Image: `projbezpieczenstwo/email_service:latest`

### 2. Zmienne aplikacji

| Name            | Description                                      |
|-----------------|--------------------------------------------------|
| SMTP_EMAIL      | Adres nadawcy (np. `korepetycjewzim@op.pl`)      |
| SMTP_PASSWORD   | Hasło do konta SMTP                              |
| SMTP_SERVER     | Host SMTP (np. `smtp.poczta.onet.pl`)            |
| SMTP_PORT       | Port SMTP (np. `465`)                            |
| FRONTEND_URI    | URL frontendu (np. `https://<twoja-app>.azurewebsites.net`) |

> Dodaj je w **Settings → Containers → Environment variables** i **Save**.

### 3. Deploy
Analogicznie jak backend
- Deployment Center → GitHub → main branch → kontener

### 4. Dostęp

- (```https://korepetycje-email.<region>.azurecontainerapps.io```) (przypadek wdrożenia, region to np: polandcentral-01)


## Azure Database dla PostgreSQL

1. **Utwórz serwer**  
   - Service: Azure Database for PostgreSQL – Flexible Server  
   - Resource group: Twój_RG  
   - Region: Central Europe (Poland)  
   - Version: 17  
   - Authentication: PostgreSQL auth only  
   - Utwórz admina (login + hasło)  

2. **Connection string**  
   Ustaw w zmiennej `DATABASE_URI` w Backendzie:
   ```bash
   postgres://<admin>:<password>@<servername>.postgres.database.azure.com:5432/<db_name>
   ```