// LOCAL PROTECTOR - 서촌·안국/북촌 현장 장소 제보 및 투표 시스템 (localStorage 기반)

export const GEOFENCES = {
  seochon: {
    id: 'seochon',
    name: '서촌',
    latMin: 37.575,
    latMax: 37.588,
    lngMin: 126.965,
    lngMax: 126.978,
    defaultCoords: [37.5805, 126.9715]
  },
  anguk: {
    id: 'anguk',
    name: '안국·북촌',
    latMin: 37.574,
    latMax: 37.588,
    lngMin: 126.979,
    lngMax: 126.993,
    defaultCoords: [37.5820, 126.9850]
  }
};

const STORAGE_KEY_PLACES = 'local_voted_places';
const STORAGE_KEY_USER_VOTES = 'local_user_voted_ids';

// 초기 시연용 샘플 데이터 (localStorage가 비어있을 때 제공)
const INITIAL_SAMPLE_PLACES = [
  {
    id: 1726000001,
    area: '서촌',
    name: '누하동 고즈넉한 작은 정원',
    address: '서울 종로구 자하문로9길 24',
    lat: 37.5812,
    lng: 126.9702,
    votes: 2, // 1표만 더 받으면 정식 승격 (투표 테스트용)
    status: 'pending'
  },
  {
    id: 1726000002,
    area: '안국·북촌',
    name: '계동길 숨은 한옥 쉼터',
    address: '서울 종로구 계동길 52',
    lat: 37.5835,
    lng: 126.9862,
    votes: 3, // 이미 3표 달성 (정식 승인 테스트용)
    status: 'verified'
  }
];

export class ReportManager {
  constructor() {
    this.initStorage();
  }

  initStorage() {
    try {
      const stored = localStorage.getItem(STORAGE_KEY_PLACES);
      if (!stored) {
        localStorage.setItem(STORAGE_KEY_PLACES, JSON.stringify(INITIAL_SAMPLE_PLACES));
      }
      if (!localStorage.getItem(STORAGE_KEY_USER_VOTES)) {
        localStorage.setItem(STORAGE_KEY_USER_VOTES, JSON.stringify([]));
      }
    } catch (err) {
      console.warn('localStorage access failed:', err);
    }
  }

  /**
   * 좌표가 서촌 또는 안국·북촌 지오펜스 안에 있는지 검사
   * @param {number} lat 
   * @param {number} lng 
   * @returns {'서촌' | '안국·북촌' | null}
   */
  checkGeofence(lat, lng) {
    const numLat = parseFloat(lat);
    const numLng = parseFloat(lng);

    if (isNaN(numLat) || isNaN(numLng)) return null;

    // 1. 서촌 권역 검사
    const sc = GEOFENCES.seochon;
    if (numLat >= sc.latMin && numLat <= sc.latMax && numLng >= sc.lngMin && numLng <= sc.lngMax) {
      return sc.name;
    }

    // 2. 안국·북촌 권역 검사
    const bk = GEOFENCES.anguk;
    if (numLat >= bk.latMin && numLat <= bk.latMax && numLng >= bk.lngMin && numLng <= bk.lngMax) {
      return bk.name;
    }

    return null;
  }

  /**
   * 전체 제보 장소 목록 조회
   */
  getReportedPlaces() {
    try {
      const data = localStorage.getItem(STORAGE_KEY_PLACES);
      return data ? JSON.parse(data) : [];
    } catch (e) {
      return [];
    }
  }

  /**
   * 신규 장소 제보 등록 (장소명 + 주소/링크 필수, 최초 1표로 시작)
   * @param {string} name 
   * @param {string} address 
   * @param {number} lat 
   * @param {number} lng 
   * @param {string} area 
   */
  addPlace(name, address, lat, lng, area) {
    const places = this.getReportedPlaces();
    const newPlace = {
      id: Date.now(),
      area: area || '서촌',
      name: name.trim(),
      address: address ? address.trim() : '위치 정보 없음',
      lat: parseFloat(lat),
      lng: parseFloat(lng),
      votes: 1, // 최초 제보 시 1표 시작
      status: 'pending' // 3표 미만: pending, 3표 이상: verified
    };

    places.unshift(newPlace);
    try {
      localStorage.setItem(STORAGE_KEY_PLACES, JSON.stringify(places));
      // 제보자 본인의 최초 투표 등록
      this.recordUserVote(newPlace.id);
    } catch (e) {
      console.error('Failed to save reported place:', e);
    }

    return newPlace;
  }

  /**
   * 장소 추천 투표 (votes + 1, 3표 도달 시 verified 자동 승격)
   * @param {number} placeId 
   */
  votePlace(placeId) {
    const places = this.getReportedPlaces();
    const target = places.find(p => p.id === Number(placeId));

    if (!target) return { success: false, message: '장소를 찾을 수 없습니다.' };

    if (this.hasUserVoted(placeId)) {
      return { success: false, message: '이미 추천 투표에 참여한 장소입니다.', place: target, alreadyVoted: true };
    }

    target.votes = (target.votes || 0) + 1;
    if (target.votes >= 3) {
      target.status = 'verified';
    }

    try {
      localStorage.setItem(STORAGE_KEY_PLACES, JSON.stringify(places));
      this.recordUserVote(placeId);
    } catch (e) {
      console.error('Failed to save vote:', e);
    }

    return {
      success: true,
      place: target,
      hasReachedVerified: target.votes === 3
    };
  }

  /**
   * 사용자가 해당 장소에 이미 투표했는지 여부 확인
   */
  hasUserVoted(placeId) {
    try {
      const votes = JSON.parse(localStorage.getItem(STORAGE_KEY_USER_VOTES) || '[]');
      return votes.includes(Number(placeId));
    } catch (e) {
      return false;
    }
  }

  /**
   * 사용자 투표 기록
   */
  recordUserVote(placeId) {
    try {
      const votes = JSON.parse(localStorage.getItem(STORAGE_KEY_USER_VOTES) || '[]');
      if (!votes.includes(Number(placeId))) {
        votes.push(Number(placeId));
        localStorage.setItem(STORAGE_KEY_USER_VOTES, JSON.stringify(votes));
      }
    } catch (e) {}
  }
}
