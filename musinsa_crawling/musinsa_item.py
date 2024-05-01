import time
from bs4 import BeautifulSoup
import pandas as pd
import requests
import json
import re
import sys
import numpy as np

ITEMS_COUNT = 100


middle_category_nums = ['001006', '001004', '001005', '001010', '001002', '001003',
                        '001001', '001011', '001013', '001008', '002022', '002001',
                        '002002', '002025', '002017', '002003', '002020', '002019',
                        '002023', '002018', '002004', '002008', '002007', '002024',
                        '002009', '002013', '002012', '002016', '002021', '002014',
                        '002006', '002015', '003002', '003007', '003008', '003004',
                        '003009', '003005', '003010', '003011', '003006', '002006',
                        '002007', '002008', '022001', '022002', '022003']

# 사용자 에이전트
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
}



def get_response(url, headers):

    # GET 요청
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    time.sleep(0.5)

    return soup



def get_items(num):
    
    url = f'https://www.musinsa.com/categories/item/{num}?d_cat_cd={num}&brand=&list_kind=small&sort=sale_high&sub_sort=1d&page=1&display_cnt=90&exclusive_yn=&sale_goods=&timesale_yn=&ex_soldout=&plusDeliveryYn=&kids=&color=&price1=&price2=&shoeSizeOption=&tags=&campaign_id=&includeKeywords=&measure='
    
    product_links = []
    flag = 0
    page = 1
    soup = get_response(url, headers)
    total_page = int(soup.select('span.totalPagingNum')[0].text)
    while flag == 0:
        
        soup = get_response(url, headers)

        products = soup.select('a.img-block')
        
        for product in products:
            product_links.append(product['href'].replace('//', 'https://'))  # URL만 추가
            
            if len(product_links) == ITEMS_COUNT:
                flag = 1
                break

        page += 1
        
        if page > total_page:
            break

        url = f'https://www.musinsa.com/categories/item/{num}?d_cat_cd={num}&brand=&list_kind=small&sort=sale_high&sub_sort=1d&page={page}&display_cnt=90&exclusive_yn=&sale_goods=&timesale_yn=&ex_soldout=&plusDeliveryYn=&kids=&color=&price1=&price2=&shoeSizeOption=&tags=&campaign_id=&includeKeywords=&measure='

    product_links = np.array(product_links)

    rankings = np.arange(1, len(product_links) + 1)
    total_items_count = np.full(len(product_links), len(product_links))

    product_links = np.column_stack((product_links, rankings, total_items_count))

    return product_links.tolist() 



def get_item_info(item_url):
    soup = get_response(item_url, headers)
    try:
        info = soup.find_all('script', {'type':'text/javascript'})[15]
    except:
        return
    info = info.string

    pattern = re.compile(r'window\.__MSS__\.product\.state = ({.*?});\s*$', re.DOTALL)
    match = pattern.search(info)
    info = match.group(1)
    
    return json.loads(info)



def extract_favorite_num(goodsNo):
    url = 'https://like.musinsa.com/like/api/v2/liketypes/goods/counts'
    data = {"relationIds":[str(goodsNo)]}
    response = requests.post(url, json=data)
    soup = BeautifulSoup(response.text, 'lxml')
    info = soup.string
    favorites = json.loads(info)['data']['contents']['items'][0]['count']

    return favorites


    
def extract_needs_info(item_info):
    # 무신사 상품번호
    product_id = item_info['goodsNo']

    # 브랜드 명명
    brand = item_info['brand']

    # 품번
    product_num = item_info['styleNo']

    # 좋아요 수
    likes = extract_favorite_num(product_id)

    # 무신사 판매가
    fixed_price = item_info['goodsPrice']['originPrice']

    # 무신사 회원가
    discounted_price = item_info['goodsPrice']['minPrice']

    # 상품 이미지 : 리스트에 str로 저장. 필요하면 수정
    image_urls = []
    image_urls.append(item_info['thumbnailImageUrl'])
    goodsImages = item_info['goodsImages']
    for goodsImage in goodsImages:
        image_urls.append(goodsImage['imageUrl'])

    stat_url = f'https://goods-detail.musinsa.com/goods/{product_id}/stat'
    response = requests.get(stat_url, headers=headers)
    add_data = response.json()
    
    # 누적 판매
    try:
        cumulative_sales = add_data['data']['purchase']['total']
    except:
        cumulative_sales = None

    # 나이
    try:
        ages = add_data['data']['purchase']['rates']
        ages = {key: f"{value}%" for key, value in ages.items()}
        under_18 = f"{ages['AGE_UNDER_18']}%"
        age_19_to_23 = f"{ages['AGE_19_TO_23']}%"
        age_24_to_28 = f"{ages['AGE_24_TO_28']}%"
        age_29_to_33 = f"{ages['AGE_29_TO_33']}%"
        age_34_to_39 = f"{ages['AGE_34_TO_39']}%"
        over_40 = f"{ages['AGE_OVER_40']}%"
    except:
        under_18, age_19_to_23, age_24_to_28, age_29_to_33, age_34_to_39, over_40 = None, None, None, None, None, None

    # 성비
    try:
        male = int(add_data['data']['purchase']['male'])
        female = int(add_data['data']['purchase']['female'])
        total_count = male + female
        male_percentage = int(round((male / total_count) * 100, -1))
        female_percentage = int(round((female / total_count) * 100, -1))
        male_percentage = f"{male_percentage}%"
        female_percentage = f"{female_percentage}%"
    except:
        male_percentage = None
        female_percentage = None

    # 대분류
    categoryDepth1Title = item_info['category']['categoryDepth1Title']

    # 중분류
    categoryDepth2Title = item_info['category']['categoryDepth2Title']


    data = {
        'product_id': product_id,
        'brand': brand,
        'product_num': product_num,
        'likes': likes,
        'fixed_price': fixed_price,
        'discounted_price': discounted_price,
        'categoryDepth1Title': categoryDepth1Title,
        'categoryDepth2Title': categoryDepth2Title,
        'url': image_urls,
        'cumulative_sales': cumulative_sales,
        'under_18': under_18,
        '19_to_23': age_19_to_23,
        '24_to_28': age_24_to_28,
        '29_to_33': age_29_to_33,
        '34_to_39': age_34_to_39,
        'over_40': over_40,
        'male_percentage': male_percentage,
        'female_percentage': female_percentage,   
    }

    return data



def get_rank_score(ranking, item_count):
    rank_score = 1 - ((ranking - 1) / (item_count - 1))

    return rank_score



def main():
    all_product_links = []
    
    for middle_category_num in middle_category_nums:
        product_links = get_items(middle_category_num)
        all_product_links += product_links
        print(len(all_product_links), product_links[-1])
    
    items_list = []

    for item_url in all_product_links:
        item_info = get_item_info(item_url[0])
        
        if item_info is None: # get_item_info로 해당 상품 정보 못 가져왔을 때. 
            continue          # 필요에 맞게 수정 필요.

        needs_info = extract_needs_info(item_info)
        needs_info['rank_score'] = get_rank_score(int(item_url[1]) , int(item_url[2]))
        items_list.append(needs_info)
        print(needs_info)


        
if __name__ == "__main__":
    main()