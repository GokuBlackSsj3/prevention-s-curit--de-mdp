from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import os
import json
from datetime import datetime
try:
    import dotenv
    dotenv.load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed. Environment variables may not be loaded from .env file.")
from openai import OpenAI
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
CORS(app)

# Initialize OpenAI client with API key from environment variable
client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY')
)

SYSTEM_MESSAGE = """Tu es un assistant expert en sécurité des mots de passe qui aide les utilisateurs à comprendre 
les bonnes pratiques de sécurité. Tu fournis des conseils clairs et précis en français sur:
- La création de mots de passe forts
- La gestion sécurisée des mots de passe
- Les risques de sécurité à éviter
- La double authentification
- La protection contre le phishing
Réponds toujours en français de manière professionnelle et concise."""

conversations = {}

@app.route('/api/ai-chat', methods=['POST'])
def ai_chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        user_id = data.get('user_id', 'default_user')

        if not user_message:
            return jsonify({'error': 'No message provided'}), 400

        if user_id not in conversations:
            conversations[user_id] = [{"role": "system", "content": SYSTEM_MESSAGE}]

        conversations[user_id].append({"role": "user", "content": user_message})

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=conversations[user_id],
                max_tokens=150,
                temperature=0.7,
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            conversations[user_id].append({"role": "assistant", "content": ai_response})
            
            if len(conversations[user_id]) > 12:
                conversations[user_id] = [conversations[user_id][0]] + conversations[user_id][-10:]
            
            return jsonify({'response': ai_response})

        except Exception as e:
            print(f"OpenAI API error: {str(e)}")
            return jsonify({
                'response': "Désolé, je rencontre des difficultés techniques. Veuillez réessayer plus tard."
            }), 500

    except Exception as e:
        print(f"Server error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

def save_to_json(data):
    try:
        # Read existing results
        results = []
        if os.path.exists('survey_results.json'):
            with open('survey_results.json', 'r') as f:
                results = json.load(f)
        
        # Add timestamp to data
        data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Append new result
        results.append(data)
        
        # Save back to file
        with open('survey_results.json', 'w') as f:
            json.dump(results, f, indent=2)
            
    except Exception as e:
        print(f"Error saving to JSON: {str(e)}")

@app.route('/api/survey-results', methods=['GET'])
def get_survey_results():
    try:
        password = request.args.get('password')
        if password != os.getenv('ADMIN_PASSWORD', 'passballs'):  # Default password if not set
            return jsonify({'error': 'Unauthorized'}), 401

        if os.path.exists('survey_results.json'):
            with open('survey_results.json', 'r') as f:
                results = json.load(f)
            return jsonify(results)
        return jsonify([])
    except Exception as e:
        print(f"Error reading results: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/send-survey-results', methods=['POST'])
def send_survey_results():
    try:
        data = request.get_json()
        username = data.get('username', 'Anonyme')
        score = data.get('score', 0)
        total = data.get('total', 5)
        answers = data.get('answers', [])

        # Always store in JSON file first (this will always work)
        save_to_json(data)
        
        # Try to send email (this might fail if email config is not set)
        try:
            # Compose email content
            body = f"Résultats du quiz de {username}:\n\n"
            body += f"Score: {score} / {total}\n\n"
            body += "Réponses:\n"
            for i, ans in enumerate(answers, 1):
                body += f"Q{i}: {ans}\n"

            # Email configuration
            sender_email = os.getenv('SENDER_EMAIL')
            sender_password = os.getenv('SENDER_PASSWORD')
            receiver_email = "collectenquetes@gmail.com"

            if sender_email and sender_password:
                message = MIMEMultipart()
                message["From"] = sender_email
                message["To"] = receiver_email
                message["Subject"] = f"Résultats du quiz de {username}"

                message.attach(MIMEText(body, "plain"))

                # Send email via Gmail SMTP
                with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                    server.login(sender_email, sender_password)
                    server.sendmail(sender_email, receiver_email, message.as_string())
                    
                print(f"Email sent successfully to {receiver_email}")
            else:
                print("Email credentials not configured, skipping email send")
                
        except Exception as email_error:
            print(f"Email sending failed: {str(email_error)}")
            # Don't fail the whole request if email fails
        
        return jsonify({'message': 'Résultats enregistrés avec succès'})

    except Exception as e:
        print(f"Survey results error: {str(e)}")
        return jsonify({'error': 'Erreur lors de l\'enregistrement'}), 500

@app.route('/webhook/survey', methods=['POST', 'OPTIONS'])
@cross_origin()
def webhook_survey():
    if request.method == 'OPTIONS':
        return '', 200
    """Simple webhook endpoint for collecting surveys from any source"""
    try:
        data = request.get_json()
        
        # Save to JSON file
        save_to_json(data)
        
        # Try to send email
        try:
            body = json.dumps(data, indent=2)  # Pretty print the JSON data
            
            sender_email = os.getenv('SENDER_EMAIL')
            sender_password = os.getenv('SENDER_PASSWORD')
            receiver_email = "collectenquetes@gmail.com"

            if sender_email and sender_password:
                message = MIMEMultipart()
                message["From"] = sender_email
                message["To"] = receiver_email
                message["Subject"] = f"Nouvelle réponse au sondage"
                message.attach(MIMEText(body, "plain"))

                with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                    server.login(sender_email, sender_password)
                    server.sendmail(sender_email, receiver_email, message.as_string())
        except Exception as email_error:
            print(f"Webhook email sending failed: {str(email_error)}")
            
        return jsonify({'success': True})
    except Exception as e:
        print(f"Webhook error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
