from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy # 追加
from datetime import datetime, date

app = Flask(__name__)

# データベースの設定（sqliteというファイルに保存しますという指定）
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://todo_list_yjzj_user:xCQtpVP90jdYBDZDbRQMFN45cx9Y4j7Y@dpg-d7ief6ho3t8c73arsijg-a.virginia-postgres.render.com/todo_list_yjzj"

db = SQLAlchemy(app)

# データベースのテーブル（表）の形を決める
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True) # 番号（自動でつく）
    content = db.Column(db.String(200), nullable=False) # 内容
    subject = db.Column(db.String(10), nullable=False) #教科
    deadline = db.Column(db.Date, nullable=False) #締切日
    done = db.Column(db.Boolean, default=False) # やったかどうか

# 最初に一回だけ実行して、空のデータベースファイルを作るおまじない
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    # データベースから全てのタスクを読み出す
    todos = Todo.query.order_by(Todo.deadline).all()
    
    #今日の日付
    today = date.today()
    
    # 各タスクに「残り日数」を追加
    for t in todos:
        t.remaining_days = (t.deadline - today).days
    
    return render_template('index.html', todos=todos)

@app.route('/add', methods=['POST'])
def add():
    task_content = request.form.get('task')
    task_subject = request.form.get('subject')
    task_deadline_str = request.form.get('deadline')

    if task_content and task_subject and task_deadline_str:
        #"2026-04-20" →date型に変換
        task_deadline = datetime.strptime(task_deadline_str, "%Y-%m-%d").date()
        
        # データベースに新しい行を追加する
        new_task = Todo(
            subject=task_subject,
            content=task_content,
            deadline=task_deadline
        )
        db.session.add(new_task)
        db.session.commit() # 「保存！」と確定させる
        
    return redirect(url_for('home'))

@app.route('/check/<int:index>')
def check(index):
    # IDを使って特定のタスクを探す（indexではなくIDを使うのがDB流）
    task = Todo.query.get(index)
    if task:
        task.done = not task.done
        db.session.commit()
    return redirect(url_for('home'))

@app.route('/delete/<int:index>')
def delete(index):
    task = Todo.query.get(index)
    if task:
        db.session.delete(task)
        db.session.commit()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
