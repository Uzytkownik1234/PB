from flask import Flask, render_template, request
import whisper
import time
import librosa
import re
import yt_dlp as youtube_dl

# Ładowanie modelu do transkrypcji
model = whisper.load_model("base")

app = Flask(__name__, static_url_path='/static')

def download_audio(url):
    # Ustawienia dla youtube_dl
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': '%(title)s.%(ext)s',
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        file_path = ydl.prepare_filename(ydl.extract_info(url, download=False))
        file_path = file_path.replace('.webm', '.mp3')
        file_path = file_path.replace('.m4a', '.mp3')

        return file_path

    except youtube_dl.utils.DownloadError as e:
        # Handle the specific DownloadError for an invalid URL
        print(f"Error downloading audio: {e}")
        return None  # or any other appropriate action

    except Exception as e:
        # Handle other exceptions
        print(f"Unexpected error: {e}")
        return None  # or any other appropriate action

def transcribe_audio(file_path):
    # Obliczanie długości pliku audio
    duration = librosa.get_duration(filename=file_path)

    # Transkrypcja pliku audio za pomocą modelu
    start = time.time()
    result = model.transcribe(file_path)
    end = time.time()
    seconds = end - start

    # Podział rezultatu na zdania
    sentences = re.split("([!?.])", result["text"])
    sentences = ["".join(i) for i in zip(sentences[0::2], sentences[1::2])]
    text = "\n\n".join(sentences)

    return duration, seconds, sentences, text

def save_transcription_to_file(file_path, text):
    # Zapisanie transkrypcji do pliku tekstowego
    name = "".join(file_path) + ".txt"
    with open(name, "w") as f:
        f.write(text)
    return name

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Pobranie URL z formularza
        url = request.form['url']

        # Pobranie audio z YouTube
        file_path = download_audio(url)

        if file_path is not None:
            # Transkrypcja pliku audio
            duration, seconds, sentences, text = transcribe_audio(file_path)
            
            # Zakrągl do dwóch mniejsc po przecinku
            duration = round(duration, 2)
            seconds = round(seconds, 2)

            # Zapisanie transkrypcji do pliku tekstowego
            name = save_transcription_to_file(file_path, text)

            # Przekazanie danych do szablonu HTML
            return render_template('index.html', duration=duration, seconds=seconds, sentences=sentences, name=name)

        else:
            # Obsługa błędu w przypadku nieudanego pobierania audio
            return render_template('error.html', message="Invalid URL")

    # Renderowanie strony głównej
    return render_template('index.html')

if __name__ == '__main__':
    # Uruchomienie aplikacji na wybranym hoście i porcie
    app.run(host='0.0.0.0', port=5000, debug=True)
