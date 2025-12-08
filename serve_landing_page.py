#!/usr/bin/env python3
"""
Servidor simples para servir a landing page do clima de Montreal.

Este servidor permite acessar a landing page diretamente no navegador
sem precisar do sistema ETL completo rodando.

Uso:
    python serve_landing_page.py

Acesso:
    http://localhost:8080
"""

import http.server
import socketserver
import os
import webbrowser
from pathlib import Path

PORT = 8080
DIRECTORY = Path(__file__).parent

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)

    def end_headers(self):
        # Adicionar headers CORS para permitir requisições da API
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_GET(self):
        # Se for requisição para a raiz, servir a landing page
        if self.path == '/' or self.path == '':
            self.path = '/landing_page_standalone.html'

        return super().do_GET()

def main():
    print("🌤️ Servidor da Landing Page - Clima Montreal")
    print("=" * 50)
    print(f"📁 Diretório: {DIRECTORY}")
    print(f"🌐 URL: http://localhost:{PORT}")
    print(f"📄 Arquivo: landing_page_standalone.html")
    print()
    print("Funcionalidades:")
    print("✅ Landing page com design moderno")
    print("✅ Dados climáticos simulados")
    print("✅ Gráficos interativos")
    print("✅ Interface responsiva")
    print("✅ Animações e efeitos visuais")
    print()
    print("Para parar o servidor: Ctrl+C")
    print()

    try:
        with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
            print(f"🚀 Servidor iniciado na porta {PORT}")
            print("📖 Abrindo navegador automaticamente...")

            # Abrir navegador automaticamente
            webbrowser.open(f"http://localhost:{PORT}")

            print("🎯 Aguardando conexões...")
            httpd.serve_forever()

    except KeyboardInterrupt:
        print("\n👋 Servidor parado pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")

if __name__ == "__main__":
    main()
