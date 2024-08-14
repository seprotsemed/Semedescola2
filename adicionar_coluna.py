import sqlite3

# Caminho para o seu banco de dados
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Comando SQL para adicionar a nova coluna
cursor.execute('ALTER TABLE webapp_aluno ADD COLUMN responsavel_cadastro_id INTEGER;')

# Salva as alterações e fecha a conexão
conn.commit()
conn.close()
