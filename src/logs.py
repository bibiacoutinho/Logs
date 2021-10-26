from flask import Flask
from flask import request
from flask_cors import CORS
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref 
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:mariadb@localhost:3306/teste'
engine = create_engine('mysql+mysqlconnector://root:mariadb@localhost:3306/teste')

db = SQLAlchemy(app)

class Tipo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    operacao = db.Column(db.String(50))
    calculos = db.relationship('Log', backref='tipo')

    def __init__(self, operacao):
        self.operacao = operacao

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    operacao = db.Column(db.String(50))
    data = db.Column(db.DateTime, default=datetime.now)
    n1 = db.Column(db.String(1000))
    n2 = db.Column(db.String(1000))
    tipo_id = db.Column(db.Integer, db.ForeignKey('tipo.id'))

@app.route('/logs', methods=['POST'])
def index():
    opr = request.form.get('opr')
    n1 = request.form.get('n1')
    n2 = request.form.get('n2')

    with Session(engine) as session:
        resultado_elementar = search('Elementar')

        if not resultado_elementar:
            elementar = Tipo(operacao='Elementar')
            session.add(elementar)
            session.commit()
            resultado_elementar = search('Elementar')
        
        resultado_transcendental = search('Transcendental')

        if not resultado_transcendental:
            transcendental = Tipo(operacao='Transcendental')
            session.add(transcendental)
            session.commit()
            resultado_transcendental = search('Transcendental')

        if opr == 'seno':
            log = Log(n1=n1, operacao='seno', tipo_id=resultado_transcendental[0].id)
        elif opr == 'soma':
            log = Log(n1=n1, n2=n2, operacao='soma', tipo_id=resultado_elementar[0].id)
        else:
            log = Log(n1=n1, n2=n2, operacao='subt', tipo_id=resultado_elementar[0].id)
        session.add(log)
        session.commit()
    return 

def search(string):
    with Session(engine) as session:
        search = select(Tipo).where(Tipo.operacao == string)
        selected = session.execute(search)
        resultado = selected.scalars().all()
        return resultado

db.create_all()

if __name__=='__main__':
    app.run(host='0.0.0.0', port=5005)