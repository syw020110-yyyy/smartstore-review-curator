"""
Sample Smartstore Reviews Dataset for testing and offline demo.
Based on authentic Korean e-commerce Smartstore review patterns.
"""
import pandas as pd

SAMPLE_REVIEWS = [
    {
        "review_id": "rev_001",
        "user_id": "minh******",
        "rating": 5,
        "created_date": "2026.07.16",
        "option_name": "오늘도새우장: 오늘도새우장 300g",
        "review_text": "메가쇼에서 사서 먹어보고 너무 맛있어서 또 구매했습니다. 새우살이 진짜 통통하고 씹는 순간 톡 터지는 쫄깃쫄깃한 식감이 일품이에요! 간장 양념이 너무 짜지도 않고 달달하면서 감칠맛이 돌아서 밥 두 공기 뚝딱 비웠습니다. 남은 간장에 계란 노른자 얹어서 비벼 먹으니 최고네요. 다 먹으면 대용량으로 무조건 재구매할 예정입니다. 조금 더 큰 용량도 만들어주시면 좋겠어요^^",
        "photo_urls": [
            "https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=600&auto=format&fit=crop&q=80",
            "https://images.unsplash.com/photo-1544025162-d76694265947?w=600&auto=format&fit=crop&q=80"
        ],
        "image_count": 2,
    },
    {
        "review_id": "rev_002",
        "user_id": "toss******",
        "rating": 5,
        "created_date": "2026.07.15",
        "option_name": "오늘도새우장: 오늘도새우장 500g",
        "review_text": "믿고 먹는 새우장 재구매 10000%입니다! 새우장 좋아하는 까다로운 중학생 아들이 다른 곳 새우장은 비리다고 절대 안 먹는데, 여기꺼 먹더니 '엄마 여기 새우는 비린 맛 하나도 없고 진짜 달아' 하면서 밥 세 그릇을 비우네요ㅋㅋ 남편도 '아들만 주지 말고 내 술안주도 남겨놔라' 하면서 쟁탈전 벌어졌습니다. 아이부터 어른까지 온 가족 입맛 제대로 사로잡았어요. 새우장은 이제 여기에 정착합니다!",
        "photo_urls": [
            "https://images.unsplash.com/photo-1615141982883-c7ad0e69fd62?w=600&auto=format&fit=crop&q=80"
        ],
        "image_count": 1,
    },
    {
        "review_id": "rev_003",
        "user_id": "kimb******",
        "rating": 5,
        "created_date": "2026.07.14",
        "option_name": "오늘도새우장: 오늘도새우장 300g (2개)",
        "review_text": "새우장은 언제 먹어도 질리지 않아요. 새우 껍질이 다 까져있어서 손에 묻힐 필요 없이 젓가락으로 쏙쏙 집어먹기만 하면 되니까 먹기가 너무 편하고 위생적입니다. 특히 새우 다 먹고 남은 간장이 진짜 만능 맛간장이에요. 버리기 너무 아까워서 사장님 추천대로 간장계란밥 해먹고 메추리알 장조림까지 만들었습니다. 1석 2조 가성비 최고입니다!",
        "photo_urls": [
            "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=600&auto=format&fit=crop&q=80"
        ],
        "image_count": 1,
    },
    {
        "review_id": "rev_004",
        "user_id": "star******",
        "rating": 5,
        "created_date": "2026.07.12",
        "option_name": "오늘도새우장: 오늘도새우장 500g",
        "review_text": "새우장 진~~~~~~짜 맛있어요ㅠㅠ!!!! 제가 워낙 해산물 귀신이라 전국 유명 맛집 다 시켜먹어봤는데, 일단 입에 넣었을 때 살이 물렁거리지 않고 탱탱 쫀득하게 씹히는 탄력감 자체가 완전히 다릅니다!! 간장도 저염이라 짜지 않아서 국물 떠먹어도 부담 없어요. 서비스로 보내주신 오징어젓갈까지 감동 그 자체... 번창하세요 꼭꼭 다시 주문합니다!",
        "photo_urls": [
            "https://images.unsplash.com/photo-1559847844-5315695dadae?w=600&auto=format&fit=crop&q=80",
            "https://images.unsplash.com/photo-1541544741938-0af808871cc0?w=600&auto=format&fit=crop&q=80"
        ],
        "image_count": 2,
    },
    {
        "review_id": "rev_005",
        "user_id": "suji******",
        "rating": 5,
        "created_date": "2026.07.10",
        "option_name": "선물세트: 새우장 500g + 전복장 300g",
        "review_text": "부산 음식 박람회 구경 갔을 때 시식해보고 눈이 번쩍 뜨여서 지인 선물용으로 여러 개 주문했습니다. 받는 분마다 여태껏 먹어본 간장새우장 중에 비린내도 안 나고 제일 깔끔하고 고급스럽다고 칭찬 일색이셔서 선물한 제가 다 뿌듯했네요. 아이스박스에 보냉팩 빵빵하게 채워져서 신선도 완벽하게 배송되었습니다. 포장도 선물하기 좋게 세련되었어요.",
        "photo_urls": [
            "https://images.unsplash.com/photo-1579871494447-9811cf80d66c?w=600&auto=format&fit=crop&q=80"
        ],
        "image_count": 1,
    },
    {
        "review_id": "rev_006",
        "user_id": "love******",
        "rating": 5,
        "created_date": "2026.07.09",
        "option_name": "오늘도새우장: 오늘도새우장 1kg 벌크",
        "review_text": "통영애서 새우장 맛있는 건 전 세계 사람들이 다 알아야 해요! 마트에서 파는 일반 새우장 사다 줬더니 10대 아들이 한 입 먹고 이건 그 맛이 아니라고 안 먹겠다고 하네요ㅋㅋ 남편도 벌크 대용량 없냐고 노래를 불러서 1kg 주문했는데 일주일도 안 돼서 바닥을 보였습니다. 밥도둑이라는 말이 괜히 나온 게 아니에요. 무조건 강추합니다.",
        "photo_urls": [
            "https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=600&auto=format&fit=crop&q=80"
        ],
        "image_count": 1,
    },
    {
        "review_id": "rev_007",
        "user_id": "july******",
        "rating": 5,
        "created_date": "2026.07.08",
        "option_name": "오늘도새우장: 오늘도새우장 300g",
        "review_text": "여름철이라 해산물 택배 주문하는 게 조금 걱정스러웠는데, 보냉팩이랑 드라이아이스가 아직 꽝꽝 얼어있는 상태로 도착해서 감동했습니다. 위생 씰링 포장도 아주 깔끔해서 간장 한 방울 새지 않고 무사히 왔어요. 새우 내장도 깔끔하게 손질되어 있어서 쓴맛이나 텁텁함 전혀 없이 순수한 단맛만 가득합니다. 정성이 느껴지는 식품입니다.",
        "photo_urls": [
            "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=600&auto=format&fit=crop&q=80"
        ],
        "image_count": 1,
    },
    {
        "review_id": "rev_008",
        "user_id": "park******",
        "rating": 5,
        "created_date": "2026.07.07",
        "option_name": "오늘도새우장: 오늘도새우장 300g",
        "review_text": "평소 입이 짧아서 밥 한 공기 다 못 먹는 7살 딸아이가 이 새우장 간장에 비벼주면 한 그릇을 싹싹 비워요! 너무 짜거나 자극적인 조미료 맛이 아니라 자연스러운 단맛이라 안심하고 아이 먹일 수 있습니다. 새우 껍질 까는 번거로움도 없으니 바쁜 워킹맘에게는 최고의 반찬 구원투수예요. 냉장고에 떨어지지 않게 계속 주문할게요.",
        "photo_urls": [
            "https://images.unsplash.com/photo-1615141982883-c7ad0e69fd62?w=600&auto=format&fit=crop&q=80"
        ],
        "image_count": 1,
    },
    # 단답형/단문 리뷰 (필터 탈락 케이스)
    {
        "review_id": "rev_009",
        "user_id": "user01****",
        "rating": 5,
        "created_date": "2026.07.05",
        "option_name": "오늘도새우장: 오늘도새우장 300g",
        "review_text": "좋아요좋아요좋아요 맛있습니다 재구매할게요.",
        "photo_urls": [],
        "image_count": 0,
    },
    {
        "review_id": "rev_010",
        "user_id": "user02****",
        "rating": 4,
        "created_date": "2026.07.04",
        "option_name": "오늘도새우장: 오늘도새우장 300g",
        "review_text": "배송 빠르고 맛 괜찮아요.",
        "photo_urls": [],
        "image_count": 0,
    },
    {
        "review_id": "rev_011",
        "user_id": "user03****",
        "rating": 5,
        "created_date": "2026.07.03",
        "option_name": "오늘도새우장: 오늘도새우장 300g",
        "review_text": "딸아이가 맛있게 먹었습니다^^",
        "photo_urls": [],
        "image_count": 0,
    },
    {
        "review_id": "rev_012",
        "user_id": "user04****",
        "rating": 5,
        "created_date": "2026.07.02",
        "option_name": "오늘도새우장: 오늘도새우장 500g",
        "review_text": "떨어질 때마다 시켜먹는 단골집이에요ㅎㅎ 강추!",
        "photo_urls": [],
        "image_count": 0,
    },
    {
        "review_id": "rev_013",
        "user_id": "user05****",
        "rating": 4,
        "created_date": "2026.07.01",
        "option_name": "오늘도새우장: 오늘도새우장 300g",
        "review_text": "포토 첨부합니다. 맛은 좋은데 양이 살짝 아쉬워요 대용량도 팔아주세요.",
        "photo_urls": ["https://images.unsplash.com/photo-1544025162-d76694265947?w=600&auto=format&fit=crop&q=80"],
        "image_count": 1,
    },
    {
        "review_id": "rev_014",
        "user_id": "user06****",
        "rating": 3,
        "created_date": "2026.06.30",
        "option_name": "오늘도새우장: 오늘도새우장 300g",
        "review_text": "가격이 저렴해서 사봤는데 제 입맛에는 조금 달아요.",
        "photo_urls": [],
        "image_count": 0,
    },
    {
        "review_id": "rev_015",
        "user_id": "cheol****",
        "rating": 5,
        "created_date": "2026.06.28",
        "option_name": "오늘도새우장: 오늘도새우장 500g",
        "review_text": "자취생 혼밥족인데 배달음식 질릴 때마다 따뜻한 쌀밥에 이거 새우 세 마리랑 간장 두 숟갈 참기름 둘러 먹으면 자취방이 고급 일식당으로 바뀝니다. 비린내에 정말 민감해서 굴이나 게장도 잘 못 먹는데 이건 신기할 정도로 비린 향이 하나도 안 나고 고소하고 감칠맛만 남아요. 혼자 사는 친구들한테도 적극 추천 중입니다!",
        "photo_urls": [
            "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=600&auto=format&fit=crop&q=80"
        ],
        "image_count": 1,
    }
]

def get_sample_dataframe() -> pd.DataFrame:
    """Returns sample reviews as a pandas DataFrame with text_length precomputed."""
    df = pd.DataFrame(SAMPLE_REVIEWS)
    df["text_length"] = df["review_text"].apply(lambda x: len(str(x)))
    return df

if __name__ == "__main__":
    df = get_sample_dataframe()
    print("Sample reviews loaded:", len(df))
    print(df[["review_id", "user_id", "rating", "image_count", "text_length"]].head())
