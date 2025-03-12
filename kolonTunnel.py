import camelot
import streamlit as st
import pdfplumber
import pandas as pd
import time
from kolonAgGrid import create_st_aggrid
from kolonKeywords import find_similar_keywords
import re
import math
import numpy as np
import os

# Streamlit 페이지 설정
st.set_page_config(layout="wide")
start_time = time.time()  # 시작 시간 측정

with st.sidebar:
    option = st.radio("#### :orange[PDF 테이블 추출 라이브러리 선택]", ["Camelot (격자 기반)", "pdfplumber (텍스트 기반)"], index=0)
    # 구분열 = st.number_input("구분열", min_value=1, max_value=100, value=1, step=1)

    # PDF 파일 업로드 UI
    uploaded_file = st.file_uploader("PDF 파일 업로드", type=["pdf"])

    # 현재 폴더에서 PDF 파일 목록 가져오기
    pdf_files = [f for f in os.listdir() if f.endswith(".pdf")]

    # 사용자에게 다운로드할 PDF 선택
    selected_pdf = st.selectbox("다운로드할 PDF 파일 선택", pdf_files, index=1)

    # 선택한 PDF 파일 다운로드 버튼
    if selected_pdf:
        with open(selected_pdf, "rb") as file:
            btn = st.download_button(label="PDF 다운로드", data=file, file_name=selected_pdf, mime="application/pdf")


# 파일 선택
if uploaded_file is not None:
    file_path = uploaded_file.name  # 사용자가 업로드한 파일
    with open(file_path, "wb") as f:
        f.write(uploaded_file.read())  # 파일 저장
else:
    file_path = "a1.pdf"  # 기본 파일 사용


@st.cache_data
def extract_tables_camelot(file_path):
    return camelot.read_pdf(file_path, pages="all", flavor="lattice")


@st.cache_data
def extract_tables_pdfplumber(file_path):
    with pdfplumber.open(file_path) as pdf:
        extracted_tables = []
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                if table:
                    df = pd.DataFrame(table)
                    extracted_tables.append(df)
    return extracted_tables


# 선택된 옵션에 따라 표 추출
if "camelot" in option:
    extracted_tables = extract_tables_camelot(file_path)
else:
    extracted_tables = extract_tables_pdfplumber(file_path)
# extracted_tables


def clean_text(text):
    # None 또는 NaN 값 처리
    if text is None or (isinstance(text, float) and math.isnan(text)):
        return ""
    if not isinstance(text, str):  # 문자열이 아닐 경우, 일단 문자열로 변환했음
        text = str(text)
    # 개행문자, 탭 등 제거 후 공백으로 치환
    text = text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    # 다중 공백을 하나의 공백으로 축소
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()  # 앞뒤 공백 제거
    return text


# extracted_tables가 DataFrame들의 리스트라고 가정
cleaned_tables = []
for df in extracted_tables:
    # df의 모든 셀에 대해 clean_text 함수 적용
    cleaned_df = df.map(clean_text)
    cleaned_tables.append(cleaned_df)

# 탭 생성
tabs = st.tabs(["Result"] + [f"표 {i+1}" for i in range(len(cleaned_tables))])
for i, tab in enumerate(tabs[1:]):
    with tab:
        df_table = cleaned_tables[i]
        if df_table.empty:
            st.warning("📌 PDF에서 데이터가 포함된 표를 찾을 수 없습니다.")
        else:
            df_table.columns = list(range(len(df_table.columns)))
            df_table = df_table.map(lambda x: "" if x is None else x)
            st.dataframe(df_table, height=1200, use_container_width=True)

with tabs[0]:
    # df = {
    #     "굴착공법": ["A", "A", "B", "B", "C", "C", "D", "D", "E", "E"],
    #     "천공장": ["터널", "터널 단면군", 300, 400, 500, 600, 700, 800, 900, 1000],
    #     "굴진장": [100, 200, "터널 단면", 400, 500, 600, 700, 800, 900, 1000],
    #     "시점방향": [100, 200, "터널", 400, 500, 600, 700, 800, 900, 1000],
    #     "종점방향": [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000],
    #     "굴착량": [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000],
    #     "여굴량": [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000],
    #     "숏크리트": [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000],
    # }
    df_output = pd.DataFrame()
    # 첫 번째 위치(인덱스 0)에 열 삽입
    v = cleaned_tables[0]
    df_output.insert(0, '이름', v.iloc[4:, 1])
    df_output.insert(0, '단면', v.iloc[4:, 2])
    df_output.insert(0, '상하부', v.iloc[4:, 3])


keyword_results = {}
for page_idx, df in enumerate(cleaned_tables):
    keyword_dict = {
        "터널 단면군": ["터널단면군", "터널단면", "터널 단면", "터널 단면군"],
        "굴착 공법": ["굴착공법", "굴착 공법"],
        "굴진장": ["굴진장", "굴진 거리", "굴진"],
        "천공장": ["천공장", "천공 거리", "천공"],
        "시점": ["시점방향", "시점", "시점 방향", "연장", "대면터널"],
        "종점": ["종점방향", "종점", "종점 방향"],
        "m당 평균단위수량": ["m당", "m당 평균단위수량"],
        "m당 굴착량": ["굴착량", "굴착 량"],
        "m당 여굴량": ["여굴량", "여굴 량"],
        "m당 숏크리트": ["숏크리트", "숏크리트 량", "숏크리트 수량", 'm당 숏크리트'],
        "m당 숏크리트 리바운드": ["숏크리트 리바운드", "숏크리트 리바운드수 량", "숏크리트 리바운드 수량"],
        "1발파 천공수": ["1발파 천공수", "1발파 천공 수", "1발파 천공 수량", "1발파 천공수(무장약공포함)"],
        "Dynamite <32mm>": ["Dynamite <32mm>", "Dynamite 32mm", "Dynamite 32mm 량"],
        "Emulsion <32mm>": ["Emulsion <32mm>", "Emulsion 32mm", "Emulsion 32mm 량"],
        "Emulsion <25mm>": ["Emulsion <25mm>", "Emulsion 25mm", "Emulsion 25mm 량"],
        "정밀 폭약": ["정밀 폭약", "정밀 폭약 량", "정밀 폭약 수량"],
        "뇌관 <MS>": ["뇌관 <MS>", "뇌관 MS", "뇌관 MS 량"],
        "뇌관 <LP>": ["뇌관 <LP>", "뇌관 LP", "뇌관 LP 량"],
        "연결뇌관 <Starter>": ["연결뇌관 <Starter>", "연결뇌관 Starter", "연결뇌관 Starter 량"],
        "연결뇌관 <Bunch>": ["연결뇌관 <Bunch>", "연결뇌관 Bunch", "연결뇌관 Bunch 량"],
        "격자 지보": ["격자 지보", "격자 지보 량", "격자 지보 수량"],
        "록볼트 규격": ["록볼트 규격", "규격"],
        "록볼트 설치수": ["록볼트 m당 설치수", "m당 설치수"],
    }
    results_df = find_similar_keywords(df, keyword_dict)

    # 결과가 비어있지 않은 경우에만 처리
    if not results_df.empty:
        # 결과에 페이지 정보 추가
        results_df['페이지'] = page_idx

        for keyword in results_df['키워드'].unique():
            keyword_df = results_df[results_df['키워드'] == keyword]

            if keyword not in keyword_results:
                keyword_results[keyword] = keyword_df.copy()
            else:
                keyword_results[keyword] = pd.concat([keyword_results[keyword], keyword_df], ignore_index=True)

page_idx_m = keyword_results["m당 평균단위수량"]["페이지"].values

keyword_dfs = []
# 최종 결과 출력 - 유사도 순으로 정렬
for keyword, df in keyword_results.items():
    # 유사도 점수 열이 있다고 가정('유사도')
    if '유사도' in df.columns:
        sorted_df = df.sort_values(by='유사도', ascending=False)  # 높은 유사도부터 정렬
    else:
        # 유사도 열이 없는 경우, 페이지 순으로 정렬
        sorted_df = df.sort_values(by='페이지')
        st.write("(유사도 점수 열을 찾을 수 없어 페이지 순으로 정렬합니다)")

    # 키워드 정보 추가
    sorted_df['키워드_분류'] = keyword  # 어떤 키워드 검색 결과인지 표시
    keyword_dfs.append(sorted_df)
    # st.write(f"\n### 키워드: {keyword} ##")
    # st.write(f"총 {len(df)}개의 항목 발견")
    # st.write(sorted_df)
    # st.write("---")

with tabs[0]:
    # 이제 모든 키워드에 대해 결과 처리
    keywords_to_process = list(keyword_results.keys())

    # 각 키워드별로 처리
    for keyword in keywords_to_process:
        if keyword in keyword_results and not keyword_results[keyword].empty:
            # 해당 키워드의 결과 가져오기
            sorted_df = (
                keyword_results[keyword].sort_values(by='유사도', ascending=False)
                if '유사도' in keyword_results[keyword].columns
                else keyword_results[keyword]
            )

            # 특정 페이지 데이터만 남기기
            if 'm당' in keyword:
                sorted_df = sorted_df[sorted_df['페이지'] == page_idx_m[0]]
            # 유사도가 가장 높은 결과 가져오기
            top_result = sorted_df.iloc[0]

            # 페이지와 열 번호 정보 가져오기
            page_idx = top_result['페이지']
            col_idx = top_result['col_idx']  # if 'col_idx' in top_result.index else 1

            # 해당 페이지의 데이터 가져오기
            if page_idx < len(cleaned_tables):
                v = cleaned_tables[page_idx]
                # 0열(첫 번째 열)에서 0행(구분) 다음 처음 데이터가 있는 행 찾기
                first_valid_row = v.iloc[1:, 0][v.iloc[1:, 0].notna() & (v.iloc[1:, 0] != "")].index[0]
                # 열이 존재하는지 확인
                if col_idx < v.shape[1]:
                    # 행 인덱스 4부터 끝까지 해당 열의 데이터 가져오기
                    column_data = v.iloc[first_valid_row:, col_idx]
                    # 숫자로 변환 (천단위 쉼표 제거, 문자는 그대로)
                    column_data = column_data.map(
                        lambda x: (
                            pd.to_numeric(x.replace(",", ""), errors="coerce")
                            if isinstance(x, str) and x.replace(",", "").replace(".", "").isdigit()
                            else x
                        )
                    )

                    # 길이 확인 및 조정
                    if len(column_data) > len(df_output):
                        column_data = column_data[: len(df_output)]
                    elif len(column_data) < len(df_output):
                        padding = [None] * (len(df_output) - len(column_data))
                        column_data = pd.concat([column_data, pd.Series(padding)])

                    # 기존 열이 있으면 삭제
                    if keyword in df_output.columns:
                        df_output = df_output.drop(columns=[keyword])

                    # 열 추가 - 0번 위치에 삽입
                    df_output.insert(0, keyword, column_data.values)


def try_convert_to_float(x):
    try:
        return float(x)
    except (ValueError, TypeError):
        return x  # 변환 실패시 원본 그대로 반환


for col in df_output.columns:
    df_output[col] = df_output[col].apply(try_convert_to_float)

# "시점" 컬럼 확인  # "종점" 컬럼 확인
col_시점 = next((col for col in df_output.columns if "시점" in col), None)
col_종점 = next((col for col in df_output.columns if "종점" in col), None)
# "연장 소계" 계산
if col_시점 and col_종점:
    df_output["연장 소계"] = df_output[col_시점].fillna(0) + df_output[col_종점].fillna(0)
elif col_시점:
    df_output["연장 소계"] = df_output[col_시점]


def sum_if_numeric(a, b):
    try:
        return float(a) + float(b)
    except (ValueError, TypeError):
        return math.nan


def multiply_if_numeric(a, b):
    try:
        return float(a) * float(b)
    except (ValueError, TypeError):
        return math.nan


df_output["굴착량"] = [multiply_if_numeric(a, b) for a, b in zip(df_output["굴진장"], df_output["m당 굴착량"])]
df_output["여굴량"] = [multiply_if_numeric(a, b) for a, b in zip(df_output["굴진장"], df_output["m당 여굴량"])]
df_output["버력 처리량"] = df_output["굴착량"] + df_output["여굴량"]
df_output["총 굴착량"] = [multiply_if_numeric(a, b) for a, b in zip(df_output["연장 소계"], df_output["m당 굴착량"])]
df_output["총 버력량"] = [
    multiply_if_numeric(length, sum_if_numeric(m_gulchak, m_yeogul))
    for length, m_gulchak, m_yeogul in zip(df_output["연장 소계"], df_output["m당 굴착량"], df_output["m당 여굴량"])
]

df_output["1발파 타설"] = [multiply_if_numeric(a, b) for a, b in zip(df_output["굴진장"], df_output["m당 숏크리트"])]
df_output["총 타설량"] = [multiply_if_numeric(a, b) for a, b in zip(df_output["연장 소계"], df_output["m당 숏크리트"])]

# 문자# 1) '연장 소계'를 숫자로 변환
df_output["연장 소계_숫자"] = pd.to_numeric(df_output["연장 소계"], errors="coerce")

# 2) 조건문 결합
df_output["천공 장비"] = np.where(
    df_output["연장 소계_숫자"].notna() & (df_output["연장 소계_숫자"] > 0),
    # 위 조건(숫자+양수) 충족하면 np.select로 '터널 단면군' 값에 따라 분기
    np.select([df_output["터널 단면군"] == "C", df_output["터널 단면군"] == "B"], [3, 2], default=0),
    # 조건 불만족 시 -> ""
    "",
)
df_output["장비 규격"] = np.where(
    df_output["연장 소계_숫자"].notna() & (df_output["연장 소계_숫자"] > 0),
    # 위 조건(숫자+양수) 충족하면 np.select로 '터널 단면군' 값에 따라 분기
    np.select([df_output["터널 단면군"] == "C", df_output["터널 단면군"] == "B"], [3.5, 0.6], default=0.0),
    # 조건 불만족 시 -> ""
    "",
)
df_output["천공 속도"] = np.where(
    df_output["연장 소계"].astype(str).str.strip() == "",  # 빈 문자열이면
    "",  # 그대로 유지
    np.where(df_output["연장 소계_숫자"] > 0, 1.0, 0.0),  # 0보다 크면 1, 그렇지 않으면 0
)
df_output["암파쇄"] = np.where(
    df_output["연장 소계"].astype(str).str.strip() == "",  # 빈 문자열이면
    "",  # 그대로 유지
    np.where(df_output["연장 소계_숫자"] > 0, 3.4, 0.0),  # 0보다 크면 1, 그렇지 않으면 0
)

df_output["장비 f"] = np.where(
    df_output["연장 소계"].astype(str).str.strip() == "",  # 빈 문자열이면
    "",  # 그대로 유지
    np.where(df_output["연장 소계_숫자"] > 0, 0.615, 0.0),  # 0보다 크면 1, 그렇지 않으면 0
)
df_output["Q (로더)"] = np.where(
    df_output["연장 소계"].astype(str).str.strip() == "",  # 빈 문자열이면
    "",  # 그대로 유지
    np.where(df_output["연장 소계_숫자"] > 0, 82.667, 0.0),  # 0보다 크면 1, 그렇지 않으면 0
)
df_output["Q (백호)"] = np.where(
    df_output["연장 소계"].astype(str).str.strip() == "",  # 빈 문자열이면
    "",  # 그대로 유지
    np.where(df_output["연장 소계_숫자"] > 0, 172.591, 0.0),  # 0보다 크면 1, 그렇지 않으면 0
)


# 3) 임시 변환 컬럼 삭제
df_output.drop(columns=["연장 소계_숫자"], inplace=True)
# st.write(df_output)

with tabs[0]:
    # df_output
    st.write("### :blue[<< pdf에서 데이터 추출 >>]")
    create_st_aggrid(df_output, 'input')
    st.write("### :blue[<< 계산 데이터 >>]")
    create_st_aggrid(df_output, 'output')


with st.sidebar:
    st.write("---")
    st.write(f"표 개수: {len(cleaned_tables)}")
    st.write(f"실행 시간: {time.time() - start_time:.2f} 초")  # 포맷팅 사용
