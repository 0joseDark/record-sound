import pyaudio
import wave
import tkinter as tk

# Variáveis globais
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "output.wav"
p = pyaudio.PyAudio()

# Função para iniciar a gravação
def start_recording():
    global stream
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    frames = []
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
    stream.stop_stream()
    stream.close()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

# Função para parar a gravação
def stop_recording():
    global stream
    stream.stop_stream()
    stream.close()

# Criar a janela principal
root = tk.Tk()
root.title("Gravador de Áudio")

# Botões
start_button = tk.Button(root, text="Iniciar Gravação", command=start_recording)
stop_button = tk.Button(root, text="Parar Gravação", command=stop_recording)
start_button.pack()
stop_button.pack()

# Menu
menubar = tk.Menu(root)
root.config(menu=menubar)
filemenu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="Arquivo", menu=filemenu)
filemenu.add_command(label="Sair", command=root.quit)

# Executar a aplicação
root.mainloop()