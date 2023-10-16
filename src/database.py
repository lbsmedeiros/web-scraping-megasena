from sqlalchemy import String, insert, select, update, delete
from sqlalchemy.orm import declarative_base, Mapped, mapped_column

# Cria uma classe base para declarar modelos de dados.
Base = declarative_base()

class DataBase(Base):
    """
    Classe que representa a tabela de sorteios no banco de dados.

    Atributos:
        __tablename__ (str): Nome da tabela no banco de dados.
        nr_sorteio (int): Número do sorteio (chave primária).
        mega_da_virada (bool): Indica se é um sorteio da Mega da Virada.
        data_sorteio (str): Data do sorteio no formato string (ex. 'dd/mm/aaaa').
        dezenas (str): Dezenas sorteadas no formato de string (ex. '01, 02, 03, ...').
        local_do_sorteio (str): Local onde o sorteio ocorreu.
        ganhadores_seis_dezenas (int): Quantidade de ganhadores com seis dezenas.
        premio_seis_dezenas (float): Valor do prêmio para seis dezenas.
        ganhadores_cinco_dezenas (int): Quantidade de ganhadores com cinco dezenas.
        premio_cinco_dezenas (float): Valor do prêmio para cinco dezenas.
        ganhadores_quatro_dezenas (int): Quantidade de ganhadores com quatro dezenas.
        premio_quatro_dezenas (float): Valor do prêmio para quatro dezenas.
    """
    __tablename__ = 'sorteios'

    nr_sorteio: Mapped[int] = mapped_column(primary_key=True)
    mega_da_virada: Mapped[bool] = mapped_column()
    data_sorteio: Mapped[str] = mapped_column(String(10))
    dezenas: Mapped[str] = mapped_column(String(21))
    local_do_sorteio: Mapped[str] = mapped_column(String(150))
    ganhadores_seis_dezenas: Mapped[int] = mapped_column()
    premio_seis_dezenas: Mapped[float] = mapped_column()
    ganhadores_cinco_dezenas: Mapped[int] = mapped_column()
    premio_cinco_dezenas: Mapped[float] = mapped_column()
    ganhadores_quatro_dezenas: Mapped[int] = mapped_column()
    premio_quatro_dezenas: Mapped[float] = mapped_column()

class DbSorteios:
    """
    Classe para realizar operações no banco de dados de sorteios.

    Atributos:
        engine: Instância do SQLAlchemy Engine para se conectar ao banco de dados.
    """
    def __init__(self, engine):
        """
        Inicializa a classe com uma instância de engine do SQLAlchemy e cria a tabela se não existir.

        Args:
            engine: Instância do SQLAlchemy Engine.
        """
        self.engine = engine
        Base.metadata.create_all(self.engine)

    def create(self, dicionario):
        """
        Insere um novo registro na tabela.

        Args:
            dicionario (dict): Dicionário contendo os valores a serem inseridos na tabela.
        """
        stmt = insert(DataBase).values(
            nr_sorteio=dicionario['nr_sorteio'],
            mega_da_virada=dicionario['mega_da_virada'],
            data_sorteio=dicionario['data_sorteio'],
            dezenas=dicionario['dezenas'],
            local_do_sorteio=dicionario['local_do_sorteio'],
            ganhadores_seis_dezenas=dicionario['ganhadores_seis_dezenas'],
            premio_seis_dezenas=dicionario['premio_seis_dezenas'],
            ganhadores_cinco_dezenas=dicionario['ganhadores_cinco_dezenas'],
            premio_cinco_dezenas=dicionario['premio_cinco_dezenas'],
            ganhadores_quatro_dezenas=dicionario['ganhadores_quatro_dezenas'],
            premio_quatro_dezenas=dicionario['premio_quatro_dezenas']
        )

        with self.engine.connect() as conn:
            conn.execute(stmt)
            conn.commit()

    def coletar_todos_sorteios(self):
        """
        Coleta todos os números de sorteios armazenados.

        Returns:
            sqlalchemy.engine.result.ResultProxy: Resultado da consulta.
        """
        stmt = select(DataBase.nr_sorteio)

        with self.engine.connect() as conn:
            return conn.execute(stmt)

    def read(self, dicionario=None):
        """
        Lê registros da tabela com base em critérios fornecidos.

        Args:
            dicionario (dict): Dicionário contendo critérios de consulta.

        Returns:
            sqlalchemy.engine.result.ResultProxy: Resultado da consulta.
        """
        stmt = select(DataBase)

        if dicionario:
            for chave, value in dicionario.items():
                match chave:
                    case 'nr_sorteio':
                        stmt = stmt.where(DataBase.nr_sorteio == value)
                    case 'mega_da_virada':
                        stmt = stmt.where(DataBase.mega_da_virada == value)
                    case 'data_sorteio':
                        stmt = stmt.where(DataBase.data_sorteio == value)
                    case 'dezenas':
                        stmt = stmt.where(DataBase.dezenas == value)
                    case 'local_do_sorteio':
                        stmt = stmt.where(DataBase.local_do_sorteio == value)
                    case 'ganhadores_seis_dezenas':
                        stmt = stmt.where(DataBase.ganhadores_seis_dezenas == value)
                    case 'premio_seis_dezenas':
                        stmt = stmt.where(DataBase.premio_seis_dezenas == value)
                    case 'ganhadores_cinco_dezenas':
                        stmt = stmt.where(DataBase.ganhadores_cinco_dezenas == value)
                    case 'premio_cinco_dezenas':
                        stmt = stmt.where(DataBase.premio_cinco_dezenas == value)
                    case 'ganhadores_quatro_dezenas':
                        stmt = stmt.where(DataBase.ganhadores_quatro_dezenas == value)
                    case 'premio_quatro_dezenas':
                        stmt = stmt.where(DataBase.premio_quatro_dezenas == value)
                    case _:
                        continue

        with self.engine.connect() as conn:
            return conn.execute(stmt)

    def update(self, sorteio: int, dicionario):
        """
        Atualiza um registro na tabela com base no número do sorteio.

        Args:
            sorteio (int): Número do sorteio a ser atualizado.
            dicionario (dict): Dicionário contendo os novos valores.

        """
        stmt = update(DataBase).values(dicionario).where(DataBase.nr_sorteio == sorteio)

        with self.engine.connect() as conn:
            conn.execute(stmt)
            conn.commit()

    def delete(self, sorteio):
        """
        Exclui um registro na tabela com base no número do sorteio.

        Args:
            sorteio: Número do sorteio a ser excluído.
        """
        stmt = delete(DataBase).where(DataBase.nr_sorteio == sorteio)

        with self.engine.connect() as conn:
            conn.execute(stmt)
            conn.commit()
