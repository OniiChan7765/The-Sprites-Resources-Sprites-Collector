import tkinter as tk
import requests
import os
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from tkinter import filedialog
from tkinter import messagebox
from tqdm import tqdm

# Função para iniciar o download dos sprites
def start_download():
    url = url_entry.get()
    if not url:
        messagebox.showwarning("Warning", "Please enter a valid URL")
        return

    response = requests.get(url)
    if response.status_code != 200:
        messagebox.showerror("Error", "Failed to fetch website content")
        return

    content = response.content

    soup = BeautifulSoup(content, "html.parser")

    game_title = soup.title.string
    game_title = game_title[:-24]

    invalid_chars = ["/", "\\", ":", "*", "?", "\"", "<", ">", "|"]
    for char in invalid_chars:
        game_title = game_title.replace(char, "")

    base_folder = filedialog.askdirectory(initialdir=os.getcwd(), title="Select Folder to Save Sprites")
    if not base_folder:
        return

    os.makedirs(base_folder, exist_ok=True)

    links = soup.find_all("a")

    sprite_links = []

    for link in links:
        if "/sheet/" in link["href"]:
            sprite_links.append(link["href"])

    if len(sprite_links) > 0:
        categorias = {}

        def download_sprite(sprite):
            sprite_name = sprite['name']
            sprite_name = sprite_name.replace("/", "_")
            sprite_download_link = sprite['download_link']

            categoria_dir = os.path.join(base_folder, categoria)
            filename = f"{categoria_dir}/{sprite_name}.png"
            filepath = os.path.join(os.getcwd(), filename)

            with open(filepath, "wb") as file:
                response = requests.get(sprite_download_link)
                file.write(response.content)

            pbar.update(1)

        for index, link in enumerate(sprite_links, start=1):
            sprite_url = "https://www.spriters-resource.com" + link
            sprite_id = link.split("/")[-2]
            download_link = f"https://www.spriters-resource.com/download/{sprite_id}/"

            sprite_response = requests.get(sprite_url)
            sprite_content = sprite_response.content
            sprite_soup = BeautifulSoup(sprite_content, "html.parser")

            game_info = sprite_soup.find("td", string="Game").find_next("a")
            section_info = sprite_soup.find("td", string="Section").find_next("div").get('title')

            if section_info not in categorias:
                categorias[section_info] = []

            categorias[section_info].append({
                "name": sprite_soup.find("div", style="width: calc(100% - 50px); float: left; clear: left; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; padding-bottom: 1px;").get('title'),
                "download_link": download_link
            })

            progress_label.config(text=f"Progress: {index}/{len(sprite_links)}")
            progress_label.update()

        total_sprites = sum(len(sprites) for sprites in categorias.values())

        with tqdm(total=total_sprites) as pbar:
            for categoria, sprites in categorias.items():
                categoria_dir = os.path.join(base_folder, categoria)
                os.makedirs(categoria_dir, exist_ok=True)

                category_label.config(text=f"Category: {categoria}")
                category_label.update()

                with ThreadPoolExecutor(max_workers=8) as executor:
                    for sprite in sprites:
                        executor.submit(download_sprite, sprite)

        messagebox.showinfo("Success", "Download completed!")
    else:
        messagebox.showwarning("Warning", "No sprites were found on the page.")

# Criação da janela principal
window = tk.Tk()
window.title("Sprite Download Program")

# Criação de um rótulo e campo de entrada para a URL
url_label = tk.Label(window, text="Enter the URL:")
url_label.pack()

url_entry = tk.Entry(window)
url_entry.pack()

# Criação de um botão para iniciar o download
download_button = tk.Button(window, text="Start Download", command=start_download)
download_button.pack()

# Criação de um rótulo para exibir o progresso
progress_label = tk.Label(window, text="Progress: 0/0")
progress_label.pack()

# Criação de um rótulo para exibir a categoria atual
category_label = tk.Label(window, text="Category: None")
category_label.pack()

# Loop principal da aplicação
window.mainloop()
