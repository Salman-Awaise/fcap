#!/usr/bin/env python3
"""
Robust GPT-OSS-20B FCAP Platform - No Fallbacks, Only Excellence
"""

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
import uvicorn
import sqlite3
from datetime import datetime
import requests
import json
import os
import logging
import time
from openai import OpenAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Robust GPT-OSS-20B FCAP Platform")

class ChatMessage(BaseModel):
    message: str
    session_id: str = "default"

# GPT-OSS-20B Configuration
HF_TOKEN = "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"
BASE_URL = "https://router.huggingface.co/v1"
MODEL = "openai/gpt-oss-20b:fireworks-ai"

# Initialize OpenAI client
client = OpenAI(base_url=BASE_URL, api_key=HF_TOKEN)

# Database setup
def init_database():
    conn = sqlite3.connect('robust_gpt_oss_platform.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            message TEXT NOT NULL,
            response TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT NOT NULL,
            patient_email TEXT NOT NULL,
            appointment_date TEXT NOT NULL,
            appointment_time TEXT NOT NULL,
            doctor_name TEXT NOT NULL,
            status TEXT DEFAULT 'scheduled',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_database()

def get_gpt_oss_response(message: str) -> str:
    """Get response from GPT-OSS-20B with maximum robustness"""
    try:
        # Create highly specific healthcare prompt
        healthcare_prompt = f"""You are Dr. Sarah, a professional AI healthcare assistant at Crescent Clinics. You help patients with appointments, health questions, and clinic information.

CRITICAL INSTRUCTIONS:
- Be warm, professional, and empathetic
- Keep responses concise (2-3 sentences max)
- Always offer specific next steps
- For medical emergencies (chest pain, severe symptoms), immediately direct to 911
- For appointments, ask for specific details (date, time, reason)
- Use medical terminology appropriately but explain simply
- End with a helpful question or next step
- Always be helpful and actionable

Patient message: {message}

Dr. Sarah's response:"""
        
        # Make API call with robust error handling
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": healthcare_prompt}],
            max_tokens=200,
            temperature=0.7,
            timeout=30
        )
        
        # Extract response with multiple validation layers
        if not response:
            raise Exception("Empty response from API")
        
        if not response.choices or len(response.choices) == 0:
            raise Exception("No choices in response")
        
        choice = response.choices[0]
        if not choice:
            raise Exception("Empty choice in response")
        
        if not choice.message:
            raise Exception("No message in choice")
        
        content = choice.message.content
        if not content:
            raise Exception("Empty content in message")
        
        # Clean and validate response
        content = content.strip()
        if not content or len(content) < 10:
            raise Exception("Response too short or empty")
        
        # Clean up the response
        if "Dr. Sarah's response:" in content:
            content = content.split("Dr. Sarah's response:")[-1].strip()
        elif "Dr. Sarah:" in content:
            content = content.split("Dr. Sarah:")[-1].strip()
        
        # Ensure response is professional and healthcare-appropriate
        healthcare_indicators = ['hello', 'hi', 'thank', 'appointment', 'help', 'clinic', 'doctor', 'medical', 'health', 'emergency', '911', 'pain', 'symptoms', 'visit', 'schedule']
        if not any(word in content.lower() for word in healthcare_indicators):
            # If no healthcare indicators, check if it's at least a reasonable response
            if len(content) < 20 or not any(char.isalpha() for char in content):
                raise Exception("Response not healthcare-appropriate")
        
        logger.info(f"GPT-OSS-20B response: {content[:50]}...")
        return content
        
    except Exception as e:
        logger.error(f"GPT-OSS-20B failed: {e}")
        raise Exception(f"GPT-OSS-20B is not available: {str(e)}")

def get_ai_response(message: str) -> str:
    """Main AI response function - GPT-OSS-20B or nothing"""
    try:
        return get_gpt_oss_response(message)
    except Exception as e:
        logger.error(f"AI response failed: {e}")
        # NO FALLBACK - Return error message
        return f"🚨 I'm currently experiencing technical difficulties with my AI system. Please try again in a moment, or contact our clinic directly at (555) 123-4567 for immediate assistance."

def save_conversation(session_id: str, message: str, response: str):
    conn = sqlite3.connect('robust_gpt_oss_platform.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO conversations (session_id, message, response) VALUES (?, ?, ?)",
        (session_id, message, response)
    )
    conn.commit()
    conn.close()

# PATIENT INTERFACE
@app.get("/", response_class=HTMLResponse)
async def patient_interface(request: Request):
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Crescent Clinics - Patient Portal</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #333;
            }
            .container { 
                max-width: 800px; 
                margin: 0 auto; 
                padding: 20px; 
                min-height: 100vh;
                display: flex;
                flex-direction: column;
            }
            .header { 
                background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%); 
                color: white; 
                padding: 20px; 
                border-radius: 15px 15px 0 0;
                text-align: center;
                position: relative;
            }
            .header h1 { font-size: 28px; font-weight: 700; margin-bottom: 10px; }
            .header p { opacity: 0.9; font-size: 16px; }
            .ai-badge {
                background: rgba(34, 197, 94, 0.2);
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 600;
                margin-top: 8px;
                display: inline-block;
            }
            .nav-links {
                position: absolute;
                top: 20px;
                right: 20px;
                display: flex;
                gap: 10px;
            }
            .nav-link {
                background: rgba(255,255,255,0.2);
                color: white;
                padding: 8px 16px;
                border-radius: 20px;
                text-decoration: none;
                font-size: 12px;
                font-weight: 600;
                transition: all 0.2s;
            }
            .nav-link:hover {
                background: rgba(255,255,255,0.3);
            }
            .chat-container { 
                background: white; 
                border-radius: 0 0 15px 15px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                flex: 1;
                display: flex;
                flex-direction: column;
            }
            .messages { 
                flex: 1; 
                padding: 20px; 
                overflow-y: auto; 
                background: #f8fafc;
                min-height: 400px;
            }
            .message { 
                margin-bottom: 16px; 
                display: flex; 
                align-items: flex-start; 
                gap: 12px;
            }
            .message.user { flex-direction: row-reverse; }
            .message-avatar { 
                width: 32px; 
                height: 32px; 
                border-radius: 50%; 
                display: flex; 
                align-items: center; 
                justify-content: center; 
                font-size: 14px; 
                font-weight: 600;
            }
            .message.user .message-avatar { background: #4f46e5; color: white; }
            .message.ai .message-avatar { background: #e5e7eb; color: #6b7280; }
            .message-content { 
                max-width: 70%; 
                padding: 12px 16px; 
                border-radius: 18px; 
                font-size: 14px; 
                line-height: 1.5;
                white-space: pre-line;
            }
            .message.user .message-content { 
                background: #4f46e5; 
                color: white; 
                border-bottom-right-radius: 4px;
            }
            .message.ai .message-content { 
                background: white; 
                color: #374151; 
                border: 1px solid #e5e7eb; 
                border-bottom-left-radius: 4px;
            }
            .input-container { 
                padding: 20px; 
                background: white; 
                border-top: 1px solid #e2e8f0;
                display: flex;
                gap: 12px;
                align-items: center;
            }
            .message-input { 
                flex: 1; 
                padding: 12px 16px; 
                border: 1px solid #e2e8f0; 
                border-radius: 24px; 
                font-size: 14px; 
                outline: none;
            }
            .message-input:focus { 
                border-color: #4f46e5; 
                box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
            }
            .send-btn { 
                background: #4f46e5; 
                color: white; 
                width: 48px; 
                height: 48px; 
                border-radius: 50%; 
                border: none; 
                cursor: pointer; 
                display: flex; 
                align-items: center; 
                justify-content: center; 
                font-size: 18px;
                transition: all 0.2s;
            }
            .send-btn:hover { background: #4338ca; }
            .send-btn:disabled { 
                background: #d1d5db; 
                cursor: not-allowed;
            }
            .quick-actions {
                padding: 16px 20px;
                background: #f1f5f9;
                border-top: 1px solid #e2e8f0;
            }
            .quick-actions-title {
                font-size: 12px;
                font-weight: 600;
                color: #64748b;
                margin-bottom: 8px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            .chips {
                display: flex;
                gap: 8px;
                flex-wrap: wrap;
            }
            .chip {
                background: white;
                border: 1px solid #d1d5db;
                border-radius: 20px;
                padding: 8px 16px;
                font-size: 12px;
                cursor: pointer;
                transition: all 0.2s;
            }
            .chip:hover {
                background: #4f46e5;
                color: white;
                border-color: #4f46e5;
                transform: translateY(-1px);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="nav-links">
                    <a href="/clinic" class="nav-link">Clinic Portal</a>
                    <a href="/admin" class="nav-link">Admin Portal</a>
                </div>
                
                <h1>🏥 Crescent Clinics</h1>
                <p>Mon-Fri 9AM-5PM • Sat 9AM-2PM • 24/7 Urgent Care Available</p>
                <div class="ai-badge">🤖 GPT-OSS-20B Powered AI Assistant</div>
            </div>
            
            <div class="chat-container">
                <div class="messages" id="messages">
                    <div class="message ai">
                        <div class="message-avatar">🤖</div>
                        <div class="message-content">
                            <strong>Welcome to Crescent Clinics! 👋</strong><br>
                            I'm Dr. Sarah, your AI assistant powered by GPT-OSS-20B. I can help you book visits, answer questions, and provide clinic information. What do you need today?
                        </div>
                    </div>
                </div>
                
                <div class="quick-actions">
                    <div class="quick-actions-title">Quick Actions</div>
                    <div class="chips">
                        <div class="chip" onclick="sendQuickMessage('Book appointment')">📅 Book Appointment</div>
                        <div class="chip" onclick="sendQuickMessage('What are your hours?')">🕒 Hours</div>
                        <div class="chip" onclick="sendQuickMessage('I have a headache')">🩺 Health Concern</div>
                        <div class="chip" onclick="sendQuickMessage('Contact info')">📞 Contact</div>
                        <div class="chip" onclick="sendQuickMessage('What is artificial intelligence?')">🤖 Test AI</div>
                    </div>
                </div>
                
                <div class="input-container">
                    <input type="text" id="messageInput" class="message-input" placeholder="Type your message..." onkeypress="handleKeyPress(event)">
                    <button class="send-btn" onclick="sendMessage()" id="sendBtn">➤</button>
                </div>
            </div>
        </div>

        <script>
            let sessionId = 'session_' + Date.now();
            let isTyping = false;
            
            // Initialize
            document.addEventListener('DOMContentLoaded', function() {
                console.log('Chat initialized');
                const input = document.getElementById('messageInput');
                if (input) {
                    input.focus();
                    console.log('Input focused');
                }
            });
            
            function addMessage(message, isUser = false) {
                console.log('Adding message:', message, 'isUser:', isUser);
                const messages = document.getElementById('messages');
                
                if (!messages) {
                    console.error('Messages container not found!');
                    return;
                }
                
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${isUser ? 'user' : 'ai'}`;
                
                messageDiv.innerHTML = `
                    <div class="message-avatar">${isUser ? '👤' : '🤖'}</div>
                    <div class="message-content">${message}</div>
                `;
                
                messages.appendChild(messageDiv);
                messages.scrollTop = messages.scrollHeight;
                console.log('Message added successfully');
            }
            
            function sendQuickMessage(message) {
                const input = document.getElementById('messageInput');
                if (input) {
                    input.value = message;
                    sendMessage();
                }
            }
            
            function handleKeyPress(event) {
                if (event.key === 'Enter') {
                    event.preventDefault();
                    sendMessage();
                }
            }
            
            async function sendMessage() {
                const input = document.getElementById('messageInput');
                const sendBtn = document.getElementById('sendBtn');
                
                if (!input || !sendBtn) {
                    console.error('Elements not found');
                    return;
                }
                
                const message = input.value.trim();
                if (!message || isTyping) return;
                
                console.log('Sending:', message);
                addMessage(message, true);
                input.value = '';
                sendBtn.disabled = true;
                isTyping = true;
                
                try {
                    console.log('Making API call...');
                    const response = await fetch('/chat', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({message: message, session_id: sessionId})
                    });
                    
                    console.log('Response status:', response.status);
                    
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    
                    const data = await response.json();
                    console.log('Response data:', data);
                    console.log('Adding response message:', data.response);
                    
                    addMessage(data.response);
                    
                } catch (error) {
                    console.error('Error:', error);
                    addMessage('Sorry, I encountered an error. Please try again.');
                } finally {
                    sendBtn.disabled = false;
                    isTyping = false;
                    input.focus();
                }
            }
        </script>
    </body>
    </html>
    """

# CLINIC INTERFACE
@app.get("/clinic", response_class=HTMLResponse)
async def clinic_interface():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Crescent Clinics - Clinic Portal</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #333;
            }
            .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
            .header { 
                background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%); 
                color: white; 
                padding: 30px; 
                border-radius: 15px;
                text-align: center;
                margin-bottom: 30px;
            }
            .header h1 { font-size: 32px; font-weight: 700; margin-bottom: 10px; }
            .header p { opacity: 0.9; font-size: 18px; }
            .nav-links {
                position: absolute;
                top: 30px;
                right: 30px;
                display: flex;
                gap: 15px;
            }
            .nav-link {
                background: rgba(255,255,255,0.2);
                color: white;
                padding: 10px 20px;
                border-radius: 25px;
                text-decoration: none;
                font-size: 14px;
                font-weight: 600;
                transition: all 0.2s;
            }
            .nav-link:hover { background: rgba(255,255,255,0.3); }
            .dashboard { 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
                gap: 20px; 
            }
            .card { 
                background: white; 
                padding: 25px; 
                border-radius: 15px; 
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                transition: transform 0.2s;
            }
            .card:hover { transform: translateY(-5px); }
            .card h3 { color: #4f46e5; margin-bottom: 15px; font-size: 20px; }
            .card p { color: #666; line-height: 1.6; margin-bottom: 15px; }
            .btn { 
                background: #4f46e5; 
                color: white; 
                padding: 12px 24px; 
                border: none; 
                border-radius: 8px; 
                cursor: pointer; 
                font-size: 14px;
                font-weight: 600;
                transition: all 0.2s;
            }
            .btn:hover { background: #4338ca; transform: translateY(-2px); }
            .stats { display: flex; justify-content: space-around; margin: 20px 0; }
            .stat { text-align: center; }
            .stat-number { font-size: 24px; font-weight: 700; color: #4f46e5; }
            .stat-label { font-size: 14px; color: #666; margin-top: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="nav-links">
                    <a href="/" class="nav-link">Patient Portal</a>
                    <a href="/admin" class="nav-link">Admin Portal</a>
                </div>
                
                <h1>🏥 Clinic Management Portal</h1>
                <p>Manage appointments, view patient interactions, and monitor AI performance</p>
            </div>
            
            <div class="dashboard">
                <div class="card">
                    <h3>📅 Appointments</h3>
                    <p>View and manage patient appointments</p>
                    <button class="btn" onclick="viewAppointments()">View Appointments</button>
                </div>
                
                <div class="card">
                    <h3>💬 Patient Conversations</h3>
                    <p>Review AI interactions with patients</p>
                    <button class="btn" onclick="viewConversations()">View Conversations</button>
                </div>
                
                <div class="card">
                    <h3>🤖 AI Health</h3>
                    <p>Monitor AI system performance</p>
                    <button class="btn" onclick="checkAIHealth()">Check AI Status</button>
                </div>
                
                <div class="card">
                    <h3>📊 Analytics</h3>
                    <p>View platform usage statistics</p>
                    <button class="btn" onclick="viewAnalytics()">View Analytics</button>
                </div>
            </div>
            
            <div class="stats">
                <div class="stat">
                    <div class="stat-number" id="totalAppointments">0</div>
                    <div class="stat-label">Total Appointments</div>
                </div>
                <div class="stat">
                    <div class="stat-number" id="todayAppointments">0</div>
                    <div class="stat-label">Today's Appointments</div>
                </div>
                <div class="stat">
                    <div class="stat-number" id="aiStatus">Checking...</div>
                    <div class="stat-label">AI Status</div>
                </div>
            </div>
        </div>

        <script>
            async function viewAppointments() {
                try {
                    const response = await fetch('/appointments');
                    const appointments = await response.json();
                    alert(`Found ${appointments.length} appointments`);
                } catch (error) {
                    alert('Error loading appointments');
                }
            }
            
            async function viewConversations() {
                alert('Conversation history feature coming soon');
            }
            
            async function checkAIHealth() {
                try {
                    const response = await fetch('/health/llm');
                    const health = await response.json();
                    if (health.ok) {
                        alert(`AI Status: Healthy\\nSample: ${health.sample}`);
                    } else {
                        alert(`AI Status: Error\\n${health.error}`);
                    }
                } catch (error) {
                    alert('Error checking AI health');
                }
            }
            
            function viewAnalytics() {
                alert('Analytics dashboard coming soon');
            }
            
            // Load initial data
            async function loadData() {
                try {
                    const response = await fetch('/appointments');
                    const appointments = await response.json();
                    document.getElementById('totalAppointments').textContent = appointments.length;
                    document.getElementById('todayAppointments').textContent = appointments.filter(apt => 
                        new Date(apt.appointment_date).toDateString() === new Date().toDateString()
                    ).length;
                } catch (error) {
                    console.error('Error loading data:', error);
                }
                
                try {
                    const response = await fetch('/health/llm');
                    const health = await response.json();
                    document.getElementById('aiStatus').textContent = health.ok ? 'Healthy' : 'Error';
                } catch (error) {
                    document.getElementById('aiStatus').textContent = 'Error';
                }
            }
            
            loadData();
        </script>
    </body>
    </html>
    """

# ADMIN INTERFACE
@app.get("/admin", response_class=HTMLResponse)
async def admin_interface():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Crescent Clinics - Admin Portal</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #333;
            }
            .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
            .header { 
                background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%); 
                color: white; 
                padding: 30px; 
                border-radius: 15px;
                text-align: center;
                margin-bottom: 30px;
            }
            .header h1 { font-size: 32px; font-weight: 700; margin-bottom: 10px; }
            .header p { opacity: 0.9; font-size: 18px; }
            .nav-links {
                position: absolute;
                top: 30px;
                right: 30px;
                display: flex;
                gap: 15px;
            }
            .nav-link {
                background: rgba(255,255,255,0.2);
                color: white;
                padding: 10px 20px;
                border-radius: 25px;
                text-decoration: none;
                font-size: 14px;
                font-weight: 600;
                transition: all 0.2s;
            }
            .nav-link:hover { background: rgba(255,255,255,0.3); }
            .dashboard { 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
                gap: 20px; 
            }
            .card { 
                background: white; 
                padding: 25px; 
                border-radius: 15px; 
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                transition: transform 0.2s;
            }
            .card:hover { transform: translateY(-5px); }
            .card h3 { color: #dc2626; margin-bottom: 15px; font-size: 20px; }
            .card p { color: #666; line-height: 1.6; margin-bottom: 15px; }
            .btn { 
                background: #dc2626; 
                color: white; 
                padding: 12px 24px; 
                border: none; 
                border-radius: 8px; 
                cursor: pointer; 
                font-size: 14px;
                font-weight: 600;
                transition: all 0.2s;
            }
            .btn:hover { background: #b91c1c; transform: translateY(-2px); }
            .btn.secondary { 
                background: #6b7280; 
            }
            .btn.secondary:hover { background: #4b5563; }
            .stats { display: flex; justify-content: space-around; margin: 20px 0; }
            .stat { text-align: center; }
            .stat-number { font-size: 24px; font-weight: 700; color: #dc2626; }
            .stat-label { font-size: 14px; color: #666; margin-top: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="nav-links">
                    <a href="/" class="nav-link">Patient Portal</a>
                    <a href="/clinic" class="nav-link">Clinic Portal</a>
                </div>
                
                <h1>🔧 Admin Portal</h1>
                <p>System administration, user management, and platform control</p>
            </div>
            
            <div class="dashboard">
                <div class="card">
                    <h3>👥 User Management</h3>
                    <p>Manage clinic access and user permissions</p>
                    <button class="btn" onclick="manageUsers()">Manage Users</button>
                </div>
                
                <div class="card">
                    <h3>🏥 Clinic Management</h3>
                    <p>Add, remove, and configure clinic access</p>
                    <button class="btn" onclick="manageClinics()">Manage Clinics</button>
                </div>
                
                <div class="card">
                    <h3>🤖 AI Configuration</h3>
                    <p>Configure AI settings and model parameters</p>
                    <button class="btn" onclick="configureAI()">Configure AI</button>
                </div>
                
                <div class="card">
                    <h3>📊 System Analytics</h3>
                    <p>View comprehensive platform analytics</p>
                    <button class="btn" onclick="viewSystemAnalytics()">View Analytics</button>
                </div>
                
                <div class="card">
                    <h3>🔒 Security Settings</h3>
                    <p>Manage security and access controls</p>
                    <button class="btn secondary" onclick="securitySettings()">Security</button>
                </div>
                
                <div class="card">
                    <h3>📈 Performance Monitoring</h3>
                    <p>Monitor system performance and health</p>
                    <button class="btn secondary" onclick="performanceMonitoring()">Monitoring</button>
                </div>
            </div>
            
            <div class="stats">
                <div class="stat">
                    <div class="stat-number" id="totalUsers">0</div>
                    <div class="stat-label">Total Users</div>
                </div>
                <div class="stat">
                    <div class="stat-number" id="activeClinics">0</div>
                    <div class="stat-label">Active Clinics</div>
                </div>
                <div class="stat">
                    <div class="stat-number" id="systemStatus">Checking...</div>
                    <div class="stat-label">System Status</div>
                </div>
            </div>
        </div>

        <script>
            function manageUsers() {
                alert('User management feature coming soon');
            }
            
            function manageClinics() {
                alert('Clinic management feature coming soon');
            }
            
            function configureAI() {
                alert('AI configuration feature coming soon');
            }
            
            function viewSystemAnalytics() {
                alert('System analytics feature coming soon');
            }
            
            function securitySettings() {
                alert('Security settings feature coming soon');
            }
            
            function performanceMonitoring() {
                alert('Performance monitoring feature coming soon');
            }
            
            // Load initial data
            async function loadData() {
                try {
                    const response = await fetch('/health/llm');
                    const health = await response.json();
                    document.getElementById('systemStatus').textContent = health.ok ? 'Healthy' : 'Error';
                } catch (error) {
                    document.getElementById('systemStatus').textContent = 'Error';
                }
            }
            
            loadData();
        </script>
    </body>
    </html>
    """

# API ENDPOINTS
@app.post("/chat")
async def chat_endpoint(chat_data: ChatMessage):
    """Chat endpoint with GPT-OSS-20B integration - no fallbacks"""
    response = get_ai_response(chat_data.message)
    save_conversation(chat_data.session_id, chat_data.message, response)
    return {"response": response, "session_id": chat_data.session_id}

@app.get("/appointments")
async def get_appointments():
    """Get all appointments"""
    conn = sqlite3.connect('robust_gpt_oss_platform.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM appointments ORDER BY created_at DESC")
    appointments = cursor.fetchall()
    conn.close()
    
    return [
        {
            "id": apt[0],
            "patient_name": apt[1],
            "patient_email": apt[2],
            "appointment_date": apt[3],
            "appointment_time": apt[4],
            "doctor_name": apt[5],
            "status": apt[6],
            "created_at": apt[7]
        }
        for apt in appointments
    ]

@app.post("/appointments")
async def create_appointment(
    patient_name: str = Form(...),
    patient_email: str = Form(...),
    appointment_date: str = Form(...),
    appointment_time: str = Form(...),
    doctor_name: str = Form("Dr. Smith")
):
    """Create a new appointment"""
    conn = sqlite3.connect('robust_gpt_oss_platform.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO appointments (patient_name, patient_email, appointment_date, appointment_time, doctor_name) VALUES (?, ?, ?, ?, ?)",
        (patient_name, patient_email, appointment_date, appointment_time, doctor_name)
    )
    conn.commit()
    conn.close()
    return {"message": "Appointment created successfully"}

@app.get("/health/llm")
async def llm_health():
    """LLM health check endpoint"""
    try:
        response = get_gpt_oss_response("Say 'Hello from GPT-OSS-20B' in one sentence.")
        return {"ok": True, "sample": response[:40], "model": "gpt-oss-20b"}
    except Exception as e:
        logger.error(f"LLM health check failed: {e}")
        return {"ok": False, "error": str(e), "model": "gpt-oss-20b"}

if __name__ == "__main__":
    print("🏥 Starting Robust GPT-OSS-20B FCAP Platform...")
    print("🌐 Patient Interface: http://localhost:8000")
    print("🏥 Clinic Interface: http://localhost:8000/clinic")
    print("🔧 Admin Interface: http://localhost:8000/admin")
    print("🤖 AI Assistant: GPT-OSS-20B ONLY - No Fallbacks")
    print("🔍 Health Check: http://localhost:8000/health/llm")
    print("=" * 60)
    
    # Test GPT-OSS-20B connection on startup
    try:
        test_response = get_gpt_oss_response("Hello")
        print(f"✅ GPT-OSS-20B Connection Test: {test_response[:50]}...")
    except Exception as e:
        print(f"❌ GPT-OSS-20B Connection Test Failed: {e}")
        print("   Platform will start but AI may not work properly")
    
    uvicorn.run("robust_gpt_oss_platform:app", host="0.0.0.0", port=8000, reload=True)
