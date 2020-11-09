"""Detects text in the file."""
from google.cloud import vision_v1 as vision3
import io
import re
from flask import Flask, request, jsonify
from PIL import Image
from google.cloud import vision
from google.oauth2 import service_account
import os

app = Flask(__name__)


def hello():
    creds = service_account.Credentials.from_service_account_file(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', 'service.json'))
    client = vision.ImageAnnotatorClient(
        credentials=creds,
    )
    value = request.files['image']
    # client = vision.ImageAnnotatorClient()
    img = Image.open(value)
    content = image_to_byte_array(img)

    image = vision3.types.Image(content=content)

    result = ["", ""]

    response = client.text_detection(image=image)
    texts = response.text_annotations
    # -*- Encoding:UTF-8 -*- #
    text_arr = texts[0].description.split("\n")
    # s = '123abc.-30=*/-'

    limit_texts = ['가능', '원산지', '표기', '용기', '개당', 'g당', '기간', '추천', ',', '단위', '가격', '카드', '할인', '마트', '박스', '그대로',
                   '온라인몰', '행사']
    hangul = re.compile('[^ ㄱ-ㅣ가-힣]+')  # 한글과 띄어쓰기를 제외한 모든 글자

    for text in text_arr:
        str_num = "".join(re.findall('\d+', text))
        hangul_result = hangul.sub('', text)  # 한글과 띄어쓰기를 제외한 모든 부분을 제거
        # print("[" + str_num + "]")
        if len(str_num) != 0:

            if len(hangul_result) < 3 and 100 < int(str_num) < 500000 and text.find('/') == -1:
                print("후보 가격 !! : " + str(str_num) + " , " + hangul_result)
                result[1] = str_num

        #

        if len(hangul_result) > 3:
            token = False

            for limit in limit_texts:
                if text.find(limit) != -1:
                    token = True
                    break

            if token is False:
                print("후보 물건 이름!!! : " + text)
                result[0] = text
            # if text.find('가능') == -1 and text.find('원산지') == -1 and text.find('표기') == -1 and text.find(
            #         '용기') == -1 and text.find(
            #     '개당') == -1 and text.find('g당') == -1 and text.find('기간') == -1 and text.find('추천') == -1 \
            #         and text.find(',') == -1 and text.find('단위') == -1 and text.find('가격') == -1 and text.find(
            #     '카드') == -1 \
            #         and text.find('할인') == -1:
            #     print("후보 물건 이름!!! : " + text)
            # if result[0][0]=='|'
            #     print("후보 물건 이름!!! : " + text)

            # result[0] = text

    # print('Texts:')
    #
    # for text in texts:
    #     content = text.description
    #     content = content.replace(',', '')
    #     print('\n"{}"'.format(content))

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))

    json_response = {'name': result[0], 'price': result[1]}

    return jsonify(json_response)


def detect_text(path):
    """Detects text in the file."""
    import io
    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations
    print('Texts:')

    for text in texts:
        print('\n"{}"'.format(text.description))

        vertices = (['({},{})'.format(vertex.x, vertex.y)
                     for vertex in text.bounding_poly.vertices])

        print('bounds: {}'.format(','.join(vertices)))

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))


def image_to_byte_array(image: Image):
    imgByteArr = io.BytesIO()
    image.save(imgByteArr, format=image.format)
    imgByteArr = imgByteArr.getvalue()
    return imgByteArr


if __name__ == '__main__':
    app.run()
