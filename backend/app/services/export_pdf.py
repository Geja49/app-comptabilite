from io import BytesIO
from decimal import Decimal

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.services.export_excel import NOMS_MOIS


def _fmt(v: Decimal | float | int) -> str:
    return f"{float(v):,.2f} $"


def exporter_annee_pdf(annee: int, sommaire_annuel: dict, details_mensuels: list[dict]) -> BytesIO:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = [
        Paragraph(f"Rapport comptable annuel — {annee}", styles["Title"]),
        Spacer(1, 12),
        Paragraph("Sommaire annuel de performance et taxes", styles["Heading2"]),
        Spacer(1, 8),
    ]

    entetes = [
        "Mois", "Revenu brut", "TPS perçue", "TVQ perçue", "Dépenses",
        "TPS payée", "TVQ payée", "TPS à remettre", "TVQ à remettre", "Dép. proratées",
    ]
    lignes = [entetes]
    for mois in sommaire_annuel["mois"]:
        lignes.append([
            mois["mois_nom"],
            _fmt(mois["revenu_brut"]),
            _fmt(mois["tps_percue"]),
            _fmt(mois["tvq_percue"]),
            _fmt(mois["depenses_totales"]),
            _fmt(mois["tps_payee"]),
            _fmt(mois["tvq_payee"]),
            _fmt(mois["tps_a_remettre"]),
            _fmt(mois["tvq_a_remettre"]),
            _fmt(mois["depenses_admissibles_proratees"]),
        ])
    total = sommaire_annuel["total"]
    lignes.append([
        "Total annuel",
        _fmt(total["revenu_brut"]),
        _fmt(total["tps_percue"]),
        _fmt(total["tvq_percue"]),
        _fmt(total["depenses_totales"]),
        _fmt(total["tps_payee"]),
        _fmt(total["tvq_payee"]),
        _fmt(total["tps_a_remettre"]),
        _fmt(total["tvq_a_remettre"]),
        _fmt(total["depenses_admissibles_proratees"]),
    ])

    table = Table(lignes, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e40af")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#e2e8f0")),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 16))

    for detail in details_mensuels:
        if not detail["revenus"] and not detail["depenses"] and not detail["kilometrage"]["entrees"]:
            continue
        mois_nom = NOMS_MOIS[detail["periode"]["mois"] - 1]
        elements.append(Paragraph(f"Détail — {mois_nom} {annee}", styles["Heading3"]))
        elements.append(Spacer(1, 6))
        elements.append(Paragraph(
            f"Revenu brut : {_fmt(detail['sommaire']['revenu_brut'])} | "
            f"Dépenses : {_fmt(detail['sommaire']['depenses_totales'])} | "
            f"TPS à remettre : {_fmt(detail['sommaire']['tps_a_remettre'])}",
            styles["Normal"],
        ))
        elements.append(Spacer(1, 10))

    doc.build(elements)
    buffer.seek(0)
    return buffer
