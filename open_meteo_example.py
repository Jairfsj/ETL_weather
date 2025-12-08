#!/usr/bin/env python3
"""
Exemplo de uso do Open-Meteo API no ETL Weather Dashboard

Este script demonstra como usar a melhor API gratuita para monitoramento
semi-real de Montreal (3-4 vezes por semana), com dados atuais, históricos
e previsões sem necessidade de chave API.

Características do Open-Meteo:
- Gratuita e sem chave API
- Dados históricos de até 60 anos
- Dados atuais e previsões
- Melhor para monitoramento semi-real
"""

import requests
import pandas as pd
from datetime import datetime, date, timedelta
import json


class OpenMeteoClient:
    """Cliente para acessar dados do Open-Meteo API"""

    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.api_prefix = "/api/v1/weather"

    def get_current_weather(self):
        """Busca dados climáticos atuais via API do dashboard"""
        url = f"{self.base_url}{self.api_prefix}/openmeteo/current"

        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar dados atuais: {e}")
            return None

    def get_forecast(self, days=7):
        """Busca previsão do tempo via API do dashboard"""
        url = f"{self.base_url}{self.api_prefix}/openmeteo/forecast"
        params = {'days': days}

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar previsão: {e}")
            return None

    def get_monitoring_data(self, weeks=4):
        """Busca dados de monitoramento semanal (3-4 vezes por semana)"""
        url = f"{self.base_url}{self.api_prefix}/openmeteo/monitoring"
        params = {'weeks': weeks}

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar dados de monitoramento: {e}")
            return None

    def get_historical_data(self, start_date, end_date):
        """Busca dados históricos via API do dashboard"""
        url = f"{self.base_url}{self.api_prefix}/openmeteo/historical"
        params = {
            'start_date': start_date,
            'end_date': end_date
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar dados históricos: {e}")
            return None

    def generate_historical_csv(self, start_date, end_date):
        """Gera CSV com dados históricos"""
        url = f"{self.base_url}{self.api_prefix}/openmeteo/historical/csv"
        params = {
            'start_date': start_date,
            'end_date': end_date
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao gerar CSV histórico: {e}")
            return None


def main():
    """Função principal com exemplos de uso do Open-Meteo"""

    print("🌤️ ETL Weather Dashboard - Exemplos com Open-Meteo API")
    print("📍 Melhor API gratuita para monitoramento semi-real de Montreal")
    print("=" * 70)

    client = OpenMeteoClient()

    # Exemplo 1: Dados atuais (melhor para monitoramento em tempo real)
    print("\n📊 Exemplo 1: Dados climáticos atuais (Monitoramento em Tempo Real)")
    print("-" * 60)

    result = client.get_current_weather()

    if result and result.get('success'):
        weather = result['data']
        print("✅ Dados atuais obtidos com sucesso!")
        print(f"   Localização: {weather['location']}")
        print(f"   Temperatura: {weather['temperature']}°C")
        print(f"   Sensação térmica: {weather['feels_like']}°C")
        print(f"   Velocidade do vento: {weather['wind_speed']} km/h")
        print(f"   Timestamp: {weather['timestamp']}")
        print(f"   Fonte: {weather['source']}")
        print(f"   Nota: {weather['note']}")
    else:
        print("❌ Erro ao obter dados atuais")
        print("   Verifique se o dashboard está rodando: docker compose up -d")

    # Exemplo 2: Previsão para os próximos dias
    print("\n🌤️ Exemplo 2: Previsão do tempo para 7 dias")
    print("-" * 60)

    result = client.get_forecast(days=7)

    if result and result.get('success'):
        forecast = result['data']
        print(f"✅ Previsão obtida para {len(forecast)} dias:")
        print("<10")
        for i, day in enumerate(forecast[:5]):  # Mostra apenas os primeiros 5 dias
            date_obj = datetime.strptime(day['date'], '%Y-%m-%d')
            weekday = date_obj.strftime('%A')
            print(f"   {weekday[:3]}: {day['temperature_max']}°C / {day['temperature_min']}°C")
        print(f"   ... e mais {len(forecast)-5} dias")
        print(f"   Fonte: {result['source']}")
    else:
        print("❌ Erro ao obter previsão")

    # Exemplo 3: Dados de monitoramento semanal (3-4 vezes por semana)
    print("\n📅 Exemplo 3: Monitoramento semanal (3 vezes por semana)")
    print("-" * 60)

    result = client.get_monitoring_data(weeks=4)

    if result and result.get('success'):
        summary = result['summary']
        print("✅ Dados de monitoramento obtidos!")
        print(f"   Período: {summary['period_weeks']} semanas")
        print(f"   Total de registros: {summary['total_records']}")
        print(f"   Agendamento: {result['monitoring_schedule']}")

        print("   📊 Estatísticas de Temperatura:"        print(f"      Máxima: {summary['temperature']['max']}°C")
        print(f"      Mínima: {summary['temperature']['min']}°C")
        print(f"      Média: {summary['temperature']['mean']:.1f}°C")
        print(f"      Desvio padrão: {summary['temperature']['std']:.1f}°C")

        print("   🌧️ Estatísticas de Precipitação:"        print(f"      Total: {summary['precipitation']['total']:.1f} mm")
        print(f"      Dias com chuva: {summary['precipitation']['days_with_rain']}")
        print(f"      Média diária: {summary['precipitation']['mean_daily']:.1f} mm")

        print(f"   📍 Localização: {summary['location']}")
        print(f"   Fonte: {summary['source']}")
    else:
        print("❌ Erro ao obter dados de monitoramento")

    # Exemplo 4: Dados históricos mensais
    print("\n📈 Exemplo 4: Dados históricos mensais")
    print("-" * 60)

    # Último mês
    end_date = date.today()
    start_date = end_date - timedelta(days=30)

    result = client.get_historical_data(
        start_date.strftime('%Y-%m-%d'),
        end_date.strftime('%Y-%m-%d')
    )

    if result and result.get('success'):
        data = result['data']
        print(f"✅ Dados históricos obtidos para {len(data)} dias!")
        print(f"   Período: {result['date_range']['start']} até {result['date_range']['end']}")
        print(f"   Total de dias: {result['date_range']['days']}")
        print(f"   Localizações: {result['locations']}")
        print(f"   Fonte: {result['source']}")
        print(f"   Nota: {result['note']}")

        if len(data) > 0:
            # Mostra estatísticas básicas
            temps = [d.get('temperature_mean', 0) for d in data if d.get('temperature_mean')]
            if temps:
                print("   📊 Estatísticas do período:"                print(f"      Temperatura média: {sum(temps)/len(temps):.1f}°C")
                print(f"      Temperatura máxima: {max(temps):.1f}°C")
                print(f"      Temperatura mínima: {min(temps):.1f}°C")
    else:
        print("❌ Erro ao obter dados históricos")

    # Exemplo 5: Geração de CSV histórico
    print("\n💾 Exemplo 5: Geração de arquivo CSV histórico")
    print("-" * 60)

    result = client.generate_historical_csv(
        start_date.strftime('%Y-%m-%d'),
        end_date.strftime('%Y-%m-%d')
    )

    if result and result.get('success'):
        print("✅ Arquivo CSV gerado com sucesso!")
        print(f"   Arquivo: {result['file_path']}")
        print(f"   Período: {result['date_range']['start']} até {result['date_range']['end']}")
        print(f"   Dias: {result['date_range']['days']}")
        print(f"   Localizações: {result['locations']}")
        print(f"   Fonte: {result['source']}")
        print("   💡 O arquivo CSV foi salvo no diretório csv_output/ do container")
    else:
        print("❌ Erro ao gerar CSV histórico")

    print("\n" + "=" * 70)
    print("🎯 Resumo - Open-Meteo é a melhor opção para seu projeto:")
    print()
    print("✅ Vantagens:")
    print("   • Gratuita e SEM CHAVE API necessária")
    print("   • Dados históricos de até 60 anos")
    print("   • Dados atuais e previsões precisas")
    print("   • Coordenadas exatas de Montreal (45.5019, -73.5673)")
    print("   • Ideal para monitoramento 3-4 vezes por semana")
    print("   • API JSON simples e documentada")
    print()
    print("🚀 Para usar em produção:")
    print("   1. O dashboard já está integrado com Open-Meteo")
    print("   2. Acesse: http://localhost:5000/dashboard")
    print("   3. Na seção 'Análise Avançada - PowerBI Style', use os botões Open-Meteo")
    print("   4. Configure coletas automáticas 3-4 vezes por semana")
    print()
    print("📊 Para gráficos PowerBI-style:")
    print("   • Use o painel 'Análise Avançada' no dashboard")
    print("   • KPIs interativos com tendências")
    print("   • Gráficos de correlação e mapas de calor")
    print("   • Rosa dos ventos e séries temporais")
    print()
    print("🔗 Links úteis:")
    print("   • Documentação: https://open-meteo.com/")
    print("   • API Forecast: https://open-meteo.com/en/docs")
    print("   • API Histórica: https://open-meteo.com/en/docs/historical-weather-api")


if __name__ == "__main__":
    main()
