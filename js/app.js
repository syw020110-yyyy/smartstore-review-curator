import { SPOTS_DATA, ALLEYS_DATA, PUBLIC_CONGESTION_FEED, MOCK_USER_LOCATIONS, REGIONS } from './data.js?v=20260922_02';
import { 
  calculateRealtimeScore, 
  findAlternativeSpots, 
  calculateDistance, 
  calculateWalkingTime, 
  generateNaverMapWalkUrl
} from './congestionEngine.js?v=20260922_02';
import { MapManager } from './mapManager.js?v=20260922_02';
import { UIManager } from './uiManager.js?v=20260922_02';
import { ReportManager } from './reportManager.js?v=20260922_02';

class App {
  constructor() {
    this.state = {
      activeRegion: 'all',
      activeCategory: 'all',
      currentLocationId: 'loc_gbg_sta',
      customUserCoords: null,
      customUserLocName: null,
      filterOnlySmooth: false,
      spots: [],
      alleys: [],
      activeSpot: null,
      isBottomSheetExpanded: false
    };

    this.mapManager = null;
    this.uiManager = null;
    this.reportManager = new ReportManager();
    this.toastTimeout = null;
  }

  init() {
    // 1. 혼잡도 점수 초기 계산 (현재 실시간 시각 기준)
    this.updateCongestionScores();
    this.state.alleys = [...ALLEYS_DATA];

    // 2. UI 매니저 인스턴스 초기화
    this.uiManager = new UIManager({
      onCategorySelect: (catId) => this.handleCategorySelect(catId),
      onRegionSelect: (regionId) => this.handleRegionSelect(regionId),
      onLocationChange: (locId) => this.handleLocationChange(locId),
      onSpotSelect: (spot) => this.handleSpotSelect(spot),
      onAlternativeSelect: (crowdedSpot, altSpot) => this.handleAlternativeSelect(crowdedSpot, altSpot)
    });

    // 3. 지도 인스턴스 초기화
    this.mapManager = new MapManager('map', (spot) => {
      this.handleSpotSelect(spot);
    });
    this.mapManager.init();

    // 4. 초기 데이터 및 렌더링
    this.renderAll();

    // 5. 전역 이벤트 리스너 바인딩
    this.bindGlobalEvents();

    // 6. 스플래시 인트로 화면 제어 (2초 유지 & 탭 시 즉시 스킵)
    this.initSplashScreen();

    console.log('🗺️ LOCAL PROTECTOR (로컬 프로텍터) 서촌·안국 실시간 혼잡도 서비스 시작');
  }

  initSplashScreen() {
    const splash = document.getElementById('splashScreen');
    if (!splash) return;

    let isDismissed = false;
    const dismiss = () => {
      if (isDismissed) return;
      isDismissed = true;
      splash.classList.add('fade-out');
      setTimeout(() => {
        splash.style.display = 'none';
      }, 650);
    };

    // 2초(2000ms) 후 자동 부드러운 페이드아웃
    setTimeout(dismiss, 2000);

    // 화면 터치/클릭 시 즉시 페이드아웃 스킵
    splash.addEventListener('click', dismiss);
    splash.addEventListener('touchstart', dismiss, { passive: true });
  }

  /**
   * 바텀 시트 인터랙티브 스와이프/드래그 제스처 컨트롤러
   * 모바일 터치 스와이프 및 PC 마우스 드래그를 모두 지원
   */
  initBottomSheetGesture() {
    const sheet = document.getElementById('bottomSheet');
    const handle = document.getElementById('sheetHandle');
    const header = sheet?.querySelector('.sheet-header');
    const listContainer = document.getElementById('spotListContainer');
    if (!sheet) return;

    let startY = 0;
    let initialTranslateY = 0;
    let isDragging = false;
    let startTime = 0;
    let isExpanded = sheet.classList.contains('expanded');

    // 접힘(Collapsed) 상태의 translateY (상단 헤더 약 88px만 노출)
    const getCollapsedY = () => {
      const sheetHeight = sheet.offsetHeight || 400;
      return Math.max(180, sheetHeight - 88);
    };

    const setTranslateY = (y, withTransition = false) => {
      if (withTransition) {
        sheet.style.transition = 'transform 0.36s cubic-bezier(0.16, 1, 0.3, 1)';
      } else {
        sheet.style.transition = 'none';
      }
      sheet.style.transform = `translateY(${y}px)`;
    };

    const expandSheet = () => {
      isExpanded = true;
      sheet.classList.add('expanded');
      sheet.classList.remove('dragging');
      setTranslateY(0, true);
    };

    const collapseSheet = () => {
      isExpanded = false;
      sheet.classList.remove('expanded');
      sheet.classList.remove('dragging');
      setTranslateY(getCollapsedY(), true);
    };

    // 초기 상태 반영
    if (isExpanded) {
      expandSheet();
    } else {
      collapseSheet();
    }

    const onStart = (clientY) => {
      isDragging = true;
      startY = clientY;
      startTime = Date.now();
      
      sheet.classList.add('dragging');

      // 현재 transform translateY 추출
      const style = window.getComputedStyle(sheet);
      const matrix = new DOMMatrixReadOnly(style.transform);
      initialTranslateY = matrix.m42;
      
      sheet.style.transition = 'none';
    };

    const onMove = (clientY, e) => {
      if (!isDragging) return;
      const deltaY = clientY - startY;

      // 리스트 내부 스크롤 중일 때 위로 드래그하는 동작은 리스트 스크롤에 양보
      if (isExpanded && listContainer && listContainer.scrollTop > 0 && deltaY < 0) {
        return;
      }

      let newY = initialTranslateY + deltaY;
      const collapsedY = getCollapsedY();

      // 상단 0px 위로 올릴 때 고무줄 저항
      if (newY < 0) {
        newY = newY * 0.22;
      } else if (newY > collapsedY + 40) {
        newY = collapsedY + (newY - collapsedY) * 0.22;
      }

      setTranslateY(newY, false);
      if (e && e.cancelable) e.preventDefault();
    };

    const onEnd = (clientY) => {
      if (!isDragging) return;
      isDragging = false;
      sheet.classList.remove('dragging');

      const deltaY = clientY - startY;
      const deltaTime = Math.max(1, Date.now() - startTime);
      const velocity = deltaY / deltaTime; // px/ms
      const collapsedY = getCollapsedY();

      // 단순 탭/클릭 판정 (이동거리 6px 미만, 시간 300ms 미만)
      if (Math.abs(deltaY) < 6 && deltaTime < 300) {
        if (isExpanded) {
          collapseSheet();
        } else {
          expandSheet();
        }
        return;
      }

      // 빠른 스와이프 제스처 (Flick) 감지
      if (velocity < -0.3) {
        expandSheet(); // 위로 빠르게 스와이프 -> 확장
      } else if (velocity > 0.3) {
        collapseSheet(); // 아래로 빠르게 스와이프 -> 축소
      } else {
        // 위치 기반 스냅 (절반 기준)
        const style = window.getComputedStyle(sheet);
        const matrix = new DOMMatrixReadOnly(style.transform);
        const currentPos = matrix.m42;

        if (currentPos < collapsedY * 0.5) {
          expandSheet();
        } else {
          collapseSheet();
        }
      }
    };

    // 터치 이벤트 리스너 (모바일)
    const dragTargets = [handle, header].filter(Boolean);
    dragTargets.forEach(el => {
      el.addEventListener('touchstart', (e) => {
        if (e.touches.length === 1) {
          onStart(e.touches[0].clientY);
        }
      }, { passive: true });
    });

    // 리스트 상단(scrollTop 0)에서 아래로 당길 때 바텀시트 제스처 연동
    listContainer?.addEventListener('touchstart', (e) => {
      if (listContainer.scrollTop <= 0 && e.touches.length === 1) {
        onStart(e.touches[0].clientY);
      }
    }, { passive: true });

    window.addEventListener('touchmove', (e) => {
      if (isDragging && e.touches.length === 1) {
        onMove(e.touches[0].clientY, e);
      }
    }, { passive: false });

    window.addEventListener('touchend', (e) => {
      if (isDragging) {
        const touch = e.changedTouches[0];
        onEnd(touch ? touch.clientY : startY);
      }
    });

    // 마우스 드래그 이벤트 리스너 (PC / 웹)
    dragTargets.forEach(el => {
      el.addEventListener('mousedown', (e) => {
        if (e.button === 0) {
          onStart(e.clientY);
          e.preventDefault();
        }
      });
    });

    window.addEventListener('mousemove', (e) => {
      if (isDragging) {
        onMove(e.clientY, e);
      }
    });

    window.addEventListener('mouseup', (e) => {
      if (isDragging) {
        onEnd(e.clientY);
      }
    });
  }

  updateCongestionScores() {
    const publicAreaScore = this.state.activeRegion === 'anguk' 
      ? PUBLIC_CONGESTION_FEED.areas.anguk.score 
      : PUBLIC_CONGESTION_FEED.areas.seochon.score;

    // 현재 실제 시각(Live Hour) 기준 자동 산출
    const currentHour = new Date().getHours();

    this.state.spots = SPOTS_DATA.map(spot => {
      const liveScore = calculateRealtimeScore(spot, currentHour, publicAreaScore);
      return {
        ...spot,
        currentCongestionScore: liveScore
      };
    });
  }

  getUserCoords() {
    if (this.state.customUserCoords) {
      return this.state.customUserCoords;
    }
    const loc = MOCK_USER_LOCATIONS.find(l => l.id === this.state.currentLocationId) || MOCK_USER_LOCATIONS[0];
    return loc.coords;
  }

  getUserLocName() {
    if (this.state.customUserLocName) {
      return this.state.customUserLocName;
    }
    const loc = MOCK_USER_LOCATIONS.find(l => l.id === this.state.currentLocationId) || MOCK_USER_LOCATIONS[0];
    return loc.name;
  }

  renderAll() {
    const userCoords = this.getUserCoords();

    // 1. 지도 렌더링
    this.mapManager.renderAlleys(this.state.alleys, this.state.activeRegion);
    this.mapManager.renderSpots(this.state.spots, this.state.activeCategory, this.state.activeSpot?.id, this.state.activeRegion);
    this.renderReportedPlaces();
    this.mapManager.updateUserLocation(userCoords, this.getUserLocName());

    // 2. UI 렌더링
    this.uiManager.renderCategoryBar(this.state.activeCategory, this.state.spots);
    this.uiManager.updateAreaStatus(this.state.activeRegion, PUBLIC_CONGESTION_FEED);
    this.uiManager.renderSpotList(
      this.state.spots,
      userCoords,
      this.state.activeCategory,
      this.state.filterOnlySmooth,
      this.state.activeRegion
    );
  }

  renderReportedPlaces() {
    const places = this.reportManager.getReportedPlaces();
    this.mapManager.renderReportedPlaces(
      places,
      this.state.activeRegion,
      (placeId) => this.handleVotePlace(placeId),
      (placeId) => this.reportManager.hasUserVoted(placeId)
    );
  }

  handleCategorySelect(catId) {
    this.state.activeCategory = catId;
    this.mapManager.renderSpots(this.state.spots, catId, this.state.activeSpot?.id, this.state.activeRegion);
    this.uiManager.renderCategoryBar(catId, this.state.spots);
    this.uiManager.renderSpotList(
      this.state.spots,
      this.getUserCoords(),
      catId,
      this.state.filterOnlySmooth,
      this.state.activeRegion
    );
  }

  handleRegionSelect(regionId) {
    this.state.activeRegion = regionId;
    const region = REGIONS[regionId.toUpperCase()] || REGIONS.ALL;

    this.mapManager.flyToLocation(region.center, region.zoom);
    this.updateCongestionScores();
    this.renderAll();

    // 탭 UI 갱신
    document.querySelectorAll('.region-tab-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.region === regionId);
    });
  }

  handleLocationChange(locId) {
    if (locId === 'custom_gps') {
      this.handleGpsLocationRequest();
      return;
    }

    this.state.customUserCoords = null;
    this.state.customUserLocName = null;
    this.state.currentLocationId = locId;

    const gpsBtn = document.getElementById('mapGpsBtn');
    if (gpsBtn) gpsBtn.classList.remove('active');

    const userCoords = this.getUserCoords();
    const locName = this.getUserLocName();

    this.mapManager.updateUserLocation(userCoords, locName);
    this.mapManager.flyToLocation(userCoords, 16);
    this.uiManager.renderLocationSelector(locId);
    this.uiManager.renderSpotList(
      this.state.spots,
      userCoords,
      this.state.activeCategory,
      this.state.filterOnlySmooth
    );

    this.showToast(`📍 기준 위치가 [${locName}]으로 변경되었습니다.`);
  }

  handleGpsLocationRequest() {
    const gpsBtn = document.getElementById('mapGpsBtn');
    if (gpsBtn) gpsBtn.classList.add('loading');

    if (!navigator.geolocation) {
      if (gpsBtn) gpsBtn.classList.remove('loading');
      this.showToast('⚠️ 현재 브라우저가 GPS 위치 확인을 지원하지 않습니다.');
      return;
    }

    this.showToast('🧭 현재 GPS 실시간 위치를 확인하고 있습니다...');

    navigator.geolocation.getCurrentPosition(
      (position) => {
        if (gpsBtn) {
          gpsBtn.classList.remove('loading');
          gpsBtn.classList.add('active');
        }

        const lat = position.coords.latitude;
        const lng = position.coords.longitude;
        const coords = [lat, lng];

        this.state.customUserCoords = coords;
        this.state.customUserLocName = '내 실시간 GPS 위치';
        this.state.currentLocationId = 'custom_gps';

        this.mapManager.updateUserLocation(coords, '내 실시간 위치 (GPS)');
        this.mapManager.flyToLocation(coords, 16);
        this.uiManager.renderLocationSelector('custom_gps', '내 실시간 위치 (GPS)');
        this.uiManager.renderSpotList(
          this.state.spots,
          coords,
          this.state.activeCategory,
          this.state.filterOnlySmooth
        );

        this.showToast('🎯 내 실시간 위치(GPS)를 감지하여 지도를 이동했습니다.');
      },
      (error) => {
        if (gpsBtn) gpsBtn.classList.remove('loading');
        console.warn('GPS Error:', error);
        let errorMsg = '⚠️ GPS 위치 권한이 거부되었거나 위치를 가져올 수 없습니다.';
        if (error.code === 1) {
          errorMsg = '⚠️ 브라우저 위치 권한 허용이 필요합니다.';
        }
        this.showToast(errorMsg);
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0
      }
    );
  }

  handleSpotSelect(spot) {
    this.state.activeSpot = spot;
    const userCoords = this.getUserCoords();
    const alternatives = findAlternativeSpots(spot, this.state.spots, userCoords);

    this.mapManager.flyToLocation(spot.coords, 17);
    this.mapManager.highlightMarker(spot.id);

    // 혼잡 스팟일 경우 상단 배너 표시
    const score = spot.currentCongestionScore || spot.baseCongestionScore;
    if (score >= 70) {
      this.uiManager.renderAlternativeBanner(spot, alternatives);
    }

    // 상세 모달 열기
    this.uiManager.openSpotModal(spot, alternatives, userCoords);
  }

  handleAlternativeSelect(originSpot, destSpot) {
    if (!originSpot || !destSpot) return;

    this.state.activeSpot = destSpot;
    
    // 네이버 지도 도보 길찾기 URL 생성 및 새 탭 오픈
    const targetUrl = generateNaverMapWalkUrl(originSpot, destSpot);
    window.open(targetUrl, '_blank');

    // 앱 내 지도에서는 도착 장소 마커를 포커스 및 하이라이트
    this.mapManager.clearRoute();
    this.mapManager.flyToLocation(destSpot.coords, 16);
    this.mapManager.highlightMarker(destSpot.id);

    // 거리 및 도보 소요시간 계산 후 알림 토스트 표시
    const dist = calculateDistance(originSpot.coords[0], originSpot.coords[1], destSpot.coords[0], destSpot.coords[1]);
    const walkMin = calculateWalkingTime(dist);

    this.showToast(`🗺️ 네이버 지도 길찾기가 열렸습니다! [출발: ${originSpot.name} → 도착: ${destSpot.name}] (도보 약 ${walkMin}분)`);
  }

  bindGlobalEvents() {
    // 1. 권역 탭 선택 (전체, 서촌, 안국)
    document.querySelectorAll('.region-tab-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const region = btn.dataset.region;
        this.handleRegionSelect(region);
      });
    });

    // 2. 여유 공간만 보기 필터 토글
    const smoothFilterToggle = document.getElementById('toggleSmoothOnly');
    smoothFilterToggle?.addEventListener('change', (e) => {
      this.state.filterOnlySmooth = e.target.checked;
      this.uiManager.renderSpotList(
        this.state.spots,
        this.getUserCoords(),
        this.state.activeCategory,
        this.state.filterOnlySmooth,
        this.state.activeRegion
      );
    });

    // 3. 바텀 시트 모바일 터치 스와이프 & 웹 마우스 드래그 제스처 초기화
    this.initBottomSheetGesture();

    // 4. 공공데이터 LIVE 대시보드 모달 열기 버튼
    const openDashboardModal = () => {
      const targetArea = this.state.activeRegion === 'anguk' ? '북촌한옥마을' : '경복궁';
      this.uiManager.openPublicDataModal(targetArea);
    };

    document.getElementById('btnOpenDashboard')?.addEventListener('click', openDashboardModal);
    document.getElementById('regionCrowdBadge')?.addEventListener('click', openDashboardModal);

    // 6. 우회 경로 클리어 버튼
    document.getElementById('btnClearRoute')?.addEventListener('click', () => {
      this.mapManager.clearRoute();
      this.showToast('지도 안내 경로가 해제되었습니다.');
    });

    // 7. 지도 좌측 하단 현위치(GPS) 탐색 버튼
    const mapGpsBtn = document.getElementById('mapGpsBtn');
    mapGpsBtn?.addEventListener('click', () => {
      this.handleGpsLocationRequest();
    });

    // 8. 지도 우측 하단 현장 장소 제보 플로팅 버튼
    const mapReportBtn = document.getElementById('mapReportBtn');
    mapReportBtn?.addEventListener('click', () => {
      this.handleOpenReportModal();
    });

    // 9. 최근 일주일 NEW UPDATE 장소 모달 열기 버튼 (매주 월요일 기준)
    const btnNewUpdate = document.getElementById('btnNewUpdate');
    btnNewUpdate?.addEventListener('click', () => {
      this.handleOpenNewUpdateModal();
    });
  }

  handleOpenNewUpdateModal() {
    const verifiedPlaces = this.reportManager.getReportedPlaces().filter(p => (p.votes || 0) >= 3);
    const newCuratedSpots = this.state.spots.slice(0, 4); // 상위 신규 큐레이션 스팟

    this.uiManager.openNewUpdateModal({
      verifiedPlaces,
      newSpots: newCuratedSpots,
      onNavigateToSpot: (coords, id) => {
        this.mapManager.flyToLocation(coords, 17);
        this.mapManager.highlightMarker(id);
        const targetSpot = this.state.spots.find(s => s.id === id);
        if (targetSpot) {
          this.handleSpotSelect(targetSpot);
        }
        this.showToast('🗺️ 선택한 신규 업데이트 장소로 이동했습니다.');
      }
    });
  }

  handleOpenReportModal() {
    // 1. 브라우저 Geolocation으로 현재 위치 판별
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          const lat = pos.coords.latitude;
          const lng = pos.coords.longitude;
          const detectedArea = this.reportManager.checkGeofence(lat, lng);

          this.uiManager.openReportModal({
            detectedArea: detectedArea || '서촌',
            detectedCoords: [lat, lng],
            isOutsideGeofence: !detectedArea,
            onSubmit: (data) => this.handleSubmitReport(data),
            onToast: (msg) => this.showToast(msg),
            onCheckGps: (checkLat, checkLng) => this.reportManager.checkGeofence(checkLat, checkLng)
          });
        },
        (err) => {
          // GPS 실패 시 서촌 기본값으로 오픈
          this.uiManager.openReportModal({
            detectedArea: '서촌',
            detectedCoords: [37.5805, 126.9715],
            isOutsideGeofence: false,
            onSubmit: (data) => this.handleSubmitReport(data),
            onToast: (msg) => this.showToast(msg),
            onCheckGps: (checkLat, checkLng) => this.reportManager.checkGeofence(checkLat, checkLng)
          });
        },
        { timeout: 3500, enableHighAccuracy: false }
      );
    } else {
      this.uiManager.openReportModal({
        detectedArea: '서촌',
        detectedCoords: [37.5805, 126.9715],
        isOutsideGeofence: false,
        onSubmit: (data) => this.handleSubmitReport(data),
        onToast: (msg) => this.showToast(msg),
        onCheckGps: (checkLat, checkLng) => this.reportManager.checkGeofence(checkLat, checkLng)
      });
    }
  }

  handleSubmitReport(data) {
    const newPlace = this.reportManager.addPlace(data.name, data.address, data.lat, data.lng, data.area);
    this.renderReportedPlaces();
    this.mapManager.flyToLocation([newPlace.lat, newPlace.lng], 16);
    this.showToast(`✨ [${newPlace.name}] 제보가 등록되었습니다! (초기 1표 / [검토 중 ⏳] 핀)`);
  }

  handleVotePlace(placeId) {
    const result = this.reportManager.votePlace(placeId);
    if (result.success) {
      this.renderReportedPlaces();
      if (result.hasReachedVerified) {
        this.showToast(`🎉 [${result.place.name}] 추천이 3표에 도달하여 [정식 핀 ✨]으로 승격되었습니다!`);
      } else {
        this.showToast(`👍 [${result.place.name}] 추천 투표가 반영되었습니다! (현재 ${result.place.votes}/3표)`);
      }
    } else {
      this.showToast(result.message || '이미 투표하셨거나 처리할 수 없습니다.');
    }
  }

  showToast(message) {
    let toast = document.getElementById('toastNotification');
    if (!toast) {
      toast = document.createElement('div');
      toast.id = 'toastNotification';
      toast.className = 'toast-notification';
      document.body.appendChild(toast);
    }
    toast.textContent = message;
    toast.classList.add('show');
    clearTimeout(this.toastTimeout);
    this.toastTimeout = setTimeout(() => {
      toast.classList.remove('show');
    }, 3500);
  }
}

// DOM 로드 완료 시 애플리케이션 기동
document.addEventListener('DOMContentLoaded', () => {
  const app = new App();
  app.init();
});
