from bs4 import BeautifulSoup
import pandas as pd
import requests
import json
import numpy as np

ITEM_COUNTS = 100

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Display-Api-Key': 'VWmkUPgs6g2fviPZ5JQFQ3pERP4tIXv/J2jppLqSRBk='
}


middle_category_nums = ['10101201', '10101202', '10101203', '10101204', '10101205',
                        '10101206', '10101207', '10101208', '10101209', '10101210',
                        '10101211', '10101212']


def get_item_cds_fp(middle_category_num, gender):
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

    item_cds_fp = []

    for item in info:
        item_cds_fp.append([item['itemCd'], item['finalPrice']])
        
    item_cds_fp = np.array(item_cds_fp)
    rankings = np.arange(1, len(item_cds_fp) + 1)
    total_items_count = np.full(len(item_cds_fp), len(item_cds_fp))

    item_cds_fp = np.column_stack((item_cds_fp, rankings, total_items_count))

    return item_cds_fp.tolist()



def get_item_data(info, item_fp):
    # 브랜드
    brandNameKr = info['brandNameKr']

    # 품번
    itemCd = info['itemCd']

    # 좋아요
    heartCnt = info['heartCnt']

    # 품절 여부
    statusName = info['statusName']

    # 정상가
    fixed_price = info['customerPrice']

    # 쿠폰 적용가 
    discounted_price = item_fp

    # 색상
    color = info['color1']

    # 사이즈

    # 이미지
    url = f'https://www.wconcept.co.kr/Product/{itemCd}?rccode=pc_topseller'
    response = requests.get(url, headers)
    soup = BeautifulSoup(response.text, 'lxml')
    imageUrls = []
    try:
        images = soup.select('ul#gallery > li > a > img') 
        for image in images:
            imageUrls.append(image['src'])

    except:
        pass

    # 카테고리
    categories = info['category']
    category_per_depth = []
    for category in categories:
        medium_name = category['mediumName']
        category_depthname1 = category['categoryDepthname1']
        category_depthname2 = category['categoryDepthname2']
        category_depthname3 = category['categoryDepthname3']
        
        dic = {'medium_name': medium_name,
               'category_depthname1': category_depthname1,
               'category_depthname2': category_depthname2,
               'category_depthname3': category_depthname3}
        
        category_per_depth.append(dic)


    # 상품명
    itemName = info['itemName']

    data = {
        'brand': brandNameKr,
        'product_id': itemCd,
        'likes': heartCnt,
        'sold_out': statusName,
        'fixed_price': fixed_price,
        'discounted_price': discounted_price,
        'product_name': itemName,
        'url': imageUrls,
        'category_per_depth': category_per_depth,
        'color': color,
        
    }

    return data



def get_item_info(item_cd, item_fp):
    
    url = f'https://www.wconcept.co.kr/Ajax/GetProductsInfo'
    data = {'itemcds': item_cd}
    response = requests.post(url, headers=headers, data=data)

    soup = BeautifulSoup(response.text, 'lxml')
    info = json.loads(soup.string)[0]
    
    info = get_item_data(info, item_fp)

    return info



def get_rank_score(ranking, item_count):
    rank_score = 1 - ((ranking - 1) / (item_count - 1))

    return rank_score



def main():
    item_cds_list = []
    for gender in ['men', 'women']:
        for middle_category_num in middle_category_nums:
            item_cds_fp = get_item_cds_fp(middle_category_num, gender)
            item_cds_list += item_cds_fp
    
    item_info = []
    for item_cd, item_fp, ranking, middle_item_count in item_cds_list:
        info = get_item_info(item_cd, item_fp)
        info['rank_score'] = get_rank_score(int(ranking), int(middle_item_count))
        item_info.append(info)
        print(info)
    df = pd.DataFrame(item_info)
    df.to_csv('wconcept.csv', index=False)

    
    
if __name__ == '__main__':
    main()