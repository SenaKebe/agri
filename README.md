🌾 AI Crop Advisor
AI-powered agricultural advisory system for Ethiopian farmers delivering real-time farming recommendations via Telegram.

🚀 Overview
AI Crop Advisor is an intelligent agricultural platform that provides Ethiopian farmers with real-time, AI-powered farming advice through automated Telegram alerts. The system combines weather monitoring, multi-agent AI consultation, and instant messaging to deliver actionable agricultural recommendations.

✨ Key Features
🤖 Multi-Agent AI System - Specialized agronomist and weather advisor agents

🌤 Real-time Weather Monitoring - Automated 3-hour checks across 6 Ethiopian cities

⚡ Instant Telegram Alerts - Direct messaging with actionable farming advice

🎓 Teacher Demo Mode - Educational tool for agricultural training

🌾 Ethiopia-Specific Intelligence - Tailored advice for local growing conditions

🔄 n8n Automation - Workflow automation for continuous monitoring

🏗 System Architecture
text
OpenWeather API → AI Crop Advisor → n8n Automation → Telegram Alerts
↓
Multi-Agent AI System
(Agronomist + Weather Advisor)

🛠 Installation
Prerequisites
Python 3.11+

Telegram Bot Token

OpenWeatherMap API Key

Google Gemini API Key

Quick Start
Clone the repository

bash
git clone https://github.com/SenaKebe/agri.git
cd ai-crop-advisor
Install dependencies

bash
pip install -r requirements.txt
Set up environment variables

bash
cp .env.example .env

# Edit .env with your API keys

Start the application

bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
Access the API documentation

text
http://localhost:8000/docs
Docker Deployment
bash

📚 API Documentation
Core Endpoints
GET /health - Service health check

POST /api/v1/chat - Chat with AI agricultural advisor

POST /api/v1/mcp/n8n/enhance-alert - Enhance alerts with AI intelligence

GET /api/v1/agents - List available AI agents

Example Usage
bash

# Test the health endpoint

curl http://localhost:8000/health

# Get agricultural advice

curl -X POST http://my-backend/api/v1/chat \
 -H "Content-Type: application/json" \
 -d '{
"message": "Best time to plant maize?",
"location": "Central Ethiopia",
"crop_type": "maize"
}'
🤖 AI Agents
Agronomist Agent
Planting timing and techniques

Soil preparation and fertilizer

Pest and disease management

Water management and irrigation

Harvesting and post-harvest handling

Weather Advisor Agent
Optimal planting windows

Weather risk management

Harvest timing considerations

Microclimate adaptations

⚡ n8n Automation
The system includes pre-configured n8n workflows for:

3-hour automated weather monitoring

Risk detection and analysis

AI-enhanced alert generation

Telegram message delivery

Workflow Integration
text
Schedule Trigger → Ethiopian Cities → Weather API → Risk Analysis → AI Enhancement → Telegram
🔧 Configuration
Environment Variables
env
WEATHER_API_KEY=your_openweathermap_key
GOOGLE_API_KEY=your_gemini_ai_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
JWT_SECRET_KEY=your_jwt_secret_key
Telegram Bot Setup
Create a bot with @BotFather

Get your bot token

Configure webhook (if needed)

Share bot username with farmers

🎯 Usage Examples
For Farmers
Receive automatic weather risk alerts every 3 hours

Get AI-powered farming advice for specific conditions

Access expert knowledge without internet browsing

For Educators
Use demo mode for classroom demonstrations

Teach agricultural risk management

Show real-world AI applications in farming

Sample Alert
text
📍 Addis Ababa | 🌡️ 35°C | 🔴 High Risk

🤖 AI AGRONOMIST ADVICE:
• Increase irrigation to twice daily
• Apply mulch to retain soil moisture  
• Use shade nets for young plants
• Water during cooler hours

🌾 Confidence: 85% based on Central Ethiopia conditions
🗂 Project Structure
text
ai-crop-advisor/
├── app/
│ ├── agents/  
│ ├── workflows/  
│ ├── models/  
│ ├── rag/
├─|──rag/  
│ └── mcp/  
├── tests/
