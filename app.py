import json
import logging

from flask import Flask, Response, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import psycopg2
import logging
import requests
from flask_cors import CORS


logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.INFO)
logger = logging.getLogger("main-app")


app = Flask(__name__)
CORS(app)

# Configuração de banco de dados
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:wlfc@localhost:5432/perfil'

db = SQLAlchemy(app)


# Entidade
class Modelo(db.Model):
    __tablename__ = 'tb_modelo'
    id = db.Column(db.INTEGER, primary_key=True)
    nome = db.Column(db.String(50))
    url_foto = db.Column(db.String(50))

    # Formato de retorno
    def to_json(self):
        return {"id": self.id, "nome": self.nome, "url_foto": self.url_foto}

# Selecionar tudo
@app.route("/modelos", methods=["GET"])
def listar_modelos():
    lista_modelos = Modelo.query.all()
    #print(lista_modelos)

    modelos_json = [modelo.to_json() for modelo in lista_modelos]

    logger.info("Listando modelos")

    return gera_response(200, "modelos", modelos_json, f"{len(lista_modelos)} itens")


# Selecionar um
@app.route("/modelo/<modelo_id>", methods=["GET"])
def modelo_por_id(modelo_id):
    logger.info("Modelo por ID")
    try:
        modelo = Modelo.query.filter_by(id=modelo_id).first()
        modelo_json = modelo.to_json()

        logger.info({"Modelo": modelo_json})

        return gera_response(200, "modelo", modelo_json, "ok")
    except Exception as e:
        logger.error("Modelo não encontrada")
        return gera_response(404, "modelo", {}, "Modelo não encontrada")


# Cadastrar
@app.route("/modelo", methods=["POST"])
def criar_modelo():
    body = request.get_json()
    logger.info("Cadastrar modelo")
    logger.info({"body": body})

    try:
        modelo = Modelo(nome=body["nome"], url_foto=body["url_foto"])
        db.session.add(modelo)
        db.session.commit()
        return gera_response(201, "modelo", modelo.to_json(), "Criado com sucesso!")
    except Exception as e:
        print(f"Erro: {e}")
        return gera_response(400, "modelo", {}, "Erro ao cadastrar")


# Atualizar
@app.route("/modelo/<modelo_id>", methods=["PUT"])
def atualizar_modelo(modelo_id):
    dados_modelo = request.get_json()

    modelo = Modelo.query.filter_by(id=modelo_id).first()

    print(f"Modelo encontrada: {modelo.nome}")

    try:
        for atributo in dados_modelo.keys():
            if dados_modelo[atributo] != "":
                if atributo == 'url_foto':
                    modelo.url_foto = dados_modelo[atributo]
                if atributo == 'nome':
                    modelo.nome = dados_modelo[atributo]

        db.session.add(modelo)
        db.session.commit()
        return gera_response(200, "modelo", modelo.to_json(), "Modelo atualizada com sucesso!")
    except Exception as e:
        print(f"Erro {e}")
        return gera_response(400, "modelo", {}, "Erro ao atualizar modelo")


# Deletar
@app.route("/modelo/<modelo_id>", methods=["DELETE"])
def deletar_modelo(modelo_id):
    try:
        modelo = Modelo.query.filter_by(id=modelo_id).first()
        db.session.delete(modelo)
        db.session.commit()
        return gera_response(200, "modelo", modelo.to_json(), "Medelo excluida com sucesso!")
    except Exception as e:
        print(f"Erro: {e}")
        return gera_response(404, "modelo", {}, "Medelo não encontrada!")




# Gerar um response Entity personalizado
def gera_response(status, nome_do_conteudo, conteudo, mensagem=False):
    body = {nome_do_conteudo: conteudo}

    if mensagem:
        body["mensagem"] = mensagem

    return Response(json.dumps(body), status=status, mimetype="application/json")


if __name__ == '__main__':

    app.run()
