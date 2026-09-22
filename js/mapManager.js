// 나비 (NABI) - Leaflet 기반 인터랙티브 혼잡도 지도 및 골목 렌더러

import { getCongestionMeta } from './congestionEngine.js?v=20260922_02';

// 카테고리별 대표 이모지 매핑
export function getSpotCategoryEmoji(spot) {
  const name = spot.name || '';
  const tags = (spot.tags || []).join(' ');
  const category = spot.category || '';
  
  if (name.includes('베이글') || name.includes('베이커리') || tags.includes('베이커리') || tags.includes('베이글')) {
    return '🥯';
  }
  if (category === 'cafe' || tags.includes('카페') || tags.includes('커피') || tags.includes('티룸') || tags.includes('티하우스')) {
    return '☕️';
  }
  if (category === 'book' || tags.includes('서점') || tags.includes('문학') || tags.includes('책')) {
    return '📚';
  }
  if (category === 'gallery' || tags.includes('미술관') || tags.includes('전시') || tags.includes('갤러리')) {
    return '🖼️';
  }
  if (category === 'dining' || tags.includes('식당') || tags.includes('맛집') || tags.includes('메밀') || tags.includes('삼계탕')) {
    return '🍽️';
  }
  if (category === 'relax' || tags.includes('쉼터') || tags.includes('정원') || tags.includes('산책') || tags.includes('공원')) {
    return '🌿';
  }
  return '📍';
}

// 3~4글자 핵심 장소명 간결화
export function getShortSpotName(name) {
  if (!name) return '';
  const customMap = {
    '아키비스트 서촌': '아키비스트',
    '호라 (HORA) 서촌 티하우스': '호라 티룸',
    '대오서점 카페': '대오서점',
    '보안여관 & 보안책방': '보안책방',
    '그라운드시소 서촌': '그라운드시소',
    '이상의 집 (문학 쉼터)': '이상의 집',
    '종로구립 박노수미술관 & 야외정원': '박노수미술관',
    '토속촌 삼계탕': '토속촌',
    '잘빠진메밀 서촌본점': '잘빠진메밀',
    '스태픽스 (STAFFPICKS)': '스태픽스',
    '카페 사이 (SAI) 갤러리 앤 티': '카페 사이',
    '체부동 한옥마을 금천교시장 골목 쉼터': '체부동 쉼터',
    '어니언 안국 (Onion Anguk)': '어니언',
    '톤티커피 (Tonti Coffee) 안국': '톤티커피',
    '런던베이글뮤지엄 안국점': '런던베이글',
    '북촌 이음서재 & 한옥 쉼터': '이음서재',
    '국립현대미술관(MMCA) 서울': 'MMCA 서울',
    '아트선재센터 & 더북소사이어티': '아트선재',
    '정독도서관 잔디정원 & 산책로': '정독도서관',
    '배렴가옥 (등록문화재 한옥 쉼터)': '배렴가옥',
    '프릳츠 원서점 (아라리오 뮤지엄)': '프릳츠 원서',
    '찻마시는뜰 (삼청동 한옥 찻집)': '찻마시는뜰'
  };

  if (customMap[name]) return customMap[name];

  let clean = name.replace(/\([^)]*\)/g, '').replace(/\[[^\]]*\]/g, '').trim();
  clean = clean.split('&')[0].split('·')[0].split(',')[0].trim();
  clean = clean.replace(/\s*(본점|서촌점|안국점|삼청점|북촌점)$/g, '').trim();
  return clean;
}

export class MapManager {
  constructor(mapContainerId, onSpotSelect) {
    this.containerId = mapContainerId;
    this.onSpotSelect = onSpotSelect;
    this.map = null;
    this.markersLayer = null;
    this.alleysLayer = null;
    this.routeLayer = null;
    this.userMarker = null;
    this.spotMarkerMap = new Map();
  }

  init(initialCenter = [37.5800, 126.9770], initialZoom = 15) {
    if (this.map) return;

    // Leaflet 맵 인스턴스 생성
    this.map = L.map(this.containerId, {
      center: initialCenter,
      zoom: initialZoom,
      zoomControl: false,
      attributionControl: false
    });

    // 워터마크 없는 고해상도 벡터 Positron 베이스맵 (Carto Positron 디자인 완벽 구현)
    try {
      if (typeof L.maplibreGL === 'function') {
        L.maplibreGL({
          style: 'https://tiles.openfreemap.org/styles/positron',
          attribution: '&copy; OpenStreetMap contributors &copy; CARTO'
        }).addTo(this.map);
      } else {
        throw new Error('MapLibre GL Leaflet plugin is not loaded');
      }
    } catch (err) {
      console.warn('MapLibre GL init error, falling back to tile layer:', err);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; OpenStreetMap contributors'
      }).addTo(this.map);
    }

    // 줌 컨트롤러 우측 상단 배치
    L.control.zoom({ position: 'topright' }).addTo(this.map);

    // 레이어 그룹 초기화
    this.alleysLayer = L.layerGroup().addTo(this.map);
    this.markersLayer = L.layerGroup().addTo(this.map);
    this.reportedLayer = L.layerGroup().addTo(this.map);
    this.routeLayer = L.layerGroup().addTo(this.map);
  }

  /**
   * 골목 네트워크 혼잡도 폴리라인 렌더링 (두께 1/3 완화 & 투명도 0.22~0.25의 은은한 배경선)
   */
  renderAlleys(alleys, activeRegion = 'all') {
    this.alleysLayer.clearLayers();

    const filteredAlleys = activeRegion === 'all'
      ? alleys
      : alleys.filter(a => a.region === activeRegion);

    filteredAlleys.forEach(alley => {
      let color = '#10B981'; // smooth (여유 - 에메랄드)
      let weight = 2.6;
      let opacity = 0.22;

      if (alley.congestionLevel === 'crowded') {
        color = '#EF4444'; // 혼잡 - 레드
        weight = 3.2;
        opacity = 0.25;
      } else if (alley.congestionLevel === 'moderate') {
        color = '#F59E0B'; // 보통 - 앰버 옐로우
        weight = 2.8;
        opacity = 0.24;
      } else {
        color = '#10B981';
        weight = 2.6;
        opacity = 0.22;
      }

      // 얇은 실선 형태의 보행선 (지도의 도로와 마커 텍스트를 가리지 않는 은은한 배경 요소)
      const mainLine = L.polyline(alley.coordinates, {
        color: color,
        weight: weight,
        opacity: opacity,
        lineCap: 'round',
        lineJoin: 'round'
      });

      // 마우스 인터랙션: 호버 시 살짝 선명화
      mainLine.on('mouseover', function () {
        this.setStyle({ opacity: 0.65, weight: weight + 1.2 });
      });
      mainLine.on('mouseout', function () {
        this.setStyle({ opacity: opacity, weight: weight });
      });

      // 툴팁 바인딩
      const statusEmoji = alley.congestionLevel === 'smooth' ? '🟢 여유' : (alley.congestionLevel === 'moderate' ? '🟡 보통' : '🔴 혼잡');
      mainLine.bindTooltip(`
        <div class="alley-tooltip">
          <strong>${alley.name}</strong>
          <span class="alley-badge badge-${alley.congestionLevel}">${statusEmoji}</span>
          <p class="alley-desc">${alley.description}</p>
        </div>
      `, {
        sticky: true,
        direction: 'top',
        className: 'custom-leaflet-tooltip'
      });

      this.alleysLayer.addLayer(mainLine);
    });
  }

  /**
   * 로컬 스팟 커스텀 마커 렌더링 ('이모지 미니 캡슐 핀' & 카테고리 필터 연동)
   */
  renderSpots(spots, activeCategory = 'all', activeSpotId = null, activeRegion = 'all') {
    this.markersLayer.clearLayers();
    this.spotMarkerMap.clear();

    const filteredByRegion = activeRegion === 'all'
      ? spots
      : spots.filter(s => s.region === activeRegion);

    filteredByRegion.forEach(spot => {
      const score = spot.currentCongestionScore || spot.baseCongestionScore;
      const meta = getCongestionMeta(score);
      const isSelected = activeSpotId === spot.id;

      // 카테고리 필터 연동 상태
      const isAll = activeCategory === 'all';
      const isMatch = isAll || spot.category === activeCategory;
      const isDimmed = !isAll && !isMatch;
      const isCategoryActive = !isAll && isMatch;

      const emoji = getSpotCategoryEmoji(spot);
      const shortName = getShortSpotName(spot.name);

      // [이모지 + 3~4글자 핵심 장소명] 둥근 미니 캡슐 마커 HTML
      const iconHtml = `
        <div class="custom-spot-marker ${meta.level} ${isSelected ? 'selected' : ''} ${isDimmed ? 'dimmed' : ''} ${isCategoryActive ? 'category-highlight' : ''}" data-spot-id="${spot.id}">
          <div class="marker-capsule" style="border-color: ${meta.color};">
            <span class="marker-emoji">${emoji}</span>
            <span class="marker-name">${shortName}</span>
          </div>
        </div>
      `;

      const customIcon = L.divIcon({
        html: iconHtml,
        className: 'leaflet-capsule-marker-container',
        iconSize: null,
        iconAnchor: null
      });

      // z-index 우선순위: 선택된 마커(1000) > 카테고리 강조 마커(300) > 기본(50) > 비선택 반투명(5)
      let zIndexOffset = 50;
      if (isSelected) {
        zIndexOffset = 1000;
      } else if (isCategoryActive) {
        zIndexOffset = 300;
      } else if (isDimmed) {
        zIndexOffset = 5;
      }

      const marker = L.marker(spot.coords, { 
        icon: customIcon,
        zIndexOffset: zIndexOffset 
      });
      
      marker.on('click', () => {
        if (this.onSpotSelect) {
          this.onSpotSelect(spot);
        }
      });

      this.markersLayer.addLayer(marker);
      this.spotMarkerMap.set(spot.id, marker);
    });
  }

  /**
   * 현장 제보 장소 마커 및 투표 팝업 렌더링 (미니 캡슐 핀 스타일 통일)
   * @param {Array} reportedPlaces 
   * @param {string} activeRegion 
   * @param {Function} onVoteClick 
   * @param {Function} hasUserVotedFn 
   */
  renderReportedPlaces(reportedPlaces = [], activeRegion = 'all', onVoteClick, hasUserVotedFn) {
    this.reportedLayer.clearLayers();

    const filtered = activeRegion === 'all'
      ? reportedPlaces
      : reportedPlaces.filter(p => {
          if (activeRegion === 'seochon') return p.area === '서촌';
          if (activeRegion === 'anguk') return p.area === '안국·북촌';
          return true;
        });

    filtered.forEach(place => {
      const isPending = (place.votes || 0) < 3;
      const hasVoted = hasUserVotedFn ? hasUserVotedFn(place.id) : false;
      const shortName = getShortSpotName(place.name);

      // 커스텀 HTML 아이콘 (미니 캡슐 스타일)
      const iconHtml = isPending ? `
        <div class="custom-reported-marker pending" data-place-id="${place.id}">
          <div class="reported-capsule">
            <span class="reported-emoji">⏳</span>
            <span class="reported-name">${shortName}</span>
            <span class="reported-vote-badge">${place.votes}/3</span>
          </div>
        </div>
      ` : `
        <div class="custom-spot-marker smooth verified-pin-marker" data-place-id="${place.id}">
          <div class="marker-capsule verified" style="border-color: #059669;">
            <span class="marker-emoji">✨</span>
            <span class="marker-name">${shortName}</span>
          </div>
        </div>
      `;

      const customIcon = L.divIcon({
        html: iconHtml,
        className: 'leaflet-capsule-marker-container',
        iconSize: null,
        iconAnchor: null
      });

      const marker = L.marker([place.lat, place.lng], { icon: customIcon });

      // 방문객 추천 투표 인터랙티브 팝업
      const popupHtml = `
        <div class="reported-popup-card">
          <div class="reported-popup-header">
            <span class="reported-area-tag">📍 ${place.area}</span>
            <span class="reported-status-pill ${isPending ? 'pending' : 'verified'}">
              ${isPending ? '⏳ 현장 검토 중' : '✨ 정식 추천지 인증'}
            </span>
          </div>
          <h4 class="reported-popup-title">${place.name}</h4>
          ${place.address ? `
            <div class="reported-popup-address-row">
              <span class="addr-text">📍 ${place.address}</span>
              <a href="${place.address.startsWith('http') ? place.address : `https://map.naver.com/v5/search/${encodeURIComponent(place.address || place.name)}`}" target="_blank" class="reported-naver-link">
                네이버 지도 ↗
              </a>
            </div>
          ` : ''}
          
          <div class="reported-gauge-box">
            <div class="gauge-header">
              <span>방문객 추천 투표</span>
              <span class="gauge-count"><strong>${place.votes}</strong> / 3명</span>
            </div>
            <div class="gauge-track">
              <div class="gauge-fill ${isPending ? 'pending' : 'verified'}" style="width: ${Math.min(100, ((place.votes || 1) / 3) * 100)}%;"></div>
            </div>
            <p class="gauge-guide">
              ${isPending ? '💡 3명이 추천하면 [초록색 정식 핀]으로 자동 전환됩니다.' : '🎉 3명 이상의 현장 추천을 받아 인증된 공간입니다.'}
            </p>
          </div>

          <div class="reported-popup-actions">
            ${hasVoted ? `
              <button class="btn-vote-submit voted" disabled>
                ✅ 이미 추천 투표 완료 (${place.votes}표)
              </button>
            ` : `
              <button class="btn-vote-submit" data-place-id="${place.id}">
                👍 저도 여기 추천해요! (+1표)
              </button>
            `}
          </div>
        </div>
      `;

      marker.bindPopup(popupHtml, {
        className: 'reported-custom-popup',
        maxWidth: 280,
        minWidth: 260
      });

      marker.on('popupopen', (e) => {
        const popupNode = e.popup.getElement();
        if (!popupNode) return;
        const voteBtn = popupNode.querySelector('.btn-vote-submit:not(.voted)');
        if (voteBtn) {
          voteBtn.addEventListener('click', () => {
            if (onVoteClick) {
              onVoteClick(place.id);
            }
          });
        }
      });

      this.reportedLayer.addLayer(marker);
    });
  }

  /**
   * 사용자 위치 핀 업데이트
   */
  updateUserLocation(coords, name = '현재 위치') {
    if (this.userMarker) {
      this.userMarker.setLatLng(coords);
      this.userMarker.setTooltipContent(`<div class="user-gps-tooltip">📍 ${name}</div>`);
    } else {
      const userIcon = L.divIcon({
        html: `
          <div class="user-gps-marker">
            <div class="gps-pulse"></div>
            <div class="gps-core"></div>
          </div>
        `,
        className: 'leaflet-user-marker',
        iconSize: [32, 32],
        iconAnchor: [16, 16]
      });

      this.userMarker = L.marker(coords, { icon: userIcon, zIndexOffset: 1000 }).addTo(this.map);
      this.userMarker.bindTooltip(`<div class="user-gps-tooltip">📍 ${name}</div>`, {
        permanent: false,
        direction: 'top'
      });
    }
  }

  /**
   * 만석 스팟 -> 대체 공간 간의 도보 우회 경로 (Dashed Line) 시각화
   */
  drawAlternativeRoute(originCoords, destCoords, originName, destName) {
    this.routeLayer.clearLayers();

    if (!originCoords || !destCoords) return;

    // 경로 라인 그리기
    const pathCoords = [originCoords, destCoords];

    // 글로우 언더레이
    const routeGlow = L.polyline(pathCoords, {
      color: '#10B981',
      weight: 8,
      opacity: 0.35,
      lineCap: 'round'
    });
    this.routeLayer.addLayer(routeGlow);

    // 애니메이션 점선
    const routeLine = L.polyline(pathCoords, {
      color: '#10B981',
      weight: 4,
      dashArray: '8, 8',
      className: 'animated-walking-route',
      lineCap: 'round'
    });
    this.routeLayer.addLayer(routeLine);

    // 지도 뷰포트를 두 지점이 모두 보이도록 맞춤
    const bounds = L.latLngBounds(pathCoords);
    this.map.fitBounds(bounds, { padding: [80, 80], maxZoom: 17, animate: true });
  }

  clearRoute() {
    this.routeLayer.clearLayers();
  }

  flyToLocation(coords, zoom = 16) {
    if (this.map) {
      this.map.flyTo(coords, zoom, {
        duration: 0.8,
        easeLinearity: 0.25
      });
    }
  }

  highlightMarker(spotId) {
    // DOM 업데이트
    document.querySelectorAll('.custom-spot-marker').forEach(el => {
      if (el.dataset.spotId === spotId || el.dataset.placeId === String(spotId)) {
        el.classList.add('selected');
        el.classList.remove('dimmed');
      } else {
        el.classList.remove('selected');
      }
    });

    // Leaflet 마커 zIndexOffset 업데이트
    this.spotMarkerMap.forEach((marker, id) => {
      if (id === spotId) {
        marker.setZIndexOffset(1000);
      }
    });
  }
}
