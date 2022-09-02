import json
from pathlib import Path

def get_answers():
    path = Path(Path(__file__).parent, 'answers.json')
    with open(path, 'r') as ans_file:
        answers = json.load(ans_file)
    return answers


answers: dict = get_answers()

