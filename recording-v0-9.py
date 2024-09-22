import tkinter as tk
from tkinter import filedialog, messagebox
import pyaudio
import wave
import threading

class AudioRecorderApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Gravador de Áudio")
        self.master.geometry("300x200")
        
        # Menu
        menu = tk.Menu(master)
        master.config(menu=menu)
        
        file_menu = tk.Menu(menu)
        menu.add_cascade(label="Arquivo", menu=file_menu)
        file_menu.add_command(label="Selecionar Pasta", command=self.select_directory)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.exit_app)

        # Botões
        self.btn_record = tk.Button(master, text="Gravar", command=self.start_recording)
        self.btn_record.pack(pady=10)
        
        self.btn_stop = tk.Button(master, text="Parar", state=tk.DISABLED, command=self.stop_recording)
        self.btn_stop.pack(pady=10)
        
        self.btn_exit = tk.Button(master, text="Sair", command=self.exit_app)
        self.btn_exit.pack(pady=10)
        
        # Variáveis para gravação
        self.is_recording = False
        self.filename = "output.wav"
        self.directory = ""
        self.frames = []
        
        # Configuração de áudio
        self.audio = pyaudio.PyAudio()
        self.stream = None
        
    def select_directory(self):
        self.directory = filedialog.askdirectory()
        messagebox.showinfo("Pasta Selecionada", f"Pasta selecionada: {self.directory}")
    
    def start_recording(self):
        if not self.directory:
            messagebox.showwarning("Erro", "Selecione uma pasta primeiro!")
            return
        
        self.btn_record.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        
        self.filename = filedialog.asksaveasfilename(initialdir=self.directory, 
                                                     title="Salvar como", 
                                                     defaultextension=".wav", 
                                                     filetypes=(("wav files", "*.wav"), ("all files", "*.*")))
        
        self.is_recording = True
        self.frames = []
        
        # Configurações de stream de áudio
        self.stream = self.audio.open(format=pyaudio.paInt16,
                                      channels=1,
                                      rate=44100,
                                      input=True,
                                      frames_per_buffer=1024)
        
        # Thread para gravação
        self.recording_thread = threading.Thread(target=self.record)
        self.recording_thread.start()
    
    def record(self):
        while self.is_recording:
            data = self.stream.read(1024)
            self.frames.append(data)
    
    def stop_recording(self):
        self.is_recording = False
        self.btn_record.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        
        self.stream.stop_stream()
        self.stream.close()
        
        # Salva o arquivo de áudio
        wf = wave.open(self.filename, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(44100)
        wf.writeframes(b''.join(self.frames))
        wf.close()
        
        messagebox.showinfo("Gravação", f"Gravação salva como: {self.filename}")
    
    def exit_app(self):
        if self.is_recording:
            self.is_recording = False
            self.stream.stop_stream()
            self.stream.close()
        self.audio.terminate()
        self.master.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioRecorderApp(root)
    root.mainloop()
