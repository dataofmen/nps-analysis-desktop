#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Commerce (B마트/배민스토어) 종합 NPS 분석
★ 수정 (2025-10-29): 모든 분석에 gender × age_group (8개 그룹) 가중치 통일 적용
- Total 분석: gender × age_group 가중치
- 세부집단 분석: gender × age_group 가중치
  1. bmclub (배민클럽 구독 여부)
  2. division (서비스 종류)
  3. rgn_nm (지역)
"""

import pandas as pd
import numpy as np

# ===== 파일 경로 설정 =====
# 데이터 파일
NPS_DATA = '/Users/hmkwon/Project/011_NPS/csv_output/commerce_nps_data.csv'
DATA_01 = '/Users/hmkwon/Project/011_NPS/csv_output/commerce_nps_data_01.csv'

# 변수 설명 파일
NPS_VAR = '/Users/hmkwon/Project/011_NPS/csv_output/commerce_nps_var.csv'
VAR_01 = '/Users/hmkwon/Project/011_NPS/csv_output/commerce_nps_var_01.csv'

# 가중치 파일 (8개 그룹 통일)
WEIGHT_GA = '/Users/hmkwon/Project/011_NPS/weight_commerce_ga.csv'

# 출력 파일
OUTPUT_TOTAL = '/Users/hmkwon/Project/011_NPS/result_commerce_total.csv'
OUTPUT_BMCLUB = '/Users/hmkwon/Project/011_NPS/result_commerce_by_bmclub.csv'
OUTPUT_DIVISION = '/Users/hmkwon/Project/011_NPS/result_commerce_by_division.csv'
OUTPUT_REGION = '/Users/hmkwon/Project/011_NPS/result_commerce_by_region.csv'

# ===== 상수 설정 =====
POSITIVE_THRESHOLD = 5  # 긍정응답 기준 (5, 6, 7점)

def classify_nps(score):
    """NPS 분류"""
    if pd.isna(score):
        return None
    if score <= 6:
        return 'Detractor'
    elif score <= 8:
        return 'Passive'
    else:
        return 'Promoter'

def calculate_nps(df, nps_col='Q1'):
    """NPS 점수 계산"""
    df = df.copy()
    df['nps_category'] = df[nps_col].apply(classify_nps)

    total = len(df[df['nps_category'].notna()])
    if total == 0:
        return None, None, None, None

    promoters = len(df[df['nps_category'] == 'Promoter'])
    passives = len(df[df['nps_category'] == 'Passive'])
    detractors = len(df[df['nps_category'] == 'Detractor'])

    promoter_pct = (promoters / total) * 100
    passive_pct = (passives / total) * 100
    detractor_pct = (detractors / total) * 100
    nps = promoter_pct - detractor_pct

    return nps, promoter_pct, detractor_pct, passive_pct

def calculate_nps_weighted(df, weight_col, nps_col='Q1'):
    """가중치 적용 NPS 점수 계산"""
    df = df.copy()
    df['nps_category'] = df[nps_col].apply(classify_nps)

    # 가중치 적용
    df_valid = df[df['nps_category'].notna()].copy()
    total_weight = df_valid[weight_col].sum()

    if total_weight == 0:
        return None, None, None, None, 0

    promoter_weight = df_valid[df_valid['nps_category'] == 'Promoter'][weight_col].sum()
    passive_weight = df_valid[df_valid['nps_category'] == 'Passive'][weight_col].sum()
    detractor_weight = df_valid[df_valid['nps_category'] == 'Detractor'][weight_col].sum()

    promoter_pct = (promoter_weight / total_weight) * 100
    passive_pct = (passive_weight / total_weight) * 100
    detractor_pct = (detractor_weight / total_weight) * 100
    nps = promoter_pct - detractor_pct

    return nps, promoter_pct, passive_pct, detractor_pct, len(df_valid)

def calculate_positive_rate(df, var_col):
    """긍정응답률 계산"""
    df_valid = df[df[var_col].notna()].copy()
    total = len(df_valid)

    if total == 0:
        return None, 0

    positive = len(df_valid[df_valid[var_col] >= POSITIVE_THRESHOLD])
    rate = (positive / total) * 100

    return rate, total

def calculate_positive_rate_weighted(df, var_col, weight_col):
    """가중치 적용 긍정응답률 계산"""
    df_valid = df[df[var_col].notna()].copy()
    total_weight = df_valid[weight_col].sum()

    if total_weight == 0:
        return None, 0

    positive_weight = df_valid[df_valid[var_col] >= POSITIVE_THRESHOLD][weight_col].sum()
    rate = (positive_weight / total_weight) * 100

    return rate, len(df_valid)

def add_calibrated_weights(df, weight_df, group_cols):
    """
    Raking/Calibration 방식의 가중치 계산
    표본 비율을 고려한 올바른 가중치 계산
    가중치 = 모집단비율 / 표본비율
    """
    # 집단별 응답수 계산
    group_counts = df.groupby(group_cols).size().reset_index(name='sample_count')
    total_count = len(df)
    group_counts['sample_ratio'] = group_counts['sample_count'] / total_count

    # 가중치 정보 병합
    group_weights = group_counts.merge(weight_df, on=group_cols, how='left')

    # 가중치 계산: mem_rate / sample_ratio
    group_weights['weight'] = group_weights['mem_rate'] / group_weights['sample_ratio']

    # 원본 데이터에 가중치 병합
    df_weighted = df.merge(group_weights[group_cols + ['weight']], on=group_cols, how='left')

    return df_weighted

def create_variable_description_map():
    """변수 설명 매핑 생성"""
    # NPS 변수
    df_nps_var = pd.read_csv(NPS_VAR, encoding='utf-8-sig')
    nps_desc = dict(zip(df_nps_var['Variable'], df_nps_var['Description']))

    # Dataset 1 변수
    df_var1 = pd.read_csv(VAR_01, encoding='utf-8-sig')
    var1_desc = dict(zip(df_var1['Variable'], df_var1['Description']))

    return nps_desc, var1_desc

def load_and_prepare_data():
    """데이터 로드 및 전처리"""
    print("="*60)
    print("데이터 로드 및 전처리 시작")
    print("="*60)

    # 1. NPS 데이터 로드
    print("\n1. NPS 데이터 로드")
    df_nps = pd.read_csv(NPS_DATA, encoding='utf-8-sig')
    print(f"   로드 완료: {len(df_nps):,}행")

    # gender 결측값 제거
    print(f"\n[NPS 데이터] gender 변수 결측값 확인...")
    print(f"  전체 행수: {len(df_nps):,}행")
    gender_missing = df_nps['gender'].isna().sum()
    print(f"  gender 결측값: {gender_missing}행 ({gender_missing/len(df_nps)*100:.2f}%)")
    if gender_missing > 0:
        print(f"  → gender 결측값 제거 중...")
        df_before = len(df_nps)
        df_nps = df_nps[df_nps['gender'].notna()].copy()
        df_removed = df_before - len(df_nps)
        print(f"  → {df_removed}행 제거 완료")
        print(f"  → 최종 행수: {len(df_nps):,}행")

    # 2. Dataset 1 로드
    print("\n2. Dataset 1 로드")
    df1 = pd.read_csv(DATA_01, encoding='utf-8-sig')
    print(f"   로드 완료: {len(df1):,}행")

    # gender 결측값 제거
    print(f"\n[Dataset 1] gender 변수 결측값 확인...")
    print(f"  전체 행수: {len(df1):,}행")
    gender_missing = df1['gender'].isna().sum()
    print(f"  gender 결측값: {gender_missing}행 ({gender_missing/len(df1)*100:.2f}%)")
    if gender_missing > 0:
        print(f"  → gender 결측값 제거 중...")
        df_before = len(df1)
        df1 = df1[df1['gender'].notna()].copy()
        df_removed = df_before - len(df1)
        print(f"  → {df_removed}행 제거 완료")
        print(f"  → 최종 행수: {len(df1):,}행")

    # age_group 공백 정규화 (CRITICAL: "20대 이하" -> "20대이하", "50대 이상" -> "50대이상")
    print("\nage_group 공백 정규화 중...")
    df_nps['age_group'] = df_nps['age_group'].str.replace(' ', '', regex=False)
    df1['age_group'] = df1['age_group'].str.replace(' ', '', regex=False)
    print("  ✓ age_group 공백 제거 완료")

    # 변수 타입 변환
    print("\n변수 타입 변환 중...")
    df_nps['Q1'] = pd.to_numeric(df_nps['Q1'], errors='coerce')

    # Dataset 1 변수들
    vars_1 = ['Q2', 'Q3', 'Q4', 'Q6', 'Q7', 'Q8', 'Q10', 'Q11', 'Q12']
    for var in vars_1:
        if var in df1.columns:
            df1[var] = pd.to_numeric(df1[var], errors='coerce')

    # 가중치 파일 로드 (8개 그룹 통일)
    print("\n가중치 파일 로드 중...")
    weight_ga = pd.read_csv(WEIGHT_GA)

    # 가중치 파일도 age_group 정규화
    weight_ga['age_group'] = weight_ga['age_group'].str.replace(' ', '', regex=False)

    print(f"★ 모든 분석에 동일한 가중치 적용: gender × age_group ({len(weight_ga)}개 그룹)")

    return df_nps, df1, weight_ga

def analyze_total(df_nps, df1, weight_ga, nps_desc, var1_desc):
    """Total 분석 (gender × age_group 가중치)"""
    print("\n" + "="*60)
    print("1. Total 분석 (gender × age_group 가중치)")
    print("="*60)

    results = []

    # NPS 데이터 가중치 병합
    df_nps_w = df_nps[['gender', 'age_group', 'Q1']].copy()
    df_nps_w = add_calibrated_weights(df_nps_w, weight_ga, ['gender', 'age_group'])

    # NPS 계산
    nps_w, pro_w, pas_w, det_w, cnt = calculate_nps_weighted(df_nps_w, 'weight', 'Q1')
    nps_uw, pro_uw, det_uw, pas_uw = calculate_nps(df_nps_w, 'Q1')

    results.append({
        '구분': 'Total',
        '세부집단': 'All',
        '변수': 'NPS',
        '변수명': 'Q1',
        '변수_설명': nps_desc.get('Q1', ''),
        '가중_값': round(nps_w, 2) if nps_w is not None else None,
        '비가중_값': round(nps_uw, 2) if nps_uw is not None else None,
        '응답수': cnt,
        '추천자_가중': round(pro_w, 2) if pro_w is not None else None,
        '중립자_가중': round(pas_w, 2) if pas_w is not None else None,
        '비추천자_가중': round(det_w, 2) if det_w is not None else None,
        '추천자_비가중': round(pro_uw, 2) if pro_uw is not None else None,
        '중립자_비가중': round(pas_uw, 2) if pas_uw is not None else None,
        '비추천자_비가중': round(det_uw, 2) if det_uw is not None else None
    })

    print(f"\nNPS:")
    print(f"  가중: {nps_w:.2f}%")
    print(f"    - 추천자 (9-10점): {pro_w:.2f}%")
    print(f"    - 중립자 (7-8점): {pas_w:.2f}%")
    print(f"    - 비추천자 (0-6점): {det_w:.2f}%")
    print(f"  비가중: {nps_uw:.2f}% (추천자: {pro_uw:.2f}%, 비추천자: {det_uw:.2f}%)")
    print(f"  응답수: {cnt:,}")

    # Dataset 1 7점 척도 변수들
    print("\nDataset 1 긍정응답률:")
    for var in ['Q2', 'Q3', 'Q4', 'Q6', 'Q7', 'Q8', 'Q10', 'Q11', 'Q12']:
        df_temp = df1[['gender', 'age_group', var]].copy()
        df_temp = add_calibrated_weights(df_temp, weight_ga, ['gender', 'age_group'])

        rate_w, cnt = calculate_positive_rate_weighted(df_temp, var, 'weight')
        rate_uw, _ = calculate_positive_rate(df_temp, var)

        results.append({
            '구분': 'Total',
            '세부집단': 'All',
            '변수': f'{var}_긍정응답률',
            '변수명': var,
            '변수_설명': var1_desc.get(var, ''),
            '가중_값': round(rate_w, 2) if rate_w is not None else None,
            '비가중_값': round(rate_uw, 2) if rate_uw is not None else None,
            '응답수': cnt,
            '추천자_가중': None,
            '중립자_가중': None,
            '비추천자_가중': None,
            '추천자_비가중': None,
            '중립자_비가중': None,
            '비추천자_비가중': None
        })

        print(f"  {var}: 가중 {rate_w:.2f}%, 비가중 {rate_uw:.2f}% (n={cnt:,})")

    return pd.DataFrame(results)

def analyze_by_group(df_nps, df1, weight_ga, group_col, group_name, nps_desc, var1_desc):
    """세부 집단별 분석 (gender × age_group 가중치)"""
    print("\n" + "="*60)
    print(f"2. {group_name} 분석 (gender × age_group 가중치)")
    print("="*60)

    results = []

    # 집단 목록 확인
    groups = sorted(df_nps[group_col].dropna().unique())
    print(f"\n집단: {groups}")

    for group in groups:
        print(f"\n[{group}]")

        # NPS 계산
        df_nps_group = df_nps[df_nps[group_col] == group][['gender', 'age_group', 'Q1']].copy()
        df_nps_group = add_calibrated_weights(df_nps_group, weight_ga, ['gender', 'age_group'])

        nps_w, pro_w, pas_w, det_w, cnt = calculate_nps_weighted(df_nps_group, 'weight', 'Q1')
        nps_uw, pro_uw, det_uw, pas_uw = calculate_nps(df_nps_group, 'Q1')

        results.append({
            '구분': group_name,
            '세부집단': group,
            '변수': 'NPS',
            '변수명': 'Q1',
            '변수_설명': nps_desc.get('Q1', ''),
            '가중_값': round(nps_w, 2) if nps_w is not None else None,
            '비가중_값': round(nps_uw, 2) if nps_uw is not None else None,
            '응답수': cnt,
            '추천자_가중': round(pro_w, 2) if pro_w is not None else None,
            '중립자_가중': round(pas_w, 2) if pas_w is not None else None,
            '비추천자_가중': round(det_w, 2) if det_w is not None else None,
            '추천자_비가중': round(pro_uw, 2) if pro_uw is not None else None,
            '중립자_비가중': round(pas_uw, 2) if pas_uw is not None else None,
            '비추천자_비가중': round(det_uw, 2) if det_uw is not None else None
        })

        print(f"  NPS: 가중 {nps_w:.2f}%, 비가중 {nps_uw:.2f}% (n={cnt:,})")

        # Dataset 1 7점 척도
        for var in ['Q2', 'Q3', 'Q4', 'Q6', 'Q7', 'Q8', 'Q10', 'Q11', 'Q12']:
            df_temp = df1[df1[group_col] == group][['gender', 'age_group', var]].copy()
            df_temp = add_calibrated_weights(df_temp, weight_ga, ['gender', 'age_group'])

            rate_w, cnt = calculate_positive_rate_weighted(df_temp, var, 'weight')
            rate_uw, _ = calculate_positive_rate(df_temp, var)

            results.append({
                '구분': group_name,
                '세부집단': group,
                '변수': f'{var}_긍정응답률',
                '변수명': var,
                '변수_설명': var1_desc.get(var, ''),
                '가중_값': round(rate_w, 2) if rate_w is not None else None,
                '비가중_값': round(rate_uw, 2) if rate_uw is not None else None,
                '응답수': cnt,
                '추천자_가중': None,
                '중립자_가중': None,
                '비추천자_가중': None,
                '추천자_비가중': None,
                '중립자_비가중': None,
                '비추천자_비가중': None
            })

    return pd.DataFrame(results)

def main():
    # 데이터 로드
    df_nps, df1, weight_ga = load_and_prepare_data()
    nps_desc, var1_desc = create_variable_description_map()

    # 1. Total 분석 (8개 그룹 가중치)
    df_total = analyze_total(df_nps, df1, weight_ga, nps_desc, var1_desc)
    df_total.to_csv(OUTPUT_TOTAL, index=False, encoding='utf-8-sig')
    print(f"\n저장 완료: {OUTPUT_TOTAL}")

    # 2. 배민클럽별 분석
    df_bmclub = analyze_by_group(df_nps, df1, weight_ga, 'bmclub', '배민클럽', nps_desc, var1_desc)
    df_bmclub.to_csv(OUTPUT_BMCLUB, index=False, encoding='utf-8-sig')
    print(f"\n저장 완료: {OUTPUT_BMCLUB}")

    # 3. 서비스종류별 분석
    df_division = analyze_by_group(df_nps, df1, weight_ga, 'division', '서비스종류', nps_desc, var1_desc)
    df_division.to_csv(OUTPUT_DIVISION, index=False, encoding='utf-8-sig')
    print(f"\n저장 완료: {OUTPUT_DIVISION}")

    # 4. 지역별 분석
    df_region = analyze_by_group(df_nps, df1, weight_ga, 'rgn_nm', '지역', nps_desc, var1_desc)
    df_region.to_csv(OUTPUT_REGION, index=False, encoding='utf-8-sig')
    print(f"\n저장 완료: {OUTPUT_REGION}")

    print("\n" + "="*60)
    print("전체 분석 완료!")
    print("="*60)

if __name__ == "__main__":
    main()
