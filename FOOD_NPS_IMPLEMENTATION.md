# Food NPS Implementation Summary

## 완료된 작업 (Completed Work)

### 1. 더미 데이터 분석 (Dummy Data Analysis) ✅
- `dummy_qualtrics_food.csv`: 배달의민족 Qualtrics 설문 데이터 분석
- `dummy_population_food.csv`: 241개 인구통계 가중치 세그먼트 확인
- `dummy_coding_food.csv`: 개방형 응답 카테고리 분류 데이터 파악
- `dummy_var_food.csv`: 변수 설명 및 질문 텍스트 매핑

### 2. Food NPS 전용 모듈 개발 ✅
**파일**: `backend/food_nps.py`

**주요 기능**:
- `load_food_qualtrics_data()`: 한글 Qualtrics 데이터 로딩
- `load_food_population_data()`: 241개 세그먼트 가중치 데이터 로딩
- `load_food_coding_data()`: 카테고리 분류 데이터 로딩
- `calculate_food_nps_with_weighting()`: 가중 NPS 계산 (정규화 포함)
- `calculate_category_response_rates()`: NPS 그룹별 카테고리 응답율 계산

### 3. API 엔드포인트 추가 ✅
**파일**: `backend/main.py`

**신규 엔드포인트**:
- `POST /food-nps/upload/qualtrics`: Qualtrics 데이터 업로드
- `POST /food-nps/upload/population`: 인구통계 가중치 업로드
- `POST /food-nps/upload/coding`: 카테고리 분류 데이터 업로드
- `POST /food-nps/analyze`: 가중 NPS 분석 실행
- `GET /food-nps/status`: 업로드 상태 확인

### 4. 60그룹 가중치 로직 구현 ✅
**알고리즘**:
1. 설문 데이터를 인구통계 가중치와 병합
2. mem_rate 사용하여 가중치 적용
3. 정규화: scale_factor = unweighted_total / weighted_total
4. NPS 그룹별 가중 백분율 계산 (Promoter 9-10, Passive 7-8, Detractor 0-6)
5. 인구통계 세그먼트별 NPS 분해

**세그먼트 구조**:
- gender (2) × age_group (5) × rgn_nm (3) × bmclub (2) = 60 기본 그룹
- 실제 데이터는 division, is_mfo 포함하여 241개 세그먼트

### 5. 카테고리 응답율 계산 ✅
**기능**:
- NPS 그룹별 (Promoter/Passive/Detractor) 카테고리 분포
- 가중치 적용된 응답율 계산
- 카테고리별 응답 수 및 가중치 합계
- 응답율 순으로 정렬

### 6. 테스트 스크립트 작성 ✅
**파일**: `test_food_nps_api.py`

**테스트 내용**:
1. Qualtrics 데이터 업로드 테스트
2. Population 데이터 업로드 테스트
3. Coding 데이터 업로드 테스트
4. 업로드 상태 확인
5. 가중 NPS 분석 실행
6. 결과 검증 (예상 NPS ~-18.0)

**실행 방법**:
```bash
python test_food_nps_api.py
```

### 7. 문서화 업데이트 ✅
**파일**: `CLAUDE.md`

**추가 내용**:
- Food NPS API 엔드포인트 상세 설명
- 데이터 구조 요구사항
- 예제 워크플로우
- 예상 결과값
- 테스트 방법

## 기술 스택 (Technical Stack)

### Backend
- Python FastAPI
- pandas (데이터 처리)
- chardet (인코딩 감지)
- UTF-8-BOM (한글 지원)

### 핵심 알고리즘
- **60그룹 가중치**: 인구통계 기반 가중치 적용
- **정규화**: 샘플 크기 보존을 위한 스케일 팩터 적용
- **NPS 계산**: (Promoters% - Detractors%) × 100
- **카테고리 분석**: NPS 그룹별 가중 응답율

## 사용 방법 (Usage)

### 1. 백엔드 서버 시작
```bash
cd backend
uvicorn main:app --reload
```

### 2. 데이터 업로드 및 분석
```python
import requests

BASE_URL = "http://localhost:8000"

# Qualtrics 데이터 업로드
with open("dummy_qualtrics_food.csv", "rb") as f:
    files = {"file": f}
    r = requests.post(f"{BASE_URL}/food-nps/upload/qualtrics", files=files)
    print(r.json())

# Population 데이터 업로드
with open("dummy_population_food.csv", "rb") as f:
    files = {"file": f}
    r = requests.post(f"{BASE_URL}/food-nps/upload/population", files=files)
    print(r.json())

# Coding 데이터 업로드 (선택사항)
with open("dummy_coding_food.csv", "rb") as f:
    files = {"file": f}
    r = requests.post(f"{BASE_URL}/food-nps/upload/coding", files=files)
    print(r.json())

# 분석 실행
r = requests.post(f"{BASE_URL}/food-nps/analyze")
result = r.json()

print(f"Weighted NPS: {result['nps_score']}")
print(f"Total Responses: {result['total_responses']}")
print(f"Promoters: {result['promoters_pct']}%")
print(f"Detractors: {result['detractors_pct']}%")
```

### 3. 테스트 실행
```bash
python test_food_nps_api.py
```

## 예상 결과 (Expected Results)

Based on `guide/MANUAL_monthly_analysis.md`:
- **NPS Score**: ~-18.0
- **Sample Size**: ~2,409 respondents
- **Weighting**: 241 demographic segments
- **Response Rate**: 20-40% (카테고리별 차이)

## 다음 단계 (Next Steps)

### 필요시 추가 개발 가능 항목:
1. **프론트엔드 통합**: React 컴포넌트에서 Food NPS API 호출
2. **시각화**: 인구통계별 NPS 차트
3. **엑셀 내보내기**: 분석 결과 Excel 다운로드
4. **시계열 분석**: 월별 NPS 트렌드
5. **벤치마크 비교**: 경쟁사 대비 NPS 비교

### 성능 최적화:
1. **캐싱**: 분석 결과 캐싱
2. **비동기 처리**: 대용량 데이터 처리
3. **데이터베이스**: 영구 저장소 통합
4. **API 속도**: 응답 시간 최적화

## 참고 자료 (References)

- `guide/MANUAL_monthly_analysis.md`: 월간 NPS 분석 워크플로우
- `CLAUDE.md`: 프로젝트 전체 문서
- `backend/food_nps.py`: Food NPS 모듈 소스코드
- `test_food_nps_api.py`: API 테스트 스크립트
