import csv
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

def process_csv(input_csv, output_docx):
    # 读取CSV数据并检查重复项
    entries = {}
    duplicates = []

    with open(input_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row['Title'].strip(), row['Abstract'].strip())
            if key in entries:
                duplicates.append(key[0])
                continue
            entries[key] = row

    # 创建Word文档
    doc = Document()
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(12)

    # 添加标题
    para = doc.add_paragraph()
    para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    run = para.add_run('IEEE上关于dysarthria论文题目与摘要汇总')
    run.bold = True
    run.font.size = Pt(14)
    doc.add_paragraph()

    # 添加条目
    for (title, abstract), data in entries.items():
        # 添加题目
        title_para = doc.add_paragraph()
        title_para.paragraph_format.space_after = Pt(6)
        run = title_para.add_run(title)
        run.bold = True

        # 添加摘要
        abstract_para = doc.add_paragraph(abstract)
        abstract_para.paragraph_format.space_after = Pt(12)
        abstract_para.paragraph_format.line_spacing = 1.5

    # 保存文档
    doc.save(output_docx)

    # 输出重复信息
    if duplicates:
        print(f'发现 {len(duplicates)} 条重复条目:')
        for dup in duplicates:
            print(f'- {dup}')
    else:
        print('未发现重复条目')

# 使用示例
process_csv('IEEE_paper_metadata.csv', 'Papers_Summary.docx')