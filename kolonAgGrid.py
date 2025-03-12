from thefuzz import process
import pandas as pd
import numpy as np
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
from kolonFcn import get_header_groups


def create_st_aggrid(df, display_mode):
    # 기본 스타일 설정
    basic_style = {
        "display": "-webkit-box",  # 웹킷 기반 박스 모델 사용
        "-webkit-line-clamp": "2",  # 텍스트 줄 수 제한
        "-webkit-box-orient": "vertical",  # 박스 방향 세로 설정
        "overflow": "hidden",  # 넘치는 텍스트 숨김
        "textOverflow": "ellipsis",  # 텍스트 말줄임 (...)
        "lineHeight": "20px",  # 줄 간격 설정
        "minHeight": "20px",  # 최소 높이 설정
        "padding": "6px",  # 여백
        "whiteSpace": "normal",  # 텍스트 줄바꿈 허용
        "textAlign": "center",  # 텍스트 가운데 정렬
        "justifyContent": "center",  # 가로 중앙 정렬
        "alignItems": "center",  # 세로 중앙 정렬
        "wordBreak": "break-word",  # 긴 단어 줄바꿈 처리
        "fontWeight": "bold",  # 글자 굵기
        "fontSize": "16px",
        "display": "flex",  # 플렉스 박스 사용
    }

    # GridOptions 설정
    gb = GridOptionsBuilder.from_dataframe(df)

    gb.configure_default_column(
        editable=True,
        sortable=True,
        # filter=True,
        resizable=True,
        # maxWidth=600,
        cellStyle={**basic_style},
    )
    # 그리드 옵션 설정 (페이지)
    gb.configure_grid_options(
        pagination=True, paginationPageSize=50, rowHeight=40, suppressRowTransform=True, rowSelection="multiple", suppressMenuHide=True
    )

    # 그리드 옵션 빌드
    gridOptions = gb.build()

    # 최대/최소값 색상 표시를 위한 JS 함수
    max_min_cell_style = JsCode(
        """
        function(params) {
            // 기본 스타일을 복사
            var style = {
                "display": "flex",
                "textAlign": "right", 
                "justifyContent": "right",
                "alignItems": "center",
                "lineHeight": "20px",
                "minHeight": "20px",
                "padding": "6px",
                "fontSize": "126px",
                "fontWeight": "bold",                
            };
            
            // 값이 없으면 기본 스타일 반환
            if (params.value === null || params.value === undefined) {
                return style;
            }
            
            // 현재 행의 최대/최소 단가 값 가져오기
            var maxValue = params.data['최대 단가'];
            var minValue = params.data['최소 단가'];
            var currentValue = Number(params.value);
            
            // 값이 최대값과 같은 경우 (숫자로 비교)
            if (currentValue === maxValue && maxValue !== undefined && maxValue !== null) {
                style.backgroundColor = 'rgba(255,165,0,0.3)';  // 주황색 배경
                style.fontWeight = 'bold';
                style.color = '#d32f2f';  // 빨간색 글자
            } 
            // 값이 최소값과 같은 경우 (숫자로 비교)
            else if (currentValue === minValue && minValue !== undefined && minValue !== null) {
                style.backgroundColor = 'rgba(0,191,255,0.3)';  // 하늘색 배경
                style.fontWeight = 'bold';
                style.color = '#1976d2';  // 파란색 글자
            }
            
            return style;
        }
        """
    )

    column_groups = get_header_groups(basic_style, display_mode)
    gridOptions = {
        "columnDefs": column_groups,
        "columnHoverHighlight": True,  # 열 호버 활성화
        "rowHoverHighlight": True,
        # 모든 컬럼에 동일 옵션 주고 싶으면 defaultColDef 활용
        "defaultColDef": {"autoHeaderHeight": True},  # "wrapHeaderText": True,
    }

    # AgGrid 출력
    AgGrid(
        df,
        key=display_mode,
        gridOptions=gridOptions,
        theme="streamlit",  # streamlit 테마 적용
        fit_columns_on_grid_load=False,
        update_mode="value_changed",
        allow_unsafe_jscode=True,
        # enable_enterprise_modules=False,  # 옆에 필터 ... 세로 숨기기
        height=800,
        custom_css={
            ".ag-header-group-cell": {"border": "1px solid gray"},
            ".ag-header-group-cell-label": {
                "color": "green",
                "font-weight": "bold",
                "font-size": "18px",
                "width": "100%",  # 추가: 너비 100%로 설정
                "justify-content": "center",  # 추가: 직접 중앙 정렬 설정
                "align-items": "center",  # 추가: 수직 중앙 정렬
                "text-align": "center",
            },
            ".ag-header-cell": {"border": "1px solid gray"},
            ".ag-header-cell-label": {
                # "background-color": "rgba(217, 242, 217, 0.5)",
                "justify-content": "center",  # 추가: 직접 중앙 정렬 설정
                "align-items": "center",  # 추가: 수직 중앙 정렬
                "text-align": "center",
                "color": "orange",
                "font-weight": "bold",
                "font-size": "16px",
            },
            ".input-style": {"background-color": "rgba(0, 0, 255, 0.2)"},
            ".output-style": {"background-color": "rgba(255, 0, 0, 0.2)"},
            ".ag-row:hover .ag-cell": {"background-color": "rgba(0,255,0,0.2) !important"},
            ".ag-column-hover": {"background-color": "rgba(255, 0, 0, 0.2) !important"},
            ".ag-cell.ag-column-hover": {"background-color": "rgba(255, 0, 255, 0.2) !important"},
            ".ag-cell": {
                "background-color": "rgba(20, 20, 20, 0.9) !important",
                # "color": "black !important",
                "font-size": "16px",
                "border": "1px solid lightgray",  # 셀 사이 구분선
            },
            ".ag-cell-label": {
                # "color": "black !important",
            },
        },
    )
