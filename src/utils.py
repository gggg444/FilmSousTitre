import whisper
import subprocess
from pathlib import Path

def extract_audio(video_path, audio_path):
    """Extrait l'audio d'une vidéo en format WAV 16kHz mono"""
    command = [
        'ffmpeg',
        '-i', video_path,
        '-vn',
        '-acodec', 'pcm_s16le',
        '-ac', '1',
        '-ar', '16000',
        audio_path,
        '-y'
    ]
    subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def transcribe_video(video_path, model_name='small', output_format='txt'):
    """Transcrit les dialogues d'un fichier vidéo"""
    # Préparation des chemins
    video_path = Path(video_path)
    audio_path = video_path.with_suffix('.wav')
    
    # Extraction audio
    extract_audio(str(video_path), str(audio_path))
    
    # Chargement du modèle
    model = whisper.load_model(model_name)
    
    # Transcription
    result = model.transcribe(str(audio_path))
    
    # Formatage du résultat
    if output_format == 'srt':
        return format_to_srt(result['segments'])
    else:
        return result['text']

def format_to_srt(segments):
    """Formatte la transcription en SRT (sous-titres)"""
    srt_output = []
    for i, segment in enumerate(segments):
        start = format_time(segment['start'])
        end = format_time(segment['end'])
        srt_output.append(f"{i+1}\n{start} --> {end}\n{segment['text'].strip()}\n")
    return "\n".join(srt_output)

def format_time(seconds):
    """Convertit les secondes en format HH:MM:SS,mmm"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}".replace('.', ',')
