import sys
import os
import threading  # Adicionado para permitir a execução de gravação em uma thread separada
import numpy as np
import sounddevice as sd
import soundfile as sf
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog, QMessageBox

# Variáveis globais
is_recording = False
is_paused = False
audio_data = []
audio_filename = "1.wav"
output_directory = "recordings"

class AudioRecorder(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Configurações da janela principal
        self.setWindowTitle("Gravador de Áudio")
        self.setGeometry(100, 100, 300, 200)

        # Layout
        layout = QVBoxLayout()

        # Botões
        self.start_button = QPushButton("Gravar")
        self.start_button.clicked.connect(self.start_recording)
        layout.addWidget(self.start_button)

        self.pause_button = QPushButton("Pausar")
        self.pause_button.clicked.connect(self.pause_recording)
        layout.addWidget(self.pause_button)

        self.stop_button = QPushButton("Parar")
        self.stop_button.clicked.connect(self.stop_recording)
        layout.addWidget(self.stop_button)

        self.choose_directory_button = QPushButton("Escolher Pasta")
        self.choose_directory_button.clicked.connect(self.choose_directory)
        layout.addWidget(self.choose_directory_button)

        self.setLayout(layout)

    def choose_directory(self):
        global output_directory
        directory = QFileDialog.getExistingDirectory(self, "Escolher Pasta")
        if directory:
            output_directory = directory
            QMessageBox.information(self, "Informação", f"Pasta de gravação definida para:\n{output_directory}")

    def record_audio(self):
        global is_recording, is_paused, audio_data, audio_filename

        # Verifica se o diretório de saída existe, caso contrário, cria-o
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        # Gera um nome de arquivo único
        file_index = 1
        while os.path.exists(f"{output_directory}/{file_index}.wav"):
            file_index += 1
        audio_filename = f"{output_directory}/{file_index}.wav"

        samplerate = 44100
        channels = 2

        def callback(indata, frames, time, status):
            if not is_paused:
                audio_data.append(indata.copy())

        # Inicia a gravação de áudio
        with sd.InputStream(samplerate=samplerate, channels=channels, callback=callback):
            while is_recording:
                sd.sleep(1000)  # Aguarda 1 segundo

        # Salva o arquivo de áudio ao parar a gravação
        if audio_data:
            audio_array = np.concatenate(audio_data, axis=0)
            sf.write(audio_filename, audio_array, samplerate)
            QMessageBox.information(self, "Informação", f"Gravação salva como {audio_filename}")

    def start_recording(self):
        global is_recording, is_paused, audio_data
        if not is_recording:
            is_recording = True
            is_paused = False
            audio_data = []
            self.record_thread = threading.Thread(target=self.record_audio)
            self.record_thread.start()
            QMessageBox.information(self, "Informação", "Gravação iniciada.")

    def pause_recording(self):
        global is_paused
        if is_recording:
            is_paused = not is_paused
            state = "pausada" if is_paused else "retomada"
            QMessageBox.information(self, "Informação", f"Gravação {state}.")

    def stop_recording(self):
        global is_recording, audio_filename
        if is_recording:
            is_recording = False
            if audio_data:
                duration = self.get_audio_duration(audio_filename)
                new_filename = f"{os.path.splitext(audio_filename)[0]}_{duration}.wav"
                if os.path.exists(audio_filename):
                    os.rename(audio_filename, new_filename)
                    QMessageBox.information(self, "Informação", f"Arquivo salvo como {new_filename}")
                else:
                    QMessageBox.warning(self, "Erro", "O arquivo de áudio não foi encontrado.")
            else:
                QMessageBox.information(self, "Informação", "Nenhum áudio gravado.")

    def get_audio_duration(self, filename):
        if os.path.exists(filename):
            with sf.SoundFile(filename) as f:
                return int(len(f) / f.samplerate)
        else:
            return 0

if __name__ == '__main__':
    app = QApplication(sys.argv)
    recorder = AudioRecorder()
    recorder.show()
    sys.exit(app.exec_())
