from bs4 import BeautifulSoup
import requests
import json
import sys

ITEMS_COUNT = 100

responses = []

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    
}

def get_response(url, headers):

    # GET 요청
    response = requests.get(url, headers=headers)
    responses.append(response.text)
    soup = BeautifulSoup(response.text, 'lxml')

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
            middle_category_num = categories[i]['midCtgList'][j]['dispCtgNo']
            middle_category_name = categories[i]['midCtgList'][j]['dispCtgNm']
            for k in range(1, len(categories[i]['midCtgList'][j]['smlCtgList'])):
                small_category_num = categories[i]['midCtgList'][j]['smlCtgList'][k]['dispCtgNo']
                small_category_name = categories[i]['midCtgList'][j]['smlCtgList'][k]['dispCtgNm']
                category_index.append({'top': gender,'middle': [middle_category_num, middle_category_name], 'small': [small_category_num, small_category_name]})

    return category_index



def get_item_info(goods):
    # 상품 id
    goodsNo = goods['goodsNo']

    # 브랜드 명
    brandNm = goods['brandNm']

    # 정가
    norPrc = goods['norPrc']

    # 할인가
    salePrc = goods['salePrc']

    # 이미지    
    image_urls = []      
    try:    
        for i in range(len(goods['colorInfo'])):
            for j in range(len(goods['colorInfo'][i]['colorContInfo'])):
                colorContInfo = goods['colorInfo'][i]['colorContInfo'][j]['dispGoodsContUrl']
                image_urls.append(colorContInfo)
    except:
        pass

    # 색상 정보
    colors = []
    try:
        for color in goods['colorInfo']:
            colors.append(color['optnNm'])
    except:
        pass

    # 사이즈 정보
    sizes = []
    for i in range(len(goods['colorInfo'][0]['colorSizeInfo'])):
        size_info = goods['colorInfo'][0]['colorSizeInfo'][i]['erpSzCd']
        sizes.append(size_info)


    data = {
        'product_id': goodsNo,
        'brand': brandNm,
        'fixed_price': norPrc,
        'discounted_price': salePrc,
        'url': image_urls,
        'colors': colors,
        'sizes': sizes,
    }

    return data



def get_rank_score(ranking, item_count):
    try:
        rank_score = 1 - ((ranking - 1) / (item_count - 1))
    except:
        rank_score = 1

    return rank_score



def get_items(index):
    small_category_num = index['small'][0]

    url = f'https://www.thehandsome.com/api/display/1/ko/category/categoryGoodsList?dispMediaCd=10&sortGbn=20&pageSize={ITEMS_COUNT}&pageNo=1&norOutletGbCd=J&dispCtgNo={small_category_num}&productListLayout=4&theditedYn=N'

    goods_info = []

    soup = get_response(url, headers)
    info = soup.string
    goods_in_page = json.loads(info)['payload']['goodsList']

    for rank, goods in enumerate(goods_in_page, 1):
        
        goods_data = get_item_info(goods)
        goods_data['rank_score'] = get_rank_score(int(rank), len(goods_in_page))
        goods_data['top'] = index['top']
        goods_data['middle'] = index['middle'][1]
        goods_data['small'] = index['small'][1]
        goods_info.append(goods_data)
        print(len(goods_info), goods_data)


    return goods_info



def get_additional_info(product_id):
    url = f'https://pcw.thehandsome.com/ko/PM/productDetail/{product_id}?itmNo=003'

    soup = get_response(url, headers=headers)

    # 상품 설명
    try:
        product_info = soup.select('div.prd-desc-box')[0].text
    except:
        product_info = None

    # 피팅 정보
    try:
        fitting_info = soup.select('p.cmp-font')[0].text
    except:
        fitting_info = None

    # 상품 추가 정보
    try:
        additional_infos = soup.select('ul.cmp-list.list-dotType2.bottom6')
        additional_info_processed = []
        
        for info in additional_infos:
            additional_info_processed.append(info.text)
    except:
        additional_info_processed = None

    data = {
        'product_id': product_id,
        'product_info': product_info,
        'fitting_info': fitting_info,
        'additional_info': additional_info_processed
    }
    
    return data



def main():
    category_index = get_small_categories()
    all_info = []
    for index in category_index:
        small_category_info = get_items(index)
        all_info += small_category_info

    id_list = [item['product_id'] for item in all_info]
    
    all_additional_info = []
    for product_id in id_list:
        additional_info = get_additional_info(product_id)
        all_additional_info.append(additional_info)
        print(additional_info)

    print(sys.getsizeof(responses))



if __name__ == '__main__':
    main()  