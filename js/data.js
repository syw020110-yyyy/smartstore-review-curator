// 나비 (NABI) - 서촌 & 안국 로컬 공간 및 골목 네트워크 데이터셋

export const REGIONS = {
  ALL: { id: 'all', name: '서촌 & 안국 전체', center: [37.5800, 126.9770], zoom: 15 },
  SEOCHON: { id: 'seochon', name: '서촌 (경복궁 서측)', center: [37.5802, 126.9708], zoom: 16 },
  ANGUK: { id: 'anguk', name: '안국 & 북촌 (경복궁 동측)', center: [37.5798, 126.9835], zoom: 16 }
};

export const CATEGORIES = [
  { id: 'all', name: '전체', icon: 'compass', emoji: '✨' },
  { id: 'cafe', name: '한옥 카페', icon: 'coffee', emoji: '☕️' },
  { id: 'book', name: '독립서점·문학', icon: 'book-open', emoji: '📚' },
  { id: 'gallery', name: '전시·갤러리', icon: 'palette', emoji: '🖼️' },
  { id: 'relax', name: '조용한 쉼터·정원', icon: 'trees', emoji: '🌿' },
  { id: 'dining', name: '로컬 식당·티바', icon: 'utensils', emoji: '🍽️' }
];

export const MOCK_USER_LOCATIONS = [
  { id: 'loc_gbg_sta', name: '경복궁역 3번 출구 (서촌 입구)', coords: [37.5768, 126.9734], region: 'seochon' },
  { id: 'loc_tongin', name: '통인시장 앞 골목', coords: [37.5808, 126.9705], region: 'seochon' },
  { id: 'loc_anguk_sta', name: '안국역 1번 출구', coords: [37.5765, 126.9854], region: 'anguk' },
  { id: 'loc_yoonboseon', name: '윤보선길 돌담 앞', coords: [37.5786, 126.9828], region: 'anguk' },
  { id: 'loc_samcheong', name: '삼청동 카페거리 중심', coords: [37.5842, 126.9818], region: 'anguk' }
];

export const SPOTS_DATA = [
  // ================= 서촌 (SEOCHON) =================
  {
    id: 'sc_01',
    name: '아키비스트 서촌',
    category: 'cafe',
    region: 'seochon',
    coords: [37.5815, 126.9712],
    address: '서울 종로구 효자로13길 52',
    baseCongestionScore: 88, // 혼잡
    capacity: 22,
    rating: 4.6,
    reviewCount: 1820,
    tags: ['아인슈페너 명소', '웨이팅 잦음', '모던 인테리어'],
    imageUrl: 'https://images.unsplash.com/photo-1554118811-1e0d58224f24?auto=format&fit=crop&w=600&q=80',
    description: '서울 3대 아인슈페너로 유명한 인기 카페로, 주말 및 오후 피크시간대 웨이팅이 길게 형성됩니다.',
    peakHours: '13:00 ~ 17:00 (웨이팅 평균 30~50분)',
    alternativeReason: '현재 만석 대기 7팀 발생 중. 도보 3분 거리의 고즈넉한 한옥 티룸을 추천합니다.',
    suggestedAlternativeIds: ['sc_02', 'sc_04', 'sc_06']
  },
  {
    id: 'sc_02',
    name: '호라 (HORA) 서촌 티하우스',
    category: 'cafe',
    region: 'seochon',
    coords: [37.5819, 126.9698],
    address: '서울 종로구 옥인길 24 2층',
    baseCongestionScore: 25, // 여유
    capacity: 18,
    rating: 4.8,
    reviewCount: 340,
    tags: ['한적한 골목 2층', '정갈한 차와 다과', '차분한 음악'],
    imageUrl: 'https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?auto=format&fit=crop&w=600&q=80',
    description: '옥인동 골목 안쪽에 숨겨진 정갈한 티하우스. 잔잔한 재즈와 함께 다도를 즐길 수 있는 쉼표 같은 공간입니다.',
    peakHours: '대체로 여유로움 (평균 잔여좌석 6~8석)',
    availableSeats: 8,
    highlight: '아키비스트에서 도보 2분! 대기 없이 바로 입장 가능한 숨은 티룸'
  },
  {
    id: 'sc_03',
    name: '대오서점 카페',
    category: 'book',
    region: 'seochon',
    coords: [37.5801, 126.9702],
    address: '서울 종로구 자하문로7길 55',
    baseCongestionScore: 55, // 보통
    capacity: 25,
    rating: 4.5,
    reviewCount: 2100,
    tags: ['서울 최고령 서점', '레트로 한옥', '감성 포토존'],
    imageUrl: 'https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?auto=format&fit=crop&w=600&q=80',
    description: '1951년 개점한 서촌의 상징적 헌책방 겸 한옥 문화공간. 고즈넉한 안채 마당이 매력적입니다.',
    peakHours: '14:00 ~ 16:30',
    availableSeats: 4
  },
  {
    id: 'sc_04',
    name: '보안여관 & 보안책방',
    category: 'book',
    region: 'seochon',
    coords: [37.5786, 126.9729],
    address: '서울 종로구 효자로 33',
    baseCongestionScore: 32, // 여유
    capacity: 40,
    rating: 4.7,
    reviewCount: 950,
    tags: ['경복궁 돌담뷰', '예술 인문 서적', '복합문화공간'],
    imageUrl: 'https://images.unsplash.com/photo-1457369804613-52c61a468e7d?auto=format&fit=crop&w=600&q=80',
    description: '시인 서정주가 머물던 유서 깊은 여관을 개조한 곳으로, 2층 서점 창가에서 경복궁 영추문 돌담이 한눈에 들어옵니다.',
    peakHours: '주말 15:00 전후 약간 붐빔',
    availableSeats: 12,
    highlight: '넓은 2층 서가와 창가 좌석이 넉넉해 여유롭게 독서 가능'
  },
  {
    id: 'sc_05',
    name: '그라운드시소 서촌',
    category: 'gallery',
    region: 'seochon',
    coords: [37.5794, 126.9722],
    address: '서울 종로구 자하문로6길 18-8',
    baseCongestionScore: 82, // 혼잡
    capacity: 120,
    rating: 4.6,
    reviewCount: 4300,
    tags: ['감성 대형 전시', '중정 연못', '주말 대기 필수'],
    imageUrl: 'https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?auto=format&fit=crop&w=600&q=80',
    description: '원형 중정과 연못이 아름다운 복합 전시 공간. 인기 기획전으로 시간대별 관람 인파가 집중됩니다.',
    peakHours: '주말 전시간대 혼잡',
    suggestedAlternativeIds: ['sc_04', 'sc_07', 'sc_11']
  },
  {
    id: 'sc_06',
    name: '이상의 집 (문학 쉼터)',
    category: 'relax',
    region: 'seochon',
    coords: [37.5790, 126.9715],
    address: '서울 종로구 자하문로7길 18',
    baseCongestionScore: 18, // 여유
    capacity: 20,
    rating: 4.7,
    reviewCount: 880,
    tags: ['무료 개방', '천재 시인 이상 생가터', '고요한 암실 체험'],
    imageUrl: 'https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=600&q=80',
    description: '작가 이상이 유년시절을 보낸 집터에 조성된 문화공간. 누구나 무료로 차를 마시며 쉬어갈 수 있습니다.',
    peakHours: '상시 여유로움',
    availableSeats: 10,
    highlight: '자하문로 메인길 바로 뒤편, 북적이는 인파를 피해 쉬어가는 최고의 쉼터'
  },
  {
    id: 'sc_07',
    name: '종로구립 박노수미술관 & 야외정원',
    category: 'gallery',
    region: 'seochon',
    coords: [37.5828, 126.9678],
    address: '서울 종로구 옥인1길 34',
    baseCongestionScore: 30, // 여유
    capacity: 50,
    rating: 4.7,
    reviewCount: 1250,
    tags: ['아름다운 석조 한옥', '수목원급 뒷마당 정원', '인왕산 조망'],
    imageUrl: 'https://images.unsplash.com/photo-1544816155-12df9643f363?auto=format&fit=crop&w=600&q=80',
    description: '화백 박노수의 가옥과 정원. 인왕산 자락 숲속 정원을 산책하며 고요한 미술 관람이 가능합니다.',
    peakHours: '14:00 전후 약간 방문객 증가',
    availableSeats: 25,
    highlight: '그라운드시소 대기 대신 옥인동 정원 산책 코스로 강력 추천'
  },
  {
    id: 'sc_08',
    name: '토속촌 삼계탕',
    category: 'dining',
    region: 'seochon',
    coords: [37.5779, 126.9718],
    address: '서울 종로구 자하문로5길 5',
    baseCongestionScore: 92, // 혼잡
    capacity: 180,
    rating: 4.3,
    reviewCount: 7800,
    tags: ['한옥 맛집', '외국인 관광객 밀집', '줄 서는 식당'],
    imageUrl: 'https://images.unsplash.com/photo-1569718212165-3a8278d5f624?auto=format&fit=crop&w=600&q=80',
    description: '서촌의 대표적인 한옥 대형 맛집으로 식사 시간대 골목 전체에 긴 대기줄이 형성됩니다.',
    peakHours: '11:30 ~ 14:00, 17:30 ~ 19:30',
    suggestedAlternativeIds: ['sc_09', 'sc_12']
  },
  {
    id: 'sc_09',
    name: '잘빠진메밀 서촌본점',
    category: 'dining',
    region: 'seochon',
    coords: [37.5798, 126.9711],
    address: '서울 종로구 자하문로11길 4',
    baseCongestionScore: 48, // 보통
    capacity: 35,
    rating: 4.6,
    reviewCount: 2200,
    tags: ['순메밀 막국수', '전통주 샘플러', '깔끔한 한식'],
    imageUrl: 'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=600&q=80',
    description: '100% 순메밀 막국수와 수육을 맛볼 수 있는 정갈한 한식당입니다.',
    peakHours: '점심 피크 12:30 전후',
    availableSeats: 5
  },
  {
    id: 'sc_10',
    name: '스태픽스 (STAFFPICKS)',
    category: 'cafe',
    region: 'seochon',
    coords: [37.5818, 126.9665],
    address: '서울 종로구 사직로9길 22',
    baseCongestionScore: 78, // 혼잡
    capacity: 60,
    rating: 4.5,
    reviewCount: 3100,
    tags: ['거대 은행나무 잔디밭', '반려견 동반', '파운드케이크 맛집'],
    imageUrl: 'https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?auto=format&fit=crop&w=600&q=80',
    description: '서촌 언덕 위 넓은 잔디마당과 고목 은행나무 뷰로 사계절 내내 테라스 좌석 쟁탈전이 일어납니다.',
    peakHours: '주말 오후 전 시간대 만석',
    suggestedAlternativeIds: ['sc_02', 'sc_06', 'sc_11']
  },
  {
    id: 'sc_11',
    name: '카페 사이 (SAI) 갤러리 앤 티',
    category: 'cafe',
    region: 'seochon',
    coords: [37.5824, 126.9692],
    address: '서울 종로구 필운대로 65-1',
    baseCongestionScore: 22, // 여유
    capacity: 24,
    rating: 4.8,
    reviewCount: 290,
    tags: ['조용한 필운대로', '미니 갤러리', '드립 커피'],
    imageUrl: 'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=600&q=80',
    description: '필운대로 안쪽에 위치하여 관광객 발길이 덜 닿는 여유로운 갤러리형 카페입니다.',
    peakHours: '상시 쾌적',
    availableSeats: 9,
    highlight: '스태픽스 인파를 벗어나 도보 4분 만에 만나는 평온한 드립커피 공간'
  },
  {
    id: 'sc_12',
    name: '체부동 한옥마을 금천교시장 골목 쉼터',
    category: 'relax',
    region: 'seochon',
    coords: [37.5772, 126.9715],
    address: '서울 종로구 자하문로1길 32',
    baseCongestionScore: 35, // 여유
    capacity: 20,
    rating: 4.6,
    reviewCount: 420,
    tags: ['세종마을 음식문화거리 안쪽', '한옥 사랑방', '잠깐의 휴식'],
    imageUrl: 'https://images.unsplash.com/photo-1528728329032-2972f65dfb3f?auto=format&fit=crop&w=600&q=80',
    description: '식후 북적이는 음식거리를 벗어나 숨을 고를 수 있는 마을 주민 쉼터형 한옥 공간입니다.',
    peakHours: '저녁 18:30 이후 약간 증가',
    availableSeats: 7
  },

  // ================= 안국 & 북촌 (ANGUK & BUKCHON) =================
  {
    id: 'ag_01',
    name: '어니언 안국 (Onion Anguk)',
    category: 'cafe',
    region: 'anguk',
    coords: [37.5781, 126.9866],
    address: '서울 종로구 계동길 5',
    baseCongestionScore: 95, // 극심한 혼잡
    capacity: 85,
    rating: 4.4,
    reviewCount: 9200,
    tags: ['대표 대형 한옥 베이커리', '웨이팅 1시간+', '좌식 대청마루'],
    imageUrl: 'https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=600&q=80',
    description: '안국역 바로 앞 전통 한옥 베이커리로, 오픈 직후부터 마감까지 국내외 관광객 대기가 끊이지 않습니다.',
    peakHours: '11:00 ~ 18:00 (웨이팅 평균 40~80분)',
    alternativeReason: '현재 웨이팅 24팀(약 50분 소요 예상). 3분 거리의 정갈한 한옥 다실을 즉시 추천합니다.',
    suggestedAlternativeIds: ['ag_02', 'ag_06', 'ag_09']
  },
  {
    id: 'ag_02',
    name: '톤티커피 (Tonti Coffee) 안국',
    category: 'cafe',
    region: 'anguk',
    coords: [37.5792, 126.9859],
    address: '서울 종로구 북촌로 6-8',
    baseCongestionScore: 28, // 여유
    capacity: 20,
    rating: 4.9,
    reviewCount: 680,
    tags: ['골목 안 숨은 스페셜티', '호주식 플랫화이트', '조용한 중정'],
    imageUrl: 'https://images.unsplash.com/photo-1507133750040-3a7f573045f4?auto=format&fit=crop&w=600&q=80',
    description: '안국역 대로변에서 살짝 들어간 골목 안쪽에 위치해 조용하게 최고급 원두 커피를 즐길 수 있습니다.',
    peakHours: '13:30 전후 약간 북적임',
    availableSeats: 7,
    highlight: '어니언 안국에서 도보 3분! 대기 0명, 바로 착석 가능한 스페셜티 카페'
  },
  {
    id: 'ag_03',
    name: '런던베이글뮤지엄 안국점',
    category: 'cafe',
    region: 'anguk',
    coords: [37.5791, 126.9863],
    address: '서울 종로구 북촌로4길 20',
    baseCongestionScore: 98, // 극심한 혼잡
    capacity: 45,
    rating: 4.5,
    reviewCount: 14500,
    tags: ['수백 명 캐치테이블 대기', '베이글 성지', '인파 극심'],
    imageUrl: 'https://images.unsplash.com/photo-1586985289688-ca3cf47d3e6e?auto=format&fit=crop&w=600&q=80',
    description: '북촌에서 가장 혼잡도가 높은 베이커리. 현장 대기 접수 시 기본 2시간 이상 대기가 발생합니다.',
    peakHours: '08:00 ~ 17:00 (상시 극심한 혼잡)',
    suggestedAlternativeIds: ['ag_02', 'ag_04', 'ag_08']
  },
  {
    id: 'ag_04',
    name: '북촌 이음서재 & 한옥 쉼터',
    category: 'book',
    region: 'anguk',
    coords: [37.5812, 126.9845],
    address: '서울 종로구 계동길 105',
    baseCongestionScore: 20, // 여유
    capacity: 25,
    rating: 4.8,
    reviewCount: 310,
    tags: ['무료 독서 쉼터', '고즈넉한 한옥 툇마루', '북촌 주민 커뮤니티'],
    imageUrl: 'https://images.unsplash.com/photo-1481627834876-b7833e8f5570?auto=format&fit=crop&w=600&q=80',
    description: '북촌 계동길 꼭대기 부근에 위치한 공공 한옥 서재. 툇마루에 앉아 책을 읽으며 고요를 만끽할 수 있습니다.',
    peakHours: '상시 여유로움',
    availableSeats: 11,
    highlight: '런던베이글·어니언 대기에 지친 도보객들의 오아시스 같은 힐링 공간'
  },
  {
    id: 'ag_05',
    name: '국립현대미술관(MMCA) 서울',
    category: 'gallery',
    region: 'anguk',
    coords: [37.5799, 126.9806],
    address: '서울 종로구 삼청로 30',
    baseCongestionScore: 62, // 보통
    capacity: 500,
    rating: 4.8,
    reviewCount: 12000,
    tags: ['대형 현대미술관', '넓은 마당 잔디밭', '테라로사 카페'],
    imageUrl: 'https://images.unsplash.com/photo-1565008447742-97f6f38c985c?auto=format&fit=crop&w=600&q=80',
    description: '종친부 경내와 어우러진 현대미술관. 실내 전시공간이 광활하여 인파가 분산되는 편입니다.',
    peakHours: '주말 14:00 ~ 16:00',
    availableSeats: 35
  },
  {
    id: 'ag_06',
    name: '아트선재센터 & 더북소사이어티',
    category: 'gallery',
    region: 'anguk',
    coords: [37.5794, 126.9822],
    address: '서울 종로구 율곡로3길 87',
    baseCongestionScore: 30, // 여유
    capacity: 80,
    rating: 4.7,
    reviewCount: 1800,
    tags: ['실험적 현대미술', '예술 서점', '윤보선길 초입'],
    imageUrl: 'https://images.unsplash.com/photo-1579783902614-a3fb3927b675?auto=format&fit=crop&w=600&q=80',
    description: '윤보선길과 감고당길 사이에 위치한 현대미술 전문 미술관. 차분하고 밀도 높은 전시를 감상할 수 있습니다.',
    peakHours: '주말 15:00 전후 약간 증가',
    availableSeats: 18,
    highlight: '삼청로 인파를 피해 예술 서적과 한적한 전시를 즐기기 좋은 공간'
  },
  {
    id: 'ag_07',
    name: '정독도서관 잔디정원 & 산책로',
    category: 'relax',
    region: 'anguk',
    coords: [37.5810, 126.9824],
    address: '서울 종로구 북촌로5길 48',
    baseCongestionScore: 24, // 여유
    capacity: 200,
    rating: 4.7,
    reviewCount: 3400,
    tags: ['도심 속 거대 정원', '등나무 벤치', '무료 휴식'],
    imageUrl: 'https://images.unsplash.com/photo-1519331379826-f10be5486c6f?auto=format&fit=crop&w=600&q=80',
    description: '옛 경기고등학교 터에 자리한 도서관. 사계절 꽃과 나무가 우거진 거대한 잔디마당 벤치에서 누구나 쉴 수 있습니다.',
    peakHours: '봄/가을 주말 피크닉 시즌 외 상시 여유',
    availableSeats: 45,
    highlight: '북촌 카페 만석 시 테이크아웃 커피 한 잔 들고 쉬어가기 가장 좋은 녹지'
  },
  {
    id: 'ag_08',
    name: '배렴가옥 (등록문화재 한옥 쉼터)',
    category: 'relax',
    region: 'anguk',
    coords: [37.5817, 126.9856],
    address: '서울 종로구 계동길 89',
    baseCongestionScore: 15, // 여유
    capacity: 25,
    rating: 4.8,
    reviewCount: 420,
    tags: ['한국화가 배렴 생가', '조용한 한옥 사랑채', '무료 관람/휴식'],
    imageUrl: 'https://images.unsplash.com/photo-1578632767115-351597cf2477?auto=format&fit=crop&w=600&q=80',
    description: '전통 근대 한옥의 원형을 보존한 문화공간. 고즈넉한 대청마루에서 바람 소리를 들으며 쉴 수 있는 완벽한 아지트입니다.',
    peakHours: '상시 한적함',
    availableSeats: 12,
    highlight: '계동길 관광객들이 대부분 지나치는 숨겨진 보물 같은 한옥 쉼터'
  },
  {
    id: 'ag_09',
    name: '프릳츠 원서점 (아라리오 뮤지엄)',
    category: 'cafe',
    region: 'anguk',
    coords: [37.5776, 126.9892],
    address: '서울 종로구 율곡로 83',
    baseCongestionScore: 50, // 보통
    capacity: 50,
    rating: 4.6,
    reviewCount: 4800,
    tags: ['김수근 건축 공간사옥', '탑골 한옥 뷰', '스페셜티 & 크루아상'],
    imageUrl: 'https://images.unsplash.com/photo-1442512595331-e89e73853f31?auto=format&fit=crop&w=600&q=80',
    description: '한국 현대건축의 걸작 공간사옥 앞마당 한옥에 자리한 카페. 야외 석탑을 바라보며 커피를 즐깁니다.',
    peakHours: '13:00 ~ 15:30',
    availableSeats: 6
  },
  {
    id: 'ag_10',
    name: '찻마시는뜰 (삼청동 한옥 찻집)',
    category: 'cafe',
    region: 'anguk',
    coords: [37.5833, 126.9838],
    address: '서울 종로구 북촌로11길 26',
    baseCongestionScore: 68, // 보통
    capacity: 35,
    rating: 4.6,
    reviewCount: 1950,
    tags: ['북촌 한옥 전경 뷰', '전통 야생차', '중정 꽃밭'],
    imageUrl: 'https://images.unsplash.com/photo-1544787219-7f47ccb76574?auto=format&fit=crop&w=600&q=80',
    description: '삼청동과 북촌이 내려다보이는 높은 지대에 위치한 전통 찻집. 한옥 마당 꽃밭과 기와 풍경이 수려합니다.',
    peakHours: '14:00 ~ 17:00',
    availableSeats: 3
  }
];

// 골목길 네트워크 (Polyline coordinates and live congestion level)
export const ALLEYS_DATA = [
  // 서촌 골목
  {
    id: 'alley_sc_main',
    name: '자하문로 메인 로드',
    region: 'seochon',
    congestionLevel: 'crowded', // 혼잡
    congestionScore: 85,
    coordinates: [
      [37.5768, 126.9734],
      [37.5790, 126.9723],
      [37.5815, 126.9715],
      [37.5835, 126.9708]
    ],
    description: '서촌의 주 통행로로 버스 및 보행객이 집중되는 구간'
  },
  {
    id: 'alley_sc_hanok_inner',
    name: '누하동·체부동 한옥 샛길 (Breeze Route)',
    region: 'seochon',
    congestionLevel: 'smooth', // 여유
    congestionScore: 24,
    coordinates: [
      [37.5775, 126.9708],
      [37.5792, 126.9703],
      [37.5805, 126.9698],
      [37.5822, 126.9692]
    ],
    description: '돌담과 고즈넉한 한옥 처마가 이어지는 한적한 산책 골목'
  },
  {
    id: 'alley_sc_okin',
    name: '옥인길 인왕산 조망 샛길',
    region: 'seochon',
    congestionLevel: 'smooth', // 여유
    congestionScore: 30,
    coordinates: [
      [37.5808, 126.9705],
      [37.5818, 126.9685],
      [37.5828, 126.9678]
    ],
    description: '수성동 계곡 방면으로 이어지는 정취 있는 서촌 안쪽 길'
  },

  // 안국 & 북촌 골목
  {
    id: 'alley_ag_bukchon_main',
    name: '북촌로 메인 로드',
    region: 'anguk',
    congestionLevel: 'crowded', // 혼잡
    congestionScore: 92,
    coordinates: [
      [37.5765, 126.9854],
      [37.5791, 126.9863],
      [37.5815, 126.9858],
      [37.5838, 126.9850]
    ],
    description: '베이커리 및 외국인 관광객 밀집 구간 (웨이팅 인파)'
  },
  {
    id: 'alley_ag_yoonboseon',
    name: '윤보선길 돌담길 (Breeze Route)',
    region: 'anguk',
    congestionLevel: 'smooth', // 여유
    congestionScore: 22,
    coordinates: [
      [37.5768, 126.9835],
      [37.5786, 126.9828],
      [37.5805, 126.9824]
    ],
    description: '고택 돌담과 작은 공방들이 이어져 인파 없이 걷기 좋은 우회길'
  },
  {
    id: 'alley_ag_gamgodang',
    name: '감고당길 (보행자 전용로)',
    region: 'anguk',
    congestionLevel: 'moderate', // 보통
    congestionScore: 58,
    coordinates: [
      [37.5772, 126.9820],
      [37.5794, 126.9818],
      [37.5810, 126.9812]
    ],
    description: '덕성여고와 미술관 사이의 벽화 돌담길'
  },
  {
    id: 'alley_ag_gyedong_inner',
    name: '계동길 한옥 주거 샛길 (Breeze Route)',
    region: 'anguk',
    congestionLevel: 'smooth', // 여유
    congestionScore: 26,
    coordinates: [
      [37.5800, 126.9868],
      [37.5815, 126.9862],
      [37.5830, 126.9858]
    ],
    description: '옛 목욕탕과 참기름집 등 로컬 정취가 남은 한적한 골목길'
  }
];

// 서울시 실시간 인구혼잡도 모의 데이터 (Seoul City Data API 기준)
export const PUBLIC_CONGESTION_FEED = {
  updatedAt: '2026-09-08 19:15:00',
  areas: {
    seochon: {
      name: '경복궁·서촌 구역',
      status: '보통',
      score: 52,
      populationIndex: '약 12,500명 체류 중',
      weather: '맑음 22℃ (도보 산책 쾌적)',
      airQuality: '좋음'
    },
    anguk: {
      name: '북촌한옥마을·안국 구역',
      status: '약간 붐빔',
      score: 68,
      populationIndex: '약 18,200명 체류 중',
      weather: '맑음 22℃',
      airQuality: '좋음'
    }
  }
};
