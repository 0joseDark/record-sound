import tkinter as tk
from tkinter import filedialog, messagebox
import sounddevice as sd
import wave
import threading
import vlc

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

        self.btn_play = tk.Button(master, text="Reproduzir", state=tk.DISABLED, command=self.play_audio)
        self.btn_play.pack(pady=10)

        self.btn_exit = tk.Button(master, text="Sair", command=self.exit_app)
        self.btn_exit.pack(pady=10)

        # Variáveis para gravação
        self.is_recording = False
        self.filename = "output.wav"
        self.directory = ""
        self.frames = []
        self.sample_rate = 44100  # Taxa de amostragem padrão
        self.channels = 2  # Áudio em estéreo (2 canais)

        # Variável para o dispositivo de áudio
        self.device = None
        self.stream = None

        # Media player VLC
        self.player = None

    def select_directory(self):
        self.directory = filedialog.askdirectory()
        messagebox.showinfo("Pasta Selecionada", f"Pasta selecionada: {self.directory}")

    def select_audio_device(self):
        devices = sd.query_devices()
        device_list = [f"{i}: {device['name']}" for i, device in enumerate(devices)]
        selected_device = tk.simpledialog.askinteger("Selecionar Dispositivo", "Selecione o ID do dispositivo de áudio:\n" + "\n".join(device_list))
        if selected_device is not None and 0 <= selected_device < len(devices):
            self.device = selected_device
            messagebox.showinfo("Dispositivo Selecionado", f"Dispositivo selecionado: {devices[selected_device]['name']}")
        else:
            messagebox.showwarning("Erro", "Dispositivo inválido selecionado!")

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

        try:
            if self.device is None:
                self.select_audio_device()

            self.recording_thread = threading.Thread(target=self.record)
            self.recording_thread.start()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao iniciar a gravação: {e}")
            self.btn_record.config(state=tk.NORMAL)
            self.btn_stop.config(state=tk.DISABLED)

    def record(self):
        try:
            with sd.InputStream(samplerate=self.sample_rate, channels=self.channels, device=self.device, callback=self.callback):
                while self.is_recording:
                    sd.sleep(1000)
        except Exception as e:
            self.is_recording = False
            messagebox.showerror("Erro", f"Erro durante a gravação: {e}")
            self.stop_recording()

    def callback(self, indata, frames, time, status):
        if status:
            print(status)
        self.frames.append(indata.copy())

    def stop_recording(self):
        if not self.is_recording:
            return

        self.is_recording = False
        self.btn_record.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)

        try:
            wf = wave.open(self.filename, 'wb')
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)
            wf.setframerate(self.sample_rate)
            wf.writeframes(b''.join(self.frames))
            wf.close()

            messagebox.showinfo("Gravação", f"Gravação salva como: {self.filename}")
            self.btn_play.config(state=tk.NORMAL)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar o arquivo: {e}")

    def play_audio(self):
        if not self.filename:
            messagebox.showwarning("Erro", "Nenhum arquivo de áudio disponível!")
            return

        try:
            self.player = vlc.MediaPlayer(self.filename)
            self.player.play()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao reproduzir o áudio: {e}")

    def exit_app(self):
        self.is_recording = False
        self.master.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioRecorderApp(root)
    root.mainloop()
