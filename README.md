# 무신사

## 상품 정보

1. 각 중분류 top100 페이지 돌면서 총 4700개의 item id 획득 **(여기서 requests)**
2. 그 id 갖고 각 상품의 url을 저장하고, 4700개의 각 상품 페이지 모두 돌기 시작
3. get_item_info에서 한 상품의 url에 **requests를 날리고** 필요한 정보 들어있는 부분만 json 형식으로 변환해서 return
4. 상품번호, 브랜드, 품번, 판매가, 회원가, 상품이미지, 대분류, 중분류 는 위 return값에서 구할수있음
5. 좋아요 수 구하려면 https://like.musinsa.com/like/api/v2/liketypes/goods/counts 에 **post requests**를 따로 날려야함
6. 누적판매, 나이, 성비는 f'[https://goods-detail.musinsa.com/goods/{goodsNo}/stat](https://goods-detail.musinsa.com/goods/%7BgoodsNo%7D/stat)' 에 **post requests** 날려야함
-> 한 상품에 대한 정보 뽑는데 request를 총 4번 날림

## 리뷰

1. 상품 정보 1단계와 마찬가지로 각 중분류 top100 상품들의 item id 획득(**requests**)
2. for문에서 한 상품의 리뷰들을 모두 긁음
    1. 한 상품에 대한 리뷰 정보는 f'[https://goods.musinsa.com/api/goods/v2/review/{review_type}/list?similarNo=0&sort=up_cnt_desc&selectedSimilarNo={product_num}&page={page_num}&goodsNo={product_num}&rvck=202404150551&_=1713416512533](https://goods.musinsa.com/api/goods/v2/review/%7Breview_type%7D/list?similarNo=0&sort=up_cnt_desc&selectedSimilarNo=%7Bproduct_num%7D&page=%7Bpage_num%7D&goodsNo=%7Bproduct_num%7D&rvck=202404150551&_=1713416512533)
        
        각 페이지에 10개씩 얻어올 수 있음. **각 페이지 별로 requests.**
        
        즉, 한 상품에 5만개의 리뷰가 있다면 한 상품 리뷰에서만 requests 5천번 필요
        

처음 모든 데이터를 긁어오는 과정은 굉장히

 오래 걸림. 처음에 모두 수집 후 주기적으로 돌릴 땐 처음 5개 페이지 정보만 받아올 수 있도록 해야함.

# w컨셉

## 상품 정보

1. main의 첫 for문에서는 https://api-display.wconcept.co.kr/display/api/v2/best/products 에서 한 번 마다 **post requests**를 날려 한 중분류의 top 100 item들의 id, finalPrice(쿠폰 할인가인데 여기서만 확인 가능함)
2. 다음 for 문에서는 얻어온 item id들을 가지고 돌림. https://www.wconcept.co.kr/Ajax/GetProductsInfo api에 item id를 payload로 써서 **post requests** 날려서 온 response를 json 형식으로 변환하고, 여기서 브랜드, 품번, 좋아요, 품절 여부, 정상가 , 상품명 까지 받아올 수 있음. 이미지 url들은 한번더 상품의 url에 **requests** 날려서 html 파싱 해야함.
    - sku는 아직 못함. 파싱 시도해보자

## 리뷰

1. 상품 정보의 1단계와 똑같이 진행하는데 id만 뽑아옴
2. 각 product id별로 https://www.wconcept.co.kr/Ajax/GetProductsInfo api 에 item id를 payload로 **post requests** 날려서 상품의 medium_cd, category_cd, itemtypecd를 저장(얘네를 payload로 써서 api에서 리뷰 얻어올 수 있음)
3. https://www.wconcept.co.kr/Ajax/ProductReViewList 위에서 얻어온 각 상품 id 별 medium_cd, category_cd, itemtypecd (+ page)를 payload로 써서 **post requests** 날리면 한 페이지의 10개 리뷰 정보를 스크래핑 가능. 한 상품에서 마지막 리뷰 페이지의 정보까지 받아올 때 까지 **post requests** 날리면서 리뷰 모두 수집

# 한섬

## 상품 정보

1. main의 첫  for문에서는 https://www.thehandsome.com/api/display/1/ko/category/categoryGoodsList?dispMediaCd=10&sortGbn=20&pageSize={ITEMS_COUNT}&pageNo=1&norOutletGbCd=J&dispCtgNo={num}&productListLayout=4&theditedYn=N  api **requests response**에서 각 중분류의 100개씩 아이템 info 다 얻어서 all_info에 저장. 한섬은 위 api에서 원하는 모든 정보(상품 id, 브랜드, 정가, 할인가, image urls, 색상 사이즈, 리뷰 개수) 다 저장 가능함.

## 리뷰

1. 상품 정보와 똑같은 response를 얻지만, 그 중에서 product_id, 리뷰 개수만 저장
2. 위에서 얻은 모든 상품 각각의 상품 id랑 리뷰 개수만 따로 뽑아서 리뷰 코드 실행. api를 통해서상품id, 리뷰 수를 payload로 **get requests** 날리면  한 번에 한 상품의 리뷰 몽땅 스크래핑 가능. 
    
    f'[https://www.thehandsome.com/api/goods/1/ko/goods/{goodsNo}/reviews?sortTypeCd=latest&revGbCd=&pageSize={goodsRevCnt}&pageNo=1](https://www.thehandsome.com/api/goods/1/ko/goods/%7BgoodsNo%7D/reviews?sortTypeCd=latest&revGbCd=&pageSize=%7BgoodsRevCnt%7D&pageNo=1)'
