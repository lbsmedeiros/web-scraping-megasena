from pathlib import Path
from time import sleep

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver import ActionChains as AC
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from webdriver_manager.chrome import ChromeDriverManager

from src.database import DbSorteios
from src.config import config


class LoteriasCaixa:
    """
    Classe para automatizar a coleta de dados dos sorteios da Loteria Caixa.
    """

    url = config.url

    options = Options()
    options.add_argument("--log-level=3")

    locators = {
        "tipo_de_sorteio": (By.XPATH, '//*[@id="wp_resultados"]/div[2]/div/div/h3[2]'),
        "numero_do_sorteio": (By.XPATH, '//*[@id="wp_resultados"]/div[1]/div/h2/span'),
        "dezenas": (By.XPATH, '//*[@id="ulDezenas"]//li'),
        "btn_proximo": (
            By.XPATH,
            '//*[@id="wp_resultados"]/div[1]/div/div[2]/ul/li[3]/a',
        ),
        "imput_nr_sorteio": (By.XPATH, '//*[@id="buscaConcurso"]'),
        "local": (By.XPATH, '//*[@id="wp_resultados"]/div[2]/div/div/p'),
        "seis_acertos": (By.XPATH, '//*[@id="wp_resultados"]/div[3]/div/p[1]'),
        "seis_acertos2": (By.XPATH, '//*[@id="wp_resultados"]/div[3]/div[2]/p[1]'),
        "cinco_acertos": (By.XPATH, '//*[@id="wp_resultados"]/div[3]/div/p[2]'),
        "cinco_acertos2": (By.XPATH, '//*[@id="wp_resultados"]/div[3]/div[2]/p[2]'),
        "quatro_acertos": (By.XPATH, '//*[@id="wp_resultados"]/div[3]/div/p[3]'),
        "quatro_acertos2": (By.XPATH, '//*[@id="wp_resultados"]/div[3]/div[2]/p[3]'),
    }

    def find_element(
        self, driver, locator, timer=10, condition=EC.presence_of_element_located
    ):
        """
        Encontra um elemento no DOM e espera até que ele seja visível.

        :param driver: Instância do driver do Selenium.
        :param locator: Localizador do elemento (por exemplo, (By.XPATH, 'xpath_do_elemento')).
        :param timer: Tempo máximo para aguardar (padrão é 10 segundos).
        :param condition: Condição para esperar (padrão é EC.presence_of_element_located).
        :return: O elemento encontrado.
        """
        return WebDriverWait(driver, timer).until(condition(locator))

    def find_elements(
        self, driver, locator, timer=10, condition=EC.presence_of_all_elements_located
    ):
        """
        Encontra uma lista de elementos no DOM e espera até que eles sejam visíveis.

        :param driver: Instância do driver do Selenium.
        :param locator: Localizador dos elementos (por exemplo, (By.XPATH, 'xpath_do_elemento')).
        :param timer: Tempo máximo para aguardar (padrão é 10 segundos).
        :param condition: Condição para esperar (padrão é EC.presence_of_all_elements_located).
        :return: Lista de elementos encontrados.
        """
        return WebDriverWait(driver, timer).until(condition(locator))

    def abrir_navegador(self):
        """
        Abre uma nova instância do navegador Chrome e a maximiza.

        :return: Instância do driver do Selenium.
        """
        driver = Chrome(ChromeDriverManager().install(), options=self.options)
        driver.maximize_window()
        return driver

    def acessar_site_loterias_caixa(self, driver):
        """
        Acessa o site da Loteria Caixa no navegador.

        :param driver: Instância do driver do Selenium.
        """
        driver.get(self.url)

    def coletar_nr_sorteio(self, driver):
        """
        Coleta o número do sorteio.

        :param driver: Instância do driver do Selenium.
        :return: Numero do sorteio coletado da página em formato Integer.
        """
        texto_sorteio = self.find_element(
            driver, self.locators["numero_do_sorteio"]
        ).text.strip()
        valor = int(
            texto_sorteio[texto_sorteio.index(" ") + 1 : texto_sorteio.index("(") - 1]
        )
        return valor

    def coletar_ultimo_sorteio_db(self):
        """
        Define qual é o último sorteio contido no database

        :return: Número do sorteio mais recente no database ou zero.
        """
        if not Path(config.caminho_db).exists():
            return 0

        engine = create_engine(f"sqlite:///{config.caminho_db}", future=True)
        repository = DbSorteios(engine)
        res = repository.coletar_todos_sorteios()
        resp = [i for i in res]

        if resp:
            return resp[-1][0]
        else:
            return 0

    def navegar_para_sorteio(self, driver, sorteio):
        """
        Navega para a página onde será começará a coletar dados.

        :param driver: Instância do driver do Selenium.
        :param sorteio: Valor que será imputado.
        """
        ac = AC(driver)
        self.find_element(driver, self.locators["imput_nr_sorteio"]).send_keys(sorteio)
        ac.send_keys(Keys.ENTER).perform()

    def verificar_mega_virada(self, driver):
        """
        Verifica se o sorteio atual é da "Mega da Virada".

        :param driver: Instância do driver do Selenium.
        :return: True se for da "Mega da Virada", False caso contrário.
        """
        texto = self.find_element(driver, self.locators["tipo_de_sorteio"]).text.strip()
        return texto == "Mega da Virada"

    def coletar_data_sorteio(self, driver):
        """
        Coleta a data do sorteio atual.

        :param driver: Instância do driver do Selenium.
        :return: A data do sorteio no formato de string.
        """
        texto_sorteio = self.find_element(
            driver, self.locators["numero_do_sorteio"]
        ).text.strip()
        return texto_sorteio[texto_sorteio.index("(") + 1 : texto_sorteio.index(")")]

    def coletar_dezenas(self, driver):
        """
        Coleta as dezenas sorteadas no sorteio atual.

        :param driver: Instância do driver do Selenium.
        :return: Uma string com as dezenas separadas por vírgula.
        """
        elementos_dezenas = self.find_elements(driver, self.locators["dezenas"])
        dezenas = [i.text.strip() for i in elementos_dezenas]
        return ", ".join(dezenas)

    def coletar_local(self, driver):
        """
        Coleta o local do sorteio atual.

        :param driver: Instância do driver do Selenium.
        :return: O local do sorteio como uma string.
        """
        local_do_sorteio = self.find_element(
            driver, self.locators["local"]
        ).text.strip()
        try:
            return local_do_sorteio[local_do_sorteio.index(" em ") + 4 :]
        except ValueError:
            return "Não informado"

    def tratar_texto_acertos(self, texto):
        """
        Analisa e extrai informações sobre ganhadores e prêmios de acordo com o texto fornecido.

        :param texto: O texto que contém informações sobre ganhadores e prêmios.
        :return: Uma tupla contendo a quantidade de ganhadores e o valor do prêmio.
        """
        texto = texto[texto.index("\n") + 1 :]
        if texto == "Não houve ganhadores":
            return 0, 0.0
        qtd_ganhadores = int(texto[: texto.index(" ")].replace(".", ""))
        premio = float(
            texto[texto.rindex(" ") + 1 :].replace(".", "").replace(",", ".")
        )
        return qtd_ganhadores, premio

    def coletar_ganhadores_premio(self, driver, locator, locator2):
        """
        Coleta informações sobre ganhadores e prêmios do sorteio atual.

        :param driver: Instância do driver do Selenium.
        :param locator: Localizador do elemento que contém as informações.
        :param locator2: Localizador do elemento secundário  que contém as informações.
        :return: Uma tupla contendo a quantidade de ganhadores e o valor do prêmio.
        """
        texto = self.find_element(driver, locator=locator).text.strip()
        if "\n" not in texto:
            texto = self.find_element(driver, locator=locator2).text.strip()
        return self.tratar_texto_acertos(texto)

    def coletar_valores(self, driver):
        nr_sorteio_atual = self.coletar_nr_sorteio(driver=driver)
        virada = self.verificar_mega_virada(driver=driver)
        data_sorteio = self.coletar_data_sorteio(driver=driver)
        dezenas = self.coletar_dezenas(driver=driver)
        local_do_sorteio = self.coletar_local(driver=driver)
        qtd_6, premio_6 = self.coletar_ganhadores_premio(
            driver, self.locators["seis_acertos"], self.locators["seis_acertos2"]
        )
        qtd_5, premio_5 = self.coletar_ganhadores_premio(
            driver, self.locators["cinco_acertos"], self.locators["cinco_acertos2"]
        )
        qtd_4, premio_4 = self.coletar_ganhadores_premio(
            driver, self.locators["quatro_acertos"], self.locators["quatro_acertos2"]
        )
        return (
            nr_sorteio_atual,
            virada,
            data_sorteio,
            dezenas,
            local_do_sorteio,
            qtd_6,
            premio_6,
            qtd_5,
            premio_5,
            qtd_4,
            premio_4,
        )

    def inserir_no_db(self, dicionario):
        """
        Insere os dados coletados no banco de dados SQLite.

        :param dicionario: Um dicionário contendo os dados a serem inseridos no banco de dados.
        """
        engine = create_engine(f"sqlite:///{config.caminho_db}", future=True)
        repository = DbSorteios(engine)
        repository.create(dicionario)

    def clicar_no_proximo(self, driver):
        """
        Clica no botão "Próximo" para acessar o próximo sorteio.

        :param driver: Instância do driver do Selenium.
        """
        for i in range (10):
            try:
                self.find_element(driver, self.locators["btn_proximo"]).click()
                break
            except ElementClickInterceptedException:
                if i == 9:
                    raise
                sleep(0.5)

    def scrapping(self, driver, sorteio_mais_recente, nr_sorteio_atual):
        """
        Coleta dados dos sorteios e insere no banco de dados.

        :param driver: Instância do driver do Selenium.
        :param sorteio_mais_recente: O número do sorteio mais recente.
        :param sorteio_inicial: O número do sorteio inicial a ser coletado.
        """
        while nr_sorteio_atual <= sorteio_mais_recente:
            for i in range(10):  # tenta 10x caso encontre algum erro
                try:
                    (
                        nr_sorteio_atual,
                        virada,
                        data_sorteio,
                        dezenas,
                        local_do_sorteio,
                        qtd_6,
                        premio_6,
                        qtd_5,
                        premio_5,
                        qtd_4,
                        premio_4,
                    ) = self.coletar_valores(driver=driver)
                    break
                except (
                    NoSuchElementException,
                    StaleElementReferenceException,
                    TimeoutException,
                ):
                    if i == 9:
                        raise
                    continue

            try:
                self.inserir_no_db(
                    {
                        "nr_sorteio": nr_sorteio_atual,
                        "mega_da_virada": virada,
                        "data_sorteio": data_sorteio,
                        "dezenas": dezenas,
                        "local_do_sorteio": local_do_sorteio,
                        "ganhadores_seis_dezenas": qtd_6,
                        "premio_seis_dezenas": premio_6,
                        "ganhadores_cinco_dezenas": qtd_5,
                        "premio_cinco_dezenas": premio_5,
                        "ganhadores_quatro_dezenas": qtd_4,
                        "premio_quatro_dezenas": premio_4,
                    }
                )
            except IntegrityError:
                pass

            if nr_sorteio_atual == sorteio_mais_recente:
                break

            self.clicar_no_proximo(driver)

    def fechar_navegador(self, driver):
        """
        Fecha o navegador Chrome.

        :param driver: Instância do driver do Selenium.
        """
        driver.quit()

    def coletar_dados(self):
        """
        Orquestra o processo de coleta de dados dos sorteios da Loteria Caixa.
        """
        driver = self.abrir_navegador()
        self.acessar_site_loterias_caixa(driver)
        mais_recente = self.coletar_nr_sorteio(driver)
        ultimo_sorteio_db = self.coletar_ultimo_sorteio_db()
        sorteio_a_coletar = ultimo_sorteio_db + 1
        if sorteio_a_coletar != mais_recente:
            self.navegar_para_sorteio(driver, sorteio_a_coletar)
        self.scrapping(driver, mais_recente, sorteio_a_coletar)
        self.fechar_navegador(driver)
