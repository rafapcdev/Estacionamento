import logging
import sys
import os

# Garante que a pasta logs exista
os.makedirs("logs", exist_ok=True)

# Formatação do log
log_formatter = logging.Formatter(
    fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Criando o Logger Principal
logger = logging.getLogger("parking_system")
logger.setLevel(logging.INFO)

# Handler 1: Arquivo físico
file_handler = logging.FileHandler("logs/app.log", encoding="utf-8")
file_handler.setFormatter(log_formatter)

# Handler 2: Console (Standard Output)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(log_formatter)

# Adiciona os dois handlers ao logger
if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
