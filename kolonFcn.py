import streamlit as st
from st_aggrid import JsCode


def get_header_groups(basic_style, display_mode):

    # 천단위 구분자 및 소수점 처리를 위한 JS 코드 수정
    cell_renderer_js = JsCode(
        """
        function(params) {
            if (params.value === null || params.value === undefined || params.value === '') {
                return '';
            } else if (typeof params.value === 'number') {
                // precision이 0이어도 적용되도록 수정
                var precision = (typeof params.column.colDef.precision !== "undefined") ? params.column.colDef.precision : 2;
                return params.value.toLocaleString('ko-KR', { 
                    minimumFractionDigits: precision, 
                    maximumFractionDigits: precision 
                });
            } else {
                return params.value;
            }
        }
        """
    )

    # 숫자형 컬럼
    def get_number_col_config(header_name, field_name, is_site_column=False, width=None, precision=2):
        config = {"headerName": header_name, "field": field_name, "cellRenderer": cell_renderer_js, "precision": precision}
        if width:
            config["width"] = width
            config["maxWidth"] = width * 2

        # 현장 컬럼인 경우 동적 스타일 함수 적용
        if is_site_column:
            # config["cellStyle"] = max_min_cell_style
            # config["cellStyle"] = max_min_cell_style
            config["width"] = 150
            config["maxWidth"] = config["width"] * 2
        else:
            config["cellStyle"] = {**basic_style, "textAlign": "right", "justifyContent": "right"}

        return config

    # 문자형 컬럼
    def get_text_col_config(header_name, field_name, pinned=None, width=None):
        config = {"headerName": header_name, "field": field_name, "pinned": pinned}

        # 너비 설정 - 직접 픽셀 수 지정
        if width:
            config["width"] = width
            config["maxWidth"] = width * 2
        config["cellStyle"] = {**basic_style, "textAlign": "center", "justifyContent": "center"}
        return config

    # 공통 헤더(행 번호 + 구 분 열)만 따로 묶어 변수로 설정
    common_header_group = [
        {
            "headerName": "",
            "headerClass": "group-header-style",
            "children": [
                {
                    "headerName": "",
                    "field": "",  # 빈 필드명
                    "valueGetter": "node.rowIndex + 1",  # 행 번호 생성 로직
                    "maxWidth": 60,
                    "pinned": "left",
                    "cellStyle": basic_style,
                }
            ],
        },
        {
            "headerName": "구 분",
            "headerClass": "group-header-style",
            "children": [
                get_text_col_config("이름", "이름", width=140),
                get_text_col_config("단면", "단면", width=80),
                get_text_col_config("상하부", "상하부", width=90),
            ],
        },
    ]

    if display_mode == "input":
        header_group = [
            {
                "headerName": "터널굴착 설계 입력부",
                "headerClass": "input-style",
                "children": [
                    get_text_col_config("터널\n단면군", "터널 단면군", width=90),
                    get_text_col_config("굴착\n공법", "굴착 공법", width=80),
                    get_number_col_config("굴진장\n(m)", "굴진장", width=90),
                    get_number_col_config("천공장\n(m)", "천공장", width=90),
                    {
                        "headerName": "연장 (m)",
                        "headerClass": "sub-group-header-style",
                        "children": [
                            get_number_col_config("시점", "시점", width=80, precision=0),
                            get_number_col_config("종점", "종점", width=80, precision=0),
                        ],
                    },
                    {
                        "headerName": "m당 단위수량 (m³/m)",
                        "headerClass": "sub-group-header-style",
                        "children": [
                            get_number_col_config("굴착량", "m당 굴착량", width=90),
                            get_number_col_config("여굴량", "m당 여굴량", width=90),
                            get_number_col_config("숏크리트", "m당 숏크리트", width=110),
                            get_number_col_config("숏크리트\n리바운드", "m당 숏크리트 리바운드", width=110),
                        ],
                    },
                    {
                        "headerName": "발파 천공 및 장약량",
                        "headerClass": "sub-group-header-style",
                        "children": [
                            get_number_col_config("1발파\n천공수\n(공)", "1발파 천공수", width=90, precision=0),
                            get_number_col_config("Dynamite\n<32mm>\n(kg)", "Dynamite <32mm>", width=120),
                            get_number_col_config("Emulsion\n<32mm>\n(kg)", "Emulsion <32mm>", width=110),
                            get_number_col_config("Emulsion\n<25mm>\n(kg)", "Emulsion <25mm>", width=110),
                            get_number_col_config("정밀\n폭약\n(kg)", "정밀 폭약", width=80),
                            get_number_col_config("뇌관\n<MS>\n(ea)", "뇌관 <MS>", width=90, precision=0),
                            get_number_col_config("뇌관\n<LP>\n(ea)", "뇌관 <LP>", width=90, precision=0),
                            get_number_col_config("연결뇌관\n<Starter>\n(ea)", "연결뇌관 <Starter>", width=120, precision=0),
                            get_number_col_config("연결뇌관\n<Bunch>\n(ea)", "연결뇌관 <Bunch>", width=110, precision=0),
                            get_number_col_config("격자\n지보\n(set/m)", "격자 지보", width=100),
                        ],
                    },
                    {
                        "headerName": "록볼트",
                        "headerClass": "sub-group-header-style",
                        "children": [
                            get_number_col_config("규격\n(m)", "록볼트 규격", width=80, precision=1),
                            get_number_col_config("m당\n설치수\n(ea/m)", "록볼트 설치수", width=100),
                        ],
                    },
                ],
            }
        ]
    else:  # Output
        header_group = [
            {
                "headerName": "계  산  부",
                "headerClass": "output-style",
                "children": [
                    {
                        "headerName": "연장 (m)",
                        "headerClass": "sub-group-header-style",
                        "children": [get_number_col_config("연장\n소계", "연장 소계", width=90, precision=0)],
                    },
                    {
                        "headerName": "1발파당 (m³)",
                        "headerClass": "sub-group-header-style",
                        "children": [
                            get_number_col_config("굴착량", "굴착량", width=90, precision=1),
                            get_number_col_config("여굴량", "여굴량", width=90, precision=1),
                            get_number_col_config("버력\n처리량", "버력 처리량", width=90, precision=1),
                        ],
                    },
                    {
                        "headerName": "총수량 (m³)",
                        "headerClass": "sub-group-header-style",
                        "children": [
                            get_number_col_config("총\n굴착량", "총 굴착량", width=90, precision=0),
                            get_number_col_config("총\n버력량", "총 버력량", width=90, precision=0),
                        ],
                    },
                    {
                        "headerName": "숏크리트 단위수량 (m³)",
                        "headerClass": "sub-group-header-style",
                        "children": [
                            get_number_col_config("1m당\n타설", "m당 숏크리트", width=90, precision=1),
                            get_number_col_config("1발파\n타설", "1발파 타설", width=90, precision=1),
                            get_number_col_config("총\n타설량", "총 타설량", width=90, precision=1),
                        ],
                    },
                ],
            },
            {
                "headerName": "장 비 규 격",
                "headerClass": "output-style",
                "children": [
                    {
                        "headerName": "천공 드릴",
                        "headerClass": "sub-group-header-style",
                        "children": [
                            get_number_col_config("장비\n(ea)", "천공 장비", width=90, precision=0),
                            get_number_col_config("속도\n(m/min)", "천공 속도", width=100, precision=1),
                        ],
                    },
                    {
                        "headerName": "대 형",
                        "headerClass": "sub-group-header-style",
                        "children": [get_number_col_config("암파쇄\n(m³/hr)", "암파쇄", width=100, precision=1)],
                    },
                    {
                        "headerName": "적 재 장 비",
                        "headerClass": "sub-group-header-style",
                        "children": [
                            get_number_col_config("규격\n(m³)", "장비 규격", width=90, precision=1),
                            get_number_col_config("f\n(1/L)", "장비 f", width=90),
                            get_number_col_config("Q (로더)\n(m³/hr)", "Q (로더)", width=100),
                            get_number_col_config("Q (백호)\n(m³/hr)", "Q (백호)", width=100),
                        ],
                    },
                ],
            },
        ]

    column_groups = common_header_group + header_group

    return column_groups
