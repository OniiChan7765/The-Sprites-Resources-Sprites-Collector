# --------------------------------------------------------------
# Sprite Download Program 2.0
# Created by OniiChan7765, ChatGPT 4
# Creation Date: June 18, 2023 (2023/21/12 update)
#
# Description: This program downloads sprites from games based on a URL provided by the user. The sprites are
# organized into categories and saved in corresponding folders.
#
# I don't know anything about Python programming, but together, ChatGPT and I managed to create this code.
# Tested on Python 3.8, Windows 7 64-bit.
# --------------------------------------------------------------
import requests
import os
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import ntpath
from urllib.parse import urljoin

def format_sprite_name(name):
    invalid_chars = ["/", "\\", ":", "*", "?", "\"", "<", ">", "|"]
    for char in invalid_chars:
        name = name.replace(char, "_")
    return name

def download_sprite(sprite, base_folder, pbar):
    sprite_name = format_sprite_name(sprite['name'])
    sprite_download_link = sprite['download_link']

    # Define o caminho e o nome do arquivo a ser baixado
    categoria_dir = os.path.join(base_folder, categoria)
    filename = f"{categoria_dir}/{sprite_name}.png"
    filepath = os.path.join(os.getcwd(), filename)

    # Obtém apenas o nome do arquivo sem o diretório
    file_name_only = ntpath.basename(filename)

    # Faz o download do sprite e salva no arquivo
    with open(filepath, "wb") as file:
        response = requests.get(sprite_download_link)
        file.write(response.content)

    # Atualiza a barra de progresso
    pbar.update(1)

    # Exibe o nome do arquivo sendo baixado
    print(f"Downloading: {file_name_only}", end="\r")

def is_file_in_use(file_path):
    while True:
        try:
            # Tenta abrir o arquivo em modo de leitura
            with open(file_path, 'rb'):
                return False  # Se bem-sucedido, o arquivo não está em uso
        except PermissionError:
            return True  # Se ocorrer uma exceção, o arquivo está em uso
        except Exception as e:
            print(f"Erro ao verificar se o arquivo está em uso: {e}")
            return True  # Assume que o arquivo está em uso em caso de erro

def verificar_e_renomear_zip(root_folder):
    for root, dirs, files in os.walk(root_folder):
        for file_name in files:
            file_path = os.path.join(root, file_name)

            # Verifica se o arquivo tem a extensão .png
            if file_name.lower().endswith('.png'):
                # Verifica se o arquivo está em uso
                while is_file_in_use(file_path):
                    print(f"O arquivo está em uso: {file_path}. Aguardando 1 segundo...")
                    time.sleep(1)

                # Verifica se o conteúdo do arquivo parece ser um arquivo ZIP
                with open(file_path, 'rb') as file:
                    signature = file.read(2)

                # Fecha explicitamente o arquivo
                file.close()

                # A assinatura de um arquivo ZIP é 'PK'
                if signature == b'PK':
                    # Renomeia o arquivo para .zip
                    novo_nome = os.path.splitext(file_name)[0] + '.zip'
                    novo_caminho = os.path.join(root, novo_nome)

                    os.rename(file_path, novo_caminho)
                    print(f"Arquivo renomeado: {file_name} -> {novo_nome}")

while True:
    # Solicita a URL do site ao usuário
    url = input("Enter the URL of the website to download the sprites (or 'q' to quit): ")

    if url == 'q':
        break

    # Realiza a requisição HTTP e obtém o conteúdo da página
    response = requests.get(url)
    content = response.content

    # Cria um objeto BeautifulSoup para analisar o conteúdo HTML
    soup = BeautifulSoup(content, "html.parser")

    # Obtém o nome do jogo a partir do título da página
    game_title = soup.title.string

    # Remove as 24 últimas caracteres do nome do jogo
    game_title = game_title[:-24]

    # Remove caracteres inválidos do nome do jogo para criar o nome da pasta
    game_title = format_sprite_name(game_title)

    # Cria a pasta base com o nome do jogo
    base_folder = os.path.join(os.getcwd(), game_title)
    os.makedirs(base_folder, exist_ok=True)

    # Encontra todos os links da página
    links = soup.find_all("a")

    # Lista para armazenar os links dos sprites
    sprite_links = []

    # Filtra os links que contêm "/sheet/" na URL
    for link in links:
        if "/sheet/" in link.get("href", ""):
            sprite_links.append(link["href"])

    # Verifica se foram encontrados links de sprites
    if len(sprite_links) > 0:
        print("Sprites found:")

        # Dicionário para armazenar as categorias e sprites
        categorias = {}

        # Itera sobre os links encontrados e extrai as informações
        for index, link in enumerate(sprite_links, start=1):
            sprite_url = urljoin(url, link)
            sprite_id = link.split("/")[-2]  # Extrai o ID do sprite da URL
            download_link = f"https://www.spriters-resource.com/download/{sprite_id}/"

            # Realiza uma nova requisição para a página do sprite
            sprite_response = requests.get(sprite_url)
            sprite_content = sprite_response.content
            sprite_soup = BeautifulSoup(sprite_content, "html.parser")

            # Extrai as informações de "Game" e "Section" do sprite
            game_info = sprite_soup.find("td", string="Game").find_next("a")
            section_info = sprite_soup.find("td", string="Section").find_next("div").get('title')

            # Verifica se existe uma categoria para o sprite
            if section_info not in categorias:
                categorias[section_info] = []

            # Adiciona o sprite à categoria correspondente
            categorias[section_info].append({
                "name": sprite_soup.find("div", style="width: calc(100% - 50px); float: left; clear: left; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; padding-bottom: 1px;").get('title'),
                "download_link": download_link
            })

            # Mostra o processo de busca de links
            print(f"Progresso: {index}/{len(sprite_links)}", end="\r")

        print("\n")
        print("Starting sprite downloads...")

        # Total de sprites para download
        total_sprites = sum(len(sprites) for sprites in categorias.values())

        # Cria a barra de progresso
        with tqdm(total=total_sprites) as pbar:
            # Itera sobre as categorias e salva os sprites
            for categoria, sprites in categorias.items():
                categoria_dir = os.path.join(base_folder, categoria)
                os.makedirs(categoria_dir, exist_ok=True)

                print(f"\nCategoria: {categoria}")
                print("Sprites:")

                # Inicia o download de cada sprite em uma thread separada
                with ThreadPoolExecutor(max_workers=8) as executor:
                    for sprite in sprites:
                        executor.submit(download_sprite, sprite, base_folder, pbar)

        print("\nDownload completed!")

        # Verifica e renomeia arquivos ZIP na pasta criada
        verificar_e_renomear_zip(base_folder)
    else:
        print("No sprites were found on the page.")
