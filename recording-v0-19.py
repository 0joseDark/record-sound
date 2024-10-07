import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import sounddevice as sd
import wave
import threading
import vlc  # Importando o módulo VLC

# Indicar o caminho completo para a libvlc.dll
libvlc_path = r'C:\Program Files\VideoLAN\VLC\libvlc.dll'

class AudioRecorderApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Gravador de Áudio")
        self.master.geometry("300x250")

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
        self.device = None
        self.stream = None
        self.player = None  # VLC Media Player

    def select_directory(self):
        self.directory = filedialog.askdirectory()
        messagebox.showinfo("Pasta Selecionada", f"Pasta selecionada: {self.directory}")

    def select_audio_device(self):
        try:
            devices = sd.query_devices()
            device_list = [f"{i}: {device['name']}" for i, device in enumerate(devices)]
            selected_device = simpledialog.askinteger("Selecionar Dispositivo", "Selecione o ID do dispositivo de áudio:\n" + "\n".join(device_list))
            
            if selected_device is not None and 0 <= selected_device < len(devices):
                self.device = selected_device
                messagebox.showinfo("Dispositivo Selecionado", f"Dispositivo selecionado: {devices[selected_device]['name']}")
            else:
                raise ValueError("Nenhum dispositivo válido selecionado!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao selecionar o dispositivo de áudio: {e}")
            self.device = None

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
        
        if not self.filename:
            messagebox.showwarning("Erro", "Nome do arquivo não selecionado!")
            self.btn_record.config(state=tk.NORMAL)
            self.btn_stop.config(state=tk.DISABLED)
            return

        self.is_recording = True
        self.frames = []

        try:
            if self.device is None:
                self.select_audio_device()
            
            if self.device is None:
                raise ValueError("Nenhum dispositivo de áudio selecionado.")

            # Iniciar gravação em uma thread separada
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
            messagebox.showerror("Erro durante a gravação", f"Erro: {e}")
            self.stop_recording()

    def callback(self, indata, frames, time, status):
        if status:
            print(f"Status: {status}", file=sys.stderr)
        self.frames.append(indata.copy())

    def stop_recording(self):
        if not self.is_recording:
            return

        self.is_recording = False
        self.btn_record.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)

        try:
            if self.frames:
                with wave.open(self.filename, 'wb') as wf:
                    wf.setnchannels(self.channels)
                    wf.setsampwidth(2)  # 16 bits
                    wf.setframerate(self.sample_rate)
                    wf.writeframes(b''.join(self.frames))

                messagebox.showinfo("Gravação", f"Gravação salva como: {self.filename}")
                self.btn_play.config(state=tk.NORMAL)
            else:
                messagebox.showwarning("Erro", "Nenhum dado de áudio foi gravado.")
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
    # Adicionar caminho para a DLL do VLC
    if sys.platform == "win32" and os.path.exists(libvlc_path):
        os.add_dll_directory(os.path.dirname(libvlc_path))
    else:
        print(f"Erro: Caminho para 'libvlc.dll' não encontrado. Verifique o caminho: {libvlc_path}")

    root = tk.Tk()
    app = AudioRecorderApp(root)
    root.mainloop()
