# AIonCall - Exotel WebSocket to Gemini AI Bridge 🎙️

A sophisticated real-time voice integration system that bridges **Exotel's** communication platform with **Google's Gemini 2.5 Flash** AI model for intelligent audio processing, transcription, and live conversation monitoring.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [System Architecture](#system-architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Audio Processing Pipeline](#audio-processing-pipeline)
- [Dashboard Monitoring](#dashboard-monitoring)
- [Troubleshooting](#troubleshooting)
- [Performance Considerations](#performance-considerations)
- [Contributing](#contributing)

---

## 🎯 Overview

AIonCall is a WebSocket-based bridge that connects Exotel's phone call streaming with Google's Gemini AI. It enables:

- **Real-time audio streaming** from Exotel phone calls
- **AI-powered voice processing** using Gemini's native audio model
- **Live conversation analytics** with latency tracking
- **Interactive monitoring dashboard** with real-time statistics
- **Intelligent audio buffering** optimized for Exotel's requirements

### Use Cases:
- Customer support automation with AI
- Call transcription and analysis
- Real-time sentiment analysis during calls
- Voice-based chatbot integration
- Call quality monitoring and reporting

---

## ✨ Features

### Core Features
- ✅ **WebSocket Bridge**: Bidirectional audio streaming with Exotel
- ✅ **Native Audio Processing**: Direct audio input/output with Gemini AI
- ✅ **Multi-rate Audio Transcoding**: Convert between 8kHz, 16kHz, and 24kHz sample rates
- ✅ **Intelligent Buffering**: Meets Exotel's 3.2KB minimum chunk size requirement
- ✅ **Voice Configuration**: Customizable voice output (currently using "Puck")
- ✅ **Real-time Monitoring**: Live dashboard with Socket.IO updates
- ✅ **Latency Tracking**: Per-event latency measurement and analysis
- ✅ **Call History**: Persistent tracking of call sessions and events
- ✅ **Error Handling**: Comprehensive logging and error recovery

### Dashboard Features
- 📊 Real-time call statistics
- 📈 Latency metrics (first media, inter-event, end-to-end)
- 🔄 Active connection monitoring
- 📞 Call history with event details
- 🎯 Performance analytics
- 📱 Responsive UI with live updates

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Exotel Platform                         │
│              (Phone Calls & Audio Streaming)                │
└────────────────────────┬────────────────────────────────────┘
                         │ WebSocket (8kHz PCM)
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    AIonCall Server                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         WebSocket Server (server.py)                │  │
│  │  - Handles Exotel connections                       │  │
│  │  - Processes incoming audio streams                 │  │
│  │  - Manages bidirectional communication              │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │       Audio Transcoding Pipeline                    │  │
│  │  - 8kHz (Exotel) ← → 16kHz (Gemini Input)          │  │
│  │  - 24kHz (Gemini Output) ← → 8kHz (Exotel)         │  │
│  │  - AudioBuffer for Exotel chunk requirements        │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │       Flask Dashboard (dashboard.py)                │  │
│  │  - Real-time metrics via Socket.IO                  │  │
│  │  - Call session tracking                            │  │
│  │  - Latency analytics                                │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
      ┌──────────────────┴──────────────────┐
      │                                     │
      ▼ REST API                            ▼ gRPC (Native Audio)
┌──────────────────┐              ┌──────────────────────────┐
│  Monitoring      │              │   Google Gemini 2.5      │
│  Tools           │              │   Flash Native Audio     │
│  (Analytics)     │              │   (AI Processing)        │
└──────────────────┘              └──────────────────────────┘
```

---

## 🛠️ Tech Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Language** | Python | 3.8+ |
| **WebSocket** | websockets | ≥12.0 |
| **Web Framework** | Flask | ≥2.0.0 |
| **Real-time Updates** | Flask-SocketIO | ≥5.0.0 |
| **Async Runtime** | Eventlet | ≥0.33.0 |
| **AI API** | Google Generative AI | Latest |
| **Testing** | pytest | ≥7.0.0 |
| **HTTP Client** | requests | ≥2.28.0 |

---

## 📁 Project Structure

```
AIonCall/
│
├── server.py                 # Main WebSocket server & Gemini bridge
│   ├── AudioTranscoder       # Audio resampling (8k ↔ 16k ↔ 24k)
│   ├── AudioBuffer           # Chunk buffering for Exotel compliance
│   ├── GeminiClient          # Gemini AI integration
│   ├── ExotelHandler         # WebSocket connection management
│   └── main()                # Server startup & event loop
│
├── dashboard.py              # Flask dashboard with real-time monitoring
│   ├── Flask App             # REST endpoints
│   ├── Socket.IO             # WebSocket for real-time updates
│   ├── CallSession           # Call tracking & latency calculation
│   ├── Statistics            # Real-time metrics aggregation
│   └── Analytics             # Event & performance analysis
│
├── simple_server2.py         # Alternative/simplified server implementation
│
├── setup.sh                  # Automated setup script
│   ├── Python version check
│   ├── Virtual environment creation
│   ├── Pip upgrade
│   ├── Dependency installation
│   └── Environment validation
│
├── start.sh                  # Quick start script
│   ├── Virtual environment activation
│   ├── Port availability check
│   ├── Server process management
│   └── Log initialization
│
├── requirements.txt          # Python dependencies
│
├── .env                      # Environment variables (API keys)
│   └── GOOGLE_API_KEY       # Gemini API authentication
│
├── .gitignore                # Git ignore patterns
│   ├── venv/                 # Python virtual environment
│   ├── .env                  # Sensitive environment files
│   ├── logs/                 # Application logs
│   └── .python-version       # Python version marker
│
├── logs/                     # Application logs directory
│   └── voice_bot_echo.log   # Server logs
│
└── README.md                 # This file
```

---

## 📋 Prerequisites

### System Requirements
- **OS**: Linux, macOS, or Windows (with WSL)
- **Python**: 3.8 or higher
- **RAM**: Minimum 2GB (4GB recommended)
- **CPU**: 1+ cores (2+ recommended for high volume)
- **Network**: Stable internet connection for Gemini API access

### External Requirements
- **Exotel Account**: Active account with WebSocket enabled
- **Google Cloud Account**: Gemini API access enabled
- **API Keys**: Gemini API key for authentication

### Installation Tools
```bash
# Check Python installation
python3 --version

# Check pip
pip3 --version

# Verify git
git --version
```

---

## 🚀 Installation & Setup

### Quick Start (Automated)

1. **Clone or download the project:**
   ```bash
   cd AIonCall
   ```

2. **Run the setup script:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Configure environment variables** (see [Configuration](#configuration) section)

4. **Start the server:**
   ```bash
   chmod +x start.sh
   ./start.sh
   ```

### Manual Setup

1. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Create logs directory:**
   ```bash
   mkdir -p logs
   ```

4. **Set up environment file:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. **Run the server:**
   ```bash
   python3 server.py
   ```

6. **In another terminal, start the dashboard:**
   ```bash
   source venv/bin/activate
   python3 dashboard.py
   ```

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the `AIonCall` directory with the following variables:

```bash
# Required: Google Gemini API Key
GOOGLE_API_KEY="your-gemini-api-key-here"

# Optional: Server Configuration
PORT=5000
HOST=0.0.0.0
DEBUG=False

# Optional: Gemini Model Configuration
MODEL_NAME="models/gemini-2.5-flash-native-audio-preview-12-2025"
VOICE_NAME="Puck"  # Options: Puck, Charon, Kore, Fenrir, Gigachad

# Optional: Logging Configuration
LOG_LEVEL="INFO"
LOG_FILE="logs/voice_bot_echo.log"
```

### Server Configuration (in server.py)

```python
# Audio Configuration
EXOTEL_RATE = 8000           # Exotel's sample rate (Hz)
GEMINI_INPUT_RATE = 16000    # Gemini input sample rate (Hz)
GEMINI_OUTPUT_RATE = 24000   # Gemini output sample rate (Hz)

# Buffer Settings
MIN_CHUNK_SIZE = 3200        # Exotel's minimum chunk size (bytes)

# WebSocket Settings
PORT = 5000                  # Server port
HOST = "0.0.0.0"            # Bind address
```

### Exotel Integration Configuration

In your Exotel dashboard, configure the WebSocket URL:

```
ws://your-server-ip:5000/exotel
```

Or for production with SSL:

```
wss://your-domain.com:5000/exotel
```

---

## 📖 Usage

### Starting the Application

#### Option 1: Using Setup & Start Scripts (Recommended)
```bash
# Initial setup (one time)
./setup.sh

# Start the application
./start.sh
```

#### Option 2: Manual Start
```bash
# Activate virtual environment
source venv/bin/activate

# Terminal 1: Start the WebSocket server
python3 server.py

# Terminal 2: Start the dashboard (in new terminal)
python3 dashboard.py
```

#### Option 3: Production with Gunicorn
```bash
source venv/bin/activate
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 dashboard:app
```

### Accessing the Dashboard

Once the server is running:

1. **Dashboard URL**: `http://localhost:5000/`
2. **WebSocket Server**: `ws://localhost:5000` (for Exotel)
3. **API Status**: `http://localhost:5000/api/status`

### Monitoring Logs

```bash
# View live logs
tail -f logs/voice_bot_echo.log

# Search for errors
grep "ERROR" logs/voice_bot_echo.log

# Get summary statistics
grep "Audio" logs/voice_bot_echo.log | wc -l
```

---

## 🔌 API Endpoints

### WebSocket Endpoints

#### Exotel Connection
```
ws://0.0.0.0:5000/exotel
```

**Message Format (Exotel → Server):**
```json
{
  "type": "media",
  "data": "base64_encoded_audio_chunk",
  "timestamp": 1234567890
}
```

**Message Format (Server → Exotel):**
```json
{
  "type": "audio_response",
  "data": "base64_encoded_audio_response",
  "sequence": 1
}
```

#### Dashboard Updates (Socket.IO)
```
http://localhost:5000 (via Socket.IO namespace)
```

**Socket.IO Events:**
- `connect` - Client connects to dashboard
- `disconnect` - Client disconnects
- `stats_update` - Live statistics update
- `event_log` - New event logged
- `call_started` - New call session
- `call_ended` - Call session ended

### REST API Endpoints

#### Get Server Status
```http
GET /api/status
```
**Response:**
```json
{
  "status": "running",
  "uptime": "2 hours 30 minutes",
  "active_connections": 3,
  "total_calls": 15,
  "model": "gemini-2.5-flash-native-audio-preview-12-2025"
}
```

#### Get Statistics
```http
GET /api/stats
```
**Response:**
```json
{
  "total_calls": 15,
  "active_connections": 3,
  "total_media_packets": 450,
  "avg_latency_ms": 125.5,
  "first_media_latency_ms": 2300,
  "end_to_end_latency_ms": 45000
}
```

#### Get Recent Events
```http
GET /api/events?limit=50
```
**Response:**
```json
{
  "events": [
    {
      "type": "media",
      "connection_id": "conn_123",
      "timestamp": "2024-02-20T10:30:45Z",
      "inter_event_latency_ms": 125.3,
      "data_size": 3200
    }
  ]
}
```

#### Get Call History
```http
GET /api/calls
```
**Response:**
```json
{
  "calls": [
    {
      "call_id": "call_123",
      "connection_id": "conn_123",
      "start_time": "2024-02-20T10:00:00Z",
      "end_time": "2024-02-20T10:05:00Z",
      "duration_seconds": 300,
      "event_count": 450,
      "avg_latency_ms": 128.5
    }
  ]
}
```

---

## 🔊 Audio Processing Pipeline

### Input Audio Flow (Exotel → Gemini)

```
Exotel (8kHz PCM)
    ↓
AudioBuffer (accumulate 3.2KB chunks)
    ↓
Base64 Encoding
    ↓
AudioTranscoder (8kHz → 16kHz)
    ↓
Gemini API (16kHz input)
```

### Output Audio Flow (Gemini → Exotel)

```
Gemini API (24kHz PCM output)
    ↓
AudioTranscoder (24kHz → 8kHz)
    ↓
Base64 Encoding
    ↓
AudioBuffer (enforce 3.2KB minimum)
    ↓
Exotel (8kHz PCM)
```

### Audio Configuration Details

| Parameter | Value | Notes |
|-----------|-------|-------|
| **Input Sample Rate** | 8000 Hz | Exotel standard |
| **Gemini Input Rate** | 16000 Hz | Required by Gemini |
| **Gemini Output Rate** | 24000 Hz | Gemini default output |
| **Output Sample Rate** | 8000 Hz | Exotel standard |
| **Bit Depth** | 16-bit | PCM format |
| **Channels** | Mono | Single channel |
| **Min Chunk Size** | 3200 bytes | Exotel requirement |
| **Alignment** | 320 bytes | Exotel requirement |

### Resampling Algorithm

Uses Python's `audioop.ratecv()` for high-quality audio resampling:

```python
# Example: 8kHz → 16kHz
pcm_16k, state = audioop.ratecv(
    raw_bytes,          # Input audio data
    2,                  # Sample width (2 bytes for 16-bit)
    1,                  # Number of channels (1 for mono)
    8000,               # Input sample rate
    16000,              # Output sample rate
    state               # Resampling state (for continuity)
)
```

---

## 📊 Dashboard Monitoring

### Real-time Metrics

The dashboard displays live metrics updated via Socket.IO:

- **Total Calls**: Cumulative count of call sessions
- **Active Connections**: Current WebSocket connections
- **Total Media Packets**: Total audio chunks processed
- **Total Events**: Total log events
- **Calls Per Hour**: Average call frequency
- **Avg Latency**: Average inter-event latency
- **First Media Latency**: Time to first audio packet
- **End-to-End Latency**: Total call duration

### Call Session Tracking

Each call session tracks:

```python
class CallSession:
    connection_id       # Unique connection identifier
    events              # List of all events
    start_time          # Session start timestamp
    first_media_time    # First audio packet timestamp
    end_time            # Session end timestamp
    latencies[]         # Array of inter-event latencies
```

### Event Types

- `connect` - WebSocket connection established
- `media` - Audio data received
- `transcription` - Speech transcribed
- `response` - AI response generated
- `audio_out` - Audio response sent
- `disconnect` - Connection closed
- `error` - Error occurred

### Dashboard Features

- 📈 **Real-time Charts**: Latency trends and call distribution
- 📞 **Call History**: Detailed event logs per call
- 🔄 **Connection Monitoring**: Active connection details
- ⏱️ **Latency Analytics**: Min/max/avg metrics
- 📊 **Performance Graphs**: Packet rate, call duration
- 🎯 **Error Tracking**: Error events and stack traces
- 💾 **Data Export**: Export metrics as CSV/JSON

---

## 🐛 Troubleshooting

### Common Issues & Solutions

#### 1. **"Port 5000 already in use" Error**

**Problem**: Another process is using port 5000

**Solution**:
```bash
# Find process using port 5000
lsof -i :5000

# Kill the process
kill -9 <PID>

# Or use start.sh (it handles this automatically)
./start.sh
```

**Alternative**: Use a different port
```bash
# Edit server.py
PORT = 5001  # Change to different port
```

#### 2. **"Google API Key not found" Error**

**Problem**: GOOGLE_API_KEY environment variable not set

**Solution**:
```bash
# Check if .env file exists
cat .env

# If not, create it
echo 'GOOGLE_API_KEY="your-key-here"' > .env

# Verify it's loaded
python3 -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('GOOGLE_API_KEY'))"
```

#### 3. **"Connection refused" Error**

**Problem**: Cannot connect to WebSocket server

**Solution**:
```bash
# Verify server is running
ps aux | grep server.py

# Check if port is listening
netstat -tuln | grep 5000

# Start server if not running
./start.sh
```

#### 4. **Audio Transcoding Errors**

**Problem**: "Inbound Transcode Error" or "Outbound Transcode Error" in logs

**Solution**:
```bash
# Verify audio buffer state
# Check logs for details
tail -f logs/voice_bot_echo.log | grep "Transcode"

# Ensure audio chunk sizes are correct
# Minimum: 3200 bytes for Exotel
```

#### 5. **Dashboard Not Loading**

**Problem**: Can't access `http://localhost:5000`

**Solution**:
```bash
# Verify Flask is running
ps aux | grep dashboard.py

# Check Flask logs
tail -f logs/voice_bot_echo.log | grep "Flask"

# Try restarting
python3 dashboard.py
```

#### 6. **High Latency Issues**

**Problem**: Latency > 500ms

**Causes & Solutions**:
- **Network latency**: Check internet connection
- **CPU bottleneck**: Monitor CPU usage (`top`)
- **Gemini API delays**: Check Gemini service status
- **Buffer accumulation**: Increase MIN_CHUNK_SIZE? No - keep at 3200

```bash
# Monitor system resources
watch -n 1 'ps aux | grep python'

# Check network latency to Google APIs
ping api.gemini.google.com
```

#### 7. **Exotel Connection Issues**

**Problem**: Exotel not connecting to WebSocket

**Solution**:
```bash
# Verify Exotel webhook URL in dashboard
# Should be: ws://your-ip:5000/exotel

# Test with curl (WebSocket test)
wscat -c ws://localhost:5000/exotel

# Check firewall
sudo ufw status
sudo ufw allow 5000
```

#### 8. **Virtual Environment Issues**

**Problem**: "venv: command not found"

**Solution**:
```bash
# Reinstall venv
python3 -m venv venv

# On Ubuntu/Debian
sudo apt-get install python3-venv

# Activate it
source venv/bin/activate
```

---

## ⚡ Performance Considerations

### Optimization Tips

#### 1. **Reduce Latency**
- Use SSD for log storage
- Ensure stable network connection
- Increase system resources (CPU/RAM)
- Use production-grade server (Gunicorn vs. dev server)

#### 2. **Handle High Volume**
- Use multiple worker processes
- Implement connection pooling
- Add caching for repeated operations
- Monitor memory usage

#### 3. **Server Optimization**
```bash
# Run with Gunicorn (4 workers)
gunicorn --worker-class eventlet -w 4 --bind 0.0.0.0:5000 dashboard:app

# Monitor performance
htop
iotop
nethogs
```

#### 4. **Audio Buffer Tuning**
```python
# In server.py - Adjust MIN_CHUNK_SIZE if needed
# Default: 3200 bytes (3.2KB)
# Higher = less frequent updates but higher latency
# Lower = more frequent updates but may not meet Exotel requirements
MIN_CHUNK_SIZE = 3200
```

### Resource Requirements by Load

| Concurrent Calls | CPU | RAM | Bandwidth |
|------------------|-----|-----|-----------|
| 1-5 | 1 core | 512MB | 40 Mbps |
| 5-20 | 2 cores | 1GB | 160 Mbps |
| 20-50 | 4 cores | 2GB | 400 Mbps |
| 50+ | 8+ cores | 4GB+ | 1+ Gbps |

### Monitoring Commands

```bash
# CPU & Memory usage
top -p $(pgrep -f "python3 server.py")

# Network connections
netstat -an | grep 5000

# Process resource usage
ps aux | grep python

# Real-time dashboard stats
curl http://localhost:5000/api/stats | jq .

# Active connections
curl http://localhost:5000/api/status | jq .active_connections
```

---


### Areas for Contribution

- 🐛 Bug fixes and stability improvements
- 🚀 Performance optimizations
- 📚 Documentation enhancements
- ✨ New features (new AI models, metrics, etc.)
- 🧪 Test coverage improvements
- 🎨 Dashboard UI/UX improvements

---

## 📋 Logs & Debugging

### Log Location
```
AIonCall/logs/voice_bot_echo.log
```

### Log Levels
```
DEBUG   - Detailed diagnostic information
INFO    - General informational messages
WARNING - Warning messages
ERROR   - Error messages
```

### Enable Debug Mode
```bash
# Edit .env
LOG_LEVEL="DEBUG"

# Restart server
./start.sh
```

### Helpful Log Commands
```bash
# View all errors
grep "ERROR" logs/voice_bot_echo.log

# View last 100 lines
tail -100 logs/voice_bot_echo.log

# Follow live logs
tail -f logs/voice_bot_echo.log

# Search for specific connection
grep "conn_123" logs/voice_bot_echo.log

# Count events by type
grep "type:" logs/voice_bot_echo.log | cut -d: -f2 | sort | uniq -c
```

---

## 🔐 Security Considerations

⚠️ **Important Security Notes**:

1. **Never commit `.env` file** with API keys
2. **Use HTTPS/WSS** in production (add SSL certificate)
3. **Validate all inputs** from Exotel
4. **Rate limit** API endpoints
5. **Rotate API keys** regularly
6. **Monitor logs** for suspicious activity
7. **Use firewall** to restrict access
8. **Keep dependencies** updated

### Production Deployment Checklist

- [ ] Set `DEBUG = False` in configuration
- [ ] Use proper SSL/TLS certificates
- [ ] Configure firewall rules
- [ ] Set up log rotation
- [ ] Enable monitoring and alerts
- [ ] Configure backup strategy
- [ ] Use strong, unique API keys
- [ ] Set up rate limiting
- [ ] Configure CORS properly
- [ ] Document deployment process

---

## 📞 Support & Resources

### Documentation
- [Google Gemini API Docs](https://ai.google.dev/)
- [Exotel Webhook Documentation](https://exotel.com/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [WebSockets Library](https://websockets.readthedocs.io/)

### Getting Help
- Check logs: `tail -f logs/voice_bot_echo.log`
- Review GitHub issues
- Contact support team
- Check troubleshooting section above

### Related Projects
- [Gemini AI SDK](https://github.com/google-ai-python)
- [Flask-SocketIO](https://github.com/miguelgrinberg/flask-socketio)
- [websockets](https://github.com/aaugustin/websockets)

---

**Happy coding! 🚀**
