from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from openai import OpenAI
from dotenv import load_dotenv
import os


load_dotenv()

application = Flask(__name__)
application.secret_key = os.getenv('SECRET_KEY')

# Set up logging
logging.basicConfig(level=logging.INFO)


@application.route('/')
def index():
    return render_template('index.html')

@application.route('/send_message', methods=['POST'])
def send_message_route():
    name = request.form.get("name")
    email = request.form.get("email")
    message = request.form.get("message")

    # Check if all fields are completed
    if not name or not email or not message:
        flash('All fields are required!', 'danger')
        return redirect(url_for('index'))

    # Combine name, email, and message into a single string to return
    full_message = f"Name: {name}\nEmail: {email}\nMessage: {message}"

    try:
        # Create the email content
        msg = MIMEMultipart()
        msg['From'] = os.getenv('GMAIL_USERNAME')
        msg['To'] = os.getenv('GMAIL_USERNAME')
        msg['Subject'] = "Dube Travels Website Contact Form Submission"

        # Attach the message
        msg.attach(MIMEText(full_message, 'plain'))

        # Connect to the server and send the email
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(os.getenv('GMAIL_USERNAME'), os.getenv('GOOGLE_PASSWORD'))  # Hide before GitHub push
        server.send_message(msg)
        server.quit()

        flash('Message sent successfully!', 'success')
    except smtplib.SMTPAuthenticationError as e:
        logging.error(f"SMTP Authentication Error: {e}")
        flash(f'Failed to send message. Error: {str(e)}', 'danger')
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        flash(f'Failed to send message. Error: {str(e)}', 'danger')

    return redirect(url_for('index'))


@application.route('/chat_assistant', methods=['POST'])
def chat_assistant_route():
    user_message = request.json.get("message")

    client = OpenAI(
        # This is the default and can be omitted
        api_key = os.getenv('OPENAI_API_KEY')
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": user_message,
            }
        ],
        model="gpt-3.5-turbo",
    )

    # Access the content using the 'message' attribute of the Choice object
    assistant_message = chat_completion.choices[0].message.content
    print(assistant_message)
    return jsonify({"message": assistant_message})


if __name__ == '__main__':
    application.run(host='0.0.0.0', port=8000, debug=True)
