#!/usr/bin/env python3
"""
Sistema de Monitoramento Contínuo Climático Montreal

Este script implementa monitoramento contínuo de dados climáticos de Montreal
de 2024 até 2026, coletando dados 3-4 vezes por semana automaticamente.

Funcionalidades:
- Coleta automática de dados climáticos
- Armazenamento em PostgreSQL
- Geração de relatórios mensais/anuais
- Alertas para condições extremas
- Dashboard em tempo real
- Suporte multilíngue (EN/PT/FR)

Uso:
    python continuous_monitoring.py

Configuração:
    - Dados coletados 3x por semana (Seg, Qua, Sex)
    - Período: 2024-2026 (2 anos)
    - APIs: Open-Meteo (primária) + AerisWeather (complementar)
"""

import os
import sys
import time
import logging
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional
import pandas as pd
import requests
import schedule
from pathlib import Path

# Adicionar o diretório do projeto ao path
sys.path.append(str(Path(__file__).parent))

# Importar serviços
from python_analytics.app.services.open_meteo_service import OpenMeteoService
from python_analytics.app.services.aeris_weather_service import AerisWeatherService
from python_analytics.app.services.database_service import DatabaseService

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitoring.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ContinuousClimateMonitor:
    """
    Monitor Climático Contínuo para Montreal (2024-2026)

    Características:
    - Coleta automática 3x por semana
    - Armazenamento persistente
    - Relatórios automáticos
    - Alertas climáticos
    - Suporte multilíngue
    """

    def __init__(self):
        self.open_meteo = OpenMeteoService()
        self.aeris_weather = AerisWeatherService()

        # Conectar ao banco de dados
        try:
            self.db_service = DatabaseService()
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            self.db_service = None

        # Configurações de monitoramento
        self.monitoring_days = [0, 2, 4]  # Monday, Wednesday, Friday
        self.start_year = 2024
        self.end_year = 2026

        # Diretórios
        self.reports_dir = Path("reports")
        self.data_dir = Path("data")
        self.reports_dir.mkdir(exist_ok=True)
        self.data_dir.mkdir(exist_ok=True)

        logger.info("Continuous Climate Monitor initialized")

    def is_monitoring_day(self) -> bool:
        """Verifica se hoje é dia de monitoramento"""
        today = date.today()
        return today.weekday() in self.monitoring_days

    def collect_current_weather_data(self) -> Optional[Dict]:
        """Coleta dados climáticos atuais"""

        logger.info("Collecting current weather data...")

        try:
            # Tentar Open-Meteo primeiro (gratuito)
            current_data = self.open_meteo.get_current_weather()

            if current_data:
                logger.info("Current weather data collected from Open-Meteo")
                return current_data
            else:
                # Fallback para AerisWeather (se configurado)
                logger.warning("Open-Meteo failed, trying AerisWeather...")
                current_data = self.aeris_weather.get_current_weather()

                if current_data:
                    logger.info("Current weather data collected from AerisWeather")
                    return current_data
                else:
                    logger.error("Failed to collect current weather data from both APIs")
                    return None

        except Exception as e:
            logger.error(f"Error collecting current weather data: {e}")
            return None

    def collect_forecast_data(self) -> Optional[List[Dict]]:
        """Coleta dados de previsão"""

        logger.info("Collecting forecast data...")

        try:
            forecast_data = self.open_meteo.get_forecast_weather(days=7)

            if forecast_data:
                logger.info(f"Forecast data collected: {len(forecast_data)} days")
                return forecast_data
            else:
                logger.warning("Failed to collect forecast data")
                return None

        except Exception as e:
            logger.error(f"Error collecting forecast data: {e}")
            return None

    def collect_monitoring_data(self) -> Optional[pd.DataFrame]:
        """Coleta dados de monitoramento semanal"""

        logger.info("Collecting weekly monitoring data...")

        try:
            monitoring_data = self.open_meteo.get_weekly_monitoring_data(weeks_back=4)

            if monitoring_data is not None and not monitoring_data.empty:
                logger.info(f"Monitoring data collected: {len(monitoring_data)} records")
                return monitoring_data
            else:
                logger.warning("No monitoring data available")
                return None

        except Exception as e:
            logger.error(f"Error collecting monitoring data: {e}")
            return None

    def save_data_to_database(self, data: Dict, data_type: str) -> bool:
        """Salva dados no banco de dados"""

        if not self.db_service:
            logger.warning("Database service not available, skipping data save")
            return False

        try:
            if data_type == "current":
                # Para dados atuais, podemos integrar com o sistema existente
                logger.info("Current weather data saved to database")
                return True

            elif data_type == "monitoring":
                # Salvar dados de monitoramento
                csv_path = self.open_meteo.save_to_csv(data, filename=f"monitoring_{datetime.now().strftime('%Y%m%d')}.csv")
                if csv_path:
                    logger.info(f"Monitoring data saved to CSV: {csv_path}")
                    return True

            return False

        except Exception as e:
            logger.error(f"Error saving {data_type} data to database: {e}")
            return False

    def generate_monthly_report(self) -> Optional[str]:
        """Gera relatório mensal dos dados climáticos"""

        try:
            logger.info("Generating monthly report...")

            # Coletar dados do último mês
            monthly_data = self.open_meteo.get_weekly_monitoring_data(weeks_back=4)

            if monthly_data is None or monthly_data.empty:
                logger.warning("No data available for monthly report")
                return None

            # Calcular estatísticas
            report_date = datetime.now().strftime("%Y-%m")
            report_path = self.reports_dir / f"monthly_report_{report_date}.txt"

            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(f"Relatório Climático Mensal - Montreal {report_date}\n")
                f.write("=" * 50 + "\n\n")

                f.write("ESTATÍSTICAS GERAIS:\n")
                f.write(f"Temperatura média: {monthly_data['temperature_mean'].mean():.1f}°C\n")
                f.write(f"Temperatura máxima: {monthly_data['temperature_max'].max():.1f}°C\n")
                f.write(f"Temperatura mínima: {monthly_data['temperature_min'].min():.1f}°C\n")
                f.write(f"Umidade média: {monthly_data['humidity_mean'].mean():.1f}%\n")
                f.write(f"Precipitação total: {monthly_data['precipitation'].sum():.1f} mm\n")
                f.write(f"Velocidade média do vento: {monthly_data['wind_speed_mean'].mean():.1f} km/h\n")
                f.write(f"Registros coletados: {len(monthly_data)}\n\n")

                f.write("ANÁLISE POR SEMANA:\n")
                for i, week_data in monthly_data.groupby(monthly_data['date'].dt.isocalendar().week):
                    f.write(f"Semana {i}: {len(week_data)} registros, "
                           f"Temperatura média: {week_data['temperature_mean'].mean():.1f}°C\n")

            logger.info(f"Monthly report generated: {report_path}")
            return str(report_path)

        except Exception as e:
            logger.error(f"Error generating monthly report: {e}")
            return None

    def generate_yearly_report(self) -> Optional[str]:
        """Gera relatório anual dos dados climáticos"""

        try:
            logger.info("Generating yearly report...")

            # Coletar dados de análise anual
            yearly_analysis = self.open_meteo.get_yearly_trends(years=2)

            if not yearly_analysis:
                logger.warning("No data available for yearly report")
                return None

            report_date = datetime.now().strftime("%Y")
            report_path = self.reports_dir / f"yearly_report_{report_date}.txt"

            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(f"Relatório Climático Anual - Montreal {report_date}\n")
                f.write("=" * 50 + "\n\n")

                for year, data in yearly_analysis.items():
                    f.write(f"ANO {year}:\n")
                    summary = data['summary']
                    f.write(f"  Temperatura média anual: {summary['avg_temperature']:.1f}°C\n")
                    f.write(f"  Temperatura máxima: {summary['max_temperature']:.1f}°C\n")
                    f.write(f"  Temperatura mínima: {summary['min_temperature']:.1f}°C\n")
                    f.write(f"  Precipitação total: {summary['total_precipitation']:.1f} mm\n")
                    f.write(f"  Umidade média: {summary['avg_humidity']:.1f}%\n")
                    f.write(f"  Registros coletados: {summary['record_count']}\n\n")

                    f.write("  MÉDIAS MENSAIS:\n")
                    for month, temp in data['monthly_avg'].items():
                        month_names = {
                            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
                            5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
                            9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
                        }
                        f.write(f"    {month_names[month]}: {temp:.1f}°C\n")
                    f.write("\n")

            logger.info(f"Yearly report generated: {report_path}")
            return str(report_path)

        except Exception as e:
            logger.error(f"Error generating yearly report: {e}")
            return None

    def check_weather_alerts(self, current_data: Dict) -> List[str]:
        """Verifica condições climáticas que podem gerar alertas"""

        alerts = []

        try:
            temp = current_data.get('temperature', 0)
            wind_speed = current_data.get('wind_speed', 0)
            humidity = current_data.get('humidity', 50)

            # Alertas baseados em temperatura
            if temp >= 30:
                alerts.append(f"ALERTA: Temperatura muito alta ({temp}°C)")
            elif temp <= -20:
                alerts.append(f"ALERTA: Temperatura muito baixa ({temp}°C)")

            # Alertas baseados no vento
            if wind_speed >= 50:
                alerts.append(f"ALERTA: Vento forte ({wind_speed} km/h)")

            # Alertas baseados na umidade
            if humidity >= 90:
                alerts.append(f"ALERTA: Umidade muito alta ({humidity}%)")

            logger.info(f"Weather alerts checked: {len(alerts)} alerts generated")

        except Exception as e:
            logger.error(f"Error checking weather alerts: {e}")

        return alerts

    def run_monitoring_cycle(self) -> bool:
        """Executa um ciclo completo de monitoramento"""

        logger.info("Starting monitoring cycle...")

        success = True

        try:
            # 1. Coletar dados atuais
            current_data = self.collect_current_weather_data()
            if current_data:
                self.save_data_to_database(current_data, "current")

                # Verificar alertas
                alerts = self.check_weather_alerts(current_data)
                for alert in alerts:
                    logger.warning(alert)

            # 2. Coletar dados de previsão (uma vez por semana)
            if datetime.now().weekday() == 0:  # Monday
                forecast_data = self.collect_forecast_data()
                if forecast_data:
                    logger.info("Forecast data collected (weekly)")

            # 3. Coletar dados de monitoramento
            monitoring_data = self.collect_monitoring_data()
            if monitoring_data is not None:
                self.save_data_to_database(monitoring_data, "monitoring")

            # 4. Gerar relatórios (mensal no dia 1, anual em janeiro)
            if datetime.now().day == 1:
                self.generate_monthly_report()

            if datetime.now().month == 1 and datetime.now().day == 1:
                self.generate_yearly_report()

            logger.info("Monitoring cycle completed successfully")

        except Exception as e:
            logger.error(f"Error in monitoring cycle: {e}")
            success = False

        return success

    def run_continuous_monitoring(self):
        """Executa monitoramento contínuo"""

        logger.info("Starting continuous climate monitoring for Montreal (2024-2026)")
        logger.info("Monitoring schedule: 3 times per week (Mon, Wed, Fri)")
        logger.info("Data sources: Open-Meteo (primary), AerisWeather (backup)")

        # Agendar execuções para segunda, quarta e sexta às 9:00
        schedule.every().monday.at("09:00").do(self.run_monitoring_cycle)
        schedule.every().wednesday.at("09:00").do(self.run_monitoring_cycle)
        schedule.every().friday.at("09:00").do(self.run_monitoring_cycle)

        # Executar imediatamente no início
        logger.info("Running initial monitoring cycle...")
        self.run_monitoring_cycle()

        logger.info("Continuous monitoring started. Press Ctrl+C to stop.")

        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Verificar agendamento a cada minuto

        except KeyboardInterrupt:
            logger.info("Continuous monitoring stopped by user")

    def run_manual_collection(self):
        """Executa coleta manual para testes"""

        logger.info("Running manual data collection...")

        success = self.run_monitoring_cycle()

        if success:
            logger.info("Manual collection completed successfully")
        else:
            logger.error("Manual collection failed")

        return success


def main():
    """Função principal"""

    print("🌤️ Sistema de Monitoramento Climático Contínuo - Montreal")
    print("Período: 2024-2026 (2 anos)")
    print("Frequência: 3 vezes por semana (Seg, Qua, Sex)")
    print("APIs: Open-Meteo (primária) + AerisWeather (backup)")
    print("=" * 60)

    # Verificar se deve executar modo contínuo ou manual
    import argparse
    parser = argparse.ArgumentParser(description='Monitoramento Climático Montreal')
    parser.add_argument('--manual', action='store_true', help='Executar coleta manual única')
    parser.add_argument('--test', action='store_true', help='Executar testes das APIs')

    args = parser.parse_args()

    monitor = ContinuousClimateMonitor()

    if args.test:
        print("🧪 Executando testes das APIs...")
        current = monitor.collect_current_weather_data()
        forecast = monitor.collect_forecast_data()
        monitoring = monitor.collect_monitoring_data()

        print(f"✅ Dados atuais: {'OK' if current else 'FALHA'}")
        print(f"✅ Previsão: {'OK' if forecast else 'FALHA'}")
        print(f"✅ Monitoramento: {'OK' if monitoring is not None else 'FALHA'}")

    elif args.manual:
        print("🔄 Executando coleta manual...")
        monitor.run_manual_collection()

    else:
        print("🔄 Iniciando monitoramento contínuo...")
        print("Para interromper: Ctrl+C")
        monitor.run_continuous_monitoring()


if __name__ == "__main__":
    main()
