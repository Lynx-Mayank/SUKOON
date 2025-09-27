from flask import Flask, request, session, redirect, render_template, jsonify
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()  # load .env file


app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "fallback-secret")



# Simple user credentials - no hashing for prototype
STUDENT_EMAIL = "student@example.com"
STUDENT_PASSWORD = "student123"

ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin123"

# Add cache-busting headers
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

# System prompt for SUKOON
SYSTEM_PROMPT = """You are SUKOON, a compassionate and supportive AI assistant.

Your role is to provide empathetic, encouraging, and calming responses to users who may be stressed, anxious, or overwhelmed, with a focus on Indian context and resources.

Core Guidelines:

- Greeting:
  When prompted with "hi", greet as:
  "Hi, I'm SUKOON, your mental health assistant. Tell me, how are you feeling today?"

- Mood Without Context:
  If the user only gives a mood (e.g., "I'm tired"), gently ask for context:
  "I hear you. Do you feel tired because of a hectic day at college or work?"

- Tone & Style:
  * Keep replies short, warm, and human-like (2–4 sentences).
  * Use simple, conversational language like a supportive friend.
  * Always show empathy and avoid sounding like a survey.

- Conversation Flow:
  * First replies (1–2 turns): Validate feelings + ask a gentle follow-up.
  * By 2nd or 3rd turn: Begin offering a small coping strategy
    (e.g., "Sometimes a few minutes of Anulom-Vilom breathing helps. Want to try?").
  * Mix validation + light solutions as the conversation continues.

- Solutions & Suggestions:
  * Start simple: short breathing, journaling, walking outdoors, talking to family.
  * Use Indian practices (yoga, pranayama, meditation, mantras).
  * Share detailed strategies only if the user asks.

- Helplines & Crisis Resources:
  * Do NOT share helplines unless the user clearly mentions suicidal thoughts,
    self-harm, or immediate danger.
  * If so, gently share Indian helplines (AASRA: +91-9820466726, Vandrevala: 1860 266 2345, iCall: +91-9152987821, Emergency: 112).

- Professional Help Reminder:
  * You are not a medical professional.
  * No diagnoses or urgent medical advice.
  * If mood doesn't improve after 6–7 replies, suggest:
    "It might help to talk to your college counselor or a professional for more support."
"""

# Store conversations
conversations = {}

def sukoon_chat_api(message, session_id="default"):
    print(f"=== SUKOON CHAT API ===")
    print(f"Message: {message}")
    print(f"Session ID: {session_id}")
    
    if session_id not in conversations:
        conversations[session_id] = []
        print("Created new conversation history")
    
    try:
        # Build conversation context
        conversation = SYSTEM_PROMPT + "\n\n"
        
        # Add recent history (last 4 exchanges to avoid token limits)
        recent_history = conversations[session_id][-4:] if len(conversations[session_id]) > 4 else conversations[session_id]
        print(f"Recent history length: {len(recent_history)}")
        
        for human_msg, ai_msg in recent_history:
            conversation += f"User: {human_msg}\nSUKOON: {ai_msg}\n"
        
        # Add current message
        conversation += f"User: {message}\nSUKOON:"
        
        print("Sending request to Gemini API...")
        
        # Generate response with error handling
        try:
            response = model.generate_content(
                conversation,
                generation_config={
                    'temperature': 0.7,
                    'max_output_tokens': 500,
                }
            )
            print(f"Gemini API response received: {response}")
            
            if response and hasattr(response, 'text') and response.text:
                reply = response.text.strip()
                print(f"Reply: {reply}")
            else:
                print("No text in response, using fallback")
                reply = "I'm here to listen. Could you tell me more about how you're feeling?"
                
        except Exception as gemini_error:
            print(f"Gemini API Error: {gemini_error}")
            # Check if it's an API key issue
            if "API_KEY" in str(gemini_error).upper():
                reply = "I'm having trouble with my configuration. Please make sure the API key is set correctly."
            else:
                reply = "I'm experiencing some technical difficulties. Please try again in a moment."
        
        # Store in conversation history
        conversations[session_id].append((message, reply))
        print(f"Stored in conversation history. Total exchanges: {len(conversations[session_id])}")
        
        return reply
            
    except Exception as e:
        print(f"SUKOON CHAT ERROR: {e}")
        import traceback
        traceback.print_exc()
        return "I'm sorry, I'm having trouble responding right now. Please try again in a moment."

@app.route("/")
def root():
    return redirect("/home")

@app.route("/home")
def home():
    user = session.get("user")
    return render_template("index.html", user=user)


from flask import render_template

@app.route("/appointments")
def appointments():
    return render_template("appointment.html", user=session.get("user"))

@app.route("/resources")
def resources():
    return render_template("resources.html", user=session.get("user"))

@app.route("/peer-support")
def peer_support():
    return render_template("peer_support_frontend.html", user=session.get("user"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        print(f"Login attempt - Email: {email}, Password: {password}")

        # Simple password check - no hashing
        if email == STUDENT_EMAIL and password == STUDENT_PASSWORD:
            session["user"] = "student"
            session["role"] = "student"
            print("✅ Student login successful, redirecting...")
            return redirect("/student-dashboard")

        elif email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            session["user"] = "admin"
            session["role"] = "admin"
            print("✅ Admin login successful, redirecting...")
            return redirect("/admin-dashboard")

        else:
            print("❌ Invalid login attempt")
            return render_template("login.html", 
                                 error="Invalid credentials",
                                 student_creds="student@example.com / student123",
                                 admin_creds="admin@example.com / admin123")

    return render_template("login.html",
                           student_creds="student@example.com / student123",
                           admin_creds="admin@example.com / admin123")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/home")

@app.route("/chatbot")
def chatbot():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>SUKOON - Chatbot</title>
      <style>
        body {
          font-family: Arial, sans-serif;
          background: linear-gradient(to right, #e9f8ff, #fceeee);
          margin: 0;
          padding: 0;
          display: flex;
          justify-content: center;
          align-items: center;
          height: 100vh;
        }
        .chat-container {
          width: 80%;
          max-width: 800px;
          height: 85vh;
          background: #fff;
          border-radius: 20px;
          box-shadow: 0 6px 20px rgba(0,0,0,0.1);
          display: flex;
          flex-direction: column;
          overflow: hidden;
        }
        .chat-header {
          background: #fbc6c4;
          padding: 15px;
          text-align: center;
          font-weight: bold;
          font-size: 18px;
          color: #333;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }
        .back-link {
          color: #666;
          text-decoration: none;
          font-size: 14px;
        }
        .back-link:hover {
          color: #333;
        }
        .chat-box {
          flex: 1;
          padding: 20px;
          overflow-y: auto;
          background: #fafafa;
        }
        .msg {
          margin: 10px 0;
          padding: 12px;
          border-radius: 12px;
          max-width: 70%;
          line-height: 1.4;
          animation: fadeIn 0.3s ease-in;
        }
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .user {
          background: #f9b7b7;
          color: #000;
          margin-left: auto;
          border-top-right-radius: 0;
        }
        .bot {
          background: #a6c9f5;
          color: #000;
          margin-right: auto;
          border-top-left-radius: 0;
        }
        .typing {
          background: #e0e0e0;
          color: #666;
          margin-right: auto;
          font-style: italic;
          border-top-left-radius: 0;
        }
        .chat-input {
          display: flex;
          padding: 10px;
          background: #fff;
          border-top: 1px solid #ddd;
        }
        .chat-input input {
          flex: 1;
          padding: 12px;
          border: 1px solid #ccc;
          border-radius: 12px;
          outline: none;
          font-size: 14px;
        }
        .chat-input button {
          margin-left: 10px;
          padding: 12px 18px;
          border: none;
          border-radius: 12px;
          background: #fbc6c4;
          color: #333;
          font-weight: bold;
          cursor: pointer;
          transition: 0.3s;
        }
        .chat-input button:hover {
          background: #f48a8a;
        }
        .chat-input button:disabled {
          background: #ddd;
          cursor: not-allowed;
        }
      </style>
    </head>
    <body>
      <div class="chat-container">
        <div class="chat-header">
          <a href="/home" class="back-link">← Back</a>
          <span>SUKOON Chatbot</span>
          <div></div>
        </div>
        <div class="chat-box" id="chatBox">
          <div class="msg bot">Hello! 👋 I'm your SUKOON chatbot. How are you feeling today?</div>
        </div>
        <div class="chat-input">
          <input type="text" id="userInput" placeholder="Type your message..." />
          <button onclick="sendMessage()" id="sendButton">Send</button>
        </div>
      </div>

      <script>
        console.log('SUKOON Chatbot loaded');
        
        const chatBox = document.getElementById('chatBox');
        const userInput = document.getElementById('userInput');
        const sendButton = document.getElementById('sendButton');

        function addMessage(text, isUser = false) {
          console.log('Adding message:', text, 'isUser:', isUser);
          const msgDiv = document.createElement("div");
          msgDiv.className = "msg " + (isUser ? "user" : "bot");
          msgDiv.textContent = text;
          chatBox.appendChild(msgDiv);
          chatBox.scrollTop = chatBox.scrollHeight;
        }

        function showTyping() {
          console.log('Showing typing indicator');
          const typingDiv = document.createElement("div");
          typingDiv.className = "msg typing";
          typingDiv.id = "typing-indicator";
          typingDiv.textContent = "SUKOON is typing...";
          chatBox.appendChild(typingDiv);
          chatBox.scrollTop = chatBox.scrollHeight;
        }

        function hideTyping() {
          console.log('Hiding typing indicator');
          const typingDiv = document.getElementById("typing-indicator");
          if (typingDiv) {
            typingDiv.remove();
          }
        }

        async function sendMessage() {
          console.log('=== SEND MESSAGE CLICKED ===');
          
          const text = userInput.value.trim();
          console.log('Message:', text);
          
          if (text === "") {
            console.log('Empty message');
            return;
          }

          // Add user message
          addMessage(text, true);

          // Clear input and disable button
          userInput.value = "";
          sendButton.disabled = true;
          sendButton.textContent = "Sending...";

          // Show typing indicator
          showTyping();

          try {
            console.log('Making API request...');
            
            const response = await fetch('/api/chat', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({ message: text })
            });

            console.log('Response status:', response.status);

            if (!response.ok) {
              throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log('Response data:', data);

            hideTyping();

            if (data.response) {
              addMessage(data.response);
            } else if (data.error) {
              addMessage('Error: ' + data.error);
            } else {
              addMessage('Sorry, something went wrong. Please try again.');
            }

          } catch (error) {
            console.error('Fetch error:', error);
            hideTyping();
            
            let errorMessage = "I'm having trouble connecting right now. ";
            if (error.message.includes('Failed to fetch')) {
              errorMessage += "Please check your internet connection.";
            } else if (error.message.includes('500')) {
              errorMessage += "There's a server error. Please try again.";
            } else {
              errorMessage += "Please try again in a moment.";
            }
            
            addMessage(errorMessage);
          }

          // Re-enable button
          sendButton.disabled = false;
          sendButton.textContent = "Send";
          userInput.focus();
        }

        // Allow Enter key
        userInput.addEventListener("keypress", function(e) {
          console.log('Key pressed:', e.key);
          if (e.key === "Enter") {
            console.log('Enter pressed, sending message');
            sendMessage();
          }
        });

        // Focus input on load
        document.addEventListener('DOMContentLoaded', function() {
          console.log('DOM loaded, focusing input');
          userInput.focus();
        });

        console.log('Script loaded successfully');
      </script>
    </body>
    </html>
    '''

@app.route("/test")
def test():
    return jsonify({"status": "Server is running", "message": "API is working"})

@app.route("/api/chat", methods=["POST"])
def chat_api():
    print("=== CHAT API CALLED ===")
    print(f"Request method: {request.method}")
    print(f"Content-Type: {request.headers.get('Content-Type')}")
    
    try:
        data = request.get_json()
        print(f"Received data: {data}")
        
        if not data or 'message' not in data:
            print("ERROR: No message provided")
            return jsonify({'error': 'No message provided'}), 400
        
        message = data.get('message', '').strip()
        print(f"Message: '{message}'")
        
        if not message:
            print("ERROR: Empty message")
            return jsonify({'error': 'Empty message'}), 400
        
        # Use session ID if user is logged in, otherwise use IP
        session_id = session.get('user', request.remote_addr)
        print(f"Session ID: {session_id}")
        
        print("Calling sukoon_chat_api...")
        response = sukoon_chat_api(message, session_id)
        print(f"AI Response: {response}")
        
        return jsonify({'response': response})
        
    except Exception as e:
        print(f"CHAT API ERROR: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route("/student-dashboard")
def student_dashboard():
    if session.get("role") == "student":
        return render_template("studentdashboard.html", user=session.get("user"))
    return redirect("/login")

@app.route("/admin-dashboard")
def admin_dashboard():
    if session.get("role") == "admin":
        return render_template("admindashboard.html", user=session.get("user"))
    return redirect("/login")

if __name__ == "__main__":
    print("🌿 Starting SUKOON Flask App...")
    print("📱 Main site: http://127.0.0.1:5000")
    print("💬 Chatbot: http://127.0.0.1:5000/chatbot")
    print("🔑 Login credentials:")
    print("   Student: student@example.com / student123")
    print("   Admin: admin@example.com / admin123")

    app.run(debug=True)


