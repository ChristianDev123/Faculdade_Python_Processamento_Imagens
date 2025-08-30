import FreeSimpleGUI as sg
import webbrowser
from PIL import Image, ExifTags
import io
import os
import requests
import numpy as np

class ProcessamentoImagem:
    def __init__(self):
        self.path_original_image = None
        self.original_image = None
        self.resized_image = None
        self.negative_image = None
        self.sepia_image = None
        self.layout_program = self.create_layout() 
        self.window = sg.Window('CP GIMP', self.layout_program, finalize=True, resizable=True)
        self.main()

    def url_download(self,url):
        try:
            r = requests.get(url, stream=True)
            if r.status_code == 200:
                self.original_image = Image.open(io.BytesIO(r.content))
                self.show_image()
            else:
                sg.popup("Falha ao baixar a imagem. Verifique a URL e tente novamente.")
        except Exception as e:
            sg.popup(f"Erro ao baixar a imagem: {str(e)}")

    def create_layout(self):
        return [
            [sg.Menu([
                ['Arquivo', ['Abrir', 'Abrir URL' ,'Salvar', 'Fechar']],
                ['Filtros',['Negativo','Sépia', 'Original']],
                ['EXIF', ['Mostrar dados da imagem', 'Mostrar dados de GPS']], 
                ['Sobre a image', ['Informacoes']], 
                ['Sobre', ['Desenvolvedor']]
            ])],
            [sg.Image(key='-IMAGE-', size=(800, 600))]
        ]

    def get_negative_image(self, bytes_image:io.BytesIO):
        img = Image.open(bytes_image)
        color_array_img = np.array(img)

        for i,row in enumerate(color_array_img):
            for j,col in enumerate(np.array(row)):
                r,g,b = col
                r = 255 - r
                g = 255 - g
                b = 255 - b
                color_array_img[i][j] = [r,g,b]

        return Image.fromarray(color_array_img)

    def get_sepia_image(self, bytes_image:io.BytesIO):
        img = Image.open(bytes_image)
        color_array_img = np.array(img)
        for i, row in enumerate(color_array_img):
            for j, col in enumerate(np.array(row)):
                r,g,b = col
                r = min(255, max(0, 150 + r)) 
                g = min(255, max(0, 100 + g))
                b = min(255, max(0, 50 + b))
                color_array_img[i][j] = [r,g,b]
        return Image.fromarray(color_array_img)

    def show_image(self):
        try:
            self.resized_img = self.resize_image(self.original_image)
            img_bytes = io.BytesIO()
            self.resized_img.save(img_bytes, format='PNG')
            self.negative_image = self.get_negative_image(img_bytes)
            self.sepia_image = self.get_sepia_image(img_bytes)
            self.window['-IMAGE-'].update(data=img_bytes.getvalue())
        except Exception as e:
            sg.popup(f"Erro ao exibir a imagem: {str(e)}")

    def resize_image(self,img:Image.Image):
        try:
            img = img.resize((800, 600), Image.Resampling.LANCZOS) 
            return img
        except Exception as e:
            sg.popup(f"Erro ao redimensionar a imagem: {str(e)}")

    def open_image(self,filename):
        try:
            self.path_original_image = filename
            self.original_image = Image.open(filename)    
            self.show_image()
        except Exception as e:
            sg.popup(f"Erro ao abrir a imagem: {str(e)}")

    def save_image(self,filename):
        try:
            if self.original_image:
                with open(filename, 'wb') as file:
                    self.original_image.save(file)
            else:
                sg.popup("Nenhuma imagem aberta.")
        except Exception as e:
            sg.popup(f"Erro ao salvar a imagem: {str(e)}")

    def info_image(self):
        try:
            if self.original_image:
                largura, altura = self.original_image.size
                formato = self.original_image.format
                tamanho_bytes = os.path.getsize(self.path_original_image)
                tamanho_mb = tamanho_bytes / (1024 * 1024)
                sg.popup(f"Tamanho: {largura} x {altura}\nFormato: {formato}\nTamanho em MB: {tamanho_mb:.2f}")
            else:
                sg.popup("Nenhuma imagem aberta.")
        except Exception as e:
            sg.popup(f"Erro ao exibir informações da imagem: {str(e)}")

    def exif_data(self):
        try:
            if self.original_image:
                exif = self.original_image._getexif() 
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
            if self.original_image:
                exif = self.original_image._getexif()
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

    def handle_arquivo_dropdown_events(self,event):
        if event == 'Abrir':
            self.path_original_image = sg.popup_get_file('Selecionar image', file_types=(("Imagens", "*.png;*.jpg;*.jpeg;*.gif"),))
            if self.path_original_image:
                self.open_image(self.path_original_image)
        elif event == 'Abrir URL':
            url = sg.popup_get_text("Digite a url")
            if url:
                self.url_download(url)
        elif event == 'Salvar':
            if self.original_image:
                arquivo = sg.popup_get_file('Salvar image como', save_as=True, file_types=(("Imagens", "*.png;*.jpg;*.jpeg;*.gif"),))
                if arquivo:
                    self.save_image(arquivo)
        elif event == 'Informacoes':
            self.info_image()
        elif event == 'Mostrar dados da imagem':
            self.exif_data()
        elif event == 'Mostrar dados de GPS':
            self.gps_data()
        
    def handle_filters_dropdown_events(self, event):
        byte_img = io.BytesIO()
        if(self.original_image):
            if event == 'Negativo':
                self.negative_image.save(byte_img, format='PNG')
            elif event == 'Sépia':
                self.sepia_image.save(byte_img, format='PNG')
            elif event == 'Original':
                self.resized_image.save(byte_img, format='PNG')
            self.window['-IMAGE-'].update(data=byte_img.getvalue())

    def main(self):
        while True:
            event, values = self.window.read()
            if event in (sg.WINDOW_CLOSED, 'Fechar'):
                break
            elif event == 'Desenvolvedor':
                sg.popup('Desenvolvido por [Seu Nome] - BCC 6º Semestre')
            else:
                self.handle_arquivo_dropdown_events(event)
                self.handle_filters_dropdown_events(event)        

        self.window.close()

ProcessamentoImagem()