#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NPS 그룹별 카테고리 응답율 계산 (가중치 적용)

NPS 점수(Q1_1) 기준으로 추천자/비추천자/중립자 그룹을 나누어
각 그룹 내에서 카테고리별 응답율을 계산합니다.
"""

import pandas as pd
import numpy as np

# 파일 경로
DATA_FILE = '/Users/hmkwon/Project/011_NPS/csv_output/food_nps_data_open.csv'
WEIGHT_FILE = '/Users/hmkwon/Project/011_NPS/nps_by_group.csv'
OUTPUT_FILE = '/Users/hmkwon/Project/011_NPS/category_by_nps_group_weighted.csv'
OUTPUT_DETAIL_FILE = '/Users/hmkwon/Project/011_NPS/category_by_nps_group_detail.csv'

# NPS 분류 기준
DETRACTOR_MAX = 6    # 0-6: 비추천자
PASSIVE_MAX = 8      # 7-8: 중립자
PROMOTER_MIN = 9     # 9-10: 추천자

# 데이터 로드
print("=" * 80)
print("NPS 그룹별 카테고리 응답율 계산 (가중치 적용)")
print("=" * 80)

print("\n[1] 데이터 로드 중...")
df = pd.read_csv(DATA_FILE, encoding='utf-8-sig')
df_weight = pd.read_csv(WEIGHT_FILE, encoding='utf-8-sig')

print(f"   - 전체 데이터 행 수: {len(df):,}개")
print(f"   - 가중치 그룹 수: {len(df_weight):,}개")

# 결측값 필터링 (CRITICAL: gender 결측값 먼저 제거)
print("\n[2] 결측값 필터링 중...")
df_before = len(df)
df = df[df['gender'].notna()].copy()
df_removed = df_before - len(df)
print(f"   - gender 결측값 제거: {df_removed}개 행 제거")

# category, sub_category, Q1_1 결측값 제거
df = df[df['category'].notna()].copy()
df = df[df['sub_category'].notna()].copy()
df = df[df['Q1_1'].notna()].copy()
print(f"   - 최종 데이터 행 수: {len(df):,}개")

# Q1_1을 숫자로 변환
df['Q1_1'] = pd.to_numeric(df['Q1_1'], errors='coerce')
df = df[df['Q1_1'].notna()].copy()

# NPS 그룹 분류
def classify_nps(score):
    if score <= DETRACTOR_MAX:
        return 'Detractor'
    elif score <= PASSIVE_MAX:
        return 'Passive'
    else:
        return 'Promoter'

df['nps_group'] = df['Q1_1'].apply(classify_nps)

print(f"\n[3] NPS 그룹별 응답자 수:")
nps_group_counts = df.groupby('nps_group')['ResponseId'].nunique()
for group, count in nps_group_counts.items():
    print(f"   - {group}: {count:,}명")

# 각 NPS 그룹별 카테고리 응답율 계산
print("\n[4] NPS 그룹별 카테고리 응답율 계산 중...")

def calculate_nps_group_category_rate(df, df_weight, nps_group_name, grouping_col):
    """
    특정 NPS 그룹 내에서 카테고리별 가중치 적용 응답율 계산

    Args:
        df: 전체 데이터
        df_weight: 가중치 데이터
        nps_group_name: 'Promoter', 'Passive', 'Detractor'
        grouping_col: 'category' 또는 'sub_category'

    Returns:
        결과 DataFrame
    """
    # 해당 NPS 그룹 데이터만 필터링
    df_group = df[df['nps_group'] == nps_group_name].copy()

    if len(df_group) == 0:
        return pd.DataFrame()

    results = []

    # 인구통계 그룹별로 계산
    for _, weight_row in df_weight.iterrows():
        gender = weight_row['gender']
        age_group = weight_row['age_group']
        rgn_nm = weight_row['rgn_nm']
        weight = weight_row['가중치']

        # 해당 그룹의 데이터 필터링
        group_data = df_group[
            (df_group['gender'] == gender) &
            (df_group['age_group'] == age_group) &
            (df_group['rgn_nm'] == rgn_nm)
        ].copy()

        if len(group_data) == 0:
            continue

        # 해당 그룹의 전체 응답자 수 (NPS 그룹 내)
        group_total = group_data['ResponseId'].nunique()

        # 각 카테고리별 응답자 수 계산
        for cat_value in df_group[grouping_col].unique():
            cat_data = group_data[group_data[grouping_col] == cat_value]

            if len(cat_data) > 0:
                cat_respondents = cat_data['ResponseId'].nunique()

                results.append({
                    'nps_group': nps_group_name,
                    'category_type': grouping_col,
                    'category_value': cat_value,
                    'gender': gender,
                    'age_group': age_group,
                    'rgn_nm': rgn_nm,
                    'group_total_respondents': group_total,
                    'category_respondents': cat_respondents,
                    'weight': weight,
                    'weighted_respondents': cat_respondents * weight
                })

    return pd.DataFrame(results)

# 각 NPS 그룹별로 계산
all_results = []

for nps_group in ['Promoter', 'Passive', 'Detractor']:
    print(f"   - {nps_group} 그룹 계산 중...")

    # category 레벨
    df_cat = calculate_nps_group_category_rate(df, df_weight, nps_group, 'category')
    if len(df_cat) > 0:
        all_results.append(df_cat)

    # sub_category 레벨
    df_subcat = calculate_nps_group_category_rate(df, df_weight, nps_group, 'sub_category')
    if len(df_subcat) > 0:
        all_results.append(df_subcat)

df_all = pd.concat(all_results, ignore_index=True)
print(f"   - 총 계산 결과 행 수: {len(df_all):,}개")

# NPS 그룹별 가중 응답자 수 계산
print("\n[5] NPS 그룹별 가중 응답자 수 계산 중...")

nps_group_weighted_totals = {}

for nps_group in ['Promoter', 'Passive', 'Detractor']:
    df_group = df[df['nps_group'] == nps_group].copy()

    total_weighted_results = []

    for _, weight_row in df_weight.iterrows():
        gender = weight_row['gender']
        age_group = weight_row['age_group']
        rgn_nm = weight_row['rgn_nm']
        weight = weight_row['가중치']

        group_data = df_group[
            (df_group['gender'] == gender) &
            (df_group['age_group'] == age_group) &
            (df_group['rgn_nm'] == rgn_nm)
        ].copy()

        if len(group_data) > 0:
            group_respondents = group_data['ResponseId'].nunique()
            total_weighted_results.append({
                'group_respondents': group_respondents,
                'weight': weight,
                'weighted_respondents': group_respondents * weight
            })

    if len(total_weighted_results) > 0:
        df_total = pd.DataFrame(total_weighted_results)
        weighted_total = df_total['weighted_respondents'].sum()
        unweighted_total = df_group['ResponseId'].nunique()

        nps_group_weighted_totals[nps_group] = {
            'unweighted': unweighted_total,
            'weighted': weighted_total
        }

        print(f"   - {nps_group}: 비가중 {unweighted_total:,}명, 가중 {weighted_total:,.2f}명")

# 최종 집계
print("\n[6] 최종 집계 중...")

summary_results = []

for nps_group in ['Promoter', 'Passive', 'Detractor']:
    if nps_group not in nps_group_weighted_totals:
        continue

    total_weighted = nps_group_weighted_totals[nps_group]['weighted']
    total_unweighted = nps_group_weighted_totals[nps_group]['unweighted']

    df_group_all = df_all[df_all['nps_group'] == nps_group]
    df_group_data = df[df['nps_group'] == nps_group]

    for cat_type in ['category', 'sub_category']:
        df_type = df_group_all[df_group_all['category_type'] == cat_type]

        for cat_value in df_type['category_value'].unique():
            df_cat = df_type[df_type['category_value'] == cat_value]

            # 가중치 적용 응답자 수
            weighted_respondents = df_cat['weighted_respondents'].sum()

            # 비가중 응답자 수
            unweighted_data = df_group_data[df_group_data[cat_type] == cat_value]
            unweighted_respondents = unweighted_data['ResponseId'].nunique()

            # 해당 NPS 그룹 내에서의 비율 계산
            weighted_rate = (weighted_respondents / total_weighted) * 100
            unweighted_rate = (unweighted_respondents / total_unweighted) * 100

            summary_results.append({
                'nps_group': nps_group,
                'category_type': cat_type,
                'category_value': cat_value,
                'unweighted_respondents': unweighted_respondents,
                'weighted_respondents': round(weighted_respondents, 2),
                'unweighted_rate(%)': round(unweighted_rate, 2),
                'weighted_rate(%)': round(weighted_rate, 2),
                'difference(%)': round(weighted_rate - unweighted_rate, 2)
            })

df_summary = pd.DataFrame(summary_results)

# 정렬
df_summary = df_summary.sort_values(
    ['nps_group', 'weighted_rate(%)'],
    ascending=[True, False]
).reset_index(drop=True)

# 결과 저장
print("\n[7] 결과 저장 중...")

df_summary.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
print(f"   - 요약 결과 저장: {OUTPUT_FILE}")

df_all_sorted = df_all.sort_values(
    ['nps_group', 'category_type', 'category_value', 'gender', 'age_group', 'rgn_nm']
)
df_all_sorted.to_csv(OUTPUT_DETAIL_FILE, index=False, encoding='utf-8-sig')
print(f"   - 상세 결과 저장: {OUTPUT_DETAIL_FILE}")

# 결과 출력
print("\n" + "=" * 80)
print("NPS 그룹별 카테고리 응답율 (상위 20개)")
print("=" * 80)

for nps_group in ['Promoter', 'Passive', 'Detractor']:
    df_group = df_summary[
        (df_summary['nps_group'] == nps_group) &
        (df_summary['category_type'] == 'category')
    ].copy()

    if len(df_group) > 0:
        print(f"\n[{nps_group} - Category 레벨]")
        print(df_group[['category_value', 'unweighted_respondents', 'weighted_respondents',
                        'unweighted_rate(%)', 'weighted_rate(%)', 'difference(%)']].head(20).to_string(index=False))

print("\n" + "=" * 80)

for nps_group in ['Promoter', 'Passive', 'Detractor']:
    df_group = df_summary[
        (df_summary['nps_group'] == nps_group) &
        (df_summary['category_type'] == 'sub_category')
    ].copy()

    if len(df_group) > 0:
        print(f"\n[{nps_group} - Sub-Category 레벨]")
        print(df_group[['category_value', 'unweighted_respondents', 'weighted_respondents',
                        'unweighted_rate(%)', 'weighted_rate(%)', 'difference(%)']].head(20).to_string(index=False))

print("\n" + "=" * 80)
print("계산 완료!")
print("=" * 80)
print(f"\n출력 파일:")
print(f"  1. {OUTPUT_FILE}")
print(f"  2. {OUTPUT_DETAIL_FILE}")
