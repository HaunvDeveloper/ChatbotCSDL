import pyodbc
from datetime import datetime

class SQLServerConnection:
    def __init__(self, server_name, database, uid, pw):
        self.conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server}; SERVER={' + server_name +'}; Database='+ database +'; UID='+ uid +'; PWD='+ pw +';')
        self.cursor = self.conn.cursor()


    def get_info(self, username):
        query = """SELECT username, fullname, birthday, email, user_type
                FROM Account 
                WHERE username = ?"""
        
        # Thực thi câu truy vấn với tham số
        self.cursor.execute(query, (username,))
        
        # Lấy dữ liệu từ kết quả truy vấn
        data = self.cursor.fetchone()
        
        return data
    def add_account(self, account):
        script = """
                INSERT Account values (?, ?, ?, ?, ?, ?)
                """
        self.cursor.execute(script, (account['username'], account['pass'], account['fullname'], format_birthday(account['birthday']), account['email'], account['user_type']))
        self.conn.commit()
        
    def del_account(self, username):
        script = "DELETE FROM Account WHERE username = ?"
        self.cursor.execute(script, (username,))
        self.conn.commit()

    
    def correct_password(self, username, password):
        query = """SELECT pass
                FROM Account 
                WHERE username = ?"""
        self.cursor.execute(query, (username,))
        
        # Lấy dữ liệu từ kết quả truy vấn
        data = self.cursor.fetchone()
        try:
            return str(data[0]) == password
        except:
            return False
    
    def check_is_exist(self, username):
        query = """SELECT username
        FROM Account 
        WHERE username = ?"""
        self.cursor.execute(query, (username,))
        data = self.cursor.fetchone()
        if data:
            return username in list(data)
        else:
            return False



def format_birthday(birthday_str):
    # Chuyển đổi chuỗi ngày tháng sang đối tượng datetime
    birthday = datetime.strptime(birthday_str, '%Y-%m-%d')
    # Định dạng lại thành chuỗi theo định dạng YYYY-MM-DD
    formatted_birthday = birthday.strftime('%Y-%m-%d')
    return formatted_birthday

