import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pyaudio
import wave
import numpy as np
import threading

class AudioMonitorApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Monitor de Áudio")
        self.master.geometry("400x250")
        
        # Inicializar PyAudio
        self.audio = pyaudio.PyAudio()
        
        # Configurações de áudio
        self.stream_input = None
        self.stream_output = None
        self.is_monitoring = False
        self.is_recording = False
        self.selected_input_device = None
        self.selected_output_device = None
        self.frames = []  # Para armazenar os dados de áudio gravados
        
        # Listar dispositivos
        self.devices = self.list_audio_devices()

        # Combobox para dispositivos de entrada
        self.input_label = tk.Label(master, text="Dispositivo de Entrada:")
        self.input_label.pack(pady=5)
        
        self.input_combobox = ttk.Combobox(master, values=self.devices['input'], state="readonly")
        self.input_combobox.pack(pady=5)
        
        # Combobox para dispositivos de saída
        self.output_label = tk.Label(master, text="Dispositivo de Saída:")
        self.output_label.pack(pady=5)
        
        self.output_combobox = ttk.Combobox(master, values=self.devices['output'], state="readonly")
        self.output_combobox.pack(pady=5)
        
        # Botão de Iniciar Monitoramento
        self.start_button = tk.Button(master, text="Iniciar Monitoramento", command=self.start_monitoring)
        self.start_button.pack(pady=10)
        
        # Botão de Parar Monitoramento
        self.stop_button = tk.Button(master, text="Parar Monitoramento", command=self.stop_monitoring)
        self.stop_button.pack(pady=5)
        self.stop_button.config(state=tk.DISABLED)
        
        # Botão de Gravar Áudio
        self.record_button = tk.Button(master, text="Iniciar Gravação", command=self.start_recording)
        self.record_button.pack(pady=5)
        self.record_button.config(state=tk.DISABLED)
        
        # Botão de Parar Gravação
        self.stop_record_button = tk.Button(master, text="Parar Gravação", command=self.stop_recording)
        self.stop_record_button.pack(pady=5)
        self.stop_record_button.config(state=tk.DISABLED)

    def list_audio_devices(self):
        devices = {'input': [], 'output': []}
        for i in range(self.audio.get_device_count()):
            device_info = self.audio.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                devices['input'].append(f"{device_info['index']}: {device_info['name']}")
            if device_info['maxOutputChannels'] > 0:
                devices['output'].append(f"{device_info['index']}: {device_info['name']}")
        return devices
    
    def start_monitoring(self):
        # Verificar seleção de dispositivos
        input_selection = self.input_combobox.get()
        output_selection = self.output_combobox.get()
        
        if not input_selection or not output_selection:
            messagebox.showwarning("Erro", "Selecione dispositivos de entrada e saída.")
            return
        
        self.selected_input_device = int(input_selection.split(":")[0])
        self.selected_output_device = int(output_selection.split(":")[0])
        
        # Configurar stream de entrada
        self.stream_input = self.audio.open(format=pyaudio.paInt16,
                                            channels=2,
                                            rate=44100,
                                            input=True,
                                            frames_per_buffer=1024,
                                            input_device_index=self.selected_input_device)

        # Configurar stream de saída
        self.stream_output = self.audio.open(format=pyaudio.paInt16,
                                             channels=2,
                                             rate=44100,
                                             output=True,
                                             frames_per_buffer=1024,
                                             output_device_index=self.selected_output_device)
        
        # Iniciar o monitoramento
        self.is_monitoring = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.record_button.config(state=tk.NORMAL)
        self.monitor_thread = threading.Thread(target=self.monitor_audio)
        self.monitor_thread.start()
    
    def monitor_audio(self):
        try:
            while self.is_monitoring:
                # Ler dados de áudio do dispositivo de entrada
                data = self.stream_input.read(1024)
                
                # Reproduzir os dados no dispositivo de saída
                self.stream_output.write(data)
                
                # Se estiver gravando, armazenar os dados
                if self.is_recording:
                    self.frames.append(data)
        except Exception as e:
            print(f"Erro durante monitoramento: {e}")
            self.stop_monitoring()
    
    def start_recording(self):
        # Iniciar gravação
        self.is_recording = True
        self.frames = []  # Limpar dados de gravações anteriores
        self.record_button.config(state=tk.DISABLED)
        self.stop_record_button.config(state=tk.NORMAL)
        messagebox.showinfo("Gravação", "Gravação iniciada.")

    def stop_recording(self):
        # Parar gravação
        self.is_recording = False
        self.record_button.config(state=tk.NORMAL)
        self.stop_record_button.config(state=tk.DISABLED)
        
        # Salvar arquivo de áudio
        file_path = filedialog.asksaveasfilename(defaultextension=".wav",
                                                 filetypes=[("WAV files", "*.wav")],
                                                 title="Salvar Gravação",
                                                 initialfile="gravacao.wav")
        if file_path:
            self.save_recording(file_path)
            messagebox.showinfo("Gravação", f"Gravação salva em: {file_path}")
    
    def save_recording(self, file_path):
        # Salvar os frames em um arquivo .wav
        wf = wave.open(file_path, 'wb')
        wf.setnchannels(2)
        wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(44100)
        wf.writeframes(b''.join(self.frames))
        wf.close()
    
    def stop_monitoring(self):
        self.is_monitoring = False
        if self.stream_input is not None:
            self.stream_input.stop_stream()
            self.stream_input.close()
        if self.stream_output is not None:
            self.stream_output.stop_stream()
            self.stream_output.close()
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.record_button.config(state=tk.DISABLED)
        self.stop_record_button.config(state=tk.DISABLED)
    
    def __del__(self):
        # Fechar PyAudio ao sair
        self.audio.terminate()

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioMonitorApp(root)
    root.mainloop()
