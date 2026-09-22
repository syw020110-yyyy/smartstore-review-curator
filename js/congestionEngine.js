// 나비 (NABI) - 실시간 혼잡도 산출 및 대체 공간 스마트 큐레이션 엔진

import { SPOTS_DATA, ALLEYS_DATA, PUBLIC_CONGESTION_FEED } from './data.js?v=20260915_4';

/**
 * 두 좌표 간의 거리 (Haversine 공식, 단위: 미터)
 */
export function calculateDistance(lat1, lon1, lat2, lon2) {
  const R = 6371e3; // 지구 반경 (m)
  const phi1 = (lat1 * Math.PI) / 180;
  const phi2 = (lat2 * Math.PI) / 180;
  const deltaPhi = ((lat2 - lat1) * Math.PI) / 180;
  const deltaLambda = ((lon2 - lon1) * Math.PI) / 180;

  const a =
    Math.sin(deltaPhi / 2) * Math.sin(deltaPhi / 2) +
    Math.cos(phi1) * Math.cos(phi2) *
    Math.sin(deltaLambda / 2) * Math.sin(deltaLambda / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

  return Math.round(R * c);
}

/**
 * 골목 도보 이동 시간 계산 (평균 시속 4.0km + 골목길 우회 계수 1.1 적용)
 * @param {number} distanceMeters 
 * @returns {number} 도보 분(min)
 */
export function calculateWalkingTime(distanceMeters) {
  const speedMetersPerMinute = (4000 / 60); // 약 66.7 m/min
  const adjustedDistance = distanceMeters * 1.12; // 골목길 꺾임 보정
  const minutes = Math.ceil(adjustedDistance / speedMetersPerMinute);
  return Math.max(1, minutes);
}

/**
 * 혼잡도 점수에 따른 3단계 분류 및 메타데이터 반환
 */
export function getCongestionMeta(score) {
  if (score < 40) {
    return {
      level: 'smooth',
      label: '여유',
      statusText: '여유 예상',
      color: '#059669', // Vivid Emerald (초록)
      bgColor: '#ECFDF5',
      borderColor: '#A7F3D0',
      emoji: '🟢',
      badgeText: '여유 예상',
      statusSummary: '대기 없이 즉시 착석 가능한 쾌적한 상태입니다.'
    };
  } else if (score < 70) {
    return {
      level: 'moderate',
      label: '보통',
      statusText: '보통 예상',
      color: '#D97706', // Warm Amber (노랑/주황)
      bgColor: '#FFFBEB',
      borderColor: '#FDE68A',
      emoji: '🟡',
      badgeText: '보통 예상',
      statusSummary: '방문객이 있으나 즉시 또는 짧은 대기 후 입장 가능합니다.'
    };
  } else {
    return {
      level: 'crowded',
      label: '혼잡',
      statusText: '혼잡 예상',
      color: '#EF4444', // Neon Coral Red (빨강)
      bgColor: '#FEF2F2',
      borderColor: '#FECACA',
      emoji: '🔴',
      badgeText: '혼잡 예상',
      statusSummary: '현재 만석이거나 대기줄(웨이팅 30분 이상)이 예상됩니다.'
    };
  }
}

/**
 * 공공 데이터 및 실시간 시각을 반영한 실시간 혼잡도 점수 산출
 */
export function calculateRealtimeScore(spot, timeHour = new Date().getHours(), publicAreaScore = 55) {
  let score = spot.baseCongestionScore;
  
  // 시간대별 피크 반영 (13시~17시 피크 가중)
  let hourFactor = 1.0;
  if (timeHour >= 13 && timeHour <= 16) {
    hourFactor = 1.25;
  } else if (timeHour >= 18 && timeHour <= 20) {
    hourFactor = 1.15;
  } else if (timeHour < 11 || timeHour > 21) {
    hourFactor = 0.6;
  }

  // 공공 인구 혼잡도 영향 (가중치 30%)
  const publicImpact = (publicAreaScore - 50) * 0.3;
  
  const finalScore = Math.min(100, Math.max(10, Math.round(score * hourFactor + publicImpact)));
  return finalScore;
}

/**
 * 스마트 대체 공간 추천 알고리즘 (Alternative Curation Scoring)
 * - 대상 스팟이 혼잡할 때, 또는 현재 위치에서 반경 450m 내 즉시 입장 가능한 여유 공간 추천
 */
export function findAlternativeSpots(targetSpot, allSpots, userCoords = null) {
  const originCoords = targetSpot ? targetSpot.coords : userCoords;
  if (!originCoords) return [];

  // 후보 공간 필터링 (본인 제외)
  const candidates = allSpots.filter(s => !targetSpot || s.id !== targetSpot.id);

  // 각 후보 점수 매기기
  const scored = candidates.map(spot => {
    const dist = calculateDistance(originCoords[0], originCoords[1], spot.coords[0], spot.coords[1]);
    const walkMin = calculateWalkingTime(dist);
    const congestion = getCongestionMeta(spot.currentCongestionScore || spot.baseCongestionScore);
    
    // 점수 계산 (여유도 점수 50% + 거리 점수 30% + 카테고리 유사도 20%)
    let score = 0;
    
    // 1. 혼잡도 점수 (낮을수록 여유로움 -> 높은 점수)
    const rawCongestion = spot.currentCongestionScore || spot.baseCongestionScore;
    score += (100 - rawCongestion) * 0.5;

    // 2. 거리 감점 (반경 600m 기준)
    const distScore = Math.max(0, (600 - dist) / 600) * 30;
    score += distScore;

    // 3. 카테고리 유사도 (타겟 스팟과 같거나 보완적인 경우)
    if (targetSpot && spot.category === targetSpot.category) {
      score += 20;
    } else if (targetSpot && (spot.category === 'relax' || spot.category === 'cafe')) {
      score += 12;
    }

    // 4. 특별 큐레이션 보너스 (명시적 대체 추천 관계)
    if (targetSpot && targetSpot.suggestedAlternativeIds && targetSpot.suggestedAlternativeIds.includes(spot.id)) {
      score += 35;
    }

    return {
      spot,
      distanceMeters: dist,
      walkingMinutes: walkMin,
      congestionMeta: congestion,
      recommendationScore: score,
      isExplicitAlternative: targetSpot?.suggestedAlternativeIds?.includes(spot.id) || false
    };
  });

  // 추천 점수 내림차순 정렬
  scored.sort((a, b) => b.recommendationScore - a.recommendationScore);

  // 상위 3~4개 반환
  return scored.slice(0, 4);
}

/**
 * 한적한 우회 골목 산책로 (Breeze Routes) 추천
 */
export function getBreezeRoutes(region = 'all') {
  return ALLEYS_DATA.filter(alley => {
    const matchRegion = region === 'all' || alley.region === region;
    return matchRegion && alley.congestionLevel === 'smooth';
  });
}

/**
 * 네이버 지도 도보 길찾기 URL 생성 (출발지: originSpot, 도착지: destSpot)
 * - PC 웹 및 모바일 웹 환경을 자동 판별하여 최신 규격으로 출발지/도착지 자동 설정
 * @param {Object} originSpot - 출발 장소 객체 ({ name, coords: [lat, lng] })
 * @param {Object} destSpot - 도착 장소 객체 ({ name, coords: [lat, lng] })
 * @returns {string} 네이버 지도 도보 길찾기 웹 URL
 */
export function generateNaverMapWalkUrl(originSpot, destSpot) {
  if (!originSpot || !destSpot) return 'https://map.naver.com';

  const startLat = originSpot.coords[0];
  const startLng = originSpot.coords[1];
  const startName = encodeURIComponent(originSpot.name);

  const destLat = destSpot.coords[0];
  const destLng = destSpot.coords[1];
  const destName = encodeURIComponent(destSpot.name);

  // 모바일 기기 감지
  const isMobile = typeof navigator !== 'undefined' && /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);

  if (isMobile) {
    // 모바일 웹 길찾기 규격 (도보 pathType=3, 출발지 & 도착지 자동 주입)
    return `https://m.map.naver.com/route.naver?sname=${startName}&sx=${startLng}&sy=${startLat}&ename=${destName}&ex=${destLng}&ey=${destLat}&pathType=3`;
  }

  // PC 웹 최신 /p/directions 규격 (도보 walk 모드, 출발지 & 도착지 좌표 및 명칭 자동 세팅)
  return `https://map.naver.com/p/directions/${startLng},${startLat},${startName},,/${destLng},${destLat},${destName},,/-/walk?c=15.00,0,0,0,dh`;
}

/**
 * 카카오맵 도보 길찾기 URL 생성 (출발지: originSpot, 도착지: destSpot)
 */
export function generateKakaoMapWalkUrl(originSpot, destSpot) {
  if (!originSpot || !destSpot) return 'https://map.kakao.com';

  const startLat = originSpot.coords[0];
  const startLng = originSpot.coords[1];
  const startName = encodeURIComponent(originSpot.name);

  const destLat = destSpot.coords[0];
  const destLng = destSpot.coords[1];
  const destName = encodeURIComponent(destSpot.name);

  // 카카오맵 공식 길찾기 링크 규격 (/link/to/도착지/from/출발지)
  return `https://map.kakao.com/link/to/${destName},${destLat},${destLng}/from/${startName},${startLat},${startLng}`;
}

