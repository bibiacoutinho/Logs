from flask import Flask
from flask import request
from flask_cors import CORS
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref 
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
import json

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:mariadb@localhost:3306/calculadora'
engine = create_engine('mysql+mysqlconnector://root:mariadb@localhost:3306/calculadora')

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

db.create_all()

@app.route('/logs', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        with Session(engine) as session:
            opr = request.form.get('opr')
            n1 = request.form.get('n1')
            n2 = request.form.get('n2')
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
                n2 = 0
                log = Log(n1=n1, n2=n2, operacao='seno', tipo_id=resultado_transcendental[0].id)
            elif opr == 'soma':
                log = Log(n1=n1, n2=n2, operacao='soma', tipo_id=resultado_elementar[0].id)
            else:
                log = Log(n1=n1, n2=n2, operacao='subt', tipo_id=resultado_elementar[0].id)
            session.add(log)
            session.commit()
        return 'Log inserido.'
    else:
        with Session(engine) as session:
            lista = []
            for log in session.query(Log).join(Tipo, Tipo.id == Log.tipo_id).all():
                lista.append({"n1":log.n1, "n2": log.n2, "operacao": log.operacao, "data":log.data.strftime("%d/%m/%Y"), "tipo": log.tipo.operacao})
        return json.dumps(lista)

def search(string):
    with Session(engine) as session:
        search = select(Tipo).where(Tipo.operacao == string)
        selected = session.execute(search)
        resultado = selected.scalars().all()
        return resultado


if __name__=='__main__':
    app.run(host='0.0.0.0', port=5005)