import sqlite3
from datetime import datetime
import threading


class Database:
    def __init__(self):
        self.database_path = 'barbearia.db'
        self.init_db()

    def get_connection(self):
        # Cria uma nova conexão para cada thread
        return sqlite3.connect(self.database_path)

    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        # Tabela de Clientes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                celular TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Tabela de Agendamentos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agendamentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id INTEGER,
                servico TEXT NOT NULL,
                barbeiro TEXT NOT NULL,
                data DATE NOT NULL,
                hora TEXT NOT NULL,
                valor REAL NOT NULL,
                status TEXT DEFAULT 'confirmado',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cliente_id) REFERENCES clientes (id)
            )
        ''')

        conn.commit()
        conn.close()

    def criar_cliente(self, nome, celular):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO clientes (nome, celular) VALUES (?, ?)', (nome, celular))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def criar_agendamento(self, cliente_id, servico, barbeiro, data, hora, valor):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO agendamentos 
                (cliente_id, servico, barbeiro, data, hora, valor) 
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (cliente_id, servico, barbeiro, data, hora, valor))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def buscar_agendamentos_por_data(self, data):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT a.*, c.nome, c.celular 
                FROM agendamentos a 
                JOIN clientes c ON a.cliente_id = c.id 
                WHERE a.data = ?
            ''', (data,))
            return cursor.fetchall()
        finally:
            conn.close()

    def buscar_agendamentos_por_cliente(self, celular):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT a.*, c.nome, c.celular 
                FROM agendamentos a 
                JOIN clientes c ON a.cliente_id = c.id 
                WHERE c.celular = ?
                ORDER BY a.data DESC
            ''', (celular,))
            return cursor.fetchall()
        finally:
            conn.close()

    def verificar_disponibilidade(self, data, hora, barbeiro):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT COUNT(*) 
                FROM agendamentos 
                WHERE data = ? AND hora = ? AND barbeiro = ? AND status = 'confirmado'
            ''', (data, hora, barbeiro))
            return cursor.fetchone()[0] == 0
        finally:
            conn.close()

    def cancelar_agendamento(self, agendamento_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE agendamentos 
                SET status = 'cancelado' 
                WHERE id = ?
            ''', (agendamento_id,))
            conn.commit()
        finally:
            conn.close()
