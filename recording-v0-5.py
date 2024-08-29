import tkinter as tk  # Biblioteca para criar a interface gráfica
from tkinter import messagebox, filedialog  # Para caixas de diálogo
import sounddevice as sd  # Biblioteca para gravação de áudio
import soundfile as sf  # Biblioteca para salvar arquivos de áudio
import numpy as np  # Biblioteca para manipulação de arrays de áudio
import threading  # Biblioteca para executar tarefas em segundo plano
import os  # Biblioteca para operações com o sistema de arquivos

# Variáveis globais
is_recording = False  # Controla se a gravação está ativa
is_paused = False  # Controla se a gravação está pausada
audio_filename = "1"  # Nome base do arquivo de áudio
output_directory = "recordings"  # Diretório onde os arquivos serão salvos
audio_data = []  # Lista para armazenar os dados de áudio

# Função para selecionar a pasta de gravação
def choose_directory():
    global output_directory
    directory = filedialog.askdirectory()  # Abre um diálogo para selecionar o diretório
    if directory:  # Se o usuário selecionar um diretório
        output_directory = directory  # Atualiza o diretório de saída
        messagebox.showinfo("Informação", f"Pasta de gravação definida para:\n{output_directory}")

# Função para gravar áudio
def record_audio():
    global is_recording, is_paused, audio_data, audio_filename

    # Certifica-se de que o diretório de saída existe
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    file_index = 1
    # Gera um nome de arquivo único baseado em um índice
    while os.path.exists(f"{output_directory}/{file_index}.wav"):
        file_index += 1
    audio_filename = f"{output_directory}/{file_index}.wav"  # Define o nome do arquivo

    # Configurações de gravação
    samplerate = 44100  # Taxa de amostragem
    channels = 2  # Número de canais (estéreo)

    # Função de callback para capturar áudio continuamente
    def callback(indata, frames, time, status):
        if not is_paused:  # Se a gravação não estiver pausada
            audio_data.append(indata.copy())  # Adiciona os dados de áudio ao buffer

    # Inicia a gravação de áudio
    with sd.InputStream(samplerate=samplerate, channels=channels, callback=callback):
        while is_recording:  # Enquanto a gravação estiver ativa
            sd.sleep(1000)  # Aguarda 1 segundo

    # Salva o áudio ao parar a gravação
    if audio_data:  # Verifica se há dados para salvar
        audio_array = np.concatenate(audio_data, axis=0)  # Concatena todos os dados de áudio
        sf.write(audio_filename, audio_array, samplerate)  # Salva o arquivo de áudio
        messagebox.showinfo("Informação", f"Gravação salva como {audio_filename}")

# Função para iniciar a gravação
def start_recording():
    global is_recording, is_paused, audio_data
    if not is_recording:  # Se não estiver gravando
        is_recording = True
        is_paused = False
        audio_data = []  # Limpa o buffer de áudio
        threading.Thread(target=record_audio).start()  # Inicia a gravação em uma nova thread
        messagebox.showinfo("Informação", "Gravação iniciada.")

# Função para pausar a gravação
def pause_recording():
    global is_paused
    if is_recording:  # Só pode pausar se estiver gravando
        is_paused = not is_paused  # Alterna entre pausado e não pausado
        state = "pausada" if is_paused else "retomada"  # Define o estado
        messagebox.showinfo("Informação", f"Gravação {state}.")

# Função para parar a gravação
def stop_recording():
    global is_recording, audio_filename
    if is_recording:  # Só pode parar se estiver gravando
        is_recording = False
        if audio_data:  # Somente salvar se houver dados gravados
            duration = get_audio_duration(audio_filename)
            new_filename = f"{os.path.splitext(audio_filename)[0]}_{duration}.wav"
            if os.path.exists(audio_filename):  # Verifica se o arquivo foi criado
                os.rename(audio_filename, new_filename)  # Renomeia o arquivo com a duração
                messagebox.showinfo("Informação", f"Arquivo salvo como {new_filename}")
            else:
                messagebox.showerror("Erro", "O arquivo de áudio não foi encontrado.")
        else:
            messagebox.showinfo("Informação", "Nenhum áudio gravado.")

# Função para obter a duração do áudio
def get_audio_duration(filename):
    if os.path.exists(filename):  # Verifica se o arquivo existe
        with sf.SoundFile(filename) as f:
            return int(len(f) / f.samplerate)  # Calcula a duração em segundos
    else:
        return 0  # Retorna 0 se o arquivo não existir

# Função para fechar a aplicação
def close_application():
    stop_recording()  # Para a gravação ao fechar a aplicação
    root.destroy()  # Fecha a janela principal

# Configura a janela principal
root = tk.Tk()
root.title("Gravador de Áudio")
root.geometry("300x200")

# Menu para selecionar o diretório
menu = tk.Menu(root)
root.config(menu=menu)
file_menu = tk.Menu(menu)
menu.add_cascade(label="Opções", menu=file_menu)
file_menu.add_command(label="Escolher Pasta", command=choose_directory)

# Botões de controle
btn_start = tk.Button(root, text="Gravar", command=start_recording)
btn_start.pack(pady=5)

btn_pause = tk.Button(root, text="Pausar", command=pause_recording)
btn_pause.pack(pady=5)

btn_stop = tk.Button(root, text="Sair", command=close_application)
btn_stop.pack(pady=5)

# Inicia o loop da aplicação
root.mainloop()
