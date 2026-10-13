from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

NAVY = RGBColor(12, 55, 98)
BLUE = RGBColor(45, 120, 180)
LIGHT = RGBColor(240, 245, 250)
ACCENT = RGBColor(86, 168, 233)
TEXT = RGBColor(26, 32, 44)
WHITE = RGBColor(255, 255, 255)


def add_bg(slide, color=WHITE):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()


def add_title(slide, text, x=0.8, y=0.35, w=12.0, h=0.6, color=TEXT):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    p = box.text_frame.paragraphs[0]
    p.text = text
    run = p.runs[0]
    run.font.size = Pt(28)
    run.font.bold = True
    run.font.color.rgb = color
    return box


def add_bullets(slide, items, x, y, w, h, size=20, color=TEXT):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.paragraphs.add()
        p.text = item
        p.level = 0
        p.bullet = True
        p.space_after = Pt(8)
        for run in p.runs:
            run.font.size = Pt(size)
            run.font.color.rgb = color


def add_paragraph(slide, text, x, y, w, h, size=18, color=TEXT, bold=False, align=PP_ALIGN.LEFT):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    p = box.text_frame.paragraphs[0]
    p.text = text
    p.alignment = align
    run = p.runs[0]
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color

# Slide 1 - Title
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, NAVY)
shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.2), Inches(5.9), Inches(2.2))
shape.fill.solid(); shape.fill.fore_color.rgb = BLUE; shape.line.fill.background()
add_paragraph(slide, 'DSA Practice', 1.15, 1.5, 5.0, 0.8, size=30, color=WHITE, bold=True)
add_paragraph(slide, 'Randomized question selector for coding practice', 1.15, 2.2, 6.0, 0.7, size=18, color=WHITE)
card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.0), Inches(1.8), Inches(3.8), Inches(2.3))
card.fill.solid(); card.fill.fore_color.rgb = WHITE; card.line.color.rgb = WHITE
card.line.width = 1
frame = card.text_frame
frame.word_wrap = True
for idx, line in enumerate(['Project Type: Java Console App', 'Purpose: Pick 5 unique DSA questions', 'Range: 101 to 140']):
    p = frame.paragraphs[0] if idx == 0 else frame.paragraphs.add()
    p.text = line
    p.alignment = PP_ALIGN.LEFT
    run = p.runs[0]
    run.font.size = Pt(16)
    run.font.color.rgb = NAVY

# Slide 2 - Overview
slide = prs.slides.add_slide(prs.slide_layouts[6]); add_bg(slide, LIGHT)
add_title(slide, 'Project Overview', color=NAVY)
left = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.1), Inches(5.7), Inches(4.4))
left.fill.solid(); left.fill.fore_color.rgb = WHITE; left.line.color.rgb = BLUE; left.line.width = 1.2
left_tf = left.text_frame
for idx, item in enumerate([
    'Generates a list of DSA question IDs from 101 to 140',
    'Shuffles the list with a fixed random seed',
    'Selects only 5 unique values',
    'Displays the final output in the console',
    'Helps users revise different problems without repetition'
]):
    p = left_tf.paragraphs[0] if idx == 0 else left_tf.paragraphs.add()
    p.text = item
    p.bullet = True
    p.level = 0
    p.space_after = Pt(10)
    run = p.runs[0]
    run.font.size = Pt(20)
    run.font.color.rgb = TEXT

cylinder = slide.shapes.add_shape(MSO_SHAPE.CYLINDER, Inches(7.3), Inches(1.8), Inches(4.7), Inches(3.2))
cylinder.fill.solid(); cylinder.fill.fore_color.rgb = BLUE; cylinder.line.color.rgb = BLUE
cbox = slide.shapes.add_textbox(Inches(7.6), Inches(2.6), Inches(4.1), Inches(1.2))
p = cbox.text_frame.paragraphs[0]
p.text = '101-140\nQuestion Pool'
p.alignment = PP_ALIGN.CENTER
r = p.runs[0]; r.font.size = Pt(20); r.font.bold = True; r.font.color.rgb = WHITE

# Slide 3 - Key Features
slide = prs.slides.add_slide(prs.slide_layouts[6]); add_bg(slide, WHITE)
add_title(slide, 'Key Features', color=NAVY)
add_bullets(slide, [
    'Randomized selection using Collections.shuffle()',
    'Duplicates are prevented using LinkedHashSet',
    'Uses a fixed random seed for repeatable output',
    'Focuses on a small, manageable set of 5 questions',
    'Simple, beginner-friendly Java implementation'
], 0.9, 1.3, 11.0, 4.8, size=22)

# Slide 4 - How it works
slide = prs.slides.add_slide(prs.slide_layouts[6]); add_bg(slide, LIGHT)
add_title(slide, 'How the Program Works', color=NAVY)
steps = [
    ('1. Create list', 'Adds numbers from 101 to 140'),
    ('2. Shuffle', 'Uses Random(42) to randomize order'),
    ('3. Select', 'Keeps the first 5 unique values'),
    ('4. Print', 'Shows final selected IDs in the console')
]
start_x = 0.8
for idx, (title, desc) in enumerate(steps):
    x = Inches(start_x + idx * 3.0)
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(1.8), Inches(2.4), Inches(2.6))
    card.fill.solid(); card.fill.fore_color.rgb = WHITE; card.line.color.rgb = ACCENT; card.line.width = 1.2
    tf = card.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]; p.text = title; p.alignment = PP_ALIGN.CENTER
    r = p.runs[0]; r.font.size = Pt(18); r.font.bold = True; r.font.color.rgb = NAVY
    p2 = tf.paragraphs.add(); p2.text = desc; p2.alignment = PP_ALIGN.CENTER
    r2 = p2.runs[0]; r2.font.size = Pt(11); r2.font.color.rgb = TEXT
    if idx < len(steps) - 1:
        arrow = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, x + Inches(2.4), Inches(2.8), Inches(0.5), Inches(0.5))
        arrow.fill.solid(); arrow.fill.fore_color.rgb = ACCENT; arrow.line.fill.background()

# Slide 5 - Data structures
slide = prs.slides.add_slide(prs.slide_layouts[6]); add_bg(slide, WHITE)
add_title(slide, 'Data Structures Used', color=NAVY)
items = [
    ('ArrayList', 'Stores all question IDs before selection.'),
    ('Random', 'Creates a predictable random order for testing.'),
    ('LinkedHashSet', 'Ensures only unique values are kept, in insertion order.'),
    ('Set', 'Represents a collection of unique question IDs.')
]
for idx, (name, desc) in enumerate(items):
    y = Inches(1.5 + idx * 1.4)
    pill = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), y, Inches(2.3), Inches(0.8))
    pill.fill.solid(); pill.fill.fore_color.rgb = BLUE; pill.line.fill.background()
    tp = pill.text_frame.paragraphs[0]; tp.text = name; tp.alignment = PP_ALIGN.CENTER
    tr = tp.runs[0]; tr.font.size = Pt(16); tr.font.bold = True; tr.font.color.rgb = WHITE
    txt = slide.shapes.add_textbox(Inches(3.3), y, Inches(8.5), Inches(0.8))
    p = txt.text_frame.paragraphs[0]; p.text = desc
    r = p.runs[0]; r.font.size = Pt(20); r.font.color.rgb = TEXT

# Slide 6 - Code snapshot
slide = prs.slides.add_slide(prs.slide_layouts[6]); add_bg(slide, LIGHT)
add_title(slide, 'Code Snapshot', color=NAVY)
code_box = slide.shapes.add_textbox(Inches(0.7), Inches(1.3), Inches(11.7), Inches(4.5))
tf = code_box.text_frame
snippet = [
    'List<Integer> questionIds = new ArrayList<>();',
    'for (int i = 101; i <= 140; i++) {',
    '    questionIds.add(i);',
    '}',
    '',
    'Random random = new Random(42);',
    'Collections.shuffle(questionIds, random);',
    '',
    'Set<Integer> selected = new LinkedHashSet<>();',
    'for (int id : questionIds) {',
    '    if (selected.size() == 5) break;',
    '    selected.add(id);',
    '}'
]
for idx, line in enumerate(snippet):
    p = tf.paragraphs[0] if idx == 0 else tf.paragraphs.add()
    p.text = line
    run = p.runs[0]
    run.font.size = Pt(18)
    run.font.name = 'Consolas'
    run.font.color.rgb = TEXT

# Slide 7 - Sample output
slide = prs.slides.add_slide(prs.slide_layouts[6]); add_bg(slide, WHITE)
add_title(slide, 'Sample Output', color=NAVY)
panel = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.0), Inches(1.5), Inches(11.2), Inches(4.2))
panel.fill.solid(); panel.fill.fore_color.rgb = LIGHT; panel.line.color.rgb = BLUE; panel.line.width = 1.3
p = panel.text_frame.paragraphs[0]
p.text = 'DSA Practice: randomized unique question selections\nSelected question IDs: [104, 119, 126, 111, 133]'
p.alignment = PP_ALIGN.CENTER
for run in p.runs:
    run.font.size = Pt(20)
    run.font.name = 'Consolas'
    run.font.color.rgb = NAVY

# Slide 8 - Conclusion
slide = prs.slides.add_slide(prs.slide_layouts[6]); add_bg(slide, NAVY)
add_title(slide, 'Conclusion', color=WHITE)
box = slide.shapes.add_textbox(Inches(1.0), Inches(1.6), Inches(11.2), Inches(3.8))
tf = box.text_frame
lines = [
    'This project demonstrates how Java collections can be used to create a simple DSA practice selector.',
    'It is easy to understand, useful for revision, and beginner-friendly.',
    'The app shows real-world concepts like randomization, uniqueness, and list processing.',
    'Future ideas: add difficulty levels, a timer, or custom question categories.'
]
for idx, line in enumerate(lines):
    p = tf.paragraphs[0] if idx == 0 else tf.paragraphs.add()
    p.text = line
    run = p.runs[0]
    run.font.size = Pt(22)
    run.font.color.rgb = WHITE

output_path = '/workspaces/skillGauge/DSA_Practice_Presentation.pptx'
prs.save(output_path)
print('Created PowerPoint:', output_path)
print('Slide count:', len(prs.slides))
