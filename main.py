import logging
import os
from pathlib import Path
from src.coleta_de_dados import LoteriasCaixa

FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(filename='result.log', format=FORMAT, level=logging.INFO)

def deletar_db_anterior():
    caminho = Path("db_sorteios.db")
    if caminho.exists():
        os.remove(caminho)

def main():
    try:
        deletar_db_anterior()
        loterias = LoteriasCaixa()
        loterias.coletar_dados()
        logging.info('ok')
    except Exception as e:
        logging.exception(e)

if __name__ == '__main__':
    main()
