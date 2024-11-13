from flask import Flask, render_template, jsonify, request, session,redirect,url_for
import random
import json
import os
from flask_session import Session

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SESSION_TYPE'] = 'filesystem'  # Store sessions in a temporary filesystem directory
Session(app)

def initialize_session(questions):
    # Initialize session variables
    session['score'] = 0
    session['wrong_attempts'] = 0
    session['current_question'] = 0
    session['questions'] = random.sample(questions, len(questions))
    session['attempts'] = {}
    
QUESTIONS_FOLDER = 'bizz skills/questions'

@app.route('/')
def index():
    # List all JSON files in the questions folder and remove '.json' from the filenames
    question_files = [f.replace('.json', '') for f in os.listdir(QUESTIONS_FOLDER) if f.endswith('.json')]
    return render_template('index.html', question_files=question_files)

@app.route('/load_questions', methods=['POST'])
def load_questions():
    selected_file = request.json['file_name'] + '.json'  # Append .json back for loading
    file_path = os.path.join(QUESTIONS_FOLDER, selected_file)
    
    # Load the selected JSON file
    with open(file_path, 'r',encoding="utf8") as f:
        questions = json.load(f)
    
    initialize_session(questions)
    
    return jsonify('sucess')

@app.route('/quiz', methods=['GET'])
def quiz():
    if 'current_question' not in session or session['current_question'] >= len(session['questions']):
        return redirect(url_for('index'))
    
    current_question = session['questions'][session['current_question']]
    random.shuffle(current_question['options'])
    return render_template('quiz.html', question=current_question, score=session['score'], wrong_attempts=session['wrong_attempts'], question_index=session['current_question'], total_questions=len(session['questions']))

@app.route('/check_answer', methods=['POST'])
def check_answer():
    selected_options = request.json.get('selected_options')
    question_index = session['current_question']
    current_question = session['questions'][question_index]
    correct_answer = current_question['answer']

    # Strip extra spaces before comparison
    selected_options = [option.strip() for option in selected_options]
    correct_answer = [option.strip() for option in correct_answer]
    
    # Check answer
    if set(selected_options) == set(correct_answer):
        if question_index not in session['attempts']:  # First correct attempt
            session['score'] += 1
            session['attempts'][question_index] = True
        return jsonify({'result': 'correct', 'score': session['score']})
    else:
        session['wrong_attempts'] += 1
        return jsonify({'result': 'incorrect', 'score': session['score']})

@app.route('/next', methods=['POST'])
def next_question():
    session['current_question'] += 1
    return jsonify({'status': 'next'})

@app.route('/previous', methods=['POST'])
def previous_question():
    if session['current_question'] > 0:
        session['current_question'] -= 1
    return jsonify({'status': 'previous'})

@app.route('/reset', methods=['POST'])
def reset():
    initialize_session()
    return jsonify({'status': 'reset'})

if __name__ == '__main__':
    app.run(debug=True)