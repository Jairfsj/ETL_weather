#!/usr/bin/env python3
"""
Exemplo de uso dos dados históricos do AerisWeather no ETL Weather Dashboard

Este script demonstra como usar os novos endpoints de dados históricos
para baixar e processar dados climáticos históricos de Montreal.
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import json
import os
from pathlib import Path


class HistoricalWeatherClient:
    """Cliente para acessar dados históricos do AerisWeather via API"""

    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.api_prefix = "/api/v1/weather"

    def get_historical_date(self, date, locations=None, fields=None):
        """Busca dados históricos de uma data específica"""
        url = f"{self.base_url}{self.api_prefix}/aeris/historical/{date}"

        params = {}
        if locations:
            params['locations'] = locations
        if fields:
            params['fields'] = fields

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar dados históricos: {e}")
            return None

    def get_historical_range(self, start_date, end_date, locations=None, fields=None):
        """Busca dados históricos em um intervalo de datas"""
        url = f"{self.base_url}{self.api_prefix}/aeris/historical"

        params = {
            'start_date': start_date,
            'end_date': end_date
        }

        if locations:
            params['locations'] = locations
        if fields:
            params['fields'] = fields

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar intervalo histórico: {e}")
            return None

    def generate_historical_csvs(self, start_date, end_date, locations=None, fields=None):
        """Gera arquivos CSV com dados históricos"""
        url = f"{self.base_url}{self.api_prefix}/aeris/historical/csv"

        params = {
            'start_date': start_date,
            'end_date': end_date
        }

        if locations:
            params['locations'] = locations
        if fields:
            params['fields'] = fields

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao gerar CSVs históricos: {e}")
            return None


def main():
    """Função principal com exemplos de uso"""

    print("🌤️ ETL Weather Dashboard - Exemplos de Dados Históricos AerisWeather")
    print("=" * 70)

    client = HistoricalWeatherClient()

    # Exemplo 1: Dados de uma data específica
    print("\n📅 Exemplo 1: Dados históricos de uma data específica")
    print("-" * 50)

    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    result = client.get_historical_date(yesterday, locations=['montreal,ca'])

    if result and result.get('success'):
        print(f"✅ Dados encontrados para {yesterday}")
        print(f"   Localizações: {result['locations']}")
        print(f"   Registros: {result['count']}")
        print(f"   Fonte: {result['source']}")
    else:
        print(f"❌ Nenhum dado encontrado para {yesterday}")
        print("   Nota: Configure AERIS_CLIENT_ID e AERIS_CLIENT_SECRET para dados reais")

    # Exemplo 2: Intervalo de datas
    print("\n📊 Exemplo 2: Dados históricos em intervalo de datas")
    print("-" * 50)

    start_date = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
    end_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    result = client.get_historical_range(start_date, end_date, locations=['montreal,ca'])

    if result and result.get('success'):
        print(f"✅ Dados encontrados para período {start_date} até {end_date}")
        print(f"   Datas com dados: {result['total_dates']}")
        print(f"   Localizações: {result['locations']}")
        print(f"   Fonte: {result['source']}")
    else:
        print(f"❌ Nenhum dado encontrado para o período {start_date} até {end_date}")

    # Exemplo 3: Geração de CSVs
    print("\n💾 Exemplo 3: Geração de arquivos CSV históricos")
    print("-" * 50)

    result = client.generate_historical_csvs(start_date, end_date, locations=['montreal,ca'])

    if result and result.get('success'):
        print(f"✅ CSVs gerados com sucesso!")
        print(f"   Arquivos criados: {len(result['files'])}")
        print(f"   Período: {result['date_range']['start']} até {result['date_range']['end']}")
        print("   Arquivos:"        for file_path in result['files']:
            print(f"     - {file_path}")
    else:
        print("❌ Falha ao gerar CSVs"        if result:
            print(f"   Erro: {result.get('error', 'Erro desconhecido')}")

    # Exemplo 4: Uso avançado com campos específicos
    print("\n🔧 Exemplo 4: Uso avançado com campos específicos")
    print("-" * 50)

    custom_fields = [
        'periods.dateTimeISO',
        'place.name',
        'periods.tempC',
        'periods.humidity',
        'periods.windSpeedKPH'
    ]

    result = client.get_historical_date(
        yesterday,
        locations=['montreal,ca', 'toronto,ca'],
        fields=custom_fields
    )

    if result and result.get('success'):
        print(f"✅ Dados encontrados com campos específicos para {yesterday}")
        print(f"   Localizações: {result['locations']}")
        print(f"   Registros: {result['count']}")
        print("   Campos solicitados:"        for field in custom_fields:
            print(f"     - {field}")
    else:
        print(f"❌ Nenhum dado encontrado com campos específicos")

    print("\n" + "=" * 70)
    print("🎯 Para usar dados reais:")
    print("   1. Obtenha uma conta gratuita no AerisWeather (https://www.aerisweather.com/)")
    print("   2. Configure AERIS_CLIENT_ID e AERIS_CLIENT_SECRET no arquivo .env")
    print("   3. Reinicie os containers: docker compose restart")
    print("   4. Execute este script novamente para ver dados reais!")


if __name__ == "__main__":
    main()
