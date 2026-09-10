import json
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.enum.section import WD_SECTION, WD_ORIENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

doc = docx.Document()

# Page setup: Standard Thesis Margin (Left 4cm, Top 3cm, Right 3cm, Bottom 3cm)
for section in doc.sections:
    section.top_margin = Inches(1.18)    # ~3 cm
    section.bottom_margin = Inches(1.18) # ~3 cm
    section.left_margin = Inches(1.57)   # ~4 cm
    section.right_margin = Inches(1.18)  # ~3 cm

files = [
    ('OFF', 'prototype/garden-rampage/dataset/telemetry_session_2026-09-11_00-00-48.json'),
    ('FCM', 'prototype/garden-rampage/dataset/telemetry_session_2026-09-11_00-10-46.json'),
    ('GMM', 'prototype/garden-rampage/dataset/telemetry_session_2026-09-11_00-21-28.json')
]

keys = [
    'avg_hp_remaining_pct', 'total_kills', 'accuracy_pct', 'dash_frequency',
    'avg_time_per_wave_sec', 'damage_taken_total', 'near_death_events',
    'hits_taken_from_strawberry', 'hits_taken_from_jambu', 'avg_enemies_alive_simultaneously'
]

# Helper for cell shading
def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=60, bottom=60, left=100, right=100):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'''
        <w:tcMar {nsdecls("w")}>
            <w:top w:w="{top}" w:type="dxa"/>
            <w:bottom w:w="{bottom}" w:type="dxa"/>
            <w:left w:w="{left}" w:type="dxa"/>
            <w:right w:w="{right}" w:type="dxa"/>
        </w:tcMar>
    ''')
    tcPr.append(tcMar)

def set_table_borders(table):
    tblPr = table._tbl.tblPr
    borders = parse_xml(f'''
        <w:tblBorders {nsdecls("w")}>
            <w:top w:val="single" w:sz="6" w:space="0" w:color="333333"/>
            <w:bottom w:val="single" w:sz="6" w:space="0" w:color="333333"/>
            <w:insideH w:val="single" w:sz="4" w:space="0" w:color="E0E0E0"/>
            <w:insideV w:val="none"/>
            <w:left w:val="none"/>
            <w:right w:val="none"/>
        </w:tblBorders>
    ''')
    tblPr.append(borders)

# -----------------------------------------------------------------------------
# OPSI A: PORTRAIT (HEADER NOMOR 1 s.d. 10 - SANGAT RAPI, TIDAK AKAN PECAH)
# -----------------------------------------------------------------------------
title1 = doc.add_paragraph()
r1 = title1.add_run("OPSI A: FORMAT PORTRAIT (HEADER RINGKAS 1 s.d. 10)")
r1.font.name = "Times New Roman"
r1.font.size = Pt(12)
r1.font.bold = True

desc1 = doc.add_paragraph()
d1 = desc1.add_run("Format ini dirancang khusus agar muat di kertas Portrait A4 tanpa teks pecah/terlipat menjadi 1 digit. Header menggunakan nomor 1 s.d. 10 sesuai arahan dosen pembimbing.")
d1.font.name = "Times New Roman"
d1.font.size = Pt(10)
d1.font.italic = True

tbl_caption = doc.add_paragraph()
c1 = tbl_caption.add_run("Tabel Lampiran 2. Rekapitulasi Dataset Telemetri Pengujian 63 Wave")
c1.font.name = "Times New Roman"
c1.font.size = Pt(11)
c1.font.bold = True

# 12 columns: No, Skenario, Wave, 1..10
headers_portrait = ['No', 'Mode', 'Wave', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
widths_portrait = [Inches(0.40), Inches(0.50), Inches(0.45),
                   Inches(0.48), Inches(0.42), Inches(0.45), Inches(0.48),
                   Inches(0.48), Inches(0.42), Inches(0.40), Inches(0.38), Inches(0.38), Inches(0.48)]

t_a = doc.add_table(rows=1, cols=len(headers_portrait))
t_a.alignment = WD_TABLE_ALIGNMENT.CENTER
set_table_borders(t_a)

hdr_cells = t_a.rows[0].cells
for idx, title in enumerate(headers_portrait):
    hdr_cells[idx].text = title
    hdr_cells[idx].width = widths_portrait[idx]
    set_cell_background(hdr_cells[idx], "1F4E79")
    set_cell_margins(hdr_cells[idx], top=80, bottom=80, left=40, right=40)
    p = hdr_cells[idx].paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for r in p.runs:
        r.font.name = "Times New Roman"
        r.font.size = Pt(9)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)

row_num = 1
for label, path in files:
    with open(path) as f:
        data = json.load(f)
    for d in data:
        w = d['wave']
        row_cells = t_a.add_row().cells
        vals = [
            str(row_num),
            label,
            str(w),
            f"{d['avg_hp_remaining_pct']:.2f}",
            str(d['total_kills']),
            f"{d['accuracy_pct']:.2f}",
            f"{d['dash_frequency']:.1f}",
            f"{d['avg_time_per_wave_sec']:.1f}",
            str(d['damage_taken_total']),
            str(d['near_death_events']),
            str(d['hits_taken_from_strawberry']),
            str(d['hits_taken_from_jambu']),
            f"{d['avg_enemies_alive_simultaneously']:.1f}"
        ]
        for idx, val in enumerate(vals):
            row_cells[idx].text = val
            row_cells[idx].width = widths_portrait[idx]
            set_cell_margins(row_cells[idx], top=40, bottom=40, left=40, right=40)
            p = row_cells[idx].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for r in p.runs:
                r.font.name = "Times New Roman"
                r.font.size = Pt(8.5)
                if idx == 1:
                    if label == 'OFF':
                        r.font.color.rgb = RGBColor(180, 0, 0)
                        r.font.bold = True
                    elif label == 'FCM':
                        r.font.color.rgb = RGBColor(0, 50, 150)
                        r.font.bold = True
                    else:
                        r.font.color.rgb = RGBColor(200, 100, 0)
                        r.font.bold = True
        row_num += 1

# Add Legend below table
leg = doc.add_paragraph()
leg_run = leg.add_run(
    "Keterangan Kolom: 1: avg_hp_remaining_pct, 2: total_kills, 3: accuracy_pct, 4: dash_frequency, "
    "5: avg_time_per_wave_sec, 6: damage_taken_total, 7: near_death_events, 8: hits_taken_from_strawberry, "
    "9: hits_taken_from_jambu, 10: avg_enemies_alive_simultaneously."
)
leg_run.font.name = "Times New Roman"
leg_run.font.size = Pt(8.5)
leg_run.font.italic = True

# -----------------------------------------------------------------------------
# OPSI B: LANDSCAPE SECTION (NAMA KOLOM LENGKAP & SANGAT LEGA)
# -----------------------------------------------------------------------------
doc.add_page_break()
new_sec = doc.add_section(WD_SECTION.NEW_PAGE)
new_sec.orientation = WD_ORIENT.LANDSCAPE
new_sec.page_width = Inches(11.69)  # A4 Landscape width
new_sec.page_height = Inches(8.27)  # A4 Landscape height
new_sec.top_margin = Inches(1.0)
new_sec.bottom_margin = Inches(1.0)
new_sec.left_margin = Inches(1.18)
new_sec.right_margin = Inches(1.18)

title2 = doc.add_paragraph()
r2 = title2.add_run("OPSI B: FORMAT LANDSCAPE (NAMA HEADER LENGKAP & LEGA)")
r2.font.name = "Times New Roman"
r2.font.size = Pt(13)
r2.font.bold = True

desc2 = doc.add_paragraph()
d2 = desc2.add_run("Standar penulisan lampiran data telemetri pada skripsi. Menggunakan halaman Landscape sehingga semua angka dan nama metrik tertata luas tanpa berhimpitan.")
d2.font.name = "Times New Roman"
d2.font.size = Pt(10)
d2.font.italic = True

headers_landscape = [
    'No', 'Mode', 'Wave', 'HP Remaining (%)', 'Kills', 'Accuracy (%)',
    'Dash Freq (/min)', 'Wave Time (s)', 'Damage Taken', 'Near Death',
    'Hits Strawberry', 'Hits Jambu', 'Enemies Alive'
]

t_b = doc.add_table(rows=1, cols=len(headers_landscape))
t_b.alignment = WD_TABLE_ALIGNMENT.CENTER
set_table_borders(t_b)

hdr_cells_b = t_b.rows[0].cells
for idx, title in enumerate(headers_landscape):
    hdr_cells_b[idx].text = title
    set_cell_background(hdr_cells_b[idx], "1F4E79")
    set_cell_margins(hdr_cells_b[idx], top=80, bottom=80, left=60, right=60)
    p = hdr_cells_b[idx].paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for r in p.runs:
        r.font.name = "Times New Roman"
        r.font.size = Pt(9.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)

row_num = 1
for label, path in files:
    with open(path) as f:
        data = json.load(f)
    for d in data:
        w = d['wave']
        row_cells = t_b.add_row().cells
        vals = [
            str(row_num),
            label,
            str(w),
            f"{d['avg_hp_remaining_pct'] * 100:.1f}%",
            str(d['total_kills']),
            f"{d['accuracy_pct'] * 100:.1f}%",
            f"{d['dash_frequency']:.2f}",
            f"{d['avg_time_per_wave_sec']:.2f}",
            str(d['damage_taken_total']),
            str(d['near_death_events']),
            str(d['hits_taken_from_strawberry']),
            str(d['hits_taken_from_jambu']),
            f"{d['avg_enemies_alive_simultaneously']:.2f}"
        ]
        for idx, val in enumerate(vals):
            row_cells[idx].text = val
            set_cell_margins(row_cells[idx], top=50, bottom=50, left=60, right=60)
            p = row_cells[idx].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for r in p.runs:
                r.font.name = "Times New Roman"
                r.font.size = Pt(9)
                if idx == 1:
                    if label == 'OFF':
                        r.font.color.rgb = RGBColor(180, 0, 0)
                        r.font.bold = True
                    elif label == 'FCM':
                        r.font.color.rgb = RGBColor(0, 50, 150)
                        r.font.bold = True
                    else:
                        r.font.color.rgb = RGBColor(200, 100, 0)
                        r.font.bold = True
        row_num += 1

out_docx = "D:/Colleges/TA/dda_fcm_gmm/TABEL_LAMPIRAN_SIAP_PASTE.docx"
doc.save(out_docx)
print(f"[SUCCESS] File Word siap pakai telah dibuat di: {out_docx}")
