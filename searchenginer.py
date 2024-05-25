

#from rdflib import Graph, Literal, RDF
#from rdflib import URIRef, BNode
#from rdflib.namespace import FOAF, XSD
#from root import classify, matching
#from neo4jconnection import Neo4jConnection
from py2neo import Graph
#import random




graph = Graph("neo4j://localhost:7687", auth=("neo4j", "12345678"))

#conn = Neo4jConnection(uri="neo4j://localhost:7687", user="neo4j", pwd="12345678")

# p = Graph()
# p.parse("")


def get_string(q, res):
    # print(q)
    subject = q.get('@id')
    try:
        subject = subject.split('#', 1)[1]
    except:
        subject = subject
    for i in q.keys():
        if i != '@id':
            try:
                name = i.split('#', 1)[1]
            except:
                name = i

            try:
                contxt = list(q.get(i)[0].values())[0]
                try:
                    contxt = contxt.split('#', 1)[1]
                except:
                    contxt = contxt
                res.append([subject, name, contxt])

            except:
                contxt = q.get(i)

                try:
                    contxt = contxt.split('#', 1)[1]
                except:
                    try:
                        for j in q.get(i):
                            contxt = j
                            contxt = contxt.split('#', 1)[1]
                            res.append([subject, name, contxt])
                    except:
                        contxt = contxt
                        res.append([subject, name, contxt])
    return


def get_all(q):
    res = []
    for i in q:
        get_string(i, res)

    return res


def get_node(keyword):
    result = []
    # product = URIRef("urn:absolute:127.0.0.1/5000/mydatabase#Biến")
    # Đây là tham số bạn muốn truyền vào truy vấn

    # Truy vấn trả về tất cả các nodes có thuộc tính name bằng "CSDL"
    query_string = "MATCH (n) WHERE n.name = $name RETURN n"

    # Thực hiện truy vấn với tham số đã được cung cấp
    nodes = graph.run(query_string, name = keyword)

    # In kết quả truy vấn
    for node in nodes:
        result.append(node["n"])
    #print("NODEEEEEÊ:",result[0]['name'])
    return result

def getchapter(keyword):
    

    query_string = "MATCH (n) WHERE n.name = $name RETURN n"

    nodes = graph.run(query_string, name = keyword)


    return nodes[0]['n']['chapter'].replace('C', '')

def get_attr(keyword):


    query_string = "MATCH (n) WHERE n.name = $name RETURN keys(n) as keys"

    nodes = graph.run(query_string, name = keyword)
    
    keys = nodes[0]['keys'] if nodes else []
    #print(keys)

    return keys

def get_content_attr(name, attr):
    
    query_string = "MATCH (n) WHERE n.name = $name RETURN n"

    nodes = graph.run(query_string, name = name)

    return nodes[0]['n'][attr]
#print(get_attr(g, 'Mảng_1_chiều', 'Khởi_tạo_giá_trị_cho_mảng'))

def get_all_attr(node):
    properties = node
    # Chuyển đổi set thành list (nếu bạn muốn mảng)
    result = []
    #name = properties['name']
    #print(name)
    for key, value in properties.items():
        if key != 'id' and key != 'name':
            i = {'name' : str(key), 'content' : value}
            result.append(i)

    return result

def get_related_attr(node, not_get = ''):
    properties = node
    # Chuyển đổi set thành list (nếu bạn muốn mảng)
    result = []
    name = properties['name']
    #print(name)
    for key, value in properties.items():
        if key != 'id' and key != 'name' and key != 'chapter' and key != not_get:
            i = {'name' : str(key) + '#' + name, 'content' : value}
            result.append(i)

    return result

def get_relation(keyword):

    # product = URIRef("urn:absolute:127.0.0.1/5000/mydatabase#Biến")
    query_string = """
        MATCH (n {name: $name})-[:RELATED_TO]-(related)
        RETURN related
        """
    related_nodes = graph.run(query_string, name = keyword)
    result = []
    for node in related_nodes:
        i = {'name' : node['related']['name'], 'content' : node['related']['content']}
        if i not in result:
            result.append(i)
   
    return result


#print(get_relation(g, 'Biến'))



def get_diff_attr(keyw, keywo):

    rkeyw = get_attr(keyw)
    rkeywo = get_attr(keywo)

    cp_relation = []

    for i in rkeyw:
        if i in rkeywo and i != 'id' and i != 'keywords' and i != 'name':
            cp_relation.append(i)
    for i in cp_relation:
        print(i)

    """
    s = "Khái niệm của "+ (keyw.replace('_',' ')).lower() +' '+ clear_string(str(results).lower()) + ' còn khái niệm của '+(keywo.replace('_',' ')).lower()+ ' là '+ clear_string(str(rs).lower())
    """
    return cp_relation


import json
import random

with open('data/intents.json', encoding='utf-8') as json_data:
    intents = json.load(json_data)
def response(ops):
    for i in intents['intents']:
        if i['tag'] == ops:
            return random.choice(i['responses'])

if __name__ == '__main__':
    print(get_content_attr("cơ_sở_dữ_liệu", "chapter"))
    pass
