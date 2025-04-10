# app.py
from flask import Flask, render_template, request, redirect, url_for
import json
import os
import uuid

app = Flask(__name__)

DATA_FILE = 'data.json'

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        base_name = request.form['group_name'].strip().replace(' ', '-').lower()
        unique_id = uuid.uuid4().hex[:6]
        full_group_name = f"{base_name}-{unique_id}"
        return redirect(url_for('group_view', group_name=full_group_name, new='1'))
    return render_template('index.html')

@app.route('/group/<group_name>')
def group_view(group_name):
    data = load_data()
    group_data = data.get(group_name, [])
    is_new = request.args.get('new') == '1'
    return render_template('group.html', group=group_name, tasks=group_data, is_new=is_new)

@app.route('/group/<group_name>/add_task', methods=['POST'])
def add_task(group_name):
    task = request.form['task']
    amount = request.form.get('amount', '')
    note = request.form.get('note', '')
    name = request.form.get('name', '')
    child = request.form.get('child', '')
    deadline = request.form.get('deadline', '')

    data = load_data()
    if group_name not in data:
        data[group_name] = []
    data[group_name].append({
        'task': task,
        'amount': amount,
        'note': note,
        'assigned_to': name,
        'child_name': child,
        'deadline': deadline,
        'completed': False
    })
    save_data(data)
    return redirect(url_for('group_view', group_name=group_name))

@app.route('/group/<group_name>/take_task/<int:task_id>', methods=['POST'])
def take_task(group_name, task_id):
    name = request.form['name']
    child = request.form.get('child', '')
    data = load_data()
    if group_name in data and 0 <= task_id < len(data[group_name]):
        data[group_name][task_id]['assigned_to'] = name
        data[group_name][task_id]['child_name'] = child
        save_data(data)
    return redirect(url_for('group_view', group_name=group_name))

@app.route('/group/<group_name>/release_task/<int:task_id>', methods=['POST'])
def release_task(group_name, task_id):
    data = load_data()
    if group_name in data and 0 <= task_id < len(data[group_name]):
        data[group_name][task_id]['assigned_to'] = ''
        data[group_name][task_id]['child_name'] = ''
        save_data(data)
    return redirect(url_for('group_view', group_name=group_name))

@app.route('/group/<group_name>/complete_task/<int:task_id>', methods=['POST'])
def complete_task(group_name, task_id):
    data = load_data()
    if group_name in data and 0 <= task_id < len(data[group_name]):
        data[group_name][task_id]['completed'] = True
        save_data(data)
    return redirect(url_for('group_view', group_name=group_name))

@app.route('/group/<group_name>/update_amount/<int:task_id>', methods=['POST'])
def update_amount(group_name, task_id):
    change = int(request.form['change'])
    data = load_data()
    if group_name in data and 0 <= task_id < len(data[group_name]):
        current = data[group_name][task_id].get('amount') or '0'
        try:
            current_int = int(current)
        except ValueError:
            current_int = 0
        new_amount = max(0, current_int + change)
        data[group_name][task_id]['amount'] = str(new_amount)
        save_data(data)
    return redirect(url_for('group_view', group_name=group_name))

@app.route('/group/<group_name>/update_note/<int:task_id>', methods=['POST'])
def update_note(group_name, task_id):
    new_note = request.form['note']
    data = load_data()
    if group_name in data and 0 <= task_id < len(data[group_name]):
        data[group_name][task_id]['note'] = new_note
        save_data(data)
    return redirect(url_for('group_view', group_name=group_name))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
