# Korepetycje App Backend (`app`)
Instrukcja deploy’u backendu w Azure Container Apps.
> Repo: https://github.com/ProjBezpieczenstwo/app

Autorzy: Jakub Kucharek, Igor Osiakowski, Mateusz Ługowski, Mikołaj Lewandowski, Michał Kruczyński

## 1. Tworzenie Container App

1. Azure Portal → **Container Apps** → **Create**  
2. Resource group: `Twój_RG`  
3. Name: `korepetycje-backend`  
4. Region: **Central Europe**  
5. Container:
   - Registry: **GitHub Container Registry (ghcr.io)**
   - Image: `projbezpieczenstwo/backend:latest`

### 2. Zmienne aplikacji

| Name               | Description                                             |
|--------------------|---------------------------------------------------------|
| DATABASE_URI       | URI do Azure Database for PostgreSQL:  `postgres://<user>:<pass>@<server>.postgres.database.azure.com:5432/<db>` |
| SECRET_KEY         | Sekret Flask (do sesji i CSRF)(sesje)                                    |
| JWT_SECRET_KEY     | Sekret do generowania i weyfikacji tokenów JWT                       |
| EMAIL_SERVICE_URI  | URL serwisu e-mail (np. `https://<email_app>.azurewebsites.net`) , albo `https://korepetycje-email.azurecontainerapps.io/send-email` itp.|
| ADMIN_SECRET       | Klucz weryfikacyjny dla roli administratora             |

> Dodaj te zmienne w **Settings → Containers → Environment variables**, a następnie **Save**.

### 3. Deploy

- Deployment Center → GitHub → main branch → kontener

### 4. Dostęp
- https://\<korepetycje-backend\>.azurecontainerapps.io (szablon)
- (``` https://korepetycje-backend.<region>.azurecontainerapps.io```) (przypadek wdrożenia, region to np: polandcentral-01)