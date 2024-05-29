from flask import Flask, render_template, request, jsonify, redirect, render_template, url_for, session
from intent_classify import classify
from searchenginer import get_node, get_relation, get_all_attr, getchapter, get_related_attr, response
from keyword_retrieval import keywords_retriever
from SQLServerConnection import *
from datetime import timedelta
import random
import os
import json


attr_dict = {
    'chapter' : 'Chương', 'content' : 'Khái niệm', 'property' : 'Tính chất', 'using' : 'Cách sử dụng', 'name' : 'Tên', 'assignment' : 'Bài tập'
}

key_map = {
    'chapter' : 'Chương', 'define' : 'Khái niệm', 'property' : 'Tính chất', 'using' : 'Cách sử dụng', 'assignment' : 'Bài tập'
}


opt_att = [
    "ask.chapter", "ask.using", "ask.property", "ask.assignment"
]

node_attr = [
    'chapter', 'content', 'property', 'assignment', 'using'
]

related = None
##############################################################################
app = Flask(__name__)
app.static_folder = 'static'
account_socket = SQLServerConnection("LAPTOP-ENCKOU6S", "Socket_Account", "haunv", "NguyenH@u100304")
app.secret_key = 'GHbg#saga25yy12h2r@%fnsdj'
app.permanent_session_lifetime = timedelta(days=1)

@app.route('/')
def index():
    if 'logged_in' in session:
        return render_template('home.html') 
    return render_template('welcome.html')


@app.route("/result", methods=['POST'])
def result(): 
    if 'logged_in' in session:
        return render_template('home.html') 
    if request.method == 'POST':
        result = request.form
        username = result.get('username')
        password = result.get('password')
        session.permanent = True
        if account_socket.correct_password(username, password):
            session['logged_in'] = True
            session['username'] = username
            session['related'] = None
            if not os.path.exists("data_user/" + session['username']):
                # Nếu chưa tồn tại, tạo mới thư mục
                os.makedirs("data_user/" + session['username'])
            return redirect(url_for('index'))
        else:
            # Đăng nhập không thành công, hiển thị lại trang đăng nhập
            return render_template('welcome.html', error="Username hoặc mật khẩu không đúng!")
    else:
        return render_template('welcome.html')


@app.route("/signup", methods=['POST'])
def signup():
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']
    fullname = request.form['fullname']
    date = request.form['date']
    print("New username signup: ", username)
    if account_socket.check_is_exist(username):
        return jsonify({'error': 'Username already exists. Please choose a different one.'})
    elif len(password) > 19:
        return jsonify({'error': 'Maximum length of password is 20'})
    else:
        fullname = fullname.strip().capitalize()
        account = {
            'username' : username,
            'pass' : password,
            'email' : email,
            'fullname' : fullname,
            'birthday' : date,
            'user_type' : 'student'
        }
        account_socket.add_account(account=account)
        return jsonify({'success': 'Login successful'})
    


@app.route("/logout", methods=['POST'])
def logout():
    session.pop('username', None)
    session.pop('logged_in', None)
    session.pop('related', None)
    return redirect(url_for('index'))



@app.route("/get_chat")
def get_chat():
    path = "data_user/" + session["username"]
    res = []
    # Kiểm tra xem thư mục tồn tại hay không
    if os.path.exists(path=path):
        # Lấy danh sách các tệp trong thư mục
        files = os.listdir(path)

        if len(files) == 0:
            return jsonify({'data' : None})

        # Lọc các tệp có đuôi là '.json'
        for file in files:
            with open(path + '/' + file, 'r') as file:
                data = json.load(file)    
                res.append(data)

        return jsonify({'data': res})
    
    else:
        return jsonify({'data' : None})


@app.route("/get_box", methods=['POST'])
def get_box():
    uid = request.get_json()['uid']
    print(uid)
    file_path = 'data_user/' + session["username"] + '/' + uid + '.json'
    with open(file_path, 'r') as file:
        data = json.load(file)
    print(data)
    return jsonify({'data' : data})



@app.route('/create_box', methods=['POST'])
def create_box():
    uid = request.get_json()['uid']
    name = request.get_json()['name']
    data = request.get_json()['data']
    file_name = 'data_user/' + session["username"] + '/' + uid + '.json'
    data_json = {
        'uid' : uid,
        'name' : name,
        'chat' : data
    }
    #print('AAAAA', data_json)
    with open(file_name, 'w') as json_file:
        json.dump(data_json, json_file, indent=4)
    return jsonify({'status' : 'Ok'})

@app.route('/remove_box', methods=['POST'])
def remove_box():
    uid = request.get_json()['uid']
    file_name = 'data_user/' + session["username"] + '/' + uid + '.json'
    try:
        os.remove(file_name)
    except:
        print("error delete file")
    
    return jsonify({'status' : 'Ok'})
#############################################################################

def add_data(file_path, new_data):
    # Đọc dữ liệu từ file JSON
    with open(file_path, 'r') as file:
        data = json.load(file)

    # Thêm mới dữ liệu vào mảng
    data['chat'].append(new_data)

    # Ghi lại dữ liệu vào file JSON
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)      
    

def clear_string(text):
    text = text.replace("_", " ")
    text = text.replace("\\t", "&emsp;")
    text = text.replace("['", '', 1)
    text = text.replace("']", '', 1)
    text = text.replace("\\xa0", '')
    text = clearlgtext(text)
    text = text.replace("\\n", "<br> ")
    text = text.replace("\n", "<br>")
    return text


def clearlgtext(text):
    text = text.replace('<', "&lt")
    text = text.replace('>', "&gt")
    return text


classify_class = classify("data/intents.json")
keyword_class = keywords_retriever("data/keywords.json")

loop_limit_except = 100

chat = {'user' : None, 'bot' : None}
path_user_data = None

@app.route("/ask", methods=['POST'])
def ask():
    
    message = request.get_json()['message'].strip()
    box_select = request.get_json()['box']
    print("User: ", session['username'], "ask")
    print("Message: ", message)

    global loop_limit_except
    global chat
    global path_user_data
    
    chat['user'] = message
    path_user_data = 'data_user/' + session["username"] + '/'

    while (loop_limit_except > 1):
        a = [message]
        
        method = classify_class.getIntent(a[0].replace('_', ' '))

        keywordQ = keyword_class.getKeywords(a[0], 2)

        print("Method:", method)
        print("Keywords: ", keywordQ)


        # print(method)
        if method.find("common") != -1:
            print('common')
            bot_response = response(method)
            print(bot_response)
            if box_select == None:
                name_box = 'Chào hỏi'
                result = jsonify({'status': 'OK', 'answer': bot_response, 'related' : [], 'name_box' : name_box})
            else:
                chat['bot'] = bot_response
                add_data(path_user_data + box_select + '.json', chat)
                result = jsonify({'status': 'OK', 'answer': bot_response, 'related' : [], 'name_box' : None})
            print('Answer:', bot_response)
            return result
        #a = message.replace(' ', '_')

        
        return answer(method, keywordQ, box_select)
        n -= 1


@app.route("/related", methods=['POST'])
def answer_related():
    #global related
    path_user_data  = 'data_user/' + session["username"] + '/'
    chat = {'user' : None, 'bot' : None}

    index = request.get_json()['index']
    box_select = request.get_json()['box']
    bot_response = session['related'][index]['content']
    
    temp = get_relation(session['related'][index]['name'])
    session['related'] = []
    for i in temp:
        session['related'].append(i)

    key_w = [i['name'] for i in session['related']]
    key_w = format_related_key(key_w)
    print(key_w)
    chat['bot'] = bot_response
    add_data(path_user_data + box_select + '.json', chat)
    return jsonify({'status' : 'OK', 'answer': bot_response, 'related' : key_w, 'name_box' : None})





def format_related_key(keyws):
    res = []
    for key in keyws:
        tmp = ''
        if key.find('#') == -1:
            tmp = 'Bạn có muốn biết về ' + key.replace('_', ' ')
        else:
            keys = key.split('#')
            if keys[0] == 'content':
                tmp = 'Bạn có muốn biết khái niệm của '
            elif keys[0] == 'using':
                tmp = 'Bạn có muốn biết cách sử dụng của '
            elif keys[0] == 'property':
                tmp = 'Bạn có muốn biết tính chất của '
            elif keys[0] == "assignment":
                tmp = 'Bạn có muốn bài tập về '
            tmp = tmp + keys[-1].replace('_', ' ')
        tmp = tmp + '?'

        res.append(tmp)
    return res

def get_diffirent(keywords):
    node1, node2 = get_node(keywords[0])[0], get_node(keywords[1])[0]
    attr1, attr2 = get_all_attr(node1), get_all_attr(node2)
    keywords[0], keywords[1] = keywords[0].replace('_', ' ') , keywords[1].replace('_', ' ')
    ans = [["", keywords[0], keywords[1]],]

    for a in node_attr:
        a1, a2 = None, None
        for i in attr1:
            if i['name'] == a:
                a1 = i
                break
        for i in attr2:
            if i['name'] == a:
                a2 = i
                break
        if a1 != None and a2 != None:
            if a1['name'] == 'chapter':
                keywords[0], keywords[1] = keywords[0].capitalize(), keywords[1].capitalize()
                tmp_a_i = keywords[0] + ' thuộc chương ' + a1['content'].replace('C', '')
                tmp_ao_i = keywords[1] + ' thuộc chương ' + a2['content'].replace('C', '')
            elif a1['name'] != 'assignment':
                tmp_a_i = a1['content']
                tmp_ao_i = a2['content']
            ans.append([attr_dict[a1['name']],  tmp_a_i, tmp_ao_i])
        
    return ans


def create_html_table(data):
    # Khởi tạo biến chứa chuỗi HTML
    html = '<table border="1" class="compareTable">\n'
    
    # Lặp qua từng hàng trong dữ liệu
    for row in data:
        html += '  <tr>\n'  # Bắt đầu hàng mới
        
        # Lặp qua từng ô trong hàng
        for cell in row:
            # Nếu là hàng đầu tiên, sử dụng thẻ <th> cho tiêu đề
            if row == data[0]:
                html += f'    <th>{cell.capitalize()}</th>\n'
            else:
                # Sử dụng thẻ <td> cho các ô dữ liệu
                html += f'    <td>{cell}</td>\n'
        
        # Kết thúc hàng
        html += '  </tr>\n'
    
    # Kết thúc bảng
    html += '</table>'
    
    return html



def answer(method, keywords, box_select):
    #global related
    global path_user_data
    if method == 'ask.define':
        bot_response = ''

        keyword = keywords[0]
        
        node = get_node(keyword)[0]
        rm = node['content']
        print("Answer: ", rm)
        
        session['related'] = get_related_attr(node, 'content')


        temp = get_relation(keyword)
        for i in temp:
            session['related'].append(i)

        key_w = [i['name'] for i in session['related']]
        key_w = format_related_key(key_w)
        print("Related:", key_w)

        
        bot_response = bot_response + rm
        if box_select == None:
            name_box = key_map[method.replace('ask.', '')] + ' ' + keyword.replace('_', ' ')
            result = jsonify({'status': 'OK', 'answer': bot_response, 'related' : key_w, 'name_box' : name_box})
        else:
            chat['bot'] = bot_response
            add_data(path_user_data + box_select + '.json', chat)
            result = jsonify({'status': 'OK', 'answer': bot_response, 'related' : key_w, 'name_box' : None})


        return result
    
    elif method == "chapter":
        bot_response = keyword.replace('_', ' ') + ' thuộc chương ' + getchapter(keyword) + '.'
        session['related'] = []
        if box_select == None:
            name_box = key_map[method.replace('ask.', '')] + ' ' + keyword.replace('_', ' ')
            result = jsonify({'status': 'OK', 'answer': bot_response, 'related' : [], 'name_box' : name_box})
        else:
            chat['bot'] = bot_response
            add_data(path_user_data + box_select + '.json', chat)
            result = jsonify({'status': 'OK', 'answer': bot_response, 'related' : [], 'name_box' : None})
        return result
    
    elif method in opt_att:
        method = method.replace('ask.', '')
        keyword = keywords[0]
        
        node = get_node(keyword)[0]
        rm = node[method]
        print(rm)
        if rm == None:
            rm = response("common.out")
            session['related'] = []
            return jsonify({'status': 'OK', 'answer': rm, 'related' : []})
        if method == "assignment":
            exer = rm.split('###')
            rm = random.choice(exer)


        session['related'] = get_related_attr(node, method)
        temp = get_relation(keyword)
        for i in temp:
            session['related'].append(i)

        key_w = [i['name'] for i in session['related']]
        key_w = format_related_key(key_w)

        rm = rm.replace("**", "").replace("```sql", "").replace("```", "").replace("###", "")
        if box_select == None:
            name_box = key_map[method.replace('ask.', '')] + ' ' + keyword.replace('_', ' ')
            result = jsonify({'status': 'OK', 'answer': rm, 'related' : key_w, 'name_box' : name_box})
        else:
            chat['bot'] = rm
            add_data(path_user_data + box_select + '.json', chat)
            result = jsonify({'status': 'OK', 'answer': rm, 'related' : key_w, 'name_box' : None})

        return result  
    elif method == 'ask.compare':
        tmp_ans = get_diffirent(keywords)
        bot_response = create_html_table(tmp_ans)
        bot_response = bot_response.replace("**", "")
        print(bot_response)
        session['related'] = []
        if box_select == None:
            name_box = 'So sánh' + ' ' + keywords[0].replace('_', ' ') + ' và ' + keywords[1].replace('_', ' ')
            result = jsonify({'status': 'OK', 'answer': bot_response, 'related' : [], 'name_box' : name_box})
        else:
            chat['bot'] = bot_response
            add_data(path_user_data + box_select + '.json', chat)
            result = jsonify({'status': 'OK', 'answer': bot_response, 'related' : [], 'name_box' : None})
        return result

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=5000)
