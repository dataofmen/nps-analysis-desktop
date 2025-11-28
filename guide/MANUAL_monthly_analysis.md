# Food NPS 주관식 응답 카테고리 분석 월별 처리 매뉴얼

**작성일**: 2025-10-28
**대상**: Food NPS 분석 담당자
**목적**: 매월 동일한 방식으로 NPS 주관식 응답 분석을 수행하고 보고서 생성

---

## 목차

1. [전체 작업 플로우](#1-전체-작업-플로우)
2. [사전 준비사항](#2-사전-준비사항)
3. [단계별 작업 가이드](#3-단계별-작업-가이드)
4. [파일 구조 및 설명](#4-파일-구조-및-설명)
5. [검증 체크리스트](#5-검증-체크리스트)
6. [문제 해결 가이드](#6-문제-해결-가이드)
7. [월별 작업 체크리스트](#7-월별-작업-체크리스트)

---

## 1. 전체 작업 플로우

```
[1단계] 데이터 준비
   ↓
[2단계] 가중치 계산 (60개 그룹)
   ↓
[3단계] NPS 분포 계산 (정규화 적용)
   ↓
[4단계] 카테고리별 응답율 계산 (정규화 적용)
   ↓
[5단계] 결과 검증
   ↓
[6단계] 보고서 생성 (필요시 수동 업데이트)
```

**총 소요 시간**: 약 30-60분 (데이터 준비 제외)

---

## 2. 사전 준비사항

### 2.1 필수 입력 파일

모든 파일은 `/Users/hmkwon/Project/011_NPS/csv_output/` 디렉토리에 위치해야 합니다.

| 파일명 | 설명 | 필수 컬럼 | 비고 |
|--------|------|----------|------|
| `food_nps_data.csv` | NPS 점수 데이터 | `ResponseId`, `Q1_1`, `gender`, `age_group`, `rgn_nm`, `bmclub` | Q1_1은 0-10 범위 |
| `food_nps_01_data_01.csv` | 주관식 응답 데이터셋1 | `ResponseId`, `Q2` (주관식 텍스트), `gender`, `age_group`, `rgn_nm`, `bmclub` | 카테고리 분류 완료된 데이터 |
| `food_nps_02_data_02.csv` | 주관식 응답 데이터셋2 | 동일 | Dataset2는 description header 확인 필요 |
| `food_nps_01_var_01.csv` | 데이터셋1 변수 설명 | `변수명`, `변수_설명` | 참고용 |
| `food_nps_02_var_02.csv` | 데이터셋2 변수 설명 | 동일 | 참고용 |

### 2.2 필수 가중치 파일

| 파일명 | 설명 | 필수 컬럼 |
|--------|------|----------|
| `weight_gender_age_rgn_membership.csv` | 60개 그룹 가중치 | `gender`, `age_group`, `rgn_nm`, `bmclub`, `mem_rate` |

**중요**: 가중치 파일은 매월 동일하게 사용 (모집단 비율이 변경되지 않는 한)

### 2.3 환경 요구사항

- **Python 버전**: 3.8 이상
- **필수 라이브러리**: pandas, numpy
- **설치 명령**:
  ```bash
  pip install pandas numpy
  ```

---

## 3. 단계별 작업 가이드

### 3.1 데이터 준비 및 검증

#### 3.1.1 데이터 파일 확인

```bash
cd /Users/hmkwon/Project/011_NPS
ls -lh csv_output/food_nps*.csv
ls -lh weight_gender_age_rgn_membership.csv
```

**확인 사항**:
- [ ] 모든 필수 파일이 존재하는가?
- [ ] 파일 크기가 0이 아닌가?
- [ ] UTF-8-BOM 인코딩인가? (Excel에서 저장 시 "CSV UTF-8(쉼표로 분리)" 선택)

#### 3.1.2 데이터 품질 체크

**Python 스크립트로 빠른 체크**:

```python
import pandas as pd

# NPS 데이터 체크
df = pd.read_csv('csv_output/food_nps_data.csv', encoding='utf-8-sig')
print(f"총 행 수: {len(df)}")
print(f"gender 결측값: {df['gender'].isna().sum()}")
print(f"Q1_1 결측값: {df['Q1_1'].isna().sum()}")
print(f"Q1_1 범위: {df['Q1_1'].min()} ~ {df['Q1_1'].max()}")
print(f"bmclub 결측값: {df['bmclub'].isna().sum()}")
```

**기대 결과**:
- gender 결측값: 10개 내외 (제거 예정)
- Q1_1 범위: 0-10
- Q1_1 결측값: 0개
- bmclub: '구독' 또는 '미구독'만 존재

---

### 3.2 NPS 가중 분포 계산 (60개 그룹, 정규화 적용)

#### 스크립트 실행

```bash
python3 calculate_nps_weighted_60groups.py
```

#### 예상 출력

```
================================================================================
NPS 점수별 응답자 비율 계산 (60개 그룹 가중치 적용)
================================================================================

[1] 데이터 파일 읽는 중...
원본 데이터 shape: (2418, X)
가중치 데이터 shape: (60, X)

[2] gender 변수 결측값 제거
XX개 행 제거 (결측값)
최종 데이터 shape: (2409, X)

...

=== NPS 분류별 통계 (60개 그룹 가중치) ===
           응답자수   가중응답자수  비율(%)  가중비율(%)
NPS분류
Detractor  1024  2436.41  42.51    44.69
Passive     683  1560.69  28.35    28.62
Promoter    702  1455.63  29.14    26.70

=== NPS 점수 계산 (60개 그룹 가중치) ===
비가중 NPS: -13.37
가중 NPS (60개 그룹): -17.99
```

#### 검증 포인트

**✅ 체크리스트**:
- [ ] 총 응답자 수 = 2,409명 (gender 결측 제거 후)
- [ ] Promoter + Passive + Detractor = 2,409명
- [ ] 가중 NPS: 약 -18.0 (소수점 첫째자리 반올림)
- [ ] 출력 파일 생성 확인:
  - `nps_score_distribution_60groups.csv` (11행: 0-10점 분포)
  - `nps_category_summary_60groups.csv` (3행: P/P/D 요약)

#### 생성 파일 확인

```bash
# 파일 존재 확인
ls -lh nps_score_distribution_60groups.csv
ls -lh nps_category_summary_60groups.csv

# 내용 간단 확인
head -5 nps_score_distribution_60groups.csv
```

---

### 3.3 카테고리별 응답율 계산 (정규화 적용)

#### 스크립트 실행

```bash
python3 calculate_category_by_nps_group_membership.py
```

#### 예상 출력

```
================================================================================
NPS 그룹별 카테고리 응답율 계산 (멤버십 포함 60개 그룹 가중치)
================================================================================

[1] 데이터 로드 중...
   - 주관식 데이터 행 수: 4,104개
   - NPS 데이터 행 수: 2,418개
   - 가중치 그룹 수: 60개

[2] bmclub 정보 병합 중...
   - 병합 후 데이터 행 수: 4,104개

[3] 결측값 필터링 중...
   - gender 결측값 제거: XX개 행 제거
   - 최종 데이터 행 수: 4,090개

[4] NPS 그룹별 응답자 수:
   - Detractor: 1,024명
   - Passive: 683명
   - Promoter: 702명

...

[6-1] 가중 응답자 수 정규화 중...
   - 스케일 팩터: 0.4418
   - 비가중 합계 (3개 그룹): 2,409명
   - 가중 합계 (정규화 전): 5,452.73명
   - Promoter: 1,455.63명 → 643.09명
   - Passive: 1,560.69명 → 689.51명
   - Detractor: 2,436.41명 → 1,076.40명
   - High-Risk: 580.00명 → 256.24명

   ✓ 정규화 완료: 가중 합계 = 2,409명 (비가중과 동일)
```

#### 검증 포인트

**✅ 체크리스트**:
- [ ] 정규화 스케일 팩터: 약 0.4418
- [ ] 정규화 후 가중 합계 = 2,409명 (비가중과 동일)
- [ ] Promoter 정규화 가중: 약 643명
- [ ] Passive 정규화 가중: 약 690명
- [ ] Detractor 정규화 가중: 약 1,076명
- [ ] High-Risk 정규화 가중: 약 256명
- [ ] 출력 파일 생성 확인:
  - `category_by_nps_group_weighted.csv` (약 570행)
  - `category_by_nps_group_detail.csv` (약 4,400행)

#### 생성 파일 확인

```bash
# 파일 행 수 확인
wc -l category_by_nps_group_weighted.csv
wc -l category_by_nps_group_detail.csv

# 요약 파일 상위 10개 확인
head -11 category_by_nps_group_weighted.csv
```

---

### 3.4 결과 검증

#### 3.4.1 NPS 점수 정합성 확인

**두 가지 방법으로 계산한 NPS가 일치하는지 확인**:

1. **방법 1**: `calculate_nps_weighted_60groups.py` 결과
   - 가중 NPS: -17.99 → 반올림 -18.0

2. **방법 2**: `nps_category_summary_60groups.csv` 확인
   ```bash
   cat nps_category_summary_60groups.csv
   ```
   - Promoter 가중비율: 26.70% → 27.3% (반올림)
   - Detractor 가중비율: 44.69% → 44.6% (반올림)
   - NPS: 27.3% - 44.6% = -17.3 또는 26.7% - 44.7% = -18.0

**중요**: 소수점 첫째자리 반올림 기준 사용!

#### 3.4.2 정규화 검증

```bash
# Python으로 빠른 검증
python3 -c "
import pandas as pd
df = pd.read_csv('category_by_nps_group_weighted.csv')

# NPS 그룹별 가중 응답자 합계
for group in ['Promoter', 'Passive', 'Detractor', 'High-Risk']:
    group_df = df[df['nps_group'] == group]
    weighted_sum = group_df['weighted_respondents'].sum()
    print(f'{group}: {weighted_sum:.2f}')
"
```

**기대 결과**:
- Promoter: 약 643
- Passive: 약 690
- Detractor: 약 1,076
- High-Risk: 약 256
- **합계(P+P+D)**: 2,409

#### 3.4.3 카테고리 응답율 샘플 확인

```bash
# Promoter 그룹의 '앱 사용 편리성' 응답율 확인
grep "Promoter,category,앱 사용 편리성" category_by_nps_group_weighted.csv
```

**기대 결과**:
- 가중 응답율: 약 44-45%
- 비가중 응답율: 약 43%

---

## 4. 파일 구조 및 설명

### 4.1 입력 파일

```
/Users/hmkwon/Project/011_NPS/
├── csv_output/
│   ├── food_nps_data.csv              # NPS 점수 데이터 (2,418행)
│   ├── food_nps_01_data_01.csv        # 주관식 응답 Dataset1
│   ├── food_nps_02_data_02.csv        # 주관식 응답 Dataset2
│   ├── food_nps_01_var_01.csv         # Dataset1 변수 설명
│   ├── food_nps_02_var_02.csv         # Dataset2 변수 설명
│   └── food_nps_var.csv               # NPS 변수 설명
└── weight_gender_age_rgn_membership.csv  # 60개 그룹 가중치
```

### 4.2 스크립트 파일

| 파일명 | 목적 | 입력 | 출력 |
|--------|------|------|------|
| `calculate_nps_weighted_60groups.py` | NPS 분포 계산 | `food_nps_data.csv`, 가중치 파일 | `nps_score_distribution_60groups.csv`, `nps_category_summary_60groups.csv` |
| `calculate_category_by_nps_group_membership.py` | 카테고리 응답율 계산 (정규화) | 주관식 데이터, NPS 데이터, 가중치 파일 | `category_by_nps_group_weighted.csv`, `category_by_nps_group_detail.csv` |

### 4.3 출력 파일 상세

#### 4.3.1 `nps_score_distribution_60groups.csv`

**구조**: 11행 (NPS 점수 0-10별 분포)

| 컬럼명 | 설명 | 예시 |
|--------|------|------|
| NPS점수 | 0-10 점수 | 0, 1, 2, ..., 10 |
| 응답자수 | 비가중 응답자 수 | 30, 90, 51, ... |
| 가중응답자수 | 가중 응답자 수 | 71.71, 212.04, ... |
| 비율(%) | 비가중 비율 | 1.25, 3.74, ... |
| 가중비율(%) | 가중 비율 | 1.32, 3.89, ... |
| 차이(%p) | 가중-비가중 차이 | 0.07, 0.15, ... |
| NPS분류 | Detractor/Passive/Promoter | Detractor, Passive, Promoter |

#### 4.3.2 `nps_category_summary_60groups.csv`

**구조**: 3행 (P/P/D 요약)

| 컬럼명 | 설명 |
|--------|------|
| NPS분류 | Promoter, Passive, Detractor |
| 응답자수 | 비가중 응답자 수 |
| 가중응답자수 | 가중 응답자 수 |
| 비율(%) | 비가중 비율 |
| 가중비율(%) | 가중 비율 |

**주요 값**:
- Promoter: 702명 (비가중), 1,455.63명 (가중), 26.70% (가중비율)
- Passive: 683명, 1,560.69명, 28.62%
- Detractor: 1,024명, 2,436.41명, 44.69%

#### 4.3.3 `category_by_nps_group_weighted.csv`

**구조**: 약 570행 (일반 카테고리 556행 + 기타/없음 14행)

| 컬럼명 | 설명 | 예시 |
|--------|------|------|
| nps_group | NPS 그룹 | Promoter, Passive, Detractor, High-Risk |
| category_type | 카테고리 레벨 | category, sub_category |
| category_value | 카테고리 값 | 앱 사용 편리성, 배달팁, 사회적 기여 |
| unweighted_respondents | 비가중 응답자 수 | 302, 225, 28 |
| weighted_respondents | **정규화된** 가중 응답자 수 | 285.95, 267.47, 35.98 |
| unweighted_rate(%) | 비가중 응답율 | 43.02, 21.97, 12.02 |
| weighted_rate(%) | 가중 응답율 | 44.47, 24.85, 14.04 |
| difference(%) | 가중-비가중 차이 | 1.45, 2.88, 2.03 |

**특징**:
- '기타', '없음' 카테고리 포함
- Promoter, Passive, Detractor, High-Risk 각각 약 140행씩
- **정규화 적용**: 가중 응답자 수 합계 = 비가중 합계(2,409)

#### 4.3.4 `category_by_nps_group_detail.csv`

**구조**: 약 4,400행 (60개 그룹 × 카테고리 × NPS그룹별 상세)

| 컬럼명 | 설명 |
|--------|------|
| nps_group | NPS 그룹 |
| category_type | 카테고리 레벨 |
| category_value | 카테고리 값 |
| gender | 성별 (MALE/FEMALE) |
| age_group | 연령대 (10대/청년/중년/장년/60대 이상) |
| rgn_nm | 지역 (수도권/광역시/그외 지역) |
| bmclub | 멤버십 (구독/미구독) |
| respondents | 해당 그룹 응답자 수 |
| weight | 그룹 가중치 (mem_rate) |
| weighted_respondents | **정규화된** 가중 응답자 수 |

**용도**:
- 세부 집단별 분석
- 특정 demographic 그룹 필터링 분석
- 검증 및 감사 추적

---

## 5. 검증 체크리스트

### 5.1 데이터 무결성 검증

```bash
# 1. 전체 응답자 수 확인
python3 -c "
import pandas as pd
df = pd.read_csv('csv_output/food_nps_data.csv', encoding='utf-8-sig')
df = df[df['gender'].notna()]
print(f'총 응답자(gender 제거 후): {len(df)}')
print(f'Detractor: {len(df[df[\"Q1_1\"] <= 6])}')
print(f'Passive: {len(df[(df[\"Q1_1\"] >= 7) & (df[\"Q1_1\"] <= 8)])}')
print(f'Promoter: {len(df[df[\"Q1_1\"] >= 9])}')
"
```

**기대 결과**:
```
총 응답자(gender 제거 후): 2409
Detractor: 1024
Passive: 683
Promoter: 702
```

### 5.2 정규화 검증

```bash
# 2. 정규화 응답자 수 합계 확인
python3 -c "
import pandas as pd
df = pd.read_csv('category_by_nps_group_weighted.csv')

# 각 NPS 그룹별 첫 행의 가중 응답자 수 추출
for group in ['Promoter', 'Passive', 'Detractor']:
    first_row = df[df['nps_group'] == group].iloc[0]
    print(f'{group}: {first_row[\"weighted_respondents\"]:.2f}')

# High-Risk는 별도 확인
hr_row = df[df['nps_group'] == 'High-Risk'].iloc[0]
print(f'High-Risk: {hr_row[\"weighted_respondents\"]:.2f}')
"
```

**기대 결과**:
- Promoter: 약 643
- Passive: 약 690
- Detractor: 약 1,076
- High-Risk: 약 256

### 5.3 비율 일관성 검증

```bash
# 3. NPS 비율 확인
cat nps_category_summary_60groups.csv
```

**확인 사항**:
- [ ] Promoter + Passive + Detractor 비율 = 100%
- [ ] 가중 NPS = Promoter% - Detractor% ≈ -18.0

### 5.4 카테고리 응답율 샘플 검증

```bash
# 4. 상위 카테고리 응답율 확인
python3 -c "
import pandas as pd
df = pd.read_csv('category_by_nps_group_weighted.csv')

# Promoter Category 레벨 상위 3개
promoter_cat = df[(df['nps_group'] == 'Promoter') &
                  (df['category_type'] == 'category') &
                  (~df['category_value'].isin(['기타', '없음']))]
top3 = promoter_cat.nlargest(3, 'weighted_rate(%)')
print('Promoter Top 3:')
print(top3[['category_value', 'weighted_rate(%)']].to_string(index=False))
"
```

**기대 결과**:
```
Promoter Top 3:
      category_value  weighted_rate(%)
      앱 사용 편리성             44.47
     가게/메뉴 다양성             20.39
   혜택(할인 및 쿠폰)             18.10
```

---

## 6. 문제 해결 가이드

### 6.1 일반적인 오류

#### 오류 1: `FileNotFoundError`

**증상**:
```
FileNotFoundError: [Errno 2] No such file or directory: 'csv_output/food_nps_data.csv'
```

**원인**:
- 파일 경로가 잘못됨
- 파일이 존재하지 않음

**해결**:
```bash
# 1. 현재 디렉토리 확인
pwd

# 2. /Users/hmkwon/Project/011_NPS 로 이동
cd /Users/hmkwon/Project/011_NPS

# 3. 파일 존재 확인
ls -lh csv_output/food_nps_data.csv

# 4. 다시 스크립트 실행
python3 calculate_nps_weighted_60groups.py
```

#### 오류 2: `UnicodeDecodeError`

**증상**:
```
UnicodeDecodeError: 'utf-8' codec can't decode byte...
```

**원인**:
- CSV 파일 인코딩이 UTF-8이 아님

**해결**:
1. Excel에서 파일 열기
2. "다른 이름으로 저장" → "CSV UTF-8(쉼표로 분리)(*.csv)" 선택
3. 저장 후 다시 실행

#### 오류 3: `KeyError: 'gender'`

**증상**:
```
KeyError: 'gender'
```

**원인**:
- 필수 컬럼이 파일에 없음

**해결**:
```bash
# 컬럼명 확인
head -1 csv_output/food_nps_data.csv
```

**확인 사항**:
- `gender`, `age_group`, `rgn_nm`, `bmclub`, `Q1_1` 컬럼이 모두 존재하는지 확인
- 컬럼명 대소문자 확인 (정확히 일치해야 함)

#### 오류 4: 응답자 수 불일치

**증상**:
- Promoter + Passive + Detractor ≠ 2,409

**원인**:
- gender 결측값 처리가 되지 않음
- bmclub 결측값이 포함됨

**해결**:
```python
# 데이터 확인
import pandas as pd
df = pd.read_csv('csv_output/food_nps_data.csv', encoding='utf-8-sig')
print(f"gender 결측: {df['gender'].isna().sum()}")
print(f"bmclub 결측: {df['bmclub'].isna().sum()}")
print(f"Q1_1 결측: {df['Q1_1'].isna().sum()}")
```

**대응**:
- 스크립트는 자동으로 gender 결측값을 제거함
- bmclub, Q1_1 결측값이 있다면 원본 데이터 확인 필요

### 6.2 정규화 관련 문제

#### 문제: 정규화 후에도 합계가 2,409가 아님

**확인**:
```python
import pandas as pd
df = pd.read_csv('category_by_nps_group_weighted.csv')

# 스케일 팩터 역산
promoter_weighted = df[df['nps_group'] == 'Promoter']['weighted_respondents'].iloc[0]
print(f"Promoter normalized: {promoter_weighted:.2f}")

# 원본 가중치로 역산
original = promoter_weighted / 0.4418
print(f"Promoter original (역산): {original:.2f}")
```

**기대값**:
- Promoter normalized: 643.09
- Promoter original: 1,455.63

**해결**:
- 스크립트 재실행
- 가중치 파일이 올바른지 확인

---

## 7. 월별 작업 체크리스트

### 7.1 작업 전 준비 (10분)

**날짜**: ____년 __월 __일

- [ ] 1. 새로운 월 데이터 수령 확인
  - [ ] `food_nps_data.csv` (NPS 점수)
  - [ ] `food_nps_01_data_01.csv` (주관식 응답)
  - [ ] `food_nps_02_data_02.csv` (주관식 응답)

- [ ] 2. 기존 파일 백업
  ```bash
  cd /Users/hmkwon/Project/011_NPS
  mkdir -p backups/YYYYMM  # 예: backups/202510
  cp *.csv backups/YYYYMM/
  ```

- [ ] 3. 새 데이터 파일 배치
  ```bash
  # csv_output 디렉토리에 새 파일 복사
  cp /path/to/new/files/*.csv csv_output/
  ```

- [ ] 4. 가중치 파일 확인
  ```bash
  ls -lh weight_gender_age_rgn_membership.csv
  ```

### 7.2 스크립트 실행 (20분)

- [ ] 5. NPS 분포 계산
  ```bash
  python3 calculate_nps_weighted_60groups.py > logs/nps_YYYYMM.log
  ```
  - [ ] 에러 없이 완료
  - [ ] 출력 파일 생성 확인
  - [ ] 총 응답자 = 약 2,400명대

- [ ] 6. 카테고리 응답율 계산
  ```bash
  python3 calculate_category_by_nps_group_membership.py > logs/category_YYYYMM.log
  ```
  - [ ] 에러 없이 완료
  - [ ] 정규화 메시지 확인: "✓ 정규화 완료: 가중 합계 = 2,409명"
  - [ ] 출력 파일 생성 확인

### 7.3 결과 검증 (15분)

- [ ] 7. NPS 점수 확인
  ```bash
  cat nps_category_summary_60groups.csv
  ```
  - [ ] Promoter 비율: 약 26-28%
  - [ ] Passive 비율: 약 28-30%
  - [ ] Detractor 비율: 약 42-46%
  - [ ] NPS 점수: 약 -15 ~ -20

- [ ] 8. 정규화 검증
  - [ ] Promoter 정규화 가중: 약 600-700명
  - [ ] Passive 정규화 가중: 약 650-750명
  - [ ] Detractor 정규화 가중: 약 1,000-1,100명
  - [ ] 합계 = 2,409명

- [ ] 9. 카테고리 응답율 샘플 확인
  ```bash
  head -20 category_by_nps_group_weighted.csv
  ```
  - [ ] Promoter '앱 사용 편리성': 약 40-50%
  - [ ] Detractor '배달팁': 약 20-30%

### 7.4 보고서 업데이트 (15분, 필요시)

- [ ] 10. 보고서 데이터 업데이트
  - [ ] Section 1.1 응답자 현황 표 업데이트
  - [ ] NPS 점수 업데이트
  - [ ] 주요 카테고리 응답율 업데이트 (변동이 큰 경우)

- [ ] 11. 인사이트 업데이트
  - [ ] 전월 대비 주요 변화 기록
  - [ ] 새로운 이슈 발견 시 추가

### 7.5 최종 확인 및 보고 (10분)

- [ ] 12. 파일 아카이빙
  ```bash
  mkdir -p archives/YYYYMM
  cp *.csv archives/YYYYMM/
  cp REPORT_food_subjective_category_analysis.md archives/YYYYMM/
  ```

- [ ] 13. 결과 요약 작성
  - 이번 달 NPS: ______
  - 전월 대비 변화: ______
  - 주요 이슈: ______

- [ ] 14. 보고서 제출
  - [ ] PDF 또는 Markdown 파일 공유
  - [ ] 주요 인사이트 요약 공유

---

## 8. 월별 변화 추적

### 8.1 월별 NPS 추이 기록

| 월 | 비가중 NPS | 가중 NPS | Promoter% | Detractor% | High-Risk% | 비고 |
|----|-----------|---------|-----------|------------|-----------|------|
| 2024-10 | -13.37 | -18.0 | 26.7 | 44.7 | 10.6 | 기준월 |
| 2024-11 |  |  |  |  |  |  |
| 2024-12 |  |  |  |  |  |  |

### 8.2 주요 카테고리 응답율 추이

**Promoter Top 3**:

| 월 | 앱 편리성 | 가게 다양성 | 혜택 |
|----|----------|-----------|------|
| 2024-10 | 44.5% | 20.4% | 18.1% |
| 2024-11 |  |  |  |
| 2024-12 |  |  |  |

**Detractor Top 3**:

| 월 | 배달팁 | 혜택 부족 | 가격 높음 |
|----|-------|----------|----------|
| 2024-10 | 24.9% | 15.1% | 11.4% |
| 2024-11 |  |  |  |
| 2024-12 |  |  |  |

**High-Risk Top 3**:

| 월 | 배달팁 | 사회적 기여 | 혜택 부족 |
|----|-------|------------|----------|
| 2024-10 | 27.3% | 14.0% | 18.6% |
| 2024-11 |  |  |  |
| 2024-12 |  |  |  |

---

## 9. 참고 자료

### 9.1 핵심 개념 정리

**NPS 분류 기준**:
- **Promoter (추천자)**: 9-10점
- **Passive (중립자)**: 7-8점
- **Detractor (비추천자)**: 0-6점
- **High-Risk (고위험군)**: 0-3점 (Detractor의 부분집합)

**NPS 점수 계산**:
```
NPS = Promoter% - Detractor%
```

**정규화 공식**:
```
스케일 팩터 = 비가중 합계 / 가중 합계
정규화 가중값 = 원본 가중값 × 스케일 팩터
```

**가중치 구조**:
- 60개 그룹 = gender(2) × age_group(5) × rgn_nm(3) × bmclub(2)
- 각 그룹의 `mem_rate` = 모집단 비율 / 표본 비율

### 9.2 주요 파일 경로

```
/Users/hmkwon/Project/011_NPS/
├── calculate_nps_weighted_60groups.py          # NPS 분포 계산
├── calculate_category_by_nps_group_membership.py  # 카테고리 응답율 계산
├── weight_gender_age_rgn_membership.csv        # 60개 그룹 가중치
├── csv_output/                                 # 입력 데이터
│   ├── food_nps_data.csv
│   ├── food_nps_01_data_01.csv
│   └── food_nps_02_data_02.csv
├── nps_score_distribution_60groups.csv         # 출력: NPS 분포
├── nps_category_summary_60groups.csv           # 출력: NPS 요약
├── category_by_nps_group_weighted.csv          # 출력: 카테고리 응답율
├── category_by_nps_group_detail.csv            # 출력: 상세 데이터
└── REPORT_food_subjective_category_analysis.md # 분석 보고서
```

### 9.3 연락처

**문제 발생 시**:
1. 이 매뉴얼의 "문제 해결 가이드" 참조
2. 로그 파일 확인 (`logs/` 디렉토리)
3. 백업 파일로 복원 (`backups/` 디렉토리)
4. 담당자 문의: [담당자 이메일]

---

**매뉴얼 버전**: 1.0
**최종 업데이트**: 2025-10-28
**다음 업데이트 예정**: 필요시
