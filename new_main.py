import requests
from PIL import Image, ExifTags, ImageFilter, ImageDraw
import io
import FreeSimpleGUI as sg
import os
import webbrowser
import numpy as np

class GIMP:
    def __init__(self):
        self.current_image = None
        self.original_image = None
        self.image_path = None
        self.window = self.createWindow()
        self.main()

    def createWindow(self):
        layout = [
            [sg.Menu([
                    ['Arquivo', ['Abrir', 'Abrir URL', 'Salvar', 'Fechar']],
                    ['EXIF', ['Mostrar dados da imagem', 'Mostrar dados de GPS']],
                    ['Sobre a image', ['Informacoes']],
                    ['Sobre', ['Desenvolvedor']],
                    ['Imagem',[
                    'Girar',['Girar 90 graus à direita'],
                    'Filtros', ['Negativo','Sepia','Preto e Branco','4 bits', '8 bits',
                                'Blur','Contorno','Detalhe','Realce de bordas',
                                'Relevo','Detectar bordas','Nitidez','Suavizar',
                                'Filtro mínimo','Filtro máximo'],
                    'Histograma RGB'
                    ]],
                    ['Undo', ['Undo']]
                ])],
            [sg.Image(key='-IMAGE-', size=(800, 600))],
        ]
        return sg.Window('GIMP', layout, finalize=True, resizable=True)
    
    def url_download(self, url):
        try:
            r = requests.get(url, stream=True)
            if r.status_code == 200:
                self.current_image = Image.open(io.BytesIO(r.content))
                self.show_image()
            else:
                sg.popup("Falha ao baixar a imagem. Verifique a URL e tente novamente.")
        except Exception as e:
            sg.popup(f"Erro ao baixar a imagem: {str(e)}")
    
    def show_image(self):
        try:
            resized_img = self.resize_image(self.current_image)
            img_bytes = io.BytesIO()
            resized_img.save(img_bytes, format='PNG')
            self.window['-IMAGE-'].update(data=img_bytes.getvalue())
        except Exception as e:
            sg.popup(f"Erro ao exibir a imagem: {str(e)}")
    
    def resize_image(self, img):
        try:
            img = img.resize((800, 600), Image.Resampling.LANCZOS)
            return img
        except Exception as e:
            sg.popup(f"Erro ao redimensionar a imagem: {str(e)}")
    
    def open_image(self, filename):
        try:
            self.image_path = filename
            self.current_image = Image.open(filename)    
            self.show_image()
        except Exception as e:
            sg.popup(f"Erro ao abrir a imagem: {str(e)}")

    def save_image(self, filename):
        try:
            if self.current_image:
                with open(filename, 'wb') as file:
                    self.current_image.save(file)
            else:
                sg.popup("Nenhuma imagem aberta.")
        except Exception as e:
            sg.popup(f"Erro ao salvar a imagem: {str(e)}")
    
    def info_image(self):
        try:
            if self.current_image:
                largura, altura = self.current_image.size
                formato = self.current_image.format
                tamanho_bytes = os.path.getsize(self.image_path)
                tamanho_mb = tamanho_bytes / (1024 * 1024)
                sg.popup(f"Tamanho: {largura} x {altura}\nFormato: {formato}\nTamanho em MB: {tamanho_mb:.2f}")
            else:
                sg.popup("Nenhuma imagem aberta.")
        except Exception as e:
            sg.popup(f"Erro ao exibir informações da imagem: {str(e)}")

    def exif_data(self):
        try:
            if self.current_image:
                exif = self.current_image._getexif()
                if exif:
                    exif_data = ""
                    for tag, value in exif.items():
                        if tag in ExifTags.TAGS:
                            if tag == 37500 or tag == 34853: #Remove os dados customizados (37500) e de GPS (34853)
                                continue
                            tag_name = ExifTags.TAGS[tag]
                            exif_data += f"{tag_name}: {value}\n"
                    sg.popup("Dados EXIF:", exif_data)
                else:
                    sg.popup("A imagem não possui dados EXIF.")
            else:
                sg.popup("Nenhuma imagem aberta.")
        except Exception as e:
            sg.popup(f"Erro ao ler dados EXIF: {str(e)}")

    def gps_data(self):
        try:
            if self.current_image:
                exif = self.current_image._getexif()
                if exif:
                    gps_info = exif.get(34853)  #Tag para informações de GPS
                    print (gps_info[1], gps_info[3])
                    if gps_info:
                        latitude = int(gps_info[2][0]) + int(gps_info[2][1]) / 60 + int(gps_info[2][2]) / 3600
                        if gps_info[1] == 'S':  #Verifica se a direção é 'S' (sul)
                            latitude = -latitude
                        longitude = int(gps_info[4][0]) + int(gps_info[4][1]) / 60 + int(gps_info[4][2]) / 3600
                        if gps_info[3] == 'W':  #Verifica se a direção é 'W' (oeste)
                            longitude = -longitude
                        sg.popup(f"Latitude: {latitude:.6f}\nLongitude: {longitude:.6f}")
                        open_in_maps_url = f"https://www.google.com/maps?q={latitude},{longitude}"
                        if sg.popup_yes_no("Deseja abrir no Google Maps?") == "Yes":
                            webbrowser.open(open_in_maps_url)
                    else:
                        sg.popup("A imagem não possui informações de GPS.")
                else:
                    sg.popup("A imagem não possui dados EXIF.")
            else:
                sg.popup("Nenhuma imagem aberta.")
        except Exception as e:
            sg.popup(f"Erro ao ler dados de GPS: {str(e)}")

    def undo(self):
        self.current_image = self.original_image
        self.show_image()
    
    def sepia(self):
        self.original_image = self.current_image.copy()
        img_temp = self.current_image
        width, height = img_temp.size
        for x in range(width):
            for y in range(height):
                pixel_atual = img_temp.getpixel((x, y))
                #Maron 5 = 150, 100, 50
                r = min(255,pixel_atual[0] + 150)
                g = min(255,pixel_atual[1] + 100)
                b = min(255,pixel_atual[2] + 50)
                pixel_atual = (r,g,b)
                self.current_image.putpixel((x, y), pixel_atual)
        self.show_image()

    def inverte(self):
        self.original_image = self.current_image.copy()
        img_temp = self.current_image
        width, height = img_temp.size
        for x in range(width):
            for y in range(height):
                pixel_atual = img_temp.getpixel((x, y))
                pixel_atual = (((pixel_atual[0] - 255) * -1), ((pixel_atual[1] - 255) * -1), ((pixel_atual[2] - 255) * -1))
                self.current_image.putpixel((x, y), pixel_atual)
        self.show_image()

    def BlacknWhite(self):
        self.original_image = self.current_image.copy()
        img_temp = self.current_image
        width, height = img_temp.size
        for x in range(width):
            for y in range(height):
                pixel_atual = img_temp.getpixel((x, y))
                r = int(pixel_atual[0] * 0.3) 
                g = int(pixel_atual[1] * 0.59) 
                b = int(pixel_atual[2] * 0.11)
                total = r+g+b 
                pixel_atual = (total, total, total)
                self.current_image.putpixel((x, y), pixel_atual)
        self.show_image()

    def arquivo_dropdown(self, event):
        if event == 'Abrir':
            arquivo = sg.popup_get_file('Selecionar image', file_types=(("Imagens", "*.png;*.jpg;*.jpeg;*.gif"),))
            if arquivo:
                self.open_image(arquivo)
        elif event == 'Abrir URL':
            url = sg.popup_get_text("Digite a url")
            if url:
                self.url_download(url)
        elif event == 'Salvar':
            if self.current_image:
                arquivo = sg.popup_get_file('Salvar image como', save_as=True, file_types=(("Imagens", "*.png;*.jpg;*.jpeg;*.gif"),))
                if arquivo:
                    self.save_image(arquivo)

    def exif_dropdown(self, event):
        if event == 'Mostrar dados da imagem':
            self.exif_data()
        elif event == 'Mostrar dados de GPS':
            self.gps_data()

    def filtro_dropdown(self, event):
        if event == 'Negativo':
            self.inverte()
        elif event == 'Sepia':
            self.sepia()
        elif event == 'Preto e Branco':
            self.BlacknWhite()
        elif event == 'Undo':
            self.undo()
        elif event == '4 bits':
            self.apply_four_bits_filter()
        elif event == '8 bits':
            self.apply_eight_bits_filter()
        elif event == 'Blur':
            self.apply_blur_filter()

    def apply_four_bits_filter(self):
        try:
            if self.current_image:
                self.original_image = self.current_image.copy()
                self.current_image = self.current_image.convert("P",palette=Image.ADAPTIVE,colors=4)
                self.show_image()
            else:
                sg.popup("NADA AQUI IRMAO")
        except Exception as e:
                sg.popup(f"DEU ERRO MN{str(e)}")

    def apply_eight_bits_filter(self):
        try:
            if self.current_image:
                self.original_image = self.current_image.copy()
                self.current_image = self.current_image.convert("P",palette=Image.ADAPTIVE,colors=8)
                self.show_image()
            else:
                sg.popup("NADA AQUI IRMAO")
        except Exception as e:
                sg.popup(f"DEU ERRO MN{str(e)}")

    def apply_blur_filter(self):
        self.original_image = self.current_image.copy()
        radius = sg.popup_get_text("Digite a quantidade de Blur (0 a 20):", default_text="2")
        try:
            radius = int(radius)
            radius = max(0, min(20, radius)) 
        except ValueError:
            sg.popup("Por favor insira um valor válido")
            return
        try:
            if(self.current_image):
                self.current_image = self.current_image.filter(ImageFilter.GaussianBlur(radius)) 
                self.show_image()
        except Exception as e:
                sg.popup(f"DEU ERRO MN{str(e)}")

    def rotate(self, degree):
        self.original_image = self.current_image.copy()
        self.current_image = self.current_image.rotate(degree, expand=True)
        self.show_image()

    def image_girar_dropdown(self, event):
        if(event == 'Girar 90 graus à direita'):
            self.rotate(-90)

    def show_histogram_rgb(self):
        try:
            if not self.current_image:
                sg.popup("Nenhuma imagem aberta.")
                return

            #Garante que a imagem em RGB
            img_rgb = self.current_image.convert('RGB')
            hist = img_rgb.histogram()

            r = hist[0:256]
            g = hist[256:512]
            b = hist[512:768]

            #Normaliza para caber na altura do gráfico
            width, height = 256, 200
            margin = 10
            max_count = max(max(r), max(g), max(b), 1)

            hist_img = Image.new('RGB', (width, height), 'black')
            draw = ImageDraw.Draw(hist_img)

            for x in range(256):
                rh = int((r[x] / max_count) * (height - margin))
                gh = int((g[x] / max_count) * (height - margin))
                bh = int((b[x] / max_count) * (height - margin))

                #Desenha linhas verticais sobrepostas para cada canal
                draw.line([(x, height - 1), (x, height - 1 - rh)], fill=(255, 0, 0))
                draw.line([(x, height - 1), (x, height - 1 - gh)], fill=(0, 255, 0))
                draw.line([(x, height - 1), (x, height - 1 - bh)], fill=(0, 0, 255))

            #Amplia para melhor visualização mantendo aspecto
            scale_x, scale_y = 3, 2
            hist_big = hist_img.resize((width * scale_x, height * scale_y), Image.LANCZOS)

            img_bytes = io.BytesIO()
            hist_big.save(img_bytes, format='PNG')

            layout = [
                [sg.Image(data=img_bytes.getvalue(), key='-HIST-')],
                [sg.Button('Fechar')]
            ]
            win_hist = sg.Window('Histograma RGB', layout, modal=True, finalize=True)
            while True:
                e, _ = win_hist.read()
                if e in (sg.WINDOW_CLOSED, 'Fechar'):
                    break
            win_hist.close()
        except Exception as e:
            sg.popup(f"Erro ao gerar histograma: {str(e)}")

    def main(self):
        while True:
            event, values = self.window.read()
            if event in (sg.WINDOW_CLOSED, 'Fechar'):
                break
            elif event == 'Informacoes':
                self.info_image()
            elif event == 'Desenvolvedor':
                sg.popup('Desenvolvido por [Seu Nome] - BCC 6º Semestre')
            elif event == 'Histograma RGB':
                self.show_histogram_rgb()
            self.arquivo_dropdown(event)
            self.exif_dropdown(event)
            self.filtro_dropdown(event)
            self.image_girar_dropdown(event)
        self.window.close()

GIMP()