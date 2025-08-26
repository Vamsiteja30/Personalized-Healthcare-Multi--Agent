from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import pyttsx3
import os
import tempfile
from pathlib import Path

router = APIRouter()

class VoiceRequest(BaseModel):
    text: str
    user_id: int = 1

@router.post("/generate-greeting")
async def generate_voice_greeting(request: VoiceRequest):
    """Generate voice greeting for user"""
    try:
        # Initialize text-to-speech engine
        engine = pyttsx3.init()
        
        # Configure voice properties
        engine.setProperty('rate', 150)  # Speed of speech
        engine.setProperty('volume', 0.9)  # Volume level
        
        # Get available voices and set a pleasant one
        voices = engine.getProperty('voices')
        if voices:
            # Try to find a female voice for better greeting experience
            for voice in voices:
                if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                    engine.setProperty('voice', voice.id)
                    break
            else:
                # Fallback to first available voice
                engine.setProperty('voice', voices[0].id)
        
        # Create temporary file for audio
        temp_dir = Path("temp_audio")
        temp_dir.mkdir(exist_ok=True)
        
        audio_file = temp_dir / f"greeting_{request.user_id}.wav"
        
        # Generate speech
        engine.save_to_file(request.text, str(audio_file))
        engine.runAndWait()
        
        # Return the audio file
        if audio_file.exists():
            return FileResponse(
                path=str(audio_file),
                media_type="audio/wav",
                filename=f"greeting_{request.user_id}.wav"
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to generate audio file")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voice generation failed: {str(e)}")

@router.get("/greeting/{user_id}")
async def get_default_greeting(user_id: int):
    """Get default voice greeting for user"""
    greeting_text = f"Welcome to NOVA! Your personalized healthcare companion. Please enter your User ID to access your dashboard."
    
    request = VoiceRequest(text=greeting_text, user_id=user_id)
    return await generate_voice_greeting(request)
