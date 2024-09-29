import os
import zipfile
import subprocess
import re

# --------------------------------------------------------------------
modelName= "Michi_3"

wavzipfile ="wavs.zip"
wavdir = "wavs/"

srtFile = "/kaggle/input/input-stabilazingboat/Stabilizing_de.srt"
wavFile = "/kaggle/input/input-stabilazingboat/Stabilizing_de.wav"
metaCSVFile = "/kaggle/working/metadata.csv"
#---------------------------------------------------------------------

%cd /kaggle/working


%rm -rf {wavdir}
%mkdir -p {wavdir}
%rm metadata.csv

def srt_to_txt(srt_file, output_file):
    with open(srt_file, 'r', encoding='utf-8') as f:
        srt_content = f.read()

    # Splitting the SRT file into blocks (number, time, and text)
    blocks = re.split(r'\n\n+', srt_content.strip())

    with open(output_file, 'w', encoding='utf-8') as f:
        for block in blocks:
            lines = block.split('\n')
            if len(lines) >= 3:
                # Get the subtitle number
                subtitle_number = lines[0].strip("\ufeff")
                print (f"{subtitle_number} len:{len(lines[0])}" )
                # Get the text of the subtitle, which is typically on the 3rd line and beyond
                subtitle_text = ' '.join(lines[2:]).strip()
                # Write to output in the format 1.wav|Text of the subtitle
                f.write(f'wavs/{subtitle_number}.wav|{subtitle_text}\n')

    print(f'Conversion complete! The result is saved in {output_file}')
    
def zip_wav_files(directory, zip_name):
    # Erstelle eine ZIP-Datei
    with zipfile.ZipFile(zip_name, 'w') as zipf:
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.wav'):
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, arcname=file)  # arcname sorgt dafür, dass nur der Dateiname und nicht der Pfad gespeichert wird


def srt_to_timecode(srt_time):
    return srt_time.replace(',', '.')

def split_audio(wav_file, srt_file):
    with open(srt_file, 'r') as f:
        content = f.read()
    
    # Regex, um Zeitstempel zu extrahieren
    pattern = re.compile(r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})')
    matches = pattern.findall(content)

    segment_num = 1
    for match in matches:
        start_time = match[1]
        end_time = match[2]
        
        start_time = srt_to_timecode(start_time)
        end_time = srt_to_timecode(end_time)

        output_file = f"wavs/{segment_num}.wav"
        print(f"\rExtracting {output_file}")
        # FFmpeg-Befehl zum Schneiden der WAV-Datei und Konvertierung in Mono
        command = [
            'ffmpeg', '-loglevel', 'quiet', '-i', wav_file, '-ss', start_time, '-to', end_time,
            '-ac', '1', '-ar', '44100', output_file
        ]
        subprocess.run(command)
        
        segment_num += 1


print(f"extract wavs from subtitlefile /kaggle/input/input-stabilazingboat/Stabilizing_de.srt")
split_audio(wavFile, srtFile)

print(f"creating zip File {wavzipfile}")
zip_wav_files(wavdir, wavzipfile)  # '.' bedeutet aktuelles Verzeichnis

print(f"Removing directory  {wavdir}")
%rm -rf {wavdir}

print(f"Creating metadata.csv File")
srt_to_txt(srtFile, metaCSVFile)
# ﻿1 1 
