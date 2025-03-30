import http.server
import socketserver
import os

PORT = 8000

# Переходим в директорию webapp
os.chdir('webapp')

# Создаем обработчик
Handler = http.server.SimpleHTTPRequestHandler

# Создаем сервер
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Сервер запущен на порту {PORT}")
    print(f"Веб-приложение доступно по адресу: http://localhost:{PORT}")
    httpd.serve_forever() 