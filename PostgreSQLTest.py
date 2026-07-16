import psycopg2

connection = psycopg2.connect("postgresql://postgres:Tslb1112008!!@db.tvohnpbfqfofsdhrukpq.supabase.co:5432/postgres")

cursor = connection.cursor()

cursor.execute('SELECT version();')

version = cursor.fetchone()

print(version)

cursor.close()
connection.close()




