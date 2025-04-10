from flask import Flask, render_template, request, redirect, url_for
import json
import os

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

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/group/<group>')
def group_page(group):
    data = load_data()
    tasks = data.get(group, [])
    is_new = request.args.get('new') == '1'
    return render_template('group.html', group=group, tasks=tasks, is_new=is_new)

@app.route('/group/<group>/add_task', methods=['POST'])
def add_task(group):
    task = request.form['task']
    amount = request.form.get('amount')
    note = request.form.get('note')
    name = request.form.get('name')
    child = request.form.get('child')
    deadline = request.form.get('deadline')

    data = load_data()
    data.setdefault(group, []).append({
        'task': task,
        'amount': amount,
        'note': note,
        'assigned_to': name,
        'child_name': child,
        'deadline': deadline,
        'completed': False
    })
    save_data(data)
    return redirect(url_for('group_page', group=group))

@app.route('/group/<group>/update_amount/<int:task_id>', methods=['POST'])
def update_amount(group, task_id):
    change = int(request.form['change'])
    data = load_data()
    task = data[group][task_id]
    try:
        task['amount'] = str(max(0, int(task.get('amount') or 0) + change))
    except ValueError:
        task['amount'] = '0'
    save_data(data)
    return redirect(url_for('group_page', group=group))

@app.route('/group/<group>/update_note/<int:task_id>', methods=['POST'])
def update_note(group, task_id):
    note = request.form.get('note')
    data = load_data()
    data[group][task_id]['note'] = note
    data[group][task_id]['editing_note'] = False
    save_data(data)
    return redirect(url_for('group_page', group=group))

@app.route('/group/<group>/edit_note/<int:task_id>', methods=['POST'])
def edit_note(group, task_id):
    data = load_data()
    for task in data.get(group, []):
        task['editing_note'] = False
    data[group][task_id]['editing_note'] = True
    save_data(data)
    return redirect(url_for('group_page', group=group))

@app.route('/group/<group>/update_deadline/<int:task_id>', methods=['POST'])
def update_deadline(group, task_id):
    deadline = request.form.get('deadline')
    data = load_data()
    data[group][task_id]['deadline'] = deadline
    save_data(data)
    return redirect(url_for('group_page', group=group))

@app.route('/group/<group>/take_task/<int:task_id>', methods=['POST'])
def take_task(group, task_id):
    name = request.form['name']
    child = request.form.get('child')
    data = load_data()
    data[group][task_id]['assigned_to'] = name
    data[group][task_id]['child_name'] = child
    save_data(data)
    return redirect(url_for('group_page', group=group))

@app.route('/group/<group>/release_task/<int:task_id>', methods=['POST'])
def release_task(group, task_id):
    data = load_data()
    data[group][task_id]['assigned_to'] = None
    data[group][task_id]['child_name'] = None
    save_data(data)
    return redirect(url_for('group_page', group=group))

@app.route('/group/<group>/complete_task/<int:task_id>', methods=['POST'])
def complete_task(group, task_id):
    data = load_data()
    data[group][task_id]['completed'] = True
    save_data(data)
    return redirect(url_for('group_page', group=group))

@app.route('/group/<group>/delete_task/<int:task_id>', methods=['POST'])
def delete_task(group, task_id):
    data = load_data()
    if group in data and 0 <= task_id < len(data[group]):
        data[group].pop(task_id)
    save_data(data)
    return redirect(url_for('group_page', group=group))

if __name__ == '__main__':
    app.run(debug=True)
