import time
from bs4 import BeautifulSoup
import pandas as pd
import requests
import json

ITEMS_COUNT = 100
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    
}


def get_response(url, headers):

    # GET 요청
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    time.sleep(0.5)

    return soup



def get_small_categories():
    url = 'https://pcw.thehandsome.com/api/display/1/ko/category/categoryList?dispCtgNo=mainDispCtgNo'

    soup = get_response(url, headers)
    info = soup.string
    categories = json.loads(info)['payload']['lrgCtgList']
    category_index = []
    gender_type = ['여성', '남성']
    for i, gender in enumerate(gender_type):
        for j in range(1, len(categories[i]['midCtgList'])):
            for k in range(1, len(categories[i]['midCtgList'][j]['smlCtgList'])):
                small_category_num = categories[i]['midCtgList'][j]['smlCtgList'][k]['dispCtgNo']
                category_index.append(small_category_num)

    return category_index



def get_item_info(goods):
    # 상품 id
    goodsNo = goods['goodsNo']

    # 리뷰 갯수
    goodsRevCnt = goods['goodsRevCnt']

    return [goodsNo, goodsRevCnt]



def get_items(num):
    url = f'https://www.thehandsome.com/api/display/1/ko/category/categoryGoodsList?dispMediaCd=10&sortGbn=20&pageSize={ITEMS_COUNT}&pageNo=1&norOutletGbCd=J&dispCtgNo={num}&productListLayout=4&theditedYn=N'

    goods_info = []

    soup = get_response(url, headers)
    info = soup.string
    goods_in_page = json.loads(info)['payload']['goodsList']

    for goods in goods_in_page:
        
        goods_data = get_item_info(goods)
        goods_info.append(goods_data)
        print(len(goods_info), goods_data)

    return goods_info



def get_one_review(review):
    
    # 상품 id
    goodsNo = review['goodsNo']

    # 리뷰 id
    review_id = review['revNo']

    # 별 개수
    rating = review['revScrVal']

    # 작성일
    written_date = review['revWrtDtm']

    # 유저 아이디
    user_id = review['loginId']

    # 내용
    revCont = review['revCont']

    # 구매 색상
    color = review['goodsClorNm']

    # 구매 사이즈
    size = review['goodsSzNm']

    # 구매 sku
    product_sku = {'color': color, 'size': size}

    # 수입처
    import_source = review['shopNm']

    # 키
    try:
        height = review['revPrfleList'][0]['mbrPrfleValNm']
    except:
        height = None
    
    # 평소 사이즈
    try:
        nor_size = review['revPrfleList'][1]['mbrPrfleValNm']
    except:
        nor_size = None

    

    data = {
        'product_id': goodsNo,
        'review_id': review_id,
        'rating': rating,
        'written_date': written_date,
        'user_id': user_id,
        'body': revCont,
        'product_sku': product_sku,
        'import_source': import_source,
        'user_height': height,
        'user_size': nor_size,
        'rating': rating,

    }

    return data



def get_review_data(goodsNo, goodsRevCnt):
    url = f'https://www.thehandsome.com/api/goods/1/ko/goods/{goodsNo}/reviews?sortTypeCd=latest&revGbCd=&pageSize={goodsRevCnt}&pageNo=1'

    one_goods_reviews = []

    soup = get_response(url, headers)
    reviews = soup.string

    try:
        reviews = json.loads(reviews)['payload']['revAllList']

        for review in reviews:
            one_review = get_one_review(review)
            one_goods_reviews.append(one_review)
    except:
        pass
    
    print(f'{goodsNo} 상품 리뷰 수: {len(one_goods_reviews)}', one_goods_reviews)


    return one_goods_reviews


    
def main():
    category_index = get_small_categories()

    all_info = []
    for num in category_index:
        middle_category_info = get_items(num)
        all_info += middle_category_info

    all_reviews = []

    for goodsNo, goodsRevCnt in all_info:
        one_goods_reviews = get_review_data(goodsNo, goodsRevCnt)
        all_reviews += one_goods_reviews



if __name__ == '__main__':
    main()  