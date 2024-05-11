import pyodbc

connection_string = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=CELL-PC\\SQLEXPRESS;DATABASE=RecipeDB;UID=sa;PWD=123'
connection = pyodbc.connect(connection_string)
cursor = connection.cursor()
cursor.execute("SELECT 1")
row = cursor.fetchone()
print(row)
connection.close()