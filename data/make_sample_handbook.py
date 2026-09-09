"""
Generates a SAMPLE Student Handbook PDF so the RAG pipeline can be built and
tested end-to-end. Replace data/handbook/Student_Handbook.pdf with the real
handbook you were given at the start of the year, then re-run ingestion.
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import os

OUT_DIR = "data/handbook"
os.makedirs(OUT_DIR, exist_ok=True)
OUT_PATH = os.path.join(OUT_DIR, "Student_Handbook.pdf")

styles = getSampleStyleSheet()
h1 = ParagraphStyle("h1", parent=styles["Heading1"], spaceAfter=12)
body = ParagraphStyle("body", parent=styles["BodyText"], spaceAfter=10, leading=16)

# (page_title, [paragraphs]) - one entry per page
pages = [
    ("Welcome & Introduction", [
        "Welcome to the Zaio Student Handbook. This document outlines the policies, "
        "procedures, and expectations for all students enrolled in Zaio bootcamps and "
        "qualifications. Please read this handbook carefully, as it forms part of your "
        "enrolment agreement.",
        "This handbook covers attendance, code of conduct, grading and assessment, "
        "graduation requirements, support services, and administrative procedures.",
    ]),
    ("Attendance Requirements", [
        "Students are required to maintain a minimum attendance rate of 80% across all "
        "live classes and scheduled sessions for the duration of their programme.",
        "Live classes are held twice per week, with a morning session and an evening "
        "session, so students can choose the time that best suits their schedule. "
        "If a student misses a live session, a recording is made available within 24 hours.",
        "Students who fall below the 80% attendance threshold in any given month will "
        "receive a written warning from their Student Success Coach. Two consecutive "
        "months below the threshold may result in academic probation.",
    ]),
    ("Code of Conduct", [
        "All students are expected to engage respectfully with instructors, mentors, and "
        "fellow students in class, on Discord, and in all Zaio-affiliated spaces.",
        "Harassment, discrimination, plagiarism, and academic dishonesty are strictly "
        "prohibited and may result in suspension or expulsion from the programme.",
        "Students must submit their own original work for all assessments. Collaboration "
        "on practice exercises is encouraged, but graded projects must reflect individual "
        "effort unless explicitly stated as a group project.",
    ]),
    ("Grading and Assessment", [
        "Each module concludes with a project-based assessment that is graded as "
        "Competent or Not Yet Competent, in line with the requirements of the relevant "
        "NQF-aligned qualification.",
        "Students must achieve a Competent grade on all module assessments in order to "
        "progress to the next module. Students who receive Not Yet Competent may resubmit "
        "their project once, with feedback from a mentor, within 14 days.",
        "Final grades for the qualification are determined by a portfolio of evidence "
        "comprising all completed module projects and a final capstone project.",
    ]),
    ("Graduation Requirements", [
        "To graduate from a Zaio bootcamp, students must: (1) complete all required "
        "modules with a Competent grade, (2) maintain the minimum 80% attendance "
        "requirement, (3) complete the final capstone project, and (4) settle all "
        "outstanding tuition fees.",
        "Students who complete an accredited pathway (for example the Occupational "
        "Certificate: Software Development) will also need to meet the external "
        "assessment requirements set by the relevant Quality Assurance body, such as "
        "MICT SETA.",
        "Graduating students are invited to Zaio's Virtual Graduation ceremony and "
        "receive a certificate of completion or accredited qualification, as applicable.",
    ]),
    ("Tutor Support and Student Success", [
        "Zaio provides 24/7 tutor support to help students who fall behind or get stuck "
        "on course material. Support can be accessed via the student Discord community "
        "or the in-platform help desk.",
        "Each student is assigned a Student Success Coach who checks in regularly, "
        "monitors attendance and progress, and helps students who are struggling to "
        "keep up with the course pace.",
    ]),
    ("Payments and Refunds", [
        "Students may pay for their bootcamp upfront, in installments, or via one of "
        "Zaio's financing partners. Full details of financing options are available on "
        "the Zaio website under Tuition & Financing.",
        "Refund requests must be submitted in writing within 7 days of enrolment, in "
        "accordance with Zaio's Refund Policy, which is published on the Zaio website.",
    ]),
    ("Code of Conduct Violations and Disciplinary Process", [
        "Any suspected violation of the Code of Conduct will be investigated by the "
        "Student Success team. Students will be given the opportunity to respond before "
        "any disciplinary action is taken.",
        "Disciplinary outcomes may range from a verbal warning to suspension or "
        "expulsion, depending on the severity and frequency of the violation.",
    ]),
    ("Contact Information", [
        "For general enquiries, students can contact hello@zaio.io or call the Zaio "
        "office. For urgent academic support, students should use the 24/7 tutor "
        "support channel on Discord.",
        "This handbook may be updated from time to time. Students will be notified of "
        "material changes via email and the student portal.",
    ]),
]

doc = SimpleDocTemplate(OUT_PATH, pagesize=A4,
                         leftMargin=2*cm, rightMargin=2*cm,
                         topMargin=2*cm, bottomMargin=2*cm)
story = []
story.append(Paragraph("Zaio Student Handbook (SAMPLE)", styles["Title"]))
story.append(Paragraph(
    "This is a placeholder handbook generated for development/testing purposes. "
    "Replace this file with the real Student Handbook PDF you were issued.",
    body))
story.append(PageBreak())

for i, (title, paras) in enumerate(pages, start=2):
    story.append(Paragraph(f"Page {i}: {title}", h1))
    for p in paras:
        story.append(Paragraph(p, body))
    story.append(Spacer(1, 12))
    if i != len(pages) + 1:
        story.append(PageBreak())

doc.build(story)
print(f"Sample handbook written to {OUT_PATH}")
