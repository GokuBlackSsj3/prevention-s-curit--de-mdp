from flask import Flask, request, jsonify
from flask_cors import CORS
import os
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

@app.route('/api/send-survey-results', methods=['POST'])
def send_survey_results():
    try:
        data = request.get_json()
        username = data.get('username', 'Anonyme')
        score = data.get('score', 0)
        total = data.get('total', 5)
        answers = data.get('answers', [])

        # Compose email content
        body = f"Résultats du quiz de {username}:\n\n"
        body += f"Score: {score} / {total}\n\n"
        body += "Réponses:\n"
        for i, ans in enumerate(answers, 1):
            body += f"Q{i}: {ans}\n"

        # Email configuration
        sender_email = os.getenv('SENDER_EMAIL')  # Set in .env
        sender_password = os.getenv('SENDER_PASSWORD')  # Set in .env
        receiver_email = "sadekmoussaceb@gmail.com"

        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = f"Résultats du quiz de {username}"

        message.attach(MIMEText(body, "plain"))

        # Send email via Gmail SMTP
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, message.as_string())

        return jsonify({'message': 'Email envoyé avec succès'})

    except Exception as e:
        print(f"Email sending error: {str(e)}")
        return jsonify({'error': 'Erreur lors de l\'envoi de l\'email'}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
