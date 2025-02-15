import sqlite3
from datetime import datetime

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('barbearia.db')
        self.criar_tabelas()

    def criar_tabelas(self):
        cursor = self.conn.cursor()
        
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

        self.conn.commit()

    def criar_cliente(self, nome, celular):
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO clientes (nome, celular) VALUES (?, ?)', (nome, celular))
        self.conn.commit()
        return cursor.lastrowid

    def criar_agendamento(self, cliente_id, servico, barbeiro, data, hora, valor):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO agendamentos 
            (cliente_id, servico, barbeiro, data, hora, valor) 
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (cliente_id, servico, barbeiro, data, hora, valor))
        self.conn.commit()
        return cursor.lastrowid

    def buscar_agendamentos_por_data(self, data):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT a.*, c.nome, c.celular 
            FROM agendamentos a 
            JOIN clientes c ON a.cliente_id = c.id 
            WHERE a.data = ?
        ''', (data,))
        return cursor.fetchall()

    def buscar_agendamentos_por_cliente(self, celular):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT a.*, c.nome, c.celular 
            FROM agendamentos a 
            JOIN clientes c ON a.cliente_id = c.id 
            WHERE c.celular = ?
            ORDER BY a.data DESC
        ''', (celular,))
        return cursor.fetchall()

    def verificar_disponibilidade(self, data, hora, barbeiro):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) 
            FROM agendamentos 
            WHERE data = ? AND hora = ? AND barbeiro = ? AND status = 'confirmado'
        ''', (data, hora, barbeiro))
        return cursor.fetchone()[0] == 0

    def cancelar_agendamento(self, agendamento_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE agendamentos 
            SET status = 'cancelado' 
            WHERE id = ?
        ''', (agendamento_id,))
        self.conn.commit()

    def fechar_conexao(self):
        self.conn.close() 