from bs4 import BeautifulSoup
import pandas as pd
import requests
import json
import re

ITEM_COUNTS = 100

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Display-Api-Key': 'VWmkUPgs6g2fviPZ5JQFQ3pERP4tIXv/J2jppLqSRBk='
}

middle_category_nums = ['10101201', '10101202', '10101203', '10101204', '10101205',
                        '10101206', '10101207', '10101208', '10101209', '10101210',
                        '10101211', '10101212']


def get_item_cds(middle_category_num, gender):
    url = 'https://api-display.wconcept.co.kr/display/api/v2/best/products'

    if gender == 'men':
        genderType = 'men'
    else:
        genderType = 'women'

    data = {
    "custNo": "",
    "dateType": "daily",
    "domain": 'WOMEN',
    "genderType": genderType,
    "depth1Code": "10101",
    "depth2Code": middle_category_num,
    "pageNo": 1,
    "pageSize": ITEM_COUNTS
    }

    response = requests.post(url, headers=headers, json=data)

    soup = BeautifulSoup(response.text, 'lxml')
    info = soup.string
    info = json.loads(info)
    info = info['data']['content']

    item_cds = []

    for item in info:
        item_cds.append(item['itemCd'])
        
    return item_cds



def get_item_payloads(item_cd):
    url = 'https://www.wconcept.co.kr/Ajax/GetProductsInfo'

    data = {'itemcds': item_cd}

    response = requests.post(url, headers=headers, data=data)

    soup = BeautifulSoup(response.text, 'lxml')
    info = soup.string
    info = json.loads(info)[0]

    item_cd = info['itemCd']
    medium_cd = info['category'][0]['mediumCd']
    category_cd = info['category'][0]['categoryCd']
    itemtypecd = info['itemTypeCd']

    item_payloads = [item_cd, medium_cd, category_cd, itemtypecd]
    
    print(item_payloads)
    
    return item_payloads



def get_one_review(i, soup, itemCd):
    # 구매 옵션과 사이즈정보 빼내기 용
    review_info = soup.select('div.pdt_review_info')[i]

    # 리뷰 id
    review_id = soup.select('div.product_review_reaction > div > button.link_txt.open-layer.open-pop_review_report')[i]['data-idxnum']
    
    # 구매 옵션
    try:
        option = review_info.select('div.pdt_review_option > p')[0].text.strip()
        option = option.split(':')[1].strip()
    except:
        option = None

    # 사이즈 정보
    try:
        cust_size_info = review_info.select('div.pdt_review_option > p')[1].text.strip()
        cust_size_info = cust_size_info.split(':')[1].strip()
    except:
        cust_size_info = None

    # 사이즈, 색상, 소재 빼내기 용
    try:
        sku = soup.select('ul.product_review_evaluation')[i]       

        # 사이즈
        size = sku.select('ul.product_review_evaluation > li > div > em')[0].text

        # 색상
        color = sku.select('ul.product_review_evaluation > li > div > em')[1].text

        # 소재
        texture = sku.select('ul.product_review_evaluation > li > div > em')[2].text
    
    except:
        size, color, texture = None, None, None



    # user id
    user_id = soup.select('p.product_review_info_right > em')[i].text

    # 작성 시간
    time = soup.select('p.product_review_info_right > span')[i].text

    # 리뷰 내용
    content = soup.select('p.pdt_review_text')[i].text.strip()

    # rating 정보
    rating_pct = soup.select('div.star-grade > strong[style]')[i]
    rating = re.findall(r'\d+', str(rating_pct))[0]
    rating = int(int(rating) / 20)

    # 좋아요 개수
    favorite = soup.select('button.like.btn_review_recommend')[i].text


    data = {
        'product_id': itemCd,
        'review_id': review_id,
        'purchase_option': option,
        'size_info': cust_size_info,
        'size': size,
        'color': color,
        'material': texture,
        'user_id': user_id,
        'written_time': time,
        'body': content,
        'rate': rating,
        'likes': favorite
    }

    return data



def get_reviews(item_payload):
    url = 'https://www.wconcept.co.kr/Ajax/ProductReViewList'
    i = 1
    one_goods_reviews = []
    while True:
        data = {'itemcd': item_payload[0],
            'pageIndex': i,
            'order': 1,
            'IsPrdCombinOpt': 'N',
            'mediumcd': item_payload[1],
            'categorycd': item_payload[2],
            'itemtypecd': item_payload[3]
            }

        response = requests.post(url, headers=headers, data=data)
        soup = BeautifulSoup(response.text, 'lxml')

        review_count = len(soup.select('p.pdt_review_text'))

        if review_count == 0:
            break
        
        for j in range(review_count):
            review = get_one_review(j, soup, item_payload[0])
            one_goods_reviews.append(review)
            print(review)
        
        i += 1

    return one_goods_reviews


        
def main():
    item_cds_list = []
    for gender in ['men', 'women']:
        for middle_category_num in middle_category_nums:
            item_cds = get_item_cds(middle_category_num, gender)
            item_cds_list += item_cds
    print(item_cds_list)

    item_payloads_list = []
    for item_cd in item_cds_list:
        item_payloads_list.append(get_item_payloads(item_cd))


    all_reviews = []

    for item_payloads in item_payloads_list:
        review_per_goods = get_reviews(item_payloads)
        if len(review_per_goods) == 0:
            continue
        else:
            all_reviews += review_per_goods



if __name__ == '__main__':
    main()