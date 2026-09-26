"""Build the project report PDF from the saved analysis metrics.

Edit the student/course constants below, then run:
    python report/build_report.py
"""

from __future__ import annotations

import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


PROJECT_DIR = Path(__file__).resolve().parents[1]
RESULTS_PATH = PROJECT_DIR / "outputs" / "results.json"
OUTPUT_PATH = Path(__file__).resolve().parent / "Project_Report.pdf"

# Replace these before submission.
STUDENT_NAME = "[Your Name]"
COURSE_BATCH = "[Course / Batch]"
INSTITUTION = "[Institution]"

NAVY = colors.HexColor("#14304A")
BLUE = colors.HexColor("#247BA0")
PALE_BLUE = colors.HexColor("#EAF3F8")
INK = colors.HexColor("#24323D")
MUTED = colors.HexColor("#61717D")
GRID = colors.HexColor("#D7E0E6")
WHITE = colors.white

ABSTRACT = (
    "This project builds a beginner-friendly classifier to flag possible academic risk in the "
    "UCI Student Performance mathematics dataset. The dataset contains 395 records from two "
    "Portuguese secondary schools. The target is whether final grade G3 is below 10 out of 20. "
    "Only study-habit and support variables are used; G1 and G2 are excluded because they are "
    "earlier grades closely related to the target and would make evaluation less useful for early "
    "support. A fixed stratified 80/20 split compares a class-balanced logistic regression model "
    "with a majority-class baseline. On the held-out 79 records, the logistic model achieves "
    "0.646 accuracy and 0.599 balanced accuracy, with 0.462 recall for at-risk students. The "
    "majority baseline has 0.671 accuracy but zero recall for the at-risk class, showing why "
    "accuracy alone is misleading. This small observational exercise demonstrates preprocessing, "
    "logistic regression, holdout evaluation, and class-aware metrics. It does not establish that "
    "any feature causes grades or support decisions about individual students."
)


def load_results() -> dict:
    if not RESULTS_PATH.exists():
        raise FileNotFoundError(
            f"Metrics not found at {RESULTS_PATH}. Run student_grade_predictor.py first."
        )
    return json.loads(RESULTS_PATH.read_text(encoding="utf-8"))


def make_styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "ProjectTitle", parent=base["Title"], fontName="Helvetica-Bold",
            fontSize=24, leading=29, textColor=NAVY, alignment=TA_LEFT, spaceAfter=7
        ),
        "subtitle": ParagraphStyle(
            "ProjectSubtitle", parent=base["Normal"], fontName="Helvetica",
            fontSize=11, leading=15, textColor=MUTED, spaceAfter=14
        ),
        "section": ParagraphStyle(
            "Section", parent=base["Heading2"], fontName="Helvetica-Bold",
            fontSize=13, leading=17, textColor=BLUE, spaceBefore=8, spaceAfter=6,
            keepWithNext=True
        ),
        "body": ParagraphStyle(
            "Body", parent=base["BodyText"], fontName="Helvetica",
            fontSize=9.2, leading=13.2, textColor=INK, spaceAfter=6
        ),
        "small": ParagraphStyle(
            "Small", parent=base["BodyText"], fontName="Helvetica",
            fontSize=8.2, leading=11, textColor=INK, spaceAfter=3
        ),
        "abstract": ParagraphStyle(
            "Abstract", parent=base["BodyText"], fontName="Helvetica",
            fontSize=9.1, leading=13.4, textColor=INK
        ),
        "bullet": ParagraphStyle(
            "Bullet", parent=base["BodyText"], fontName="Helvetica",
            fontSize=9.1, leading=12.7, leftIndent=14, firstLineIndent=-8,
            bulletIndent=2, textColor=INK, spaceAfter=4
        ),
        "table_head": ParagraphStyle(
            "TableHead", parent=base["Normal"], fontName="Helvetica-Bold",
            fontSize=8, leading=10, textColor=WHITE
        ),
        "table": ParagraphStyle(
            "TableCell", parent=base["Normal"], fontName="Helvetica",
            fontSize=8, leading=10, textColor=INK
        ),
        "caption": ParagraphStyle(
            "Caption", parent=base["Normal"], fontName="Helvetica-Oblique",
            fontSize=7.8, leading=10, textColor=MUTED, spaceBefore=3, spaceAfter=5
        ),
    }


def para(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(text, style)


def bullet(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(f"&#8226;&nbsp; {text}", style)


def section(title: str, styles: dict) -> Paragraph:
    return para(title, styles["section"])


def header_footer(canvas, doc):
    canvas.saveState()
    page_width, page_height = letter
    canvas.setFillColor(NAVY)
    canvas.rect(0, page_height - 10, page_width, 10, fill=1, stroke=0)
    canvas.setStrokeColor(GRID)
    canvas.setLineWidth(0.5)
    canvas.line(doc.leftMargin, 34, page_width - doc.rightMargin, 34)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(doc.leftMargin, 21, "Student Grade Predictor | Minor Project")
    canvas.drawRightString(page_width - doc.rightMargin, 21, f"Page {doc.page}")
    canvas.restoreState()


def make_report(results: dict) -> None:
    styles = make_styles()
    page_width, page_height = letter
    doc = BaseDocTemplate(
        str(OUTPUT_PATH),
        pagesize=letter,
        leftMargin=0.70 * inch,
        rightMargin=0.70 * inch,
        topMargin=0.52 * inch,
        bottomMargin=0.62 * inch,
        title="Student Grade Predictor: Early Support Risk Classification",
        author=STUDENT_NAME,
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, page_width - doc.leftMargin - doc.rightMargin,
                  page_height - doc.topMargin - doc.bottomMargin, id="main")
    doc.addPageTemplates([PageTemplate(id="standard", frames=[frame], onPage=header_footer)])
    story = []

    story.append(Spacer(1, 14))
    story.append(para("MINOR PROJECT | MACHINE LEARNING", styles["small"]))
    story.append(Spacer(1, 7))
    story.append(para("Student Grade Predictor:<br/>Early Support Risk Classification", styles["title"]))
    story.append(para("A beginner classification study using study habits and support indicators", styles["subtitle"]))

    info_rows = [
        [para("PREPARED BY", styles["small"]), para("COURSE / BATCH", styles["small"]), para("INSTITUTION", styles["small"])],
        [para(STUDENT_NAME, styles["body"]), para(COURSE_BATCH, styles["body"]), para(INSTITUTION, styles["body"])],
    ]
    info = Table(info_rows, colWidths=[2.08 * inch, 2.08 * inch, 2.08 * inch], hAlign="LEFT")
    info.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PALE_BLUE),
        ("BOX", (0, 0), (-1, -1), 0.6, GRID),
        ("INNERGRID", (0, 0), (-1, -1), 0.4, GRID),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(info)
    story.append(Spacer(1, 12))
    story.append(section("Abstract", styles))
    abstract_box = Table([[para(ABSTRACT, styles["abstract"])]], colWidths=[6.24 * inch])
    abstract_box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F5F9FB")),
        ("BOX", (0, 0), (-1, -1), 0.8, BLUE),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]))
    story.append(abstract_box)

    story.append(section("1. Introduction and Problem Statement", styles))
    story.append(para(
        "Educational support is most useful when learners who may need help can be noticed early. "
        "This project explores whether a simple machine-learning classifier can identify records "
        "whose final mathematics grade is below the dataset's passing threshold using information "
        "about study habits, attendance, and available support.", styles["body"]
    ))
    story.append(para(
        "The task is binary classification: given selected pre-final-grade attributes, predict "
        "whether G3 is below 10 on a 0-20 scale. The output is a statistical estimate from a small "
        "historical dataset; it is not a judgement about a real learner.", styles["body"]
    ))
    story.append(section("2. Aim and Objectives", styles))
    for text in [
        "Prepare a public educational dataset for a reproducible classification exercise.",
        "Train a logistic regression model without using G1 or G2, which are closely related to G3.",
        "Compare it with a majority-class baseline using metrics that show performance on the at-risk class.",
    ]:
        story.append(bullet(text, styles["bullet"]))

    story.append(PageBreak())
    story.append(section("3. Dataset and Features", styles))
    story.append(para(
        "The UCI Student Performance dataset was collected from two Portuguese secondary schools. "
        "This project uses the mathematics file, which has 395 records. It includes school, family, "
        "social, and academic attributes. The target is derived as at risk/fail when G3 < 10; 130 "
        "records meet this definition and 265 do not.", styles["body"]
    ))
    story.append(para(
        "The model uses study time, past failures, school and family support, paid extra classes, "
        "activities, plans for higher education, internet access, absences, travel time, free time, "
        "going out, weekday and weekend alcohol-use indicators, and health rating. Demographic "
        "columns are not used. G1, G2, and G3 are excluded as inputs; G3 is used only to create the "
        "target label.", styles["body"]
    ))

    story.append(section("4. Methodology", styles))
    for text in [
        "A stratified 80/20 train/test split is used with random seed 42 (316 training rows and 79 test rows).",
        "Categorical indicators are one-hot encoded. Features are standardized using training-set statistics only.",
        "An L2-regularized logistic regression model is trained by gradient descent with class-balanced weights.",
        "The majority-class baseline always predicts the more common training label. At-risk/fail is the positive class.",
        "Evaluation reports accuracy, balanced accuracy, precision, recall, F1, and a confusion matrix.",
    ]:
        story.append(bullet(text, styles["bullet"]))

    story.append(section("5. Results", styles))
    baseline = results["baseline_metrics"]
    model = results["model_metrics"]
    result_data = [
        [para("Model", styles["table_head"]), para("Accuracy", styles["table_head"]),
         para("Balanced acc.", styles["table_head"]), para("At-risk precision", styles["table_head"]),
         para("At-risk recall", styles["table_head"]), para("At-risk F1", styles["table_head"])],
        [para("Majority baseline", styles["table"]), f"{baseline['accuracy']:.3f}",
         f"{baseline['balanced_accuracy']:.3f}", f"{baseline['precision_at_risk']:.3f}",
         f"{baseline['recall_at_risk']:.3f}", f"{baseline['f1_at_risk']:.3f}"],
        [para("Logistic regression", styles["table"]), f"{model['accuracy']:.3f}",
         f"{model['balanced_accuracy']:.3f}", f"{model['precision_at_risk']:.3f}",
         f"{model['recall_at_risk']:.3f}", f"{model['f1_at_risk']:.3f}"],
    ]
    result_table = Table(result_data, colWidths=[1.34 * inch, 0.72 * inch, 0.88 * inch, 1.12 * inch, 0.98 * inch, 0.68 * inch], repeatRows=1)
    result_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F5F9FB")),
        ("GRID", (0, 0), (-1, -1), 0.45, GRID),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(result_table)
    story.append(para("Table 1. Holdout metrics on 79 records; values are rounded to three decimal places.", styles["caption"]))
    cm = model["confusion_matrix"]
    cm_data = [
        [para("Actual \\ Predicted", styles["table_head"]), para("Pass / not at risk", styles["table_head"]), para("At risk / fail", styles["table_head"])],
        [para("Pass / not at risk", styles["table"]), str(cm["true_negative"]), str(cm["false_positive"])],
        [para("At risk / fail", styles["table"]), str(cm["false_negative"]), str(cm["true_positive"])],
    ]
    cm_table = Table(cm_data, colWidths=[2.30 * inch, 1.95 * inch, 1.95 * inch], hAlign="LEFT")
    cm_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BLUE),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F5F9FB")),
        ("GRID", (0, 0), (-1, -1), 0.45, GRID),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(Spacer(1, 4))
    story.append(cm_table)
    story.append(para("Table 2. Logistic-regression confusion matrix; at-risk/fail is the positive class.", styles["caption"]))
    story.append(para(
        "The majority baseline has higher accuracy (0.671) because passing is the more common class, "
        "but it misses all 26 at-risk test records. The logistic model detects 12 of 26 at-risk records "
        "and correctly identifies 39 of 53 pass records. Its recall is 0.462, with 14 false alarms and "
        "14 missed at-risk records. This illustrates why accuracy alone does not describe a model's "
        "usefulness for a less common class.", styles["body"]
    ))

    story.append(PageBreak())
    story.append(section("6. Discussion", styles))
    story.append(para(
        "On this single holdout split, the class-balanced logistic model improves balanced accuracy "
        "over the majority baseline (0.599 compared with 0.500) and finds some at-risk records. Its "
        "accuracy is lower than the baseline, and its recall of 0.462 means it misses more than half "
        "of the at-risk cases in this test set. That trade-off is visible in the confusion matrix and "
        "should be discussed instead of reporting accuracy alone.", styles["body"]
    ))
    top = results["largest_standardized_coefficients"][:3]
    top_names = ", ".join(item["feature"] for item in top)
    story.append(para(
        f"In this fitted model, the largest coefficient magnitudes include {top_names}. These are "
        "associations learned by the classifier after the chosen preprocessing; they do not show "
        "that changing one of these features would cause a grade outcome.", styles["body"]
    ))

    story.append(section("7. Limitations and Responsible Use", styles))
    for text in [
        "The data come from two schools in Portugal and may not represent other schools, countries, or current learners.",
        "There are only 395 mathematics records, and the report uses one train/test split. A different split may produce different metrics.",
        "The target threshold and model are simplifications; reported probabilities or labels are not validated student assessments.",
        "The data are observational. Correlation and model coefficients do not establish causes or fairness across groups.",
        "The project is for learning only. It must not be used to label, rank, penalize, or deny support to individual students.",
    ]:
        story.append(bullet(text, styles["bullet"]))

    story.append(section("8. Conclusion", styles))
    story.append(para(
        "This project implements an end-to-end beginner classification workflow using a public student "
        "performance dataset. It defines a transparent pass/fail target, excludes earlier grade columns, "
        "fits logistic regression, and compares the result with a baseline using metrics for the at-risk "
        "class. The test results are modest and show that a simple model can miss many cases. A useful "
        "next step would be repeated stratified cross-validation and careful review of whether the "
        "features and evaluation are appropriate for the intended learning question.", styles["body"]
    ))

    story.append(section("References and Reproducibility", styles))
    story.append(para(
        "Cortez, P. (2008). <i>Student Performance</i> [Dataset]. UCI Machine Learning Repository. "
        "<link href='https://doi.org/10.24432/C5TG7T' color='#247BA0'>https://doi.org/10.24432/C5TG7T</link>. "
        "Dataset license: Creative Commons Attribution 4.0 (CC BY 4.0).",
        styles["small"]
    ))
    story.append(para(
        "The analysis is reproducible from student_grade_predictor.py with random seed 42. "
        "Source dataset notes are included in data/uci-dataset-notes.txt.", styles["small"]
    ))
    story.append(Spacer(1, 8))
    note = Table([[para(
        "Submission note: Replace the three bracketed student/course fields in report/build_report.py "
        "and rebuild this PDF before uploading it.", styles["small"]
    )]], colWidths=[6.24 * inch])
    note.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PALE_BLUE),
        ("BOX", (0, 0), (-1, -1), 0.5, GRID),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(note)

    doc.build(story)
    print(f"Created {OUTPUT_PATH}")


if __name__ == "__main__":
    make_report(load_results())
