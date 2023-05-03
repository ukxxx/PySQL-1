import psycopg2


class Db:
    def __init__(self, conn):
        with conn.cursor() as cur:
            # Раскомментировать, если хотим очистить базу
            # cur.execute('DROP TABLE IF EXISTS phones; DROP TABLE IF EXISTS clients;')
            cur.execute('''CREATE TABLE IF NOT EXISTS clients(
                id SERIAL PRIMARY KEY,
                first_name VARCHAR(255),
                last_name VARCHAR(255),
                email VARCHAR(255));''')
            cur.execute('''CREATE TABLE IF NOT EXISTS phones(
                client_id INTEGER REFERENCES clients(id),
                phone VARCHAR(255));''')
            conn.commit()

    def add_client(self, conn, first_name, last_name, email, phone=None):
        with conn.cursor() as cur:
            cur.execute('INSERT INTO clients(first_name, last_name, email) VALUES(%s, %s, %s) RETURNING id;', (first_name, last_name, email))
            id = cur.fetchone()[0]
            if phone:
                self.add_phone(conn, id, phone)
            return id

    def add_phone(self, conn, id: int, phone):
        with conn.cursor() as cur:
            cur.execute('SELECT id FROM clients;')
            data =[item for sublist in cur.fetchall() for item in sublist]
            if int(id) in data:
                cur.execute('INSERT INTO phones(client_id, phone) VALUES(%s, %s);', (id, phone))
                conn.commit()
                res = True
            else:
                res = None
        return res
    
    def change_client(self, conn, id: int, first_name=None, last_name=None, email=None, phone=None):
        with conn.cursor() as cur:
            if first_name:
                cur.execute('UPDATE clients SET first_name = %s WHERE id = %s RETURNING first_name;', (first_name, id))
                print(f'Новое имя: {cur.fetchone()[0]}')
                conn.commit()
            if last_name:
                cur.execute('UPDATE clients SET last_name = %s WHERE id = %s RETURNING last_name;', (last_name, id))
                print(f'Новая фамилия: {cur.fetchone()[0]}')
                conn.commit()
            if email:
                cur.execute('UPDATE clients SET email = %s WHERE id = %s RETURNING email;', (email, id))
                print(f'Новая почта: {cur.fetchone()[0]}')
                conn.commit()
            if phone:
                try:
                    self.delete_phone(conn, id)
                finally:
                    self.add_phone(conn, id, phone)
                print(f'Новый телефон: {phone}')

    def delete_phone(self, conn, id: int, phone=None):
        with conn.cursor() as cur:
            if phone:
                cur.execute('DELETE FROM phones WHERE client_id = %s AND phone = %s', (id, phone))
            else:
                cur.execute('DELETE FROM phones WHERE client_id = %s', (id,))
            conn.commit()

    def delete_client(self, conn, id: int):
        with conn.cursor() as cur:
            cur.execute('DELETE FROM phones WHERE client_id = %s', (id,))
            cur.execute('DELETE FROM clients WHERE id = %s', (id,))
            conn.commit()

    def find_client(self, conn, id: int, first_name=None, last_name=None, email=None, phone=None):
        with conn.cursor() as cur:
            if first_name:
                cur.execute('SELECT * FROM clients WHERE first_name = %s', (first_name,))
                res = cur.fetchone()
            elif last_name:
                cur.execute('SELECT * FROM clients WHERE last_name = %s', (last_name,))
                res = cur.fetchone()
            elif email:
                cur.execute('SELECT * FROM clients WHERE email = %s', (email,))
                res = cur.fetchone()
            elif phone:
                cur.execute('''SELECT * FROM clients
                    JOIN phones ON clients.id = phones.client_id
                    WHERE phone = %s''', (phone,))
                res = cur.fetchone()
            elif id:
                cur.execute('SELECT * FROM clients WHERE id = %s', (id,))
                res = cur.fetchone()
            else:
                res = None
            return res

    def find_phone(self, conn, id: int, phone=None):
        with conn.cursor() as cur:
            if phone:
                cur.execute('SELECT * FROM phones WHERE client_id = %s AND phone = %s', (id, phone))
            else:
                cur.execute('SELECT * FROM phones WHERE client_id = %s', (id,))
            return cur.fetchall()

if __name__ == '__main__':

    conn = psycopg2.connect(database='clients', user='postgres', password='qgdfZi8Mpg')
    db = Db(conn)
    flag = True
    
    while flag:
        print()
        print('''Команды:
        1 - Для добавления нового клиента 
        2 - Для добавления телефона 
        3 - Для изменения клиента 
        4 - Для удаления телефона 
        5 - Для удаления клиента 
        6 - Для поиска клиента
        7 - Для выхода''')

        input_command = input('Введите команду: ')

        if input_command == '1':
            first_name = input('Введите имя: ')
            last_name = input('Введите фамилию: ')
            email = input('Введите email: ')
            phone = input('Введите телефон: ')
            id = db.add_client(conn, first_name, last_name, email, phone)
            print(f'\nКлиент {first_name} {last_name}, почта {email} добавлен под номером: {id}\n')
        elif input_command == '2':
            id = input('Введите id клиента: ')
            phone = input('Введите номер телeфона: ')
            res = db.add_phone(conn, id, phone)
            if res:
                print(f'\nТелефон {phone} добавлен.\n')
            else:
                print(f'Клиента с таким id не существует.\n')
        elif input_command == '3':
            id = input('Введите id клиента: ')
            first_name = input('Введите новое имя: ')
            last_name = input('Введите новую фамилию: ')
            email = input('Введите новый email: ')
            phone = input('Введите новый номер телефона: ')
            new_data = db.change_client(conn, id, first_name, last_name, email, phone)
            print(f'\nИзменения внесены.\n')
        elif input_command == '4':
            id = input('Введите id клиента: ')
            phone = input('Введите номер телефона: ')
            db.delete_phone(conn, id, phone)
            print(f'\nТелефон {phone} удален.\n')
        elif input_command == '5':
            id = input('Введите id клиента: ')
            db.delete_phone(conn, id)
            db.delete_client(conn, id)
            print(f'\nКлиент удален.\n')
        elif input_command == '6':
            id = input('Введите id клиента: ')
            first_name = input('Введите имя: ')
            last_name = input('Введите фамилию: ')
            email = input('Введите email: ')
            phone = input('Введите телефон: ')
            client = db.find_client(conn, id, first_name, last_name, email, phone)
            if client:
                print(f'\nID: {client[0]}\nИмя: {client[1]}\nФамилия: {client[2]}\nПочта: {client[3]}\n')
                phones = db.find_phone(conn, client[0])
                print(f'Телефоны:')
                for phone in phones:
                    print(f'{phone[2]}')
            elif client is None:
                print(f'\nКлиент не найден.\n')
        elif input_command == '7':
            conn.close()
            flag = False
            print('\nВыход из программы.\n')
        else:
            print('\nВведена несуществующая команда.\n')