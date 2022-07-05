import json
import os

def get_answers():
    path = os.path.join(os.getcwd(), 'answers.json')
    with open(path, 'r') as ans_file:
        answers = json.load(ans_file)
    return answers


answers: dict = get_answers()

