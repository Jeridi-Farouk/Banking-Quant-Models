"""
import os
from weasyprint import HTML

from models.globals import results

# ============================================================
# BUILD HTML REPORT
# ============================================================
def build_html(results):

    sensitivity_html = ""
    if "sensitivity_table" in results and results["sensitivity_table"] is not None:
        sensitivity_html = results["sensitivity_table"].to_html(classes="table", border=0)

    html = f
<html>
<head>
<style>
body {{
    font-family: Arial, sans-serif;
    margin: 40px;
    color: #333;
}}
h1 {{
    color: #003366;
    border-bottom: 2px solid #003366;
    padding-bottom: 5px;
}}
h2 {{
    color: #0055A4;
    margin-top: 40px;
    border-bottom: 1px solid #ccc;
    padding-bottom: 5px;
}}
.table {{
    width: 100%;
    border-collapse: collapse;
    margin-top: 10px;
}}
.table th, .table td {{
    border: 1px solid #ccc;
    padding: 8px;
}}
img {{
    margin-top: 20px;
    margin-bottom: 20px;
    width: 650px;
}}
.section {{
    margin-bottom: 40px;
}}
</style>
</head>
<body>

<h1>Deal Summary Report</h1>

<h2>Valuation (DCF)</h2>
<p><b>Enterprise Value (DCF):</b> {results['enterprise_value']:.2f}</p>
<p><b>Equity Value (DCF):</b> {results['equity_value']:.2f}</p>
<p><b>Fair Value per Share:</b> {results['fair_value']:.2f}</p>

<h2>Offer & Premium</h2>
<p><b>Offer Price per Share:</b> {results['offer_price']:.2f}</p>
<p><b>Premium Paid:</b> {results['premium']*100:.2f}%</p>
<p><b>Maximum Sustainable Premium:</b> {results['premium_max']*100:.2f}%</p>

<h2>Risk Metrics</h2>
<p><b>Beta (static):</b> {results['beta']:.3f}</p>
<p><b>R²:</b> {results['r2'] if results['r2'] is not None else "N/A"}</p>
<p><b>Ke (CAPM):</b> {results['ke']*100:.2f}%</p>
<p><b>WACC:</b> {results['wacc']*100:.2f}%</p>

<h2>Beta Charts</h2>


    if results.get("beta_regression_path"):
        html += f'<img src="{results["beta_regression_path"]}">'

    if results.get("rolling_beta_path"):
        html += f'<img src="{results["rolling_beta_path"]}">'

    html += f
<h2>Accretion / Dilution</h2>
<p><b>EPS pre-deal:</b> {results['eps_pre']:.4f}</p>
<p><b>EPS post-deal:</b> {results['eps_post']:.4f}</p>
<p><b>Accretion/Dilution:</b> {results['accretion_pct']*100:.2f}%</p>

<h2>Leverage</h2>
<p><b>Pro-forma Net Debt / EBITDA:</b> {results['leverage_post']:.2f}x</p>

<h2>Implied Deal Multiples</h2>
<p><b>Implied EV/EBITDA:</b> {results['ev_ebitda_implied']:.2f}x</p>
<p><b>Implied P/E:</b> {results['pe_implied']:.2f}x</p>

<h2>Contribution Analysis</h2>
<p><b>EBITDA Contribution:</b> {results['ebitda_contribution']*100:.2f}%</p>
<p><b>Net Income Contribution:</b> {results['ni_contribution']*100:.2f}%</p>
<p><b>Enterprise Value Contribution:</b> {results['ev_contribution']*100:.2f}%</p>

<h2>Sensitivity WACC / Ke → EV & Equity</h2>
{sensitivity_html}

</body>
</html>


    return html


# ============================================================
# GENERATE PDF
# ============================================================
def generate_pdf(results, filename="Deal_Report.pdf"):
    html = build_html(results)

    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    full_path = os.path.join(output_dir, filename)

    HTML(string=html).write_pdf(full_path)

    print(f"\nPDF generated successfully: {full_path}\n")

"""
from fpdf import FPDF
from models.globals import results
import os

# ============================================================
# 1) PDF CLASS — PAPER STYLE
# ============================================================

class PDFReport(FPDF):

    # ---------------------------
    # HEADER (stile paper)
    # ---------------------------
    def header(self):
        self.set_font("Serif", "B", 16)
        self.cell(0, 10, "Valuation & M&A Analysis Report", ln=True, align="C")

        self.set_font("Serif", "I", 11)
        self.cell(0, 5, "Generated via Python Financial Model", ln=True, align="C")

        self.ln(5)

    # ---------------------------
    # SECTION TITLE (stile paper)
    # ---------------------------
    def section_title(self, title):
        self.set_font("Serif", "B", 14)
        self.set_text_color(0, 0, 0)
        self.cell(0, 8, title, ln=True)

        # Linea sottile sotto il titolo
        self.set_draw_color(150, 150, 150)
        self.set_line_width(0.4)
        self.line(self.l_margin, self.get_y(), 210 - self.r_margin, self.get_y())

        self.ln(4)

    # ---------------------------
    # KEY-VALUE PAIRS
    # ---------------------------
    def add_key_value(self, key, value):
        self.set_font("Serif", "", 12)
        self.set_text_color(60, 60, 60)
        self.cell(80, 8, f"{key}:", border=0)

        self.set_font("Serif", "B", 12)
        self.set_text_color(0, 0, 0)
        self.cell(0, 8, f"{value}", ln=True)

    # ---------------------------
    # IMMAGINI (grafici)
    # ---------------------------
    def add_image_if_exists(self, path, title=None, w=180):
        if path and os.path.exists(path):
            if title:
                self.section_title(title)
            self.image(path, w=w)
            self.ln(5)
        else:
            if title:
                self.section_title(title)
            self.set_font("Serif", "I", 11)
            self.set_text_color(150, 0, 0)
            self.cell(0, 8, "Image not found", ln=True)
            self.ln(3)


# ============================================================
# 2) GENERATE PDF
# ============================================================

def generate_pdf(output_path="Deal_Valuation_Report.pdf"):
    pdf = PDFReport()

    # ---------------------------
    # FONT UTF‑8 (stile paper)
    # ---------------------------
    pdf.add_font("Serif", "", "dejavu-fonts-ttf-2.37/ttf/DejaVuSerif.ttf", uni=True)
    pdf.add_font("Serif", "B", "dejavu-fonts-ttf-2.37/ttf/DejaVuSerif-Bold.ttf", uni=True)
    pdf.add_font("Serif", "I", "dejavu-fonts-ttf-2.37/ttf/DejaVuSerif-Italic.ttf", uni=True)

    pdf.set_font("Serif", "", 12)
    pdf.add_page()

    # ============================================================
    # 1) VALUATION (DCF)
    # ============================================================
    pdf.section_title("1) Valuation (DCF)")
    pdf.add_key_value("Enterprise Value (DCF)", f"{results['enterprise_value']:.2f}")
    pdf.add_key_value("Equity Value (DCF)", f"{results['equity_value']:.2f}")
    pdf.add_key_value("Fair Value per Share", f"{results['fair_value']:.2f}")

    # ============================================================
    # 2) OFFER & PREMIUM
    # ============================================================
    pdf.section_title("2) Offer & Premium")
    pdf.add_key_value("Offer Price per Share", f"{results['offer_price']:.2f}")
    pdf.add_key_value("Premium Paid (%)", f"{results['premium_pct']*100:.2f}%")
    pdf.add_key_value("Premium Paid (€)", f"{results['premium']:.2f}")
    pdf.add_key_value("Maximum Sustainable Premium", f"{results['premium_max_pct']*100:.2f}%")

    # ============================================================
    # 3) RISK METRICS
    # ============================================================
    pdf.section_title("3) Risk Metrics")
    pdf.add_key_value("Beta", f"{results['beta']:.3f}")

    r2 = results.get("r2")
    pdf.add_key_value("R²", "N/A" if r2 is None else f"{r2:.3f}")

    pdf.add_key_value("Ke (CAPM)", f"{results['ke']*100:.2f}%")
    pdf.add_key_value("WACC", f"{results['wacc']*100:.2f}%")
    pdf.add_key_value("Kd", f"{results['kd']*100:.2f}%")
    pdf.add_key_value("Estimated Growth", f"{results['g']*100:.2f}%")

    # ============================================================
    # 4) ACCRETION / DILUTION
    # ============================================================
    pdf.section_title("4) Accretion / Dilution")
    pdf.add_key_value("EPS pre-deal", f"{results['eps_pre']:.4f}")
    pdf.add_key_value("EPS post-deal", f"{results['eps_post']:.4f}")
    pdf.add_key_value("Accretion/Dilution", f"{results['accretion_pct']*100:.2f}%")

    # ============================================================
    # 5) LEVERAGE
    # ============================================================
    pdf.section_title("5) Leverage")
    pdf.add_key_value("Net Debt / EBITDA (Pro-forma)", f"{results['leverage_post']:.2f}x")

    # ============================================================
    # 6) IMPLIED MULTIPLES
    # ============================================================
    pdf.section_title("6) Implied Deal Multiples")
    pdf.add_key_value("EV/EBITDA", f"{results['ev_ebitda_implied']:.2f}x")
    pdf.add_key_value("P/E", f"{results['pe_implied']:.2f}x")

    # ============================================================
    # 7) CONTRIBUTION ANALYSIS
    # ============================================================
    pdf.section_title("7) Contribution Analysis")
    pdf.add_key_value("EBITDA Contribution", f"{results['ebitda_contribution']*100:.2f}%")
    pdf.add_key_value("Net Income Contribution", f"{results['ni_contribution']*100:.2f}%")
    pdf.add_key_value("Enterprise Value Contribution", f"{results['ev_contribution']*100:.2f}%")

    # ============================================================
    # 8) CHARTS & TABLES
    # ============================================================
    pdf.section_title("8) Charts & Tables")

    pdf.add_image_if_exists(results.get("beta_regression_path"), "Regression Beta Chart")
    pdf.add_image_if_exists(results.get("rolling_beta_path"), "Rolling Beta Chart")

    # --- Sensitivity Table ---
    pdf.section_title("Sensitivity Analysis Table")
    table = results.get("sensitivity_table")

    if table is not None:
        pdf.set_font("Serif", "", 11)
        pdf.set_fill_color(230, 230, 230)
        col_width = pdf.w / (len(table.columns) + 1)

        pdf.set_font("Serif", "B", 11)
        for col in table.columns:
            pdf.cell(col_width, 8, str(col), border=1, align="C", fill=True)
        pdf.ln(8)

        pdf.set_font("Serif", "", 11)
        for idx, row in table.iterrows():
            for col in table.columns:
                pdf.cell(col_width, 8, str(row[col]), border=1, align="C")
            pdf.ln(8)
    else:
        pdf.set_font("Serif", "I", 11)
        pdf.set_text_color(150, 0, 0)
        pdf.cell(0, 8, "Sensitivity table not found", ln=True)

    # ============================================================
    # 9) COMPARABLE COMPANIES – REGRESSION R²
    # ============================================================
    if "r2_list" in results and len(results["r2_list"]) > 0:
        pdf.section_title("9) Comparable Companies – Regression R²")

        r2_dict = results["r2_list"]

        pdf.set_font("Serif", "B", 12)
        pdf.set_fill_color(230, 230, 230)
        pdf.cell(80, 8, "Company", border=1, align="C", fill=True)
        pdf.cell(40, 8, "R²", border=1, align="C", fill=True)
        pdf.ln(8)

        pdf.set_font("Serif", "", 12)
        for comp, data in r2_dict.items():
            r2_value = data["r2"]
            r2_value = round(r2_value, 3) if r2_value is not None else "N/A"

            pdf.cell(80, 8, comp, border=1, align="C")
            pdf.cell(40, 8, str(r2_value), border=1, align="C")
            pdf.ln(8)

        pdf.ln(5)

    # ============================================================
    # 10) COMPARABLE COMPANIES – BETA CHARTS
    # ============================================================
    if "r2_list" in results and len(results["r2_list"]) > 0:
        pdf.section_title("10) Comparable Companies – Beta Charts")

        for comp, data in results["r2_list"].items():
            pdf.set_font("Serif", "B", 13)
            pdf.ln(4)
            pdf.cell(0, 8, f"{comp} – Regression Beta", ln=True)
            pdf.add_image_if_exists(data.get("beta_path"), f"{comp} Regression Beta")

            pdf.ln(2)
            pdf.set_font("Serif", "B", 13)
            pdf.cell(0, 8, f"{comp} – Rolling Beta", ln=True)
            pdf.add_image_if_exists(data.get("rolling_path"), f"{comp} Rolling Beta")

            pdf.ln(5)

    # ============================================================
    # SAVE PDF
    # ============================================================
    pdf.output(output_path)
    print(f"\nPDF generated successfully → {output_path}")