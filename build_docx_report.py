"""Create a two-page Word report for the Student Grade Predictor project."""

from __future__ import annotations

import json
from pathlib import Path

from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


PROJECT_DIR = Path(__file__).resolve().parents[1]
RESULTS_PATH = PROJECT_DIR / "outputs" / "results.json"
OUTPUT_PATH = Path(__file__).resolve().parent / "Project_Report.docx"

AUTHOR = "Shambhawi Priya"
PROGRAM = "Artificial Intelligence InternsElite"
BATCH = "August 2026"
TITLE = "Student Grade Predictor: Early Support Risk Classification"


def set_cell_shading(cell, fill: str) -> None:
    properties = cell._tc.get_or_add_tcPr()
    shading = OxmlElement("w:shd")
    shading.set(qn("w:fill"), fill)
    properties.append(shading)


def set_cell_margins(cell, top=80, start=100, bottom=80, end=100) -> None:
    properties = cell._tc.get_or_add_tcPr()
    margins = OxmlElement("w:tcMar")
    for side, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = OxmlElement(f"w:{side}")
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")
        margins.append(node)
    properties.append(margins)


def set_table_borders(table, color="B7BEC5", size="6") -> None:
    tbl_pr = table._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        element = OxmlElement(f"w:{edge}")
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), size)
        element.set(qn("w:space"), "0")
        element.set(qn("w:color"), color)
        borders.append(element)
    tbl_pr.append(borders)


def set_run_font(run, name="Arial", size=10.5, bold=None, color="000000") -> None:
    run.font.name = name
    run._element.get_or_add_rPr().rFonts.set(qn("w:ascii"), name)
    run._element.get_or_add_rPr().rFonts.set(qn("w:hAnsi"), name)
    run.font.size = Pt(size)
    run.font.color.rgb = RGBColor.from_string(color)
    if bold is not None:
        run.bold = bold


def add_paragraph(doc, text="", *, bold=False, size=10.5, align=None,
                  first_indent=0.35, before=0, after=5, keep=False):
    paragraph = doc.add_paragraph()
    paragraph.paragraph_format.space_before = Pt(before)
    paragraph.paragraph_format.space_after = Pt(after)
    paragraph.paragraph_format.line_spacing = 1.08
    if first_indent:
        paragraph.paragraph_format.first_line_indent = Inches(first_indent)
    if align is not None:
        paragraph.alignment = align
    if keep:
        paragraph.paragraph_format.keep_with_next = True
    run = paragraph.add_run(text)
    set_run_font(run, size=size, bold=bold)
    return paragraph


def add_heading(doc, text):
    return add_paragraph(doc, text, bold=True, size=11.5, first_indent=0,
                         before=5, after=3, keep=True)


def add_code_box(doc, text):
    table = doc.add_table(rows=1, cols=1)
    table.autofit = False
    table.columns[0].width = Inches(6.35)
    cell = table.cell(0, 0)
    cell.width = Inches(6.35)
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    set_cell_shading(cell, "F1F2F3")
    set_cell_margins(cell, top=100, start=140, bottom=100, end=140)
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.0
    run = p.add_run(text)
    set_run_font(run, name="Consolas", size=8.4, color="29343D")
    return table


def make_report(results: dict) -> None:
    doc = Document()
    section = doc.sections[0]
    section.page_width = Inches(8.5)
    section.page_height = Inches(11)
    section.top_margin = Inches(0.75)
    section.bottom_margin = Inches(0.72)
    section.left_margin = Inches(0.95)
    section.right_margin = Inches(0.95)

    normal = doc.styles["Normal"]
    normal.font.name = "Arial"
    normal._element.rPr.rFonts.set(qn("w:ascii"), "Arial")
    normal._element.rPr.rFonts.set(qn("w:hAnsi"), "Arial")
    normal.font.size = Pt(10.5)
    normal.paragraph_format.space_after = Pt(5)
    normal.paragraph_format.line_spacing = 1.08

    properties = doc.core_properties
    properties.title = TITLE
    properties.author = AUTHOR
    properties.subject = "Minor project report"
    properties.keywords = "student performance, logistic regression, minor project"

    # Page 1: retain the sample's identity block and report section order.
    for label, value in (("Name-", AUTHOR), ("", PROGRAM), ("Batch-", BATCH)):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.0
        if label:
            set_run_font(p.add_run(label), size=10.5, bold=True)
        set_run_font(p.add_run(value), size=10.5)

    add_paragraph(doc, TITLE, bold=True, size=14, align=WD_ALIGN_PARAGRAPH.CENTER,
                  first_indent=0, before=4, after=11, keep=True)

    add_heading(doc, "Introduction")
    add_paragraph(doc,
        "Predicting possible academic risk before final results may help educators direct attention "
        "toward students who could benefit from additional support. This project explores whether "
        "selected study-habit, attendance, and school-support information can identify students who "
        "did not reach the passing threshold in mathematics. The analysis uses 395 records from the "
        "UCI Student Performance dataset, collected from two Portuguese secondary schools.")
    add_paragraph(doc,
        "The purpose is to demonstrate a reproducible beginner machine-learning workflow. The model "
        "is an educational exercise and is not intended to assess or label individual students.")

    add_heading(doc, "Problem Statement")
    add_paragraph(doc,
        "The project classifies final mathematics grade G3 as at-risk/fail when it is below 10 on the "
        "dataset's 0-to-20 scale, and pass otherwise. The model uses study time, prior failures, "
        "school and family support, paid classes, activities, plans for higher education, internet "
        "access, absences, travel time, free time, going out, weekday and weekend alcohol-use "
        "indicators, and health rating.")
    add_paragraph(doc,
        "G1 and G2 are excluded from the inputs because earlier-period grades are strongly related "
        "to G3 and could make prediction less useful as an early-support exercise. G3 is used only "
        "to define the target class. The dataset contains 130 at-risk/fail records and 265 pass records.")

    add_heading(doc, "Results and Discussion")
    add_paragraph(doc,
        "A stratified 80/20 split with random seed 42 produced 316 training records and 79 test "
        "records. Categorical inputs were one-hot encoded, and feature scaling was fitted on the "
        "training split only. A class-balanced, L2-regularized logistic regression model trained "
        "with gradient descent was compared with a majority-class baseline. The holdout results "
        "and confusion matrix are shown on the next page.", after=0)

    # Page 2: visual results, a short code excerpt, conclusion, and source.
    doc.add_page_break()
    add_heading(doc, "Confusion Matrix")
    add_paragraph(doc,
        "The positive class is at-risk/fail. The matrix shows the logistic regression results on "
        "the 79-record test split.", first_indent=0, after=4)

    cm = results["model_metrics"]["confusion_matrix"]
    matrix = doc.add_table(rows=3, cols=3)
    matrix.autofit = False
    widths = [Inches(2.35), Inches(1.85), Inches(1.85)]
    for i, width in enumerate(widths):
        for cell in matrix.columns[i].cells:
            cell.width = width
    labels = [
        ["Actual / Predicted", "Pass / not at risk", "At risk / fail"],
        ["Pass / not at risk", str(cm["true_negative"]), str(cm["false_positive"])],
        ["At risk / fail", str(cm["false_negative"]), str(cm["true_positive"])],
    ]
    for row_index, row in enumerate(matrix.rows):
        for col_index, cell in enumerate(row.cells):
            cell.text = labels[row_index][col_index]
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            set_cell_margins(cell, top=90, start=90, bottom=90, end=90)
            for p in cell.paragraphs:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT if col_index == 0 else WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.space_after = Pt(0)
                for run in p.runs:
                    set_run_font(run, size=9, bold=(row_index == 0 or col_index == 0),
                                 color="FFFFFF" if row_index == 0 else "222222")
            if row_index == 0:
                set_cell_shading(cell, "2B3440")
            elif row_index == col_index:
                set_cell_shading(cell, "F0D8C7")
            else:
                set_cell_shading(cell, "55264F")
                for p in cell.paragraphs:
                    for run in p.runs:
                        run.font.color.rgb = RGBColor(255, 255, 255)
    set_table_borders(matrix, color="FFFFFF", size="10")

    add_paragraph(doc,
        "True negatives = 39; false positives = 14; false negatives = 14; true positives = 12.",
        size=9, first_indent=0, before=3, after=6)

    add_heading(doc, "Model Evaluation Code")
    add_code_box(doc,
        "weights, bias = fit_logistic_regression(X_train, y_train)\n"
        "probability = sigmoid(X_test @ weights + bias)\n"
        "prediction = (probability >= 0.5).astype(int)")

    baseline = results["baseline_metrics"]
    model = results["model_metrics"]
    summary = (
        f"Majority baseline: accuracy {baseline['accuracy']:.3f}; at-risk recall "
        f"{baseline['recall_at_risk']:.3f}; balanced accuracy {baseline['balanced_accuracy']:.3f}\n"
        f"Logistic regression: accuracy {model['accuracy']:.3f}; at-risk recall "
        f"{model['recall_at_risk']:.3f}; balanced accuracy {model['balanced_accuracy']:.3f}"
    )
    add_code_box(doc, summary)
    add_paragraph(doc,
        "The baseline has higher accuracy because pass is the more common class, but it misses all "
        "at-risk test records. Logistic regression finds 12 of 26 at-risk records and raises 14 false "
        "alarms. Its 0.462 recall is limited, so accuracy alone would give an incomplete view of "
        "the result. This is one small holdout split; scores may change with a different split.",
        first_indent=0, before=5, after=6)

    add_heading(doc, "Conclusion")
    add_paragraph(doc,
        "This project demonstrates data preparation, binary classification, and evaluation against "
        "a simple baseline. The model improves balanced accuracy over the baseline (0.599 versus "
        "0.500), but it misses more than half of the at-risk records in the test split. The result "
        "is modest and does not establish that any input causes a grade outcome. The model should "
        "not be used to label, rank, penalize, or make decisions about individual students.")

    add_heading(doc, "Reference")
    add_paragraph(doc,
        "Cortez, P. (2008). Student Performance [Dataset]. UCI Machine Learning Repository. "
        "https://doi.org/10.24432/C5TG7T. Dataset license: Creative Commons Attribution 4.0 (CC BY 4.0).",
        size=9, first_indent=0, after=0)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUTPUT_PATH)
    print(f"Created {OUTPUT_PATH}")


if __name__ == "__main__":
    if not RESULTS_PATH.exists():
        raise FileNotFoundError(f"Run the project first; expected metrics at {RESULTS_PATH}")
    make_report(json.loads(RESULTS_PATH.read_text(encoding="utf-8")))
