from flask import Flask, request, jsonify, render_template
import openai
from flask_cors import CORS
from Database import Database
from SentEmail import send_email  # SentEmail fonksiyonunu import ediyoruz
import threading

app = Flask(__name__, template_folder='templates')

# Set your OpenAI API key
api_key = "sk-proj-88ZmclgKFJHgSiXSpQTGT3BlbkFJQjnSbrDZ8zrdaAe4Pxjp"
openai.api_key = api_key

@app.route('/prediction_result')
def prediction_result():
    return render_template('prediction_result.html')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict_disease', methods=['POST'])
def predict_disease():
    data = request.get_json()
    symptoms = data.get('symptoms')
    age = data.get('age')
    height = data.get('height')
    weight = data.get('weight')
    email = data.get('email')
    ticked = data.get('ticked')

    conversation = [
        {"role": "system", "content": "You are a medical assistant, skilled in predicting diseases based on symptoms."},
        {"role": "user", "content": f"My age is: {age}. My height is: {height} cm. My weight is: {weight} kg. My symptoms are: {symptoms}. What is my disease?"}
    ]

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation
    )
    
    prediction = completion.choices[0].message["content"]

    if ticked:
        db = Database()
        db.save_email(email)
        
        # E-posta gönderme zamanlayıcıları
        first_email_subject = "How are you feeling today?"
        first_email_body = " If you don't feel good today,visit our website again."
        second_email_subject = "It's been a week, how are you?"
        second_email_body = " It's been a week since you visited our site. How are you feeling?"

        # E-posta gönderme zamanlayıcıları
        threading.Timer(60, send_email, args=(email, first_email_subject, first_email_body, "Visit our website page", 'sentEmail')).start()  # 1 dakika sonra
        threading.Timer(120, send_email, args=(email, second_email_subject, second_email_body, "Visit our website page again", 'sentEmail2')).start()  # 2 dakika sonra
    
    return jsonify({"prediction": prediction})

@app.route('/send_message_to_chatgpt', methods=['POST'])
def send_message_to_chatgpt():
    predicted_disease = request.json.get('prediction')
    user_message = request.json.get('user_message')
        
    conversation = [
        {"role": "system", "content": "You are a medical assistant, skilled in predicting diseases based on symptoms."},
        {"role": "assistant", "content": f"I predicted your disease as: {predicted_disease}."},
        {"role": "user", "content": user_message}
    ]

    chatgpt_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation
    )
    
    response_text = chatgpt_response.choices[0].message["content"]

    return jsonify({'message': response_text})

if __name__ == '__main__':
    app.run(debug=True)
