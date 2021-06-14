from flask import Flask, request
from celery.result import AsyncResult
from flask_mail import Mail, Message
from celery import Celery

flask_app = Flask(__name__)
flask_app.config.from_object("config")
celery_app = Celery('tasks', broker='redis://0.0.0.0:6379/2', backend='redis://0.0.0.0:6379/3')
mail = Mail(flask_app)
celery_app.conf.update(flask_app.config)


@celery_app.task
def send_mail(data):
    with flask_app.app_context():
        msg = Message("Ping!",
                      sender="admin.ping",
                      recipients=[data['email']])
        msg.body = data['message']
        mail.send(msg)


@flask_app.route('/mail', methods=['POST'])
def sender():
    if request.method == 'POST':
        data = {'email': 'sender@mail.com', 'message': 'test message'}
        result = send_mail.apply_async(args=[data])
        print(result)
        return result.id


@flask_app.route('/mail/<task_id>/', methods=['GET'])
def index(task_id):
    if request.method == 'GET':
        result = AsyncResult(task_id)
        return result.state()


if __name__ == '__main__':
    flask_app.run(debug=True)
