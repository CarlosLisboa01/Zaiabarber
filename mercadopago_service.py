import mercadopago
import logging

logger = logging.getLogger(__name__)


class MercadoPagoService:
    def __init__(self):
        # Token de teste fornecido
        self.mp = mercadopago.SDK(
            "TEST-1786945267929753-021510-056e7cd0d9efa00f6aa03af162ba0a58-403922089")

    def gerar_pix(self, dados):
        try:
            payment_data = {
                "transaction_amount": float(dados['valor']),
                "description": f"Barbearia Zaia - {dados['servico']}",
                "payment_method_id": "pix",
                "payer": {
                    "email": "cliente@teste.com",
                    "first_name": dados['nome'],
                    "last_name": "Sobrenome",
                    "identification": {
                        "type": "CPF",
                        "number": "19119119100"
                    }
                }
            }

            payment_response = self.mp.payment().create(payment_data)
            logger.info(f"Resposta PIX: {payment_response}")

            return {
                "status": "success",
                "data": payment_response["response"]
            }

        except Exception as e:
            logger.error(f"Erro ao gerar PIX: {str(e)}")
            raise

    def criar_preferencia_pagamento(self, dados):
        try:
            preference_data = {
                "items": [
                    {
                        "title": f"Barbearia Zaia - {dados['servico']}",
                        "quantity": 1,
                        "currency_id": "BRL",
                        "unit_price": float(dados['valor'])
                    }
                ],
                "payer": {
                    "name": dados['nome'],
                    "email": "cliente@teste.com"
                },
                "back_urls": {
                    "success": "http://127.0.0.1:5500/confirmacao.html",
                    "failure": "http://127.0.0.1:5500/agendamento.html",
                    "pending": "http://127.0.0.1:5500/agendamento.html"
                },
                "auto_return": "approved",
                "payment_methods": {
                    "excluded_payment_methods": [],
                    "excluded_payment_types": [],
                    "installments": 12
                },
                "notification_url": "http://127.0.0.1:5000/webhook"
            }

            preference_response = self.mp.preference().create(preference_data)
            logger.info(f"Preferência criada: {preference_response}")

            return {
                "status": "success",
                "data": preference_response["response"]
            }

        except Exception as e:
            logger.error(f"Erro ao criar preferência: {str(e)}")
            raise
