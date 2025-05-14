# Korepetycje App (Docker)

Ten README opisuje, jak postawić cały projekt (backend, frontend, email-service, baza PostgreSQL) lokalnie przy pomocy Dockera.

Aplikacja wraz z dokumentacją została stworzona przez pięcio osobowy zespół:
Jakub Kucharek, Igor Osiakowski, Mateusz Ługowski, Mikołaj Lewandowski, Michał Kruczyński

## Wymagania

- Docker ≥ 20.x  
- docker-compose ≥ 1.29.x  

## Instalacja (Docker)

Aby uruchomić aplikację lokalnie w kontenerach Docker:

1. **Sklonuj repozytorium**  
   ```bash
   git clone https://github.com/ProjBezpieczenstwo/projekt.git
   cd projekt
   ```

2. Skonfiguruj połączenie SMTP
Otwórz *docker-compose.yaml* i w sekcji *email_service* w *environment* ustaw:
- smtp-email: your-email@example.com
- smtp-password: your-email-password
- smtp-server: smtp.example.com
- smtp-port: "465"

> Jeśli Twój serwer SMTP jest niedostępny, możesz pominąć ten krok i skorzystać z rozwiązania z punktu 3.
3. (Opcjonalnie) Omijanie SMTP:

(Plik auth_api.py rejestruje ścieżkę testową jako /auth/test/register)
Omijamy SMPT rejestrując się pod:
```bash 
http://localhost:8000/auth/test/register
```

4. Uruchom całość
```bash 
docker-compose up --build
```
4. Dostępy:
- Frontend: http://localhost:8000
- Backend API: http://localhost:5000
- Flasgger: http://localhost:5000/apidocs
- (opcjonalna rejestracja jako admin (sekret to secret): http://localhost:8000/admin/register)


5. zmienne środowiske

| Nazwa              | Opis                                    |
| ------------------ | --------------------------------------- |
| POSTGRES\_USER     | Nazwa użytkownika bazy PostgreSQL       |
| POSTGRES\_PASSWORD | Hasło do bazy PostgreSQL                |
| POSTGRES\_DB       | Nazwa bazy danych                       |
| EMAIL\_SENDER      | Adres nadawcy wiadomości e-mail         |
| EMAIL\_PASSWORD    | Hasło do skrzynki SMTP                  |
| SMTP\_SERVER       | Host SMTP                               |
| SMTP\_PORT         | Port SMTP                               |
| FLASK\_APP         | Plik startowy Flask (`server.py`)       |
| FLASK\_RUN\_PORT   | Port, na którym Flask nasłuchuje (5000) |
| SECRET\_KEY        | Sekret do sesji Flask                   |
| JWT\_SECRET\_KEY   | Sekret do generowania JWT               |