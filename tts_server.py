from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import torch
import torchaudio
import io
import os
import numpy as np
import uuid
from pathlib import Path

from TTS.utils.synthesizer import Synthesizer
from g2p import G2P

app = FastAPI()

# Path dasar (lokasi file ini berada, yaitu /app)
BASE_DIR = Path(__file__).resolve().parent

# Inisialisasi G2P
g2p = G2P()

# Inisialisasi Synthesizer
try:
    synthesizer = Synthesizer(
        tts_checkpoint=str(BASE_DIR / "checkpoint.pth"),
        tts_config_path=str(BASE_DIR / "config.json"),
        use_cuda=torch.cuda.is_available()
    )
    print("Model berhasil dimuat.")
except Exception as e:
    print("Gagal memuat model:", e)
    raise e

# Load daftar speaker
try:
    speakers_path = BASE_DIR / "speakers.pth"
    speakers = torch.load(speakers_path)
    print("Daftar speaker ditemukan:", speakers)
except Exception as e:
    speakers = []
    print("Gagal load speakers.pth:", e)

# Request model
class TTSRequest(BaseModel):
    text: str
    speaker: str | None = None

@app.post("/synthesize")
async def synthesize(req: TTSRequest):
    try:
        speaker = req.speaker
        if not speaker or speaker not in speakers:
            print(f"Speaker '{speaker}' tidak ditemukan, menggunakan default.")
            speaker = list(speakers.keys())[0] if isinstance(speakers, dict) else speakers[0]

        # Fonetik
        phonem_text = g2p(req.text)
        print(f"Teks: {req.text}")
        print(f"Fonetik: {phonem_text}")
        print(f"Speaker: {speaker}")

        # Proses TTS
        wav = synthesizer.tts(phonem_text, speaker_name=speaker, phoneme_input=False)

        print("Panjang wav:", len(wav))
        print("Amplitudo maksimum:", np.max(np.abs(wav)))

        # Simpan sebagai file sementara
        filename = f"tts_output_{uuid.uuid4().hex}.wav"
        wav_tensor = torch.tensor(wav).unsqueeze(0).float()
        torchaudio.save(filename, wav_tensor, 22050, format="wav")

        return FileResponse(path=filename, media_type="audio/wav", filename="tts_output.wav")

    except Exception as e:
        print("ERROR:", str(e))
        return JSONResponse(content={"error": str(e)}, status_code=500)
