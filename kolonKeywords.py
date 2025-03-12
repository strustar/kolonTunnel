import pandas as pd
import numpy as np
import Levenshtein
from functools import lru_cache
import re
import streamlit as st


@lru_cache(maxsize=None)  # 캐시 크기 제한 없음 (자동 관리)
def calculate_similarity(str1, str2):
    """문자열 유사도 계산 (캐싱 적용)"""
    if not str1 or not str2:
        return 0.0
    return Levenshtein.ratio(str1.lower(), str2.lower())


def find_similar_keywords(df, keyword_dict, similarity_threshold=0.7):
    """데이터프레임에서 키워드와 유사한 표현 찾기"""
    results = []

    # ⚡ 최적화: DataFrame을 문자열 형태로 변환 (한 번만 변환하여 반복 줄이기)
    df_str = df.astype(str)

    def check_keyword_match(text, location_info, row_idx=None, col_idx=None):
        """주어진 텍스트에서 키워드와 유사한 표현을 찾는 함수"""
        text_lower = text.lower().strip()

        for main_keyword, similar_keywords in keyword_dict.items():
            exact_match = False
            max_similarity = 0.0
            best_match_type = ""

            for similar_keyword in similar_keywords:
                similar_keyword_lower = similar_keyword.lower().strip()

                # 완전 일치 (O(1) 비교)
                if text_lower == similar_keyword_lower:
                    max_similarity = 1.0
                    best_match_type = "완전 일치"
                    exact_match = True
                    break

            # 유사도 기반 매칭 (완전 일치 아닐 때)
            if not exact_match:
                for similar_keyword in similar_keywords:
                    similarity = calculate_similarity(text_lower, similar_keyword.lower())

                    if similarity > max_similarity and similarity >= similarity_threshold:
                        max_similarity = similarity
                        best_match_type = "유사도 매칭"

            # 결과 추가 (충분한 유사도가 있는 경우)
            if max_similarity >= similarity_threshold:
                results.append(
                    {
                        "키워드": main_keyword,
                        "발견된 표현": text,
                        "위치": location_info,
                        "row_idx": row_idx,
                        "col_idx": col_idx,
                        "유사도": round(max_similarity, 2),
                        "매칭 유형": best_match_type,
                    }
                )

    # ⚡ 데이터프레임을 한 번만 순회 (O(N*M))
    for row_idx, row in df_str.iterrows():
        for col_idx, cell_value in enumerate(row):
            if len(cell_value) >= 2:  # 짧은 문자열 필터링
                check_keyword_match(cell_value, f"행 {row_idx+1}, 열 {col_idx+1} ({df.columns[col_idx]})", row_idx, col_idx)

    # ⚡ 결과 처리 최적화
    if results:
        results_df = pd.DataFrame(results)

        # 중복 제거 및 정렬
        return results_df.sort_values(["유사도", "키워드"], ascending=[False, True]).drop_duplicates(subset=["위치", "키워드"], keep="first")

    return pd.DataFrame()
