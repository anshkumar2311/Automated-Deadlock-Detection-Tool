"""
PDF report generator using ReportLab.
Produces a professional deadlock-detection report with:
  - system input summary
  - embedded RAG graph
  - detection results
  - explanation / recommendations
"""

import os
from datetime import datetime
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# ── Colour palette ────────────────────────────────────────────────────────
C_PRIMARY   = colors.HexColor('#2563eb')
C_DANGER    = colors.HexColor('#dc2626')
C_SUCCESS   = colors.HexColor('#16a34a')
C_WARNING   = colors.HexColor('#d97706')
C_LIGHT_BG  = colors.HexColor('#f8fafc')
C_BORDER    = colors.HexColor('#e2e8f0')
C_TEXT      = colors.HexColor('#0f172a')
C_MUTED     = colors.HexColor('#64748b')


class ReportGenerator:
    # ── Public API ────────────────────────────────────────────────────────

    def generate(self, input_data: dict, result: dict, graph_path: str = None) -> bytes:
        buf = BytesIO()
        doc = SimpleDocTemplate(
            buf,
            pagesize=A4,
            leftMargin=2 * cm,
            rightMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
            title='Deadlock Detection Report',
            author='OS Simulation Tool',
        )

        styles = self._build_styles()
        story  = []

        self._add_header(story, styles, result)
        self._add_summary_banner(story, styles, result)
        self._add_system_input(story, styles, input_data)
        self._add_graph(story, styles, graph_path)
        self._add_detection_results(story, styles, result)
        self._add_resolution(story, styles, result)
        self._add_prevention(story, styles, result)
        self._add_footer(story, styles)

        doc.build(story)
        return buf.getvalue()

    # ── Styles ────────────────────────────────────────────────────────────

    def _build_styles(self):
        base = getSampleStyleSheet()

        def add(name, **kw):
            base.add(ParagraphStyle(name=name, **kw))

        add('ReportTitle',
            fontSize=22, leading=28, textColor=C_PRIMARY,
            fontName='Helvetica-Bold', alignment=TA_CENTER, spaceAfter=4)

        add('ReportSubtitle',
            fontSize=10, leading=14, textColor=C_MUTED,
            fontName='Helvetica', alignment=TA_CENTER, spaceAfter=16)

        add('SectionHeading',
            fontSize=13, leading=18, textColor=C_PRIMARY,
            fontName='Helvetica-Bold', spaceBefore=14, spaceAfter=6)

        add('BodyText2',
            fontSize=9, leading=13, textColor=C_TEXT,
            fontName='Helvetica', spaceAfter=4)

        add('BoldLabel',
            fontSize=9, leading=13, textColor=C_TEXT,
            fontName='Helvetica-Bold')

        add('MutedText',
            fontSize=8, leading=12, textColor=C_MUTED,
            fontName='Helvetica')

        add('BannerSafe',
            fontSize=12, leading=16, textColor=C_SUCCESS,
            fontName='Helvetica-Bold', alignment=TA_CENTER)

        add('BannerDeadlock',
            fontSize=12, leading=16, textColor=C_DANGER,
            fontName='Helvetica-Bold', alignment=TA_CENTER)

        return base

    # ── Sections ──────────────────────────────────────────────────────────

    def _add_header(self, story, styles, result):
        story.append(Paragraph('Deadlock Detection Report', styles['ReportTitle']))
        ts = datetime.now().strftime('%B %d, %Y  %H:%M:%S')
        story.append(Paragraph(f'Generated: {ts}', styles['ReportSubtitle']))
        story.append(HRFlowable(width='100%', thickness=1, color=C_BORDER))
        story.append(Spacer(1, 0.3 * cm))

    def _add_summary_banner(self, story, styles, result):
        has_deadlock = result.get('deadlock', False)
        if has_deadlock:
            involved = result.get('involved_processes', [])
            text = (f'⚠  DEADLOCK DETECTED — '
                    f'{len(involved)} process(es) involved: '
                    f'{", ".join(involved)}')
            style = styles['BannerDeadlock']
            bg    = colors.HexColor('#fef2f2')
            border = C_DANGER
        else:
            text  = '✓  SYSTEM IS SAFE — No deadlock detected'
            style = styles['BannerSafe']
            bg    = colors.HexColor('#f0fdf4')
            border = C_SUCCESS

        tbl = Table([[Paragraph(text, style)]], colWidths=['100%'])
        tbl.setStyle(TableStyle([
            ('BACKGROUND',  (0, 0), (-1, -1), bg),
            ('BOX',         (0, 0), (-1, -1), 1, border),
            ('ROUNDEDCORNERS', [6]),
            ('TOPPADDING',  (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 14),
            ('RIGHTPADDING', (0, 0), (-1, -1), 14),
        ]))
        story.append(tbl)
        story.append(Spacer(1, 0.4 * cm))

    def _add_system_input(self, story, styles, input_data):
        story.append(Paragraph('1. System Configuration', styles['SectionHeading']))

        # Resources table
        resources = input_data.get('resources', [])
        story.append(Paragraph('Resources', styles['BoldLabel']))
        story.append(Spacer(1, 0.1 * cm))

        res_data = [['Resource ID', 'Total Instances']]
        for r in resources:
            res_data.append([r.get('rid', ''), str(r.get('instances', 1))])

        res_tbl = Table(res_data, colWidths=[8 * cm, 8 * cm])
        res_tbl.setStyle(self._table_style(header_bg=C_PRIMARY))
        story.append(res_tbl)
        story.append(Spacer(1, 0.3 * cm))

        # Processes table
        processes = input_data.get('processes', [])
        story.append(Paragraph('Processes', styles['BoldLabel']))
        story.append(Spacer(1, 0.1 * cm))

        proc_data = [['Process ID', 'Allocated', 'Requested', 'Max Need']]
        for p in processes:
            proc_data.append([
                p.get('pid', ''),
                ', '.join(p.get('allocated', [])) or '—',
                ', '.join(p.get('requested', [])) or '—',
                ', '.join(p.get('max_need', [])) or '—',
            ])

        proc_tbl = Table(proc_data, colWidths=[3.5 * cm, 4.5 * cm, 4.5 * cm, 4.5 * cm])
        proc_tbl.setStyle(self._table_style(header_bg=C_PRIMARY))
        story.append(proc_tbl)
        story.append(Spacer(1, 0.3 * cm))

    def _add_graph(self, story, styles, graph_path):
        story.append(Paragraph('2. Resource Allocation Graph', styles['SectionHeading']))
        if graph_path and os.path.exists(graph_path):
            img = Image(graph_path, width=14 * cm, height=9 * cm, kind='proportional')
            story.append(img)
            story.append(Paragraph(
                'Circles = processes  ·  Squares = resources  ·  '
                'Red edges = requests  ·  Blue edges = allocations',
                styles['MutedText'],
            ))
        else:
            story.append(Paragraph('Graph image not available.', styles['MutedText']))
        story.append(Spacer(1, 0.3 * cm))

    def _add_detection_results(self, story, styles, result):
        story.append(Paragraph('3. Detection Results', styles['SectionHeading']))

        ba = result.get('bankers_algorithm', {})
        cd = result.get('cycle_detection', {})
        gi = result.get('graph_info', {})

        rows = [
            ['Metric', 'Value'],
            ['Overall Deadlock', 'YES' if result.get('deadlock') else 'NO'],
            ["Banker's State",   ba.get('state', '—').upper()],
            ['Safe Sequence',    ' → '.join(ba.get('safe_sequence') or []) or 'None'],
            ['Cycle Detected',   'YES' if cd.get('has_deadlock') else 'NO'],
            ['Cycles Found',     str(len(cd.get('cycles', [])))],
            ['Graph Nodes',      str(gi.get('nodes', '—'))],
            ['Graph Edges',      str(gi.get('edges', '—'))],
        ]

        tbl = Table(rows, colWidths=[8 * cm, 9 * cm])
        tbl.setStyle(self._table_style(header_bg=C_PRIMARY, zebra=True))
        story.append(tbl)

        # Cycles detail
        cycles = cd.get('cycles', [])
        if cycles:
            story.append(Spacer(1, 0.2 * cm))
            story.append(Paragraph('Detected Cycles', styles['BoldLabel']))
            for i, cycle in enumerate(cycles, 1):
                story.append(Paragraph(
                    f'Cycle {i}: {" → ".join(str(n) for n in cycle)}',
                    styles['BodyText2'],
                ))

        story.append(Spacer(1, 0.3 * cm))

    def _add_resolution(self, story, styles, result):
        resolution = result.get('resolution', {})
        actions    = resolution.get('actions', [])
        if not actions:
            return

        story.append(Paragraph('4. Resolution Recommendations', styles['SectionHeading']))
        story.append(Paragraph(
            resolution.get('description', ''), styles['BodyText2']))
        story.append(Spacer(1, 0.15 * cm))

        rows = [['Action', 'Target Process', 'Description']]
        for a in actions:
            rows.append([
                a.get('action', '').replace('_', ' ').title(),
                a.get('target', '—'),
                a.get('description', ''),
            ])

        tbl = Table(rows, colWidths=[3.5 * cm, 4 * cm, 9.5 * cm])
        tbl.setStyle(self._table_style(header_bg=C_WARNING, zebra=True))
        story.append(tbl)
        story.append(Spacer(1, 0.3 * cm))

    def _add_prevention(self, story, styles, result):
        prevention = result.get('prevention', {})
        strategies = prevention.get('strategies', [])
        if not strategies:
            return

        story.append(Paragraph('5. Prevention Strategies', styles['SectionHeading']))

        rows = [['Strategy', 'Method', 'Impact']]
        for s in strategies:
            rows.append([
                s.get('strategy', ''),
                s.get('method', ''),
                s.get('impact', ''),
            ])

        tbl = Table(rows, colWidths=[5 * cm, 7 * cm, 5 * cm])
        tbl.setStyle(self._table_style(header_bg=C_SUCCESS, zebra=True))
        story.append(tbl)
        story.append(Spacer(1, 0.3 * cm))

    def _add_footer(self, story, styles):
        story.append(HRFlowable(width='100%', thickness=1, color=C_BORDER))
        story.append(Spacer(1, 0.2 * cm))
        story.append(Paragraph(
            'OS Simulation Tool — Deadlock Detection System v2.0',
            styles['MutedText'],
        ))

    # ── Table style helper ────────────────────────────────────────────────

    def _table_style(self, header_bg=C_PRIMARY, zebra=False):
        cmds = [
            ('BACKGROUND',    (0, 0), (-1, 0),  header_bg),
            ('TEXTCOLOR',     (0, 0), (-1, 0),  colors.white),
            ('FONTNAME',      (0, 0), (-1, 0),  'Helvetica-Bold'),
            ('FONTSIZE',      (0, 0), (-1, 0),  9),
            ('BOTTOMPADDING', (0, 0), (-1, 0),  7),
            ('TOPPADDING',    (0, 0), (-1, 0),  7),
            ('FONTNAME',      (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE',      (0, 1), (-1, -1), 8),
            ('TOPPADDING',    (0, 1), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
            ('LEFTPADDING',   (0, 0), (-1, -1), 8),
            ('RIGHTPADDING',  (0, 0), (-1, -1), 8),
            ('GRID',          (0, 0), (-1, -1), 0.5, C_BORDER),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1),
             [colors.white, C_LIGHT_BG] if zebra else [colors.white]),
            ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
        ]
        return TableStyle(cmds)
