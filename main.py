
from flask import Flask, jsonify, abort, make_response, request, url_for
from flask_httpauth import HTTPBasicAuth

app = Flask(__name__)
auth = HTTPBasicAuth()

tasks = [{
		'id':1,
		'title': u'Buy Chocolates',
		'description': u'Nestle, Milkibar, Dairy Milk',
		'done': False
		},
		{
		'id':2,
		'title': u'Learn Python',
		'description': u'Find a good python tutorial online',
		'done': False
		}]

'''
Securing the API
'''
@auth.get_password
def get_password(username):
	if username == 'shivam':
		return 'python'
	return None

@auth.error_handler
def unauthorized():
	return make_response(jsonify({ 'error': 'unauthorized Access' }), 403)

'''
Method to convert taskid into task URI
'''
def make_public_task(task):
	new_task = {}
	for field in task:
		if field == 'id':
			new_task['uri'] = url_for('get_task', task_id = task['id'], _external = True)
		else:
			new_task[field] = task[field]
	return new_task

'''
PUT implementation: Updation of new task
'''
@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods = ['PUT'])
@auth.login_required
def update_task(task_id):
	task = filter(lambda t:t['id'] == task_id, tasks)
	if len(task) == 0:
		abort(400)
	if not request.json:
		abort(400)
	if 'title' in request.json and type(request.json['description']) != unicode:
		abort(400)
	if 'description' in request.json and type(request.json['description']) != unicode:
		abort(400)
	if 'done' in request.json and type(request.json['done']) != bool:
		abort(400)

	task[0]['title'] = request.json.get('title', task[0]['title'])
	task[0]['description'] = request.json.get('description', task[0]['description'])
	task[0]['done'] = request.json.get('done', task[0]['done'])
	return jsonify({ 'task' : task[0] })

'''
DELETE implementation: deleting an existing task
'''
@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods = ['DELETE'])
@auth.login_required
def delete_task(task_id):
	task = filter(lambda t: t['id'] == task_id, tasks)
	if len(task) == 0:
		abort(400)
	tasks.remove(task[0])
	return jsonify({ 'result': True })
	
'''
POST implementation: creation of new task
'''
@app.route('/todo/api/v1.0/tasks', methods = ['POST'])
@auth.login_required
def create_task():
	if not request.json or not 'title' in request.json:
		abort(400)
	task = {
	'id': tasks[-1]['id']+1,
	'title': request.json['title'],
	'description': request.json.get('description', ""),
	'done': False
	}
	tasks.append(task)
	return jsonify({ 'task' : task }),201

'''
GET implementation: get a particular task
'''
@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods = ['GET'])
@auth.login_required
def get_task(task_id):
	task = filter(lambda t: t['id'] == task_id, tasks)
	if len(task) == 0:
		abort(404)
	return jsonify({ 'task' : task[0] })

'''
GET implementation: get list of all tasks
'''
@app.route('/todo/api/v1.0/tasks', methods = ['GET'])
# @auth.login_required
def get_tasks():
	return jsonify({ 'tasks' : map(make_public_task, tasks) })

@app.errorhandler(404)
def not_found(error):
	return make_response(jsonify({ 'error' : 'Not Found' }), 404)

if __name__ == '__main__':
	app.run(debug = True)