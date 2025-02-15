from flask import Flask, request, jsonify
from flask_cors import CORS
import mercadopago
import logging
from datetime import datetime, timedelta
import sqlite3

app = Flask(__name__)
# Configuração mais permissiva do CORS
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Accept"]
    }
})

# Configuração de logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Configuração do Mercado Pago
mp = mercadopago.SDK(
    "TEST-1786945267929753-021510-056e7cd0d9efa00f6aa03af162ba0a58-403922089")


@app.route('/ping', methods=['GET'])
def ping():
    logger.info("Ping recebido")
    response = jsonify({"status": "ok", "message": "Server is running"})
    return response


@app.route('/gerar-pix', methods=['POST'])
def gerar_pix():
    try:
        logger.info("Recebendo requisição PIX")
        dados = request.json
        logger.info(f"Dados recebidos: {dados}")

        payment_data = {
            "transaction_amount": float(dados['valor']),
            "description": f"Barbearia - {dados['servico']}",
            "payment_method_id": "pix",
            "payer": {
                "email": "test@test.com",
                "first_name": dados['nome'],
                "identification": {
                    "type": "CPF",
                    "number": "19119119100"
                }
            }
        }

        logger.info("Criando pagamento no Mercado Pago")
        payment_response = mp.payment().create(payment_data)
        logger.info(f"Resposta do Mercado Pago: {payment_response}")

        return jsonify({"status": "success", "data": payment_response["response"]})

    except Exception as e:
        logger.error(f"Erro ao gerar PIX: {str(e)}")
        return jsonify({"error": str(e)}), 400


@app.route('/criar-pagamento', methods=['POST'])
def criar_pagamento():
    try:
        logger.info("Recebendo requisição de Cartão")
        dados = request.json
        logger.info(f"Dados recebidos: {dados}")

        preference_data = {
            "items": [
                {
                    "title": f"Barbearia - {dados['servico']}",
                    "quantity": 1,
                    "currency_id": "BRL",
                    "unit_price": float(dados['valor'])
                }
            ],
            "back_urls": {
                "success": "http://localhost:5500/confirmacao.html",
                "failure": "http://localhost:5500/agendamento.html",
                "pending": "http://localhost:5500/agendamento.html"
            },
            "auto_return": "approved"
        }

        logger.info("Criando preferência no Mercado Pago")
        preference_response = mp.preference().create(preference_data)
        logger.info(f"Resposta do Mercado Pago: {preference_response}")

        return jsonify({"status": "success", "data": preference_response["response"]})

    except Exception as e:
        logger.error(f"Erro ao criar pagamento: {str(e)}")
        return jsonify({"error": str(e)}), 400


@app.route('/agendamentos/<filtro>', methods=['GET'])
def buscar_agendamentos(filtro):
    try:
        hoje = datetime.now().date()

        if filtro == 'hoje':
            data_busca = hoje
        elif filtro == 'amanha':
            data_busca = hoje + timedelta(days=1)
        elif filtro == 'semana':
            data_inicio = hoje
            data_fim = hoje + timedelta(days=7)

        conn = sqlite3.connect('barbearia.db')
        cursor = conn.cursor()

        if filtro == 'semana':
            cursor.execute('''
                SELECT a.id, c.nome, c.celular, a.servico, a.barbeiro, 
                       a.data, a.hora, a.valor, a.status
                FROM agendamentos a
                JOIN clientes c ON a.cliente_id = c.id
                WHERE a.data BETWEEN ? AND ?
                ORDER BY a.data, a.hora
            ''', (data_inicio.isoformat(), data_fim.isoformat()))
        else:
            cursor.execute('''
                SELECT a.id, c.nome, c.celular, a.servico, a.barbeiro, 
                       a.data, a.hora, a.valor, a.status
                FROM agendamentos a
                JOIN clientes c ON a.cliente_id = c.id
                WHERE a.data = ?
                ORDER BY a.hora
            ''', (data_busca.isoformat(),))

        agendamentos = cursor.fetchall()
        conn.close()

        # Converter para lista de dicionários
        resultado = []
        for agend in agendamentos:
            resultado.append({
                'id': agend[0],
                'nome': agend[1],
                'celular': agend[2],
                'servico': agend[3],
                'barbeiro': agend[4],
                'data': agend[5],
                'hora': agend[6],
                'valor': float(agend[7]),
                'status': agend[8]
            })

        return jsonify(resultado)

    except Exception as e:
        logger.error(f"Erro ao buscar agendamentos: {str(e)}")
        return jsonify({"error": str(e)}), 400


@app.route('/agendamentos/<int:id>/confirmar', methods=['POST'])
def confirmar_agendamento(id):
    try:
        conn = sqlite3.connect('barbearia.db')
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE agendamentos 
            SET status = 'confirmado' 
            WHERE id = ?
        ''', (id,))

        conn.commit()
        conn.close()

        return jsonify({"message": "Agendamento confirmado com sucesso"})

    except Exception as e:
        logger.error(f"Erro ao confirmar agendamento: {str(e)}")
        return jsonify({"error": str(e)}), 400


@app.route('/agendamentos/<int:id>/cancelar', methods=['POST'])
def cancelar_agendamento(id):
    try:
        conn = sqlite3.connect('barbearia.db')
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE agendamentos 
            SET status = 'cancelado' 
            WHERE id = ?
        ''', (id,))

        conn.commit()
        conn.close()

        return jsonify({"message": "Agendamento cancelado com sucesso"})

    except Exception as e:
        logger.error(f"Erro ao cancelar agendamento: {str(e)}")
        return jsonify({"error": str(e)}), 400


if __name__ == '__main__':
    # Mudando para aceitar conexões de qualquer origem
    app.run(debug=True, host='0.0.0.0', port=5000)
