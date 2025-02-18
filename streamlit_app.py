import streamlit as st
import pandas as pd
import streamlit.components.v1 as components


def format_negatives(val):
    """Return '(x.xx)' for negative floats, or 'x.xx' if positive."""
    if isinstance(val, (int, float)):
        return f"({abs(val):,.2f})" if val < 0 else f"{val:,.2f}"
    return val


def highlight_subsections(html_table, highlight_color="#FFF7D1"):
    """
    Splits the table HTML into lines, looks for any line containing <td><b>,
    and replaces <tr> with an inline style for that row's background color.
    """
    lines = html_table.splitlines()
    new_lines = []
    for line in lines:
        if "<td><b>" in line:
            # Add style to the row
            line = line.replace(
                "<tr>",
                f"<tr style='background-color: {highlight_color};'>",
                1  # only replace first occurrence
            )
        new_lines.append(line)
    return "\n".join(new_lines)


def main():
    st.set_page_config(layout="wide", page_title="RCF - CLN Calculator")
    tab_calculator, tab_explanation = st.tabs(["Calculator", "Explanation"])

    ############################################################################
    #                           TAB 1: CALCULATOR
    ############################################################################
    with tab_calculator:
        st.title("RCF – CLN Calculator")

        # -----------------
        # Sidebar Inputs
        # -----------------
        st.sidebar.header("User Inputs")

        with st.sidebar.expander("General Inputs", expanded=True):
            company_name = st.text_input("Company Name", value="Dummy Name")

            rcf_limit = st.number_input(
                "RCF Limit (ZAR)",
                min_value=0.0, value=250_000.0, step=50_000.0
            )

            drawn_percentage = st.number_input(
                "Drawn Percentage (0.00 - 1.00)",
                min_value=0.0, max_value=1.0,
                value=0.35, step=0.05
            )

            # Additional "cap_cost" for ROC formula
            cap_cost = st.number_input(
                "Capital Cost (for ROC calculation)",
                min_value=0.0, value=10.0, step=1.0
            )

        with st.sidebar.expander("Total Cost (Drawn Portion) Inputs", expanded=True):
            margin_bps = st.number_input("Margin (bps)", value=250.0)
            funding_bps = st.number_input("Funding (bps)", value=-114.0)
            credit_bps = st.number_input("Credit (bps)", value=-29.0)
            capital_bps = st.number_input("Capital (bps)", value=-115.0)

        with st.sidebar.expander("Commitment Fee (Undrawn) Inputs", expanded=True):
            commitment_fee_bps = st.number_input("Commitment Fee (bps)", value=75.0)
            commitment_fee_funding_bps = st.number_input("Commitment Fee Funding (bps)", value=-13.0)
            commitment_fee_credit_bps = st.number_input("Commitment Fee Credit (bps)", value=-12.0)
            commitment_fee_capital_bps = st.number_input("Commitment Fee Capital (bps)", value=-50.0)

        # Calculate Button
        calc_btn = st.sidebar.button("Calculate")

        if calc_btn:
            # ---------------------------
            # CALCULATIONS
            # ---------------------------
            undrawn_percentage = 1 - drawn_percentage
            drawn_amount = rcf_limit * drawn_percentage
            undrawn_amount = rcf_limit * undrawn_percentage

            # 1) Margin
            margin_zar = drawn_amount * (margin_bps / 10_000)

            # 2) Funding, Credit, Capital (Drawn)
            funding_zar = drawn_amount * (funding_bps / 10_000)
            credit_zar = drawn_amount * (credit_bps / 10_000)
            capital_zar = drawn_amount * (capital_bps / 10_000)

            # 3) Total Cost (Drawn)
            total_cost_bps = funding_bps + credit_bps + capital_bps
            total_cost_zar = funding_zar + credit_zar + capital_zar

            # 4) Net Spread (Drawn)
            net_spread_zar = margin_zar + total_cost_zar
            net_spread_bps = (margin_bps + total_cost_bps) * drawn_percentage

            # 5) Commitment Fee (Undrawn)
            commitment_fee_zar = undrawn_amount * (commitment_fee_bps / 10_000)

            # 6) Funding, Credit, Capital (Commitment Fee)
            comm_fee_funding_zar = undrawn_amount * (commitment_fee_funding_bps / 10_000)
            comm_fee_credit_zar = undrawn_amount * (commitment_fee_credit_bps / 10_000)
            comm_fee_capital_zar = undrawn_amount * (commitment_fee_capital_bps / 10_000)

            # 7) Net Spread (Commitment Fees)
            net_commit_bps = (
                    commitment_fee_bps
                    + commitment_fee_funding_bps
                    + commitment_fee_credit_bps
                    + commitment_fee_capital_bps
            )
            net_spread_commit_fees_zar = (
                    commitment_fee_zar
                    + comm_fee_funding_zar
                    + comm_fee_credit_zar
                    + comm_fee_capital_zar
            )
            net_spread_commit_fees_bps = net_commit_bps * undrawn_percentage

            # ------------------------------------------------------------------
            # BLENDED VIEW
            # ------------------------------------------------------------------
            # (Margin)
            blended_view_margin_zar = margin_zar + commitment_fee_zar
            blended_view_margin_bps = (margin_bps * drawn_percentage) + (commitment_fee_bps * undrawn_percentage)

            # (Funding)
            blended_view_funding_zar = funding_zar + comm_fee_funding_zar
            blended_view_funding_bps = (funding_bps * drawn_percentage) + (
                        commitment_fee_funding_bps * undrawn_percentage)

            # (CLN)
            blended_view_cln_zar = 0.0
            blended_view_cln_bps = 0.0

            # (Credit)
            blended_view_credit_zar = credit_zar + comm_fee_credit_zar
            blended_view_credit_bps = (credit_bps * drawn_percentage) + (commitment_fee_credit_bps * undrawn_percentage)

            # (Capital)
            blended_view_capital_zar = capital_zar + comm_fee_capital_zar
            blended_view_capital_bps = (capital_bps * drawn_percentage) + (
                        commitment_fee_capital_bps * undrawn_percentage)

            # Net Revenue
            blended_view_net_revenue_zar = (
                    blended_view_margin_zar
                    + blended_view_funding_zar
                    + blended_view_cln_zar
                    + blended_view_credit_zar
                    + blended_view_capital_zar
            )
            blended_view_net_revenue_bps = (
                    blended_view_margin_bps
                    + blended_view_funding_bps
                    + blended_view_cln_bps
                    + blended_view_credit_bps
                    + blended_view_capital_bps
            )

            # ROC
            try:
                if blended_view_capital_bps == 0:
                    blended_view_roc_bps = 0
                else:
                    blended_view_roc_bps = (
                            (blended_view_margin_bps
                             + blended_view_funding_bps
                             + blended_view_cln_bps
                             + blended_view_credit_bps)
                            / (-blended_view_capital_bps)
                            * cap_cost
                    )
            except ZeroDivisionError:
                blended_view_roc_bps = 0

            # ------------------------------------------------------------------
            # BUILD THE OUTPUT TABLE
            # ------------------------------------------------------------------
            rows = [
                {"Item": f"<b>{company_name}</b>", "ZAR": "", "BPS": ""},
                # (Drawn portion results)
                {"Item": "<b>Margin</b>", "ZAR": margin_zar, "BPS": margin_bps},
                {"Item": "<b>Total Cost</b>", "ZAR": total_cost_zar, "BPS": total_cost_bps},
                {"Item": "Funding", "ZAR": funding_zar, "BPS": funding_bps},
                {"Item": "Credit", "ZAR": credit_zar, "BPS": credit_bps},
                {"Item": "Capital", "ZAR": capital_zar, "BPS": capital_bps},
                {"Item": "<b>Net Spread</b>", "ZAR": net_spread_zar, "BPS": net_spread_bps},
                {"Item": "", "ZAR": "", "BPS": ""},

                # (Undrawn portion - Commitment)
                {"Item": "<b>Commitment Fee</b>", "ZAR": commitment_fee_zar, "BPS": commitment_fee_bps},
                {"Item": "Funding", "ZAR": comm_fee_funding_zar, "BPS": commitment_fee_funding_bps},
                {"Item": "Credit Cost", "ZAR": comm_fee_credit_zar, "BPS": commitment_fee_credit_bps},
                {"Item": "Capital Cost", "ZAR": comm_fee_capital_zar, "BPS": commitment_fee_capital_bps},
                {"Item": "<b>Net Spread</b>", "ZAR": net_spread_commit_fees_zar, "BPS": net_spread_commit_fees_bps},

                {"Item": "", "ZAR": "", "BPS": ""},

                # (Blended View)
                {"Item": "<b>Blended View</b>", "ZAR": "", "BPS": ""},
                {"Item": "  Margin", "ZAR": blended_view_margin_zar, "BPS": blended_view_margin_bps},
                {"Item": "  Funding", "ZAR": blended_view_funding_zar, "BPS": blended_view_funding_bps},
                {"Item": "  CLN Cost", "ZAR": blended_view_cln_zar, "BPS": blended_view_cln_bps},
                {"Item": "  Credit", "ZAR": blended_view_credit_zar, "BPS": blended_view_credit_bps},
                {"Item": "  Capital", "ZAR": blended_view_capital_zar, "BPS": blended_view_capital_bps},
                {"Item": "<b>Net Revenue</b>", "ZAR": blended_view_net_revenue_zar,
                 "BPS": blended_view_net_revenue_bps},
                {"Item": "<b>ROC (bps)</b>", "ZAR": "", "BPS": blended_view_roc_bps},

                {"Item": "", "ZAR": "", "BPS": ""},

                # (Facility + Drawn/Undrawn)
                {"Item": "<b>Facility Amount</b>", "ZAR": rcf_limit, "BPS": "100%"},
                {"Item": "<b>Drawn</b>", "ZAR": drawn_amount, "BPS": f"{drawn_percentage * 100:.0f}%"},
                {"Item": "<b>Undrawn</b>", "ZAR": undrawn_amount, "BPS": f"{undrawn_percentage * 100:.0f}%"},
            ]

            df = pd.DataFrame(rows, columns=["Item", "ZAR", "BPS"])
            df["ZAR"] = df["ZAR"].apply(format_negatives)
            df["BPS"] = df["BPS"].apply(format_negatives)

            # 1. Convert DF to HTML, 2. Replace default class, 3. Then highlight bold lines
            html_table = df.to_html(index=False, border=1, escape=False)
            html_table = html_table.replace('class="dataframe"', 'class="mystyle"')
            
            # Enhanced highlighting for major rows
            custom_css = """
            <style>
            .mystyle {
                border-collapse: collapse;
                width: 90%;
                font-family: Arial, sans-serif;
                background-color: #ffffff;
                color: #000000;
                margin: 20px 0;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
            .mystyle th {
                background-color: #eaeaea;
                text-align: left;
                padding: 12px;
                font-weight: 600;
                border-bottom: 2px solid #dee2e6;
            }
            .mystyle td {
                padding: 10px;
                border: 1px solid #dee2e6;
                vertical-align: middle;
            }
            .mystyle tr:nth-child(even) {
                background-color: #f9f9f9;
            }
            .mystyle tr:hover {
                background-color: #f5f5f5;
            }
            /* Highlight rows with bold text */
            .mystyle tr td:first-child b {
                display: block;
                width: 100%;
                background-color: #FFE7B3;
                padding: 8px;
                margin: -8px;
            }
            /* Make the entire row highlighted when it contains bold text */
            .mystyle tr:has(td:first-child b) {
                background-color: #FFF7D1;
            }
            /* Style for the screenshot button */
            .screenshot-button {
                margin: 20px 0;
                padding: 10px 20px;
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                text-decoration: none;
                display: inline-block;
            }
            .screenshot-button:hover {
                background-color: #218838;
            }
            </style>
            <script>
            function downloadTableAsImage() {
                const table = document.querySelector('.mystyle');
                html2canvas(table).then(canvas => {
                    const link = document.createElement('a');
                    link.download = 'table_screenshot.png';
                    link.href = canvas.toDataURL('image/png');
                    link.click();
                });
            }
            </script>
            """

            # Add html2canvas library for screenshot functionality
            html2canvas_js = """
            <script src="https://html2canvas.hertzen.com/dist/html2canvas.min.js"></script>
            """

            # Add screenshot button
            screenshot_button = """
            <button class="screenshot-button" onclick="downloadTableAsImage()">
                Download as Image
            </button>
            """

            final_html = html2canvas_js + custom_css + html_table + screenshot_button
            st.subheader("NO CLN Output Table")

            components.html(final_html, height=850, scrolling=True)

            # Add export button with better styling
            if st.download_button(
                label="Download CSV",
                data=df.to_csv(index=False).encode('utf-8'),
                file_name=f"{company_name}_rcf_cln_calculation.csv",
                mime='text/csv'
            ):
                st.success("File downloaded successfully!")

        else:
            st.info("Enter your inputs and click Calculate to see results.")

    ############################################################################
    #                           TAB 2: EXPLANATION
    ############################################################################
    with tab_explanation:
        st.title("Explanation of Calculations")
        
        # General Overview
        st.markdown("## Overview")
        st.write("""
        The RCF-CLN Calculator determines the profitability and returns for Revolving Credit Facilities (RCF). 
        The calculations consider both drawn and undrawn portions of the facility.
        """)

        # Drawn Portion Calculations
        st.markdown("## Drawn Portion")
        
        st.markdown("### Margin")
        st.write("The margin is calculated on the drawn amount:")
        st.latex(r"\text{Margin (ZAR)} = \text{Drawn Amount} \times \frac{\text{Margin (bps)}}{10,000}")
        
        st.markdown("### Total Cost Components")
        st.write("The total cost consists of three main components:")
        
        st.markdown("1. **Funding Cost**")
        st.latex(r"\text{Funding (ZAR)} = \text{Drawn Amount} \times \frac{\text{Funding (bps)}}{10,000}")
        
        st.markdown("2. **Credit Cost**")
        st.latex(r"\text{Credit (ZAR)} = \text{Drawn Amount} \times \frac{\text{Credit (bps)}}{10,000}")
        
        st.markdown("3. **Capital Cost**")
        st.latex(r"\text{Capital (ZAR)} = \text{Drawn Amount} \times \frac{\text{Capital (bps)}}{10,000}")
        
        st.markdown("### Net Spread (Drawn)")
        st.write("The net spread for the drawn portion is:")
        st.latex(r"\text{Net Spread (ZAR)} = \text{Margin} + \text{Total Cost}")
        st.latex(r"\text{Net Spread (bps)} = (\text{Margin bps} + \text{Total Cost bps}) \times \text{Drawn \%}")

        # Undrawn Portion Calculations
        st.markdown("## Undrawn Portion (Commitment Fee)")
        
        st.markdown("### Commitment Fee")
        st.latex(r"\text{Fee (ZAR)} = \text{Undrawn Amount} \times \frac{\text{Commitment Fee (bps)}}{10,000}")
        
        st.markdown("### Associated Costs")
        st.write("Similar to the drawn portion, there are three cost components:")
        
        st.markdown("1. **Funding Cost**")
        st.latex(r"\text{Funding (ZAR)} = \text{Undrawn Amount} \times \frac{\text{Commitment Fee Funding (bps)}}{10,000}")
        
        st.markdown("2. **Credit Cost**")
        st.latex(r"\text{Credit (ZAR)} = \text{Undrawn Amount} \times \frac{\text{Commitment Fee Credit (bps)}}{10,000}")
        
        st.markdown("3. **Capital Cost**")
        st.latex(r"\text{Capital (ZAR)} = \text{Undrawn Amount} \times \frac{\text{Commitment Fee Capital (bps)}}{10,000}")

        # Blended View Calculations
        st.markdown("## Blended View")
        st.write("The blended view combines both drawn and undrawn portions:")
        
        st.markdown("### Net Revenue")
        st.latex(r"\text{Net Revenue (ZAR)} = \text{Margin} + \text{Funding} + \text{CLN} + \text{Credit} + \text{Capital}")
        st.write("Where each component combines both drawn and undrawn portions.")
        
        st.markdown("### Return on Capital (ROC)")
        st.write("ROC is calculated as:")
        st.latex(r"\text{ROC (bps)} = \frac{\text{Margin} + \text{Funding} + \text{CLN} + \text{Credit}}{-\text{Capital}} \times \text{Capital Cost}")
        st.write("This measures the return generated relative to the capital employed.")

        # Additional Notes
        st.markdown("## Additional Notes")
        st.markdown("""
        - All calculations use basis points (bps) where 100 bps = 1%
        - Negative values are shown in parentheses (e.g., (100))
        - The drawn percentage affects the weighting of drawn vs. undrawn calculations
        - Capital costs are typically negative as they represent a cost to the bank
        """)


if __name__ == "__main__":
    main()
