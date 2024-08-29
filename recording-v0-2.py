import tkinter as tk
from tkinter import messagebox, filedialog
import sounddevice as sd
import soundfile as sf
import numpy as np
import threading
import os

# Variáveis globais
is_recording = False
is_paused = False
audio_filename = "1"
output_directory = "recordings"
audio_data = []

# Função para selecionar a pasta de gravação
def choose_directory():
    global output_directory
    directory = filedialog.askdirectory()
    if directory:  # Verifica se o usuário selecionou um diretório
        output_directory = directory
        messagebox.showinfo("Informação", f"Pasta de gravação definida para:\n{output_directory}")

# Função para gravar áudio
def record_audio():
    global is_recording, is_paused, audio_data, audio_filename

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    file_index = 1
    while os.path.exists(f"{output_directory}/{file_index}.wav"):
        file_index += 1
    audio_filename = f"{output_directory}/{file_index}.wav"

    # Configurações de gravação
    samplerate = 44100  # Taxa de amostragem
    channels = 2  # Número de canais

    # Captura de áudio contínua
    def callback(indata, frames, time, status):
        if not is_paused:
            audio_data.append(indata.copy())

    # Iniciar gravação
    with sd.InputStream(samplerate=samplerate, channels=channels, callback=callback):
        while is_recording:
            sd.sleep(1000)

    # Salvar áudio ao parar
    if audio_data:  # Verifica se há dados para salvar
        audio_array = np.concatenate(audio_data, axis=0)
        sf.write(audio_filename, audio_array, samplerate)

# Função para iniciar gravação
def start_recording():
    global is_recording, is_paused, audio_data
    if not is_recording:
        is_recording = True
        is_paused = False
        audio_data = []  # Limpar buffer de áudio
        threading.Thread(target=record_audio).start()
        messagebox.showinfo("Informação", "Gravação iniciada.")

# Função para pausar gravação
def pause_recording():
    global is_paused
    if is_recording:
        is_paused = not is_paused
        state = "pausada" if is_paused else "retomada"
        messagebox.showinfo("Informação", f"Gravação {state}.")

# Função para parar gravação
def stop_recording():
    global is_recording, audio_filename
    if is_recording:
        is_recording = False
        if audio_data:  # Somente salvar se houver dados
            duration = get_audio_duration(audio_filename)
            new_filename = f"{os.path.splitext(audio_filename)[0]}_{duration}.wav"
            os.rename(audio_filename, new_filename)
            messagebox.showinfo("Informação", f"Arquivo salvo como {new_filename}")
        else:
            # Remover o arquivo vazio que pode ter sido criado
            if os.path.exists(audio_filename):
                os.remove(audio_filename)
            messagebox.showinfo("Informação", "Nenhum áudio gravado.")

# Função para obter a duração do áudio
def get_audio_duration(filename):
    if os.path.exists(filename):  # Verificar se o arquivo existe
        with sf.SoundFile(filename) as f:
            return int(len(f) / f.samplerate)
    else:
        return 0  # Retornar 0 se o arquivo não existir

# Função para fechar a aplicação
def close_application():
    stop_recording()
    root.destroy()

# Configurar janela principal
root = tk.Tk()
root.title("Gravador de Áudio")
root.geometry("300x200")

# Menu para selecionar diretório
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

# Iniciar o loop da aplicação
root.mainloop()
