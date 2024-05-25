from pyvi import ViTokenizer



keywords = [
    "khóa ngoại",
    "là gì",
    "khóa chính",
    "khóa dự tuyển",
    "nhiều nhiều",
    "một nhiều",
    "nhiều một",
    "một một",
    "nhiều - nhiều",
    "một - nhiều",
    "một - một",
    "nhiều - một",
    "siêu khóa",
    "so sánh",
    "ràng buộc khóa chính khóa ngoại",
    "n-n",
    "n-m",
    "n n",
    "n m",
    "1 n",
    "n 1"
]



def custom_tokenize(sentence):

    for i in keywords:
        if i in sentence:
            sentence = sentence.replace(i, i.replace(' ', '_'))

    tokens = ViTokenizer.tokenize(sentence).split()

    return tokens