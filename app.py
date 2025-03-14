from flask import Flask, render_template, request, send_file
import yt_dlp
import os
from pathlib import Path

app = Flask(__name__)

FFMPEG_PATH = os.path.join(os.path.dirname(__file__), 'ffmpeg', 'ffmpeg.exe')

# Obtener la ruta de la carpeta de descargas del sistema
def obtener_carpeta_descargas():
    # Usar pathlib para obtener la ruta de la carpeta de descargas del sistema
    if os.name == 'nt':  # Para Windows
        carpeta_descargas = str(Path(os.getenv('USERPROFILE')) / 'Downloads')
    else:
        # Para sistemas basados en UNIX (como Linux o macOS)
        carpeta_descargas = str(Path.home() / 'Downloads')
    
    return carpeta_descargas

def descargar_audio(url):
    try:
        opciones = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(obtener_carpeta_descargas(), '%(title)s.%(ext)s'),
            'noplaylist': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'ffmpeg_location': FFMPEG_PATH,
        }

        with yt_dlp.YoutubeDL(opciones) as ydl:
            info = ydl.extract_info(url, download=True)
            ruta = ydl.prepare_filename(info).replace(".webm", ".mp3").replace(".m4a", ".mp3")
            print(f"Archivo descargado en: {ruta}")
            return ruta
    except yt_dlp.utils.DownloadError as e:
        print(f"Error al descargar el audio: {e}")
        return None
    except Exception as e:
        print(f"Error inesperado: {e}")
        return None

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form["url"]
        print(f"URL recibida: {url}")
        try:
            ruta = descargar_audio(url)
            if ruta:
                nombre_archivo = os.path.basename(ruta)
                return send_file(ruta, as_attachment=True, download_name=nombre_archivo, mimetype='audio/mpeg')
            else:
                return "❌ Error: No se pudo descargar el audio."
        except Exception as e:
            return f"❌ Error: {e}"
    return render_template("index.html")

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))  # Usa el puerto de Render o 5000 por defecto
    app.run(host='0.0.0.0', port=port, debug=False)  # debug=False para producción