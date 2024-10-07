import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox

class VLCRecorder:
    def __init__(self, master):
        self.master = master
        self.master.title("Gravador de Som VLC")
        self.master.geometry("300x200")

        # Botões
        self.btn_record = tk.Button(master, text="Gravar", command=self.start_recording)
        self.btn_record.pack(pady=10)

        self.btn_stop = tk.Button(master, text="Parar", state=tk.DISABLED, command=self.stop_recording)
        self.btn_stop.pack(pady=10)

        self.btn_exit = tk.Button(master, text="Sair", command=self.exit_app)
        self.btn_exit.pack(pady=10)

        self.process = None
        self.output_file = None

    def start_recording(self):
        self.btn_record.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)

        # Selecionar caminho para salvar o arquivo
        self.output_file = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV files", "*.wav")])
        if not self.output_file:
            messagebox.showwarning("Erro", "Nome do arquivo não selecionado!")
            self.btn_record.config(state=tk.NORMAL)
            self.btn_stop.config(state=tk.DISABLED)
            return

        # Comando VLC para capturar áudio do dispositivo padrão (microfone) e salvar em arquivo WAV
        vlc_command = [
            'vlc', 'dshow://',  # Entrada de áudio do sistema
            '--sout', f'#transcode{{acodec=s16l,channels=2,samplerate=44100}}:std{{access=file,mux=wav,dst="{self.output_file}"}}',
            '--run-time=10',  # Duração em segundos, ajuste conforme necessário
            '--stop-time=10',  # Duração em segundos, ajuste conforme necessário
            'vlc://quit'  # Comando para fechar o VLC automaticamente
        ]

        # Executar o comando VLC
        self.process = subprocess.Popen(vlc_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        messagebox.showinfo("Gravando", "Gravação iniciada. A gravação será automaticamente salva após 10 segundos.")
        
    def stop_recording(self):
        if self.process:
            self.process.terminate()  # Para o VLC
            self.process = None
            messagebox.showinfo("Gravação Parada", "Gravação finalizada e salva.")
        else:
            messagebox.showwarning("Erro", "Nenhuma gravação em andamento.")
        
        self.btn_record.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)

    def exit_app(self):
        if self.process:
            self.process.terminate()  # Garante que o processo seja terminado ao sair
        self.master.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = VLCRecorder(root)
    root.mainloop()
