import tkinter as tk  # Interface gráfica
from tkinter import filedialog, messagebox  # Diálogo de seleção de arquivos e caixas de mensagem
import pyaudio  # Gravação de áudio
import wave  # Manipulação de arquivos de áudio .wav
import threading  # Para gravar em uma thread separada da interface

class AudioRecorderApp:
    def __init__(self, master):
        # Inicialização da interface
        self.master = master
        self.master.title("Gravador de Áudio")
        self.master.geometry("300x200")
        
        # Menu para selecionar pasta e sair
        menu = tk.Menu(master)
        master.config(menu=menu)
        
        file_menu = tk.Menu(menu)
        menu.add_cascade(label="Arquivo", menu=file_menu)
        file_menu.add_command(label="Selecionar Pasta", command=self.select_directory)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.exit_app)

        # Botões para controlar a gravação
        self.btn_record = tk.Button(master, text="Gravar", command=self.start_recording)
        self.btn_record.pack(pady=10)
        
        self.btn_stop = tk.Button(master, text="Parar", state=tk.DISABLED, command=self.stop_recording)
        self.btn_stop.pack(pady=10)
        
        self.btn_exit = tk.Button(master, text="Sair", command=self.exit_app)
        self.btn_exit.pack(pady=10)
        
        # Variáveis de controle para gravação
        self.is_recording = False  # Para controlar quando a gravação está em andamento
        self.filename = "output.wav"  # Nome padrão do arquivo
        self.directory = ""  # Diretório para salvar o arquivo
        self.frames = []  # Para armazenar os frames de áudio
        
        # Inicialização do PyAudio
        self.audio = pyaudio.PyAudio()
        self.stream = None  # O stream de áudio será inicializado quando a gravação começar
        
    def select_directory(self):
        # Função para selecionar o diretório onde o arquivo será salvo
        self.directory = filedialog.askdirectory()
        messagebox.showinfo("Pasta Selecionada", f"Pasta selecionada: {self.directory}")
    
    def start_recording(self):
        # Função chamada ao clicar em "Gravar"
        if not self.directory:
            messagebox.showwarning("Erro", "Selecione uma pasta primeiro!")
            return
        
        self.btn_record.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        
        # Diálogo para escolher o nome do arquivo .wav
        self.filename = filedialog.asksaveasfilename(initialdir=self.directory, 
                                                     title="Salvar como", 
                                                     defaultextension=".wav", 
                                                     filetypes=(("wav files", "*.wav"), ("all files", "*.*")))
        
        self.is_recording = True
        self.frames = []  # Limpa frames anteriores
        
        # Configuração de stream de áudio: 16 bits, mono, 44100 Hz
        self.stream = self.audio.open(format=pyaudio.paInt16,
                                      channels=1,
                                      rate=44100,
                                      input=True,
                                      frames_per_buffer=1024)
        
        # Inicia a gravação em uma thread separada
        self.recording_thread = threading.Thread(target=self.record)
        self.recording_thread.start()
    
    def record(self):
        # Função para capturar os dados do microfone enquanto está gravando
        while self.is_recording:
            data = self.stream.read(1024)
            self.frames.append(data)
    
    def stop_recording(self):
        # Função para parar a gravação
        self.is_recording = False
        self.btn_record.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        
        # Fecha o stream de áudio
        self.stream.stop_stream()
        self.stream.close()
        
        # Salva o áudio gravado como arquivo .wav
        wf = wave.open(self.filename, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(44100)
        wf.writeframes(b''.join(self.frames))
        wf.close()
        
        messagebox.showinfo("Gravação", f"Gravação salva como: {self.filename}")
    
    def exit_app(self):
        # Função para sair do aplicativo
        if self.is_recording:
            self.is_recording = False
            self.stream.stop_stream()
            self.stream.close()
        self.audio.terminate()  # Encerra o PyAudio
        self.master.quit()  # Fecha a interface

# Inicialização da interface
if __name__ == "__main__":
    root = tk.Tk()
    app = AudioRecorderApp(root)
    root.mainloop()
