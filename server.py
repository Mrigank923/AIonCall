#!/usr/bin/env python3
"""
Exotel (Buffered) <-> Gemini Live API Bridge
============================================

Fixes "Noise/Silence" by enforcing Exotel's chunk size requirements:
1. Minimum Chunk: 3200 bytes
2. Alignment: Multiples of 320 bytes
3. Format: 16-bit PCM, 8kHz
"""

import asyncio
import websockets
import json
import logging
import os
import base64
import audioop
import ssl

# ================= CONFIGURATION =================
PORT = 5000
HOST = "0.0.0.0"
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
MODEL_NAME = "models/gemini-2.5-flash-native-audio-preview-12-2025"
VOICE_NAME = "Puck"

# Audio Configuration
EXOTEL_RATE = 8000
GEMINI_INPUT_RATE = 16000
GEMINI_OUTPUT_RATE = 24000 

# BUFFER SETTINGS (Crucial for Exotel)
# Requirement: Minimum 3.2k (3200 bytes)
MIN_CHUNK_SIZE = 3200 

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("BufferedBridge")

# ================= TRANSCODER =================
class AudioTranscoder:
    """Handles Resampling (24k <-> 8k)"""
    def __init__(self):
        self.inbound_state = None
        self.outbound_state = None

    def exotel_to_gemini(self, raw_bytes):
        """8k -> 16k"""
        try:
            pcm_16k, self.inbound_state = audioop.ratecv(
                raw_bytes, 2, 1, 
                EXOTEL_RATE, 
                GEMINI_INPUT_RATE, 
                self.inbound_state
            )
            return pcm_16k
        except Exception as e:
            logger.error(f"Inbound Transcode Error: {e}")
            return b''

    def gemini_to_exotel(self, pcm_bytes):
        """24k -> 8k"""
        try:
            pcm_8k, self.outbound_state = audioop.ratecv(
                pcm_bytes, 2, 1, 
                GEMINI_OUTPUT_RATE, 
                EXOTEL_RATE, 
                self.outbound_state
            )
            return pcm_8k
        except Exception as e:
            logger.error(f"Outbound Transcode Error: {e}")
            return b''

# ================= AUDIO BUFFER =================
class AudioBuffer:
    """
    Accumulates audio bytes and only releases them when
    they meet Exotel's minimum size requirement (3200 bytes).
    """
    def __init__(self):
        self.buffer = bytearray()

    def add_and_get_chunks(self, new_bytes):
        self.buffer.extend(new_bytes)
        chunks_to_send = []

        # While we have enough data (> 3200 bytes)
        while len(self.buffer) >= MIN_CHUNK_SIZE:
            # Take exactly 3200 bytes (or strict multiple)
            # This ensures we meet the "Minimum chunk size: 3.2k" rule
            chunk = self.buffer[:MIN_CHUNK_SIZE]
            
            # Remove from buffer
            self.buffer = self.buffer[MIN_CHUNK_SIZE:]
            
            # Encode to Base64
            chunks_to_send.append(base64.b64encode(chunk).decode('utf-8'))
            
        return chunks_to_send

    def clear(self):
        self.buffer = bytearray()

# ================= BRIDGE SESSION =================
class BridgeSession:
    def __init__(self, connection_id, exotel_ws):
        self.id = connection_id
        self.exotel_ws = exotel_ws
        self.gemini_ws = None
        self.stream_sid = None
        self.is_active = True
        self.transcoder = AudioTranscoder()
        self.outbound_buffer = AudioBuffer() # Buffer for sending to Exotel

    async def connect_gemini(self):
        uri = f"wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1beta.GenerativeService.BidiGenerateContent?key={GOOGLE_API_KEY}"
        try:
            ssl_ctx = ssl.create_default_context()
            self.gemini_ws = await websockets.connect(uri, ssl=ssl_ctx, ping_interval=None)
            logger.info(f"[{self.id}] Gemini Connected")
            
            # Setup
            await self.gemini_ws.send(json.dumps({
                "setup": {
                    "model": MODEL_NAME,
                    "generationConfig": {
                        "responseModalities": ["AUDIO"],
                        "speechConfig": {
                            "voiceConfig": {
                                "prebuiltVoiceConfig": {
                                    "voiceName": VOICE_NAME
                                }
                            }
                        }
                    }
                }
            }))
            
            # Initial Prompt
            await self.gemini_ws.send(json.dumps({
                 "clientContent": {
                     "turns": [{
                         "role": "user",
                         "parts": [{"text": "Hello. Please greet me briefly."}]
                     }],
                     "turnComplete": True
                 }
            }))
            return True
        except Exception as e:
            logger.error(f"[{self.id}] Gemini Connection Failed: {e}")
            return False

    async def exotel_listener(self):
        """Phone -> Gemini (No Minimum Size Required for Input)"""
        try:
            async for message in self.exotel_ws:
                if not self.is_active: break
                data = json.loads(message)
                event = data.get('event')

                if event == 'media':
                    payload = data['media']['payload']
                    if self.gemini_ws:
                        raw_in = base64.b64decode(payload)
                        pcm_16k = self.transcoder.exotel_to_gemini(raw_in)
                        
                        if pcm_16k:
                            # Send to Gemini immediately (Gemini handles small chunks fine)
                            b64_out = base64.b64encode(pcm_16k).decode('utf-8')
                            await self.gemini_ws.send(json.dumps({
                                "realtimeInput": {
                                    "mediaChunks": [{
                                        "mimeType": "audio/pcm;rate=16000",
                                        "data": b64_out
                                    }]
                                }
                            }))

                elif event == 'start':
                    self.stream_sid = data.get('start', {}).get('stream_sid')
                    logger.info(f"[{self.id}] Stream Started")
                elif event == 'stop':
                    logger.info(f"[{self.id}] Call Ended")
                    self.is_active = False
                    break
        except Exception as e:
            logger.error(f"[{self.id}] Exotel Read Error: {e}")
            self.is_active = False

    async def gemini_listener(self):
        """Gemini -> Phone (Buffered to 3.2k)"""
        try:
            async for message in self.gemini_ws:
                if not self.is_active: break
                response = json.loads(message)
                server_content = response.get('serverContent')
                
                if server_content:
                    # Handle Interruptions
                    if server_content.get('interrupted'):
                        logger.info(f"[{self.id}] Interrupted - Clearing Buffer")
                        self.outbound_buffer.clear()
                        await self.exotel_ws.send(json.dumps({
                            "event": "clear", "stream_sid": self.stream_sid
                        }))
                        self.transcoder.outbound_state = None
                    
                    # Handle Audio
                    model_turn = server_content.get('modelTurn')
                    if model_turn:
                        for part in model_turn.get('parts', []):
                            inline_data = part.get('inlineData')
                            if inline_data:
                                pcm_b64 = inline_data.get('data')
                                if pcm_b64:
                                    # 1. Decode & Resample
                                    raw_24k = base64.b64decode(pcm_b64)
                                    raw_8k = self.transcoder.gemini_to_exotel(raw_24k)
                                    
                                    # 2. Add to Buffer & Get valid chunks (3.2k size)
                                    chunks = self.outbound_buffer.add_and_get_chunks(raw_8k)
                                    
                                    # 3. Send valid chunks to Exotel
                                    for chunk_b64 in chunks:
                                        await self.exotel_ws.send(json.dumps({
                                            "event": "media",
                                            "stream_sid": self.stream_sid,
                                            "media": {"payload": chunk_b64}
                                        }))
                                        # Small sleep to prevent network flooding (optional but safe)
                                        await asyncio.sleep(0.001)

        except Exception as e:
            logger.error(f"[{self.id}] Gemini Read Error: {e}")
            self.is_active = False

    async def run(self):
        if await self.connect_gemini():
            t1 = asyncio.create_task(self.exotel_listener())
            t2 = asyncio.create_task(self.gemini_listener())
            await asyncio.wait([t1, t2], return_when=asyncio.FIRST_COMPLETED)
            self.is_active = False
            if self.gemini_ws: await self.gemini_ws.close()

# ================= SERVER START =================
async def handle_websocket(websocket, path):
    session = BridgeSession(f"conn_{id(websocket)}", websocket)
    await session.run()

async def main():
    logger.info(f"🚀 Buffered Bridge Running on {HOST}:{PORT}")
    logger.info(f"📦 Minimum Chunk Size: {MIN_CHUNK_SIZE} bytes")
    async with websockets.serve(handle_websocket, HOST, PORT, ping_interval=None):
        await asyncio.Future()

if __name__ == "__main__":
    if not GOOGLE_API_KEY:
        print("❌ Error: GOOGLE_API_KEY missing")
        exit(1)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
