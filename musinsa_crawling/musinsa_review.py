import time
from bs4 import BeautifulSoup
import requests
import sys

ITEMS_COUNT = 100

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0',
    'Referer': 'https://www.musinsa.com/',
    'Accept-Language': 'en-US,en;q=0.5'
}


middle_category_nums = ['001006', '001004', '001005', '001010', '001002', '001003',
                        '001001', '001011', '001013', '001008', '002022', '002001',
                        '002002', '002025', '002017', '002003', '002020', '002019',
                        '002023', '002018', '002004', '002008', '002007', '002024',
                        '002009', '002013', '002012', '002016', '002021', '002014',
                        '002006', '002015', '003002', '003007', '003008', '003004',
                        '003009', '003005', '003010', '003011', '003006', '002006',
                        '002007', '002008', '022001', '022002', '022003']



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
    while flag == 0:
        
        soup = get_response(url, headers)

        products = soup.select('a.img-block')
        
        for product in products:
            product_links.append(product['href'].replace('//', 'https://'))
            if len(product_links) == ITEMS_COUNT:
                flag = 1
                break

        page += 1
        url = f'https://www.musinsa.com/categories/item/{num}?d_cat_cd={num}&brand=&list_kind=small&sort=sale_high&sub_sort=1d&page={page}&display_cnt=90&exclusive_yn=&sale_goods=&timesale_yn=&ex_soldout=&plusDeliveryYn=&kids=&color=&price1=&price2=&shoeSizeOption=&tags=&campaign_id=&includeKeywords=&measure='

    return product_links
        


def extract_one_review(review, product_num):
    # 댓글 단 사람
    user_name = review.select('p.review-profile__name')[0].text

    # 리뷰 id
    review_id = review.select('div.review-contents')[0]['data-review-no']
    
    # 메타 데이터
    meta_dict = {}
    metas = review.select('li.review-evaluation--type3__item')
    for meta in metas:
        key, value = meta.text.split(' ', 1)  # 공백을 기준으로 처음 나오는 부분만 분리
        meta_dict[key] = value

    # 리뷰 내용
    content = review.select('div.review-contents__text')[0].text

    # 배지
    badge = review.select('span.review-evaluation-button--type3__count')

    # 도움돼요
    helpful = badge[0].text

    # 스타일 좋아요
    try:
        style_good = badge[1].text
        
    except:
        style_good = None

    # 별 개수
    star_percentage = review.select('span.review-list__rating__active')[0]['style']

    if star_percentage == 'width: 100%':
        star = 5
    elif star_percentage == 'width: 80%':
        star = 4
    elif star_percentage == 'width: 60%':
        star = 3
    elif star_percentage == 'width: 40%':
        star = 2
    elif star_percentage == 'width: 20%':
        star = 1
    else:
        star = 0

    data = {
        'product_id': product_num,
        'review_id': review_id,
        'user_info': user_name,
        'meta_data': meta_dict,
        'body': content,
        'helpful': helpful,
        'good_style': style_good,
        'rate': star
    }

    return data



def extract_page_review_info(soup, product_num, review_type):
    one_page_reviews = []
    reviews = soup.select('div.review-list')
    for review in reviews:
        review_dict = extract_one_review(review, product_num)
        review_dict['review_type'] = review_type
        one_page_reviews.append(review_dict)
        
    return one_page_reviews



def main():
    all_product_links = []
    for middle_category_num in middle_category_nums:
        product_links = get_items(middle_category_num)
        all_product_links += product_links
        print(len(all_product_links), all_product_links[-1]) 

    product_nums = [link.split('/')[-1] for link in all_product_links]

    all_reviews = []
    for product_num in product_nums:
        review_types = ['style', 'goods', 'photo']
        product_num = str(product_num)
        for review_type in review_types:
            page_num = 1

            while True:
                url = f'https://goods.musinsa.com/api/goods/v2/review/{review_type}/list?similarNo=0&sort=up_cnt_desc&selectedSimilarNo={product_num}&page={page_num}&goodsNo={product_num}&rvck=202404150551&_=1713416512533'
                soup = get_response(url, headers)
                
                if not soup.select('p.review-profile__name'):
                    break   

                one_page_reviews = extract_page_review_info(soup, product_num, review_type)
                for one_page_review in one_page_reviews:
                    all_reviews.append(one_page_review)
                    print(one_page_review)
                    
                page_num += 1



if __name__ == '__main__':
    main()