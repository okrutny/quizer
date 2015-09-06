# -*- coding: utf-8 -*-
"""
Quizer - a quiz application created with Flask.
"""

import os
from flask import Flask, session, request, render_template, redirect, url_for
import csv
import pprint
import copy
from random import choice
import datetime

pp = pprint.PrettyPrinter(indent=4)

# create app and initialize config
app = Flask(__name__)

app.config.update(dict(
    DEBUG=True
))
app.config.from_envvar('QUIZER_SETTINGS', silent=False)


questions_list = []


@app.route('/', methods=['GET', 'POST'])
def welcome_page():
    """
    Welcome page - quiz info and username form.
    """
    username = session.get('username')

    if request.method == 'POST':
        if not username:
            username = session['username'] = request.form['username']
        if username:
            if not questions_list:
                with open('data/quiz.csv', 'rb') as csvfile:
                    spamreader = csv.reader(csvfile, delimiter=';', quotechar='|')
                    for row in spamreader:
                        q = unicode(row.pop(0), "utf8")
                        correct_answer_letter = row.pop()
                        #correct_answer = ord(correct_answer_letter)-ord('A')
                        answers_dict = {}
                        for i, answer in enumerate(row):
                            
                            answers_dict.update({unichr(i+ord('A')):unicode(answer, "utf8")})
                            
                        questions_list.append({'correct':correct_answer_letter, 'answers':answers_dict, 'question':q})
                            
                pp.pprint(questions_list)
            
            session['user_questions'] = copy.deepcopy(questions_list)
            session['answered_questions_count'] = session['correct_answers'] = session['points'] = 0
            
            return redirect(url_for('question_page'))

    return render_template('welcome.html', username=username)


@app.route('/pytanie', methods=['GET', 'POST'])
def question_page():
    """
    Quiz question page - show question, handle answer.
    """
    
    if request.method == 'GET':
        
        
        question = choice(session['user_questions'])
        q_index = session['user_questions'].index(question)
        
        print question['question']
        
        session['start_time'] = datetime.datetime.now()
        
        return render_template('question.html', question=question, q_index=q_index)
        
    else:
        
        answer = request.form['user_answer']
        q_index = int(request.form['q_index'])
        
        session['answered_questions_count'] +=1
        session['correct_answers'] +=1

        question = session['user_questions'][q_index]
        del session['user_questions'][q_index]

        session['points'] += _calc_user_points(datetime.datetime.now() - session['start_time'], question['correct'] == answer)
        
        if session['answered_questions_count'] == 5:
            return redirect(url_for("result_page"))
        else:
            return redirect(url_for("question_page"))


def _calc_user_points(timedelta_diff, correct):
    
    if not correct:
        return 0
        
    else:
        print timedelta_diff
        dir(timedelta_diff)
        if timedelta_diff.total_seconds() < 10:
            return 3
        elif timedelta_diff.total_seconds() < 30:
            return 2
        else:
            return 1
        
    
    # ToDo


@app.route('/wynik')
def result_page():
    """
    Last page - show results.
    """
    
    return render_template('results.html', username=session['username'], correct_answers=session['correct_answers'], points=session['points'])


if __name__ == '__main__':
    app.run(
        host=os.getenv('IP', '0.0.0.0'),
        port=int(os.getenv('PORT', '8080'))
    )
