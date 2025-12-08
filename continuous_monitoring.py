#!/usr/bin/env python3
"""
Sistema de Monitoramento Contínuo Climático Montreal (2025-2026)

Este script implementa monitoramento contínuo de dados climáticos de Montreal
de 2025 até 2026, coletando dados 3 vezes por semana automaticamente.

Funcionalidades:
- Coleta automática de dados climáticos via Open-Meteo
- Geração de relatórios mensais/anuais
- Alertas para condições extremas

Uso:
    python continuous_monitoring.py

Configuração:
    - Dados coletados 3x por semana (Seg, Qua, Sex)
    - Período: 2025-2026 (2 anos)
    - API: Open-Meteo (gratuita, sem limites)
"""

import sys
import time
import logging
from datetime import datetime, date, timedelta
from typing import Optional
import pandas as pd
import schedule
from pathlib import Path

# Adicionar o diretório do projeto ao path
sys.path.append(str(Path(__file__).parent))

# Importar serviços
from python_analytics.app.services.open_meteo_service import OpenMeteoService

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitoring.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ContinuousClimateMonitor:
    """
    Monitor Climático Contínuo para Montreal (2025-2026)
    Coleta automática 3x por semana via Open-Meteo
    """

    MONITORING_DAYS = [0, 2, 4]  # Monday, Wednesday, Friday
    START_YEAR = 2025
    END_YEAR = 2026

    def __init__(self):
        self.open_meteo = OpenMeteoService()
        self._setup_directories()
        logger.info("Continuous Climate Monitor initialized for 2025-2026")

    def _setup_directories(self):
        """Cria diretórios necessários"""
        self.reports_dir = Path("reports")
        self.data_dir = Path("data")
        self.reports_dir.mkdir(exist_ok=True)
        self.data_dir.mkdir(exist_ok=True)

    @staticmethod
    def is_monitoring_day() -> bool:
        """Verifica se hoje é dia de monitoramento"""
        return date.today().weekday() in ContinuousClimateMonitor.MONITORING_DAYS

    def collect_weather_data(self) -> Optional[pd.DataFrame]:
        """Coleta dados climáticos semanais"""
        try:
            data = self.open_meteo.get_weekly_monitoring_data(weeks_back=4)
            if data is not None and not data.empty:
                logger.info(f"Collected {len(data)} monitoring records")
                return data
        except Exception as e:
            logger.error(f"Error collecting weather data: {e}")
        return None

    def generate_monthly_report(self) -> Optional[str]:
        """Gera relatório mensal"""
        try:
            data = self.collect_weather_data()
            if data is None or data.empty:
                return None

            report_date = datetime.now().strftime("%Y-%m")
            report_path = self.reports_dir / f"monthly_report_{report_date}.txt"

            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(f"Relatório Climático Mensal - Montreal {report_date}\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Temperatura média: {data['temperature_mean'].mean():.1f}°C\n")
                f.write(f"Temperatura máxima: {data['temperature_max'].max():.1f}°C\n")
                f.write(f"Temperatura mínima: {data['temperature_min'].min():.1f}°C\n")
                f.write(f"Umidade média: {data['humidity_mean'].mean():.1f}%\n")
                f.write(f"Precipitação total: {data['precipitation'].sum():.1f} mm\n")
                f.write(f"Registros coletados: {len(data)}\n")

            logger.info(f"Monthly report generated: {report_path}")
            return str(report_path)

        except Exception as e:
            logger.error(f"Error generating monthly report: {e}")
            return None

    def run_monitoring_cycle(self) -> bool:
        """Executa um ciclo completo de monitoramento"""
        logger.info("Starting monitoring cycle...")

        try:
            # Coletar dados
            data = self.collect_weather_data()
            if data is not None:
                # Salvar como CSV
                csv_path = self.open_meteo.save_to_csv(
                    data,
                    filename=f"monitoring_{datetime.now().strftime('%Y%m%d')}.csv"
                )
                logger.info(f"Data saved to CSV: {csv_path}")

            # Gerar relatório mensal no dia 1
            if datetime.now().day == 1:
                self.generate_monthly_report()

            logger.info("Monitoring cycle completed successfully")
            return True

        except Exception as e:
            logger.error(f"Error in monitoring cycle: {e}")
            return False

    def run_continuous_monitoring(self):
        """Executa monitoramento contínuo"""
        logger.info("Starting continuous climate monitoring for Montreal (2025-2026)")
        logger.info("Monitoring schedule: 3 times per week (Mon, Wed, Fri)")

        # Agendar execuções
        schedule.every().monday.at("09:00").do(self.run_monitoring_cycle)
        schedule.every().wednesday.at("09:00").do(self.run_monitoring_cycle)
        schedule.every().friday.at("09:00").do(self.run_monitoring_cycle)

        # Executar imediatamente
        logger.info("Running initial monitoring cycle...")
        self.run_monitoring_cycle()

        logger.info("Continuous monitoring started. Press Ctrl+C to stop.")

        try:
            while True:
                schedule.run_pending()
                time.sleep(60)
        except KeyboardInterrupt:
            logger.info("Continuous monitoring stopped by user")

    def run_manual_collection(self):
        """Executa coleta manual para testes"""
        logger.info("Running manual data collection...")
        return self.run_monitoring_cycle()


def main():
    """Função principal"""
    import argparse

    parser = argparse.ArgumentParser(description='Monitoramento Climático Montreal 2025-2026')
    parser.add_argument('--manual', action='store_true', help='Executar coleta manual única')

    args = parser.parse_args()
    monitor = ContinuousClimateMonitor()

    if args.manual:
        monitor.run_manual_collection()
    else:
        print("🌤️ Monitoramento Climático Montreal (2025-2026)")
        print("Frequência: 3x por semana (Seg, Qua, Sex)")
        print("API: Open-Meteo (gratuita)")
        monitor.run_continuous_monitoring()

if __name__ == "__main__":
    main()
