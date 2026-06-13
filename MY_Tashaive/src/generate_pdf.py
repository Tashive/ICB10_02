"""
MY_Tashaive/report/EDA_Report.md 마크다운 보고서를 한글 폰트(맑은 고딕)가
적용된 PDF 파일로 변환하는 스크립트입니다.
차트 이미지(plot1~11), 표, 코드블록, 인용문 등 마크다운 구조를 파싱하여
ReportLab Platypus 기반의 전문적인 레이아웃의 PDF를 생성합니다.
출력 경로: MY_Tashaive/report/EDA_Report.pdf
"""

import os
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image,
    Table, TableStyle, HRFlowable, PageBreak, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ── 한글 폰트 등록 (맑은 고딕) ──────────────────────────────────────
FONT_DIR = r"C:\Windows\Fonts"
REGULAR = os.path.join(FONT_DIR, "malgun.ttf")
BOLD    = os.path.join(FONT_DIR, "malgunbd.ttf")

pdfmetrics.registerFont(TTFont("Malgun", REGULAR))
pdfmetrics.registerFont(TTFont("MalgunBold", BOLD))
pdfmetrics.registerFontFamily("Malgun", normal="Malgun", bold="MalgunBold")

# ── 색상 팔레트 ──────────────────────────────────────────────────────
C_NAVY      = colors.HexColor("#1e3a5f")
C_ACCENT    = colors.HexColor("#3b82f6")
C_LIGHT_BG  = colors.HexColor("#f0f4f8")
C_QUOTE_BG  = colors.HexColor("#eef4ff")
C_QUOTE_BAR = colors.HexColor("#3b82f6")
C_CODE_BG   = colors.HexColor("#1e1e2e")
C_CODE_FG   = colors.HexColor("#cdd6f4")
C_TABLE_HDR = colors.HexColor("#1e3a5f")
C_TABLE_ALT = colors.HexColor("#f8fafc")
C_HR        = colors.HexColor("#cbd5e1")

# ── 스타일 정의 ──────────────────────────────────────────────────────
def build_styles():
    base = getSampleStyleSheet()
    styles = {}

    styles["title"] = ParagraphStyle(
        "title",
        fontName="MalgunBold", fontSize=20, leading=28,
        textColor=C_NAVY, alignment=TA_CENTER,
        spaceAfter=6
    )
    styles["subtitle"] = ParagraphStyle(
        "subtitle",
        fontName="Malgun", fontSize=11, leading=16,
        textColor=colors.HexColor("#64748b"), alignment=TA_CENTER,
        spaceAfter=18
    )
    styles["h2"] = ParagraphStyle(
        "h2",
        fontName="MalgunBold", fontSize=15, leading=22,
        textColor=C_NAVY,
        spaceBefore=14, spaceAfter=6,
        borderPad=4,
        leftIndent=0
    )
    styles["h3"] = ParagraphStyle(
        "h3",
        fontName="MalgunBold", fontSize=12, leading=18,
        textColor=colors.HexColor("#334155"),
        spaceBefore=10, spaceAfter=4,
        leftIndent=6
    )
    styles["body"] = ParagraphStyle(
        "body",
        fontName="Malgun", fontSize=9.5, leading=15,
        textColor=colors.HexColor("#1e293b"),
        alignment=TA_JUSTIFY,
        spaceAfter=5
    )
    styles["bullet"] = ParagraphStyle(
        "bullet",
        fontName="Malgun", fontSize=9.5, leading=15,
        textColor=colors.HexColor("#1e293b"),
        leftIndent=12, bulletIndent=4,
        spaceAfter=3
    )
    styles["sub_bullet"] = ParagraphStyle(
        "sub_bullet",
        fontName="Malgun", fontSize=9, leading=14,
        textColor=colors.HexColor("#334155"),
        leftIndent=24, bulletIndent=14,
        spaceAfter=2
    )
    styles["quote"] = ParagraphStyle(
        "quote",
        fontName="Malgun", fontSize=9, leading=14,
        textColor=colors.HexColor("#1e3a5f"),
        alignment=TA_JUSTIFY,
        spaceAfter=4
    )
    styles["code"] = ParagraphStyle(
        "code",
        fontName="Courier", fontSize=7.5, leading=11,
        textColor=C_CODE_FG,
        leftIndent=0,
        spaceAfter=2
    )
    styles["caption"] = ParagraphStyle(
        "caption",
        fontName="Malgun", fontSize=8.5, leading=13,
        textColor=colors.HexColor("#475569"),
        alignment=TA_CENTER,
        spaceAfter=8
    )
    styles["table_hdr"] = ParagraphStyle(
        "table_hdr",
        fontName="MalgunBold", fontSize=8.5, leading=12,
        textColor=colors.white, alignment=TA_CENTER
    )
    styles["table_cell"] = ParagraphStyle(
        "table_cell",
        fontName="Malgun", fontSize=8.5, leading=12,
        textColor=colors.HexColor("#1e293b"), alignment=TA_LEFT
    )
    return styles

# ── 텍스트 인라인 마크다운 처리 ──────────────────────────────────────
def md_inline(text, base_style):
    """**볼드**, `코드`, *이탤릭* 등 인라인 마크다운을 ReportLab XML 태그로 변환"""
    font = base_style.fontName if base_style else "Malgun"
    bold_font = "MalgunBold"
    # **bold** → <b>
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    # `code` → <font name="Courier" color="#e11d48">
    text = re.sub(r'`([^`]+)`', r'<font name="Courier" color="#e11d48">\1</font>', text)
    # *italic* → <i>
    text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
    # $...$ 수식 → 단순 텍스트 (특수문자 제거)
    text = re.sub(r'\$(.+?)\$', lambda m: m.group(1).replace('\\', '').replace('_', ' ').replace('{', '').replace('}', ''), text)
    # $$...$$
    text = re.sub(r'\$\$(.+?)\$\$', lambda m: m.group(1).replace('\\', '').replace('_', ' ').replace('{', '').replace('}', ''), text, flags=re.DOTALL)
    # HTML 특수문자
    text = text.replace('&', '&amp;').replace('<amp>', '&')
    # 이미 치환된 태그의 & 복원
    text = re.sub(r'&amp;(lt|gt|amp);', lambda m: f'&{m.group(1)};', text)
    return text

# ── 표 파싱 ──────────────────────────────────────────────────────────
def parse_table(lines, styles):
    """마크다운 표 라인들을 ReportLab Table 객체로 변환"""
    rows = []
    for line in lines:
        if re.match(r'^\s*\|[-:| ]+\|\s*$', line):
            continue  # 구분선 스킵
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        rows.append(cells)
    if not rows:
        return None

    col_count = max(len(r) for r in rows)
    page_w = A4[0] - 4 * cm  # 좌우 여백 2cm씩
    col_w = page_w / col_count

    data = []
    for i, row in enumerate(rows):
        # 열 수 맞추기
        while len(row) < col_count:
            row.append("")
        if i == 0:
            para_style = styles["table_hdr"]
        else:
            para_style = styles["table_cell"]
        data.append([
            Paragraph(md_inline(cell, para_style), para_style)
            for cell in row
        ])

    tbl = Table(data, colWidths=[col_w] * col_count, repeatRows=1)
    ts = TableStyle([
        # 헤더 행 배경
        ("BACKGROUND", (0, 0), (-1, 0), C_TABLE_HDR),
        ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
        # 짝수 행 배경
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, C_TABLE_ALT]),
        # 테두리
        ("GRID",       (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("BOX",        (0, 0), (-1, -1), 1,   C_ACCENT),
        # 패딩
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ])
    tbl.setStyle(ts)
    return tbl

# ── 코드블록 생성 ─────────────────────────────────────────────────────
def make_code_block(lines, styles):
    """코드블록 라인들을 어두운 배경 Table로 래핑"""
    items = []
    for line in lines:
        # HTML 특수문자 이스케이프
        line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        items.append(Paragraph(line if line.strip() else " ", styles["code"]))
    inner = Table([[item] for item in items],
                  colWidths=[A4[0] - 4 * cm],
                  hAlign="LEFT")
    inner.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), C_CODE_BG),
        ("TOPPADDING",    (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("ROUNDEDCORNERS", [6]),
    ]))
    return inner

# ── 인용블록 생성 ─────────────────────────────────────────────────────
def make_quote_block(lines, styles):
    """> 인용문을 파란 사이드바 스타일 박스로 변환"""
    content = []
    for line in lines:
        line = line.lstrip("> ").rstrip()
        if not line:
            content.append(Spacer(1, 4))
        else:
            content.append(Paragraph(md_inline(line, styles["quote"]), styles["quote"]))

    # 왼쪽 파란 바 + 연한 배경
    inner = Table([[content]],
                  colWidths=[A4[0] - 4*cm - 0.3*cm])
    inner.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), C_QUOTE_BG),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
    ]))
    bar_tbl = Table(
        [[" ", inner]],
        colWidths=[0.3*cm, A4[0] - 4*cm - 0.3*cm]
    )
    bar_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (0, -1), C_QUOTE_BAR),
        ("TOPPADDING",    (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
    ]))
    return bar_tbl

# ── 이미지 삽입 ───────────────────────────────────────────────────────
def make_image(img_path, max_width, max_height=None):
    """이미지 파일을 비율 유지하며 삽입"""
    if not os.path.isfile(img_path):
        return None
    if max_height is None:
        max_height = max_width * 0.65
    try:
        from PIL import Image as PILImage
        with PILImage.open(img_path) as im:
            w, h = im.size
        ratio = min(max_width / w, max_height / h)
        return Image(img_path, width=w*ratio, height=h*ratio, hAlign="CENTER")
    except Exception:
        return Image(img_path, width=max_width, hAlign="CENTER")

# ── 헤더 / 푸터 ───────────────────────────────────────────────────────
def on_page(canvas, doc):
    canvas.saveState()
    # 헤더 라인
    canvas.setStrokeColor(C_ACCENT)
    canvas.setLineWidth(1.5)
    canvas.line(2*cm, A4[1] - 1.5*cm, A4[0] - 2*cm, A4[1] - 1.5*cm)
    # 헤더 텍스트
    canvas.setFont("MalgunBold", 8)
    canvas.setFillColor(C_NAVY)
    canvas.drawString(2*cm, A4[1] - 1.2*cm, "TruePick EDA 보고서")
    canvas.drawRightString(A4[0] - 2*cm, A4[1] - 1.2*cm, "데이터 기반 가전 소비 패턴 분석")
    # 푸터 라인
    canvas.setStrokeColor(C_HR)
    canvas.setLineWidth(0.5)
    canvas.line(2*cm, 1.2*cm, A4[0] - 2*cm, 1.2*cm)
    # 페이지 번호
    canvas.setFont("Malgun", 8)
    canvas.setFillColor(colors.HexColor("#64748b"))
    canvas.drawCentredString(A4[0]/2, 0.8*cm, f"— {doc.page} —")
    canvas.restoreState()

# ── 메인 파싱 및 PDF 빌드 ────────────────────────────────────────────
def parse_and_build(md_path, pdf_path, img_base_dir):
    styles = build_styles()
    story  = []
    max_img_w = A4[0] - 4*cm

    with open(md_path, encoding="utf-8") as f:
        lines = f.readlines()

    i = 0
    in_code  = False
    in_quote = False
    in_table = False
    code_lines  = []
    quote_lines = []
    table_lines = []

    def flush_code():
        if code_lines:
            story.append(Spacer(1, 4))
            story.append(make_code_block(code_lines, styles))
            story.append(Spacer(1, 8))
            code_lines.clear()

    def flush_quote():
        if quote_lines:
            story.append(Spacer(1, 4))
            story.append(make_quote_block(quote_lines, styles))
            story.append(Spacer(1, 8))
            quote_lines.clear()

    def flush_table():
        if table_lines:
            tbl = parse_table(table_lines, styles)
            if tbl:
                story.append(Spacer(1, 4))
                story.append(tbl)
                story.append(Spacer(1, 8))
            table_lines.clear()

    while i < len(lines):
        raw  = lines[i]
        line = raw.rstrip('\n')

        # ── 코드블록 시작/끝 ─────────────────────────────────────
        if line.startswith("```"):
            if not in_code:
                flush_quote()
                flush_table()
                in_code = True
                code_lines = []
            else:
                in_code = False
                flush_code()
            i += 1
            continue

        if in_code:
            code_lines.append(line)
            i += 1
            continue

        # ── 인용문 ───────────────────────────────────────────────
        if line.startswith(">"):
            flush_table()
            in_quote = True
            quote_lines.append(line)
            i += 1
            continue
        else:
            if in_quote:
                flush_quote()
                in_quote = False

        # ── 표 ───────────────────────────────────────────────────
        if line.startswith("|"):
            in_table = True
            table_lines.append(line)
            i += 1
            continue
        else:
            if in_table:
                flush_table()
                in_table = False

        # ── 수평선 ───────────────────────────────────────────────
        if re.match(r'^-{3,}$', line.strip()):
            story.append(Spacer(1, 4))
            story.append(HRFlowable(width="100%", thickness=0.7, color=C_HR))
            story.append(Spacer(1, 6))
            i += 1
            continue

        # ── 제목 ─────────────────────────────────────────────────
        h1 = re.match(r'^# (.+)$', line)
        if h1:
            # 표지 느낌: 배경 박스 + 중앙 정렬
            title_text = md_inline(h1.group(1), styles["title"])
            story.append(Spacer(1, 20))
            title_tbl = Table(
                [[Paragraph(title_text, styles["title"])]],
                colWidths=[max_img_w]
            )
            title_tbl.setStyle(TableStyle([
                ("BACKGROUND",    (0, 0), (-1, -1), C_NAVY),
                ("TOPPADDING",    (0, 0), (-1, -1), 14),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
                ("LEFTPADDING",   (0, 0), (-1, -1), 12),
                ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
                ("ROUNDEDCORNERS", [8]),
            ]))
            # 흰색 폰트로 오버라이드
            styles["title_white"] = ParagraphStyle(
                "title_white",
                parent=styles["title"],
                textColor=colors.white
            )
            story.append(Table(
                [[Paragraph(title_text.replace(C_NAVY.hexval(), "#ffffff"), styles["title_white"])]],
                colWidths=[max_img_w]
            ))
            story.append(Spacer(1, 16))
            i += 1
            continue

        h2 = re.match(r'^## (.+)$', line)
        if h2:
            text = md_inline(h2.group(1), styles["h2"])
            # 파란 언더라인 스타일
            story.append(Spacer(1, 8))
            story.append(Paragraph(text, styles["h2"]))
            story.append(HRFlowable(width="100%", thickness=1.5, color=C_ACCENT, spaceAfter=4))
            i += 1
            continue

        h3 = re.match(r'^### (.+)$', line)
        if h3:
            text = md_inline(h3.group(1), styles["h3"])
            story.append(Paragraph(text, styles["h3"]))
            i += 1
            continue

        # ── 이미지 ───────────────────────────────────────────────
        img_m = re.match(r'^!\[([^\]]*)\]\(([^)]+)\)$', line.strip())
        if img_m:
            alt_text = img_m.group(1)
            rel_path = img_m.group(2)
            # ../images/plotN.png → 절대 경로 변환
            abs_img  = os.path.normpath(os.path.join(img_base_dir, rel_path))
            img_flow = make_image(abs_img, max_img_w)
            if img_flow:
                story.append(Spacer(1, 6))
                story.append(img_flow)
                if alt_text:
                    story.append(Paragraph(f"[그림] {alt_text}", styles["caption"]))
                story.append(Spacer(1, 6))
            i += 1
            continue

        # ── 글머리 기호 ──────────────────────────────────────────
        bullet_m = re.match(r'^(\s*)[*\-] (.+)$', line)
        if bullet_m:
            indent = len(bullet_m.group(1))
            text   = md_inline(bullet_m.group(2), styles["bullet"])
            if indent >= 2:
                story.append(Paragraph(f"• {text}", styles["sub_bullet"]))
            else:
                story.append(Paragraph(f"• {text}", styles["bullet"]))
            i += 1
            continue

        # 번호 글머리
        num_m = re.match(r'^(\s*)\d+\. (.+)$', line)
        if num_m:
            num_part = re.match(r'^(\s*)(\d+)\. ', line)
            num  = num_part.group(2)
            text = md_inline(num_m.group(2), styles["bullet"])
            story.append(Paragraph(f"<b>{num}.</b> {text}", styles["bullet"]))
            i += 1
            continue

        # ── 빈 줄 ────────────────────────────────────────────────
        if line.strip() == "":
            story.append(Spacer(1, 4))
            i += 1
            continue

        # ── 일반 문단 ────────────────────────────────────────────
        text = md_inline(line.strip(), styles["body"])
        if text:
            story.append(Paragraph(text, styles["body"]))
        i += 1

    # 잔여 플러시
    flush_code()
    flush_quote()
    flush_table()

    # ── PDF 빌드 ──────────────────────────────────────────────────
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2.2*cm, bottomMargin=2*cm,
        title="TruePick EDA 보고서",
        author="Tashaive 팀",
        subject="데이터 기반 가전 소비 패턴 분석"
    )
    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    print(f"[완료] PDF 생성 완료: {pdf_path}")


if __name__ == "__main__":
    BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    md_path  = os.path.join(BASE, "report", "EDA_Report.md")
    pdf_path = os.path.join(BASE, "report", "EDA_Report.pdf")
    img_dir  = os.path.join(BASE, "report")   # md 파일 위치 기준

    parse_and_build(md_path, pdf_path, img_dir)
