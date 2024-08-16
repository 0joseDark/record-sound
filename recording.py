import tkinter as tk
from tkinter import messagebox
import pyaudio
import wave
import threading
import sounddevice as sd
import soundfile as sf
import simpleaudio as sa
import os

# Variáveis globais
is_recording = False
is_paused = False
audio_filename = "1"
output_directory = "recordings"

# Função para gravar áudio
def record_audio():
    global is_recording, is_paused, audio_filename

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Definir o nome do arquivo de saída
    file_index = 1
    while os.path.exists(f"{output_directory}/{file_index}.mp3"):
        file_index += 1
    audio_filename = f"{output_directory}/{file_index}.mp3"

    # Definições de gravação
    samplerate = 44100  # Taxa de amostragem
    channels = 2  # Número de canais
    dtype = 'int16'  # Tipo de dado

    # Configurar o PyAudio para gravação
    audio = pyaudio.PyAudio()

    # Função para gravar continuamente
    def callback(indata, frames, time, status):
        if is_paused:
            return
        with sf.SoundFile(audio_filename, mode='w', samplerate=samplerate, channels=channels, subtype='PCM_16') as file:
            file.write(indata)

    # Iniciar gravação com callback
    stream = sd.InputStream(samplerate=samplerate, channels=channels, callback=callback, dtype=dtype)
    with stream:
        while is_recording:
            sd.sleep(1000)

# Função para iniciar gravação
def start_recording():
    global is_recording, is_paused
    if not is_recording:
        is_recording = True
        is_paused = False
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
    global is_recording
    if is_recording:
        is_recording = False
        messagebox.showinfo("Informação", "Gravação parada.")
        duration = get_audio_duration(audio_filename)
        # Renomear arquivo para incluir duração
        new_filename = f"{os.path.splitext(audio_filename)[0]}_{duration}.mp3"
        os.rename(audio_filename, new_filename)
        messagebox.showinfo("Informação", f"Arquivo salvo como {new_filename}")

# Função para obter a duração do áudio
def get_audio_duration(filename):
    f = sf.SoundFile(filename)
    return int(len(f) / f.samplerate)

# Função para fechar a aplicação
def close_application():
    stop_recording()
    root.destroy()

# Configurar janela principal
root = tk.Tk()
root.title("Gravador de Áudio")
root.geometry("300x200")

# Botões de controle
btn_start = tk.Button(root, text="Gravar", command=start_recording)
btn_start.pack(pady=5)

btn_pause = tk.Button(root, text="Pausar", command=pause_recording)
btn_pause.pack(pady=5)

btn_stop = tk.Button(root, text="Sair", command=close_application)
btn_stop.pack(pady=5)

# Iniciar o loop da aplicação
root.mainloop()
