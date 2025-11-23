# Instructivo para correr la aplicación

## Requisitos
- Python 3.11 o superior
- pip
- Docker y Docker Compose
- Navegador web moderno (Chrome, Firefox, Edge)
- Puerto 5000 libre (backend) y 3306 (MySQL)

## Dependencias Python
El backend usa:
- Flask
- flask-cors
- mysql-connector-python

## Pasos

### 1. Clonar el repositorio
```bash
git clone <repo-url>
cd Obligatorio_BD
```

### 3. Instalar dependencias
```bash
pip install Flask flask-cors mysql-connector-python
```

### 4. Levantar base de datos con Docker
Asegurarse de estar en la carpeta raíz donde está `docker-compose.yml`:
```bash
docker compose up -d
```
Verificar estado:
```bash
docker ps
```
La BD se inicializa con el script `mysql/init.sql` automáticamente al primer arranque.

### 5. Variables de entorno
El archivo `.env` ya incluye valores para MySQL. Por defecto el backend usa:
```
host: 127.0.0.1
port: 3306
user: appuser
password: apppassword
database: obligatorio
```

### 6. Ejecutar backend
Desde la carpeta raíz:
```bash
python backend/services.py
```
Debe mostrar "status: ok" al acceder:
http://localhost:5000/api/health

### 7. Abrir frontend
No requiere servidor: abrir el archivo:
```
src/html/homepage.html
```
Doble clic o abrir desde navegador:
Arrastrar `homepage.html` al navegador.

### 8. Flujo básico
- Navegar a Consultas (botón lateral) para ver reportes.
- Login (admin) usa endpoint `/api/login` (credenciales en tabla `login`).
- Gestión de Salas, Reservas, Participantes y Sanciones vía sus páginas.

### 10. Problemas comunes
- Puertos ocupados: cerrar otros servicios en 5000 o 3306.
- Error de import `backend`: ejecutar siempre desde carpeta raíz.

