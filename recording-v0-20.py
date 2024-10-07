import sounddevice as sd
import numpy as np
import wave
import tkinter as tk
from tkinter import filedialog, messagebox

class SoundRecorder:
    def __init__(self, master):
        self.master = master
        self.master.title("Gravador de Som")
        self.master.geometry("300x200")

        # Botões
        self.btn_record = tk.Button(master, text="Gravar", command=self.start_recording)
        self.btn_record.pack(pady=10)

        self.btn_stop = tk.Button(master, text="Parar", state=tk.DISABLED, command=self.stop_recording)
        self.btn_stop.pack(pady=10)

        self.btn_exit = tk.Button(master, text="Sair", command=self.exit_app)
        self.btn_exit.pack(pady=10)

        # Configuração de gravação
        self.fs = 44100  # Taxa de amostragem (samples per second)
        self.duration = 10  # Duração da gravação em segundos
        self.channels = 2  # Estéreo
        self.recording = False
        self.audio_data = None

    def start_recording(self):
        self.btn_record.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self.recording = True

        # Gravação de áudio
        self.audio_data = sd.rec(int(self.duration * self.fs), samplerate=self.fs, channels=self.channels, dtype=np.int16)
        messagebox.showinfo("Gravando", f"Gravando por {self.duration} segundos.")
        sd.wait()  # Espera a gravação terminar

        self.save_audio()

    def save_audio(self):
        filename = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV files", "*.wav")])
        if filename:
            # Salvar o arquivo WAV
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)  # Tamanho de 2 bytes (16 bits)
                wf.setframerate(self.fs)
                wf.writeframes(self.audio_data.tobytes())

            messagebox.showinfo("Gravação Salva", f"Gravação salva como: {filename}")

        self.btn_record.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)

    def stop_recording(self):
        if self.recording:
            sd.stop()
            self.recording = False
            self.btn_record.config(state=tk.NORMAL)
            self.btn_stop.config(state=tk.DISABLED)
            messagebox.showinfo("Parado", "Gravação parada.")

    def exit_app(self):
        self.master.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = SoundRecorder(root)
    root.mainloop()
