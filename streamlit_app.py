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


def display_table(df):
    """Formats and displays a DataFrame as an HTML table with styling."""
    # Format numeric columns
    numeric_columns = [col for col in df.columns if any(x in col.lower() for x in ['zar', 'bps', 'differential'])]
    for col in numeric_columns:
        df[col] = df[col].apply(format_negatives)

    # Format column headers: replace underscores with spaces and format "bps" to "BPS"
    df.columns = [col.replace('_', ' ').replace('bps', 'BPS') for col in df.columns]
    
    # Make all headers bold
    df.columns = [f"<b>{col}</b>" for col in df.columns]

    custom_css = """
    <style>
    .rcf-table {
        width: 100%;
        border-collapse: collapse;
        font-family: -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", Roboto;
    }

    /* Column Headers */
    .rcf-table thead th {
        background-color: #4A5568;
        color: white;
        padding: 12px 16px;
        text-align: left;
        font-weight: 500;
        border: 1px solid #2D3748;
    }

    /* All cells */
    .rcf-table td {
        padding: 8px 16px;
        border: 1px solid #E2E8F0;
    }

    /* Section headers (blue background) */
    .rcf-table tr.section-header {
        background-color: #EBF8FF;
    }
    .rcf-table tr.section-header td {
        color: #2C5282;
        font-weight: 600;
    }

    /* Regular rows */
    .rcf-table tr:not(.section-header) {
        background-color: white;
    }

    /* Number columns - handle all numeric columns */
    .rcf-table td:not(:first-child) {
        text-align: right;
        font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
        color: #2D3748;
    }

    /* Empty rows */
    .rcf-table tr:has(td:empty) {
        height: 8px;
        background-color: white;
    }
    </style>
    """

    # Convert to HTML
    html_table = df.to_html(index=False, border=0, escape=False)

    # Replace default class and add section header styling
    html_table = html_table.replace('class="dataframe"', 'class="rcf-table"')
    html_table = html_table.replace('<tr>', '<tr class="data-row">')
    html_table = html_table.replace('<tr class="data-row"><td><b>', '<tr class="section-header"><td><b>')

    # Combine CSS and table
    final_html = custom_css + html_table

    # Display with adjusted height
    components.html(final_html, height=1000, scrolling=True)


def main():
    # At the start of main(), initialize session state
    if 'table_data' not in st.session_state:
        st.session_state.table_data = None
        
    # Configure page layout and styling
    st.set_page_config(
        layout="wide",
        page_title="RCF - CLN Calculator",
        page_icon="💰"
    )

    # Custom CSS for better styling with dark mode support
    st.markdown("""
        <style>
        /* Main container styling */
        .main {
            padding: 2rem;
        }
        
        /* Headers styling - dark mode friendly */
        [data-testid="stAppViewContainer"] {
            color: var(--text-color);
        }
        
        h1 {
            color: #66B2FF !important;
            padding-bottom: 1rem;
            border-bottom: 2px solid rgba(255, 255, 255, 0.1);
            margin-bottom: 2rem;
        }
        
        h2 {
            color: #7FDBCA !important;
            margin-top: 2rem;
            margin-bottom: 1rem;
        }
        
        h3 {
            color: #B2CCD6 !important;
            margin-top: 1.5rem;
        }
        
        /* Sidebar styling */
        .css-1d391kg {
            padding: 2rem 1rem;
        }
        
        /* Input fields styling */
        .stNumberInput {
            background-color: rgba(255, 255, 255, 0.05);
            border-radius: 5px;
            padding: 0.5rem;
        }
        
        /* Button styling */
        .stButton>button {
            background-color: #66B2FF;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 0.5rem 1rem;
            transition: all 0.3s ease;
        }
        
        .stButton>button:hover {
            background-color: #3399FF;
            box-shadow: 0 2px 4px rgba(102, 178, 255, 0.2);
        }
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 3rem;
            white-space: pre-wrap;
            background-color: rgba(255, 255, 255, 0.05);
            border-radius: 4px 4px 0 0;
            gap: 1rem;
            padding: 1rem 2rem;
            color: #B2CCD6;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #66B2FF !important;
            color: white !important;
        }
        
        /* Expander styling */
        .streamlit-expanderHeader {
            background-color: rgba(255, 255, 255, 0.05);
            border-radius: 4px;
        }
        
        /* LaTeX equation styling */
        .katex {
            font-size: 1.1em;
            padding: 1rem;
            background-color: rgba(255, 255, 255, 0.05);
            border-radius: 4px;
            margin: 0.5rem 0;
            display: block;
            color: #E6F3FF;
        }
        
        /* Table styling enhancements */
        .mystyle {
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
            transition: all 0.3s ease;
            background-color: rgba(255, 255, 255, 0.05);
        }
        
        .mystyle th {
            background-color: rgba(102, 178, 255, 0.1);
            color: #E6F3FF;
        }
        
        .mystyle td {
            color: #E6F3FF;
        }
        
        .mystyle tr:nth-child(even) {
            background-color: rgba(255, 255, 255, 0.02);
        }
        
        .mystyle tr:hover {
            background-color: rgba(102, 178, 255, 0.1);
        }
        
        /* Additional spacing and formatting */
        .stMarkdown {
            line-height: 1.6;
            color: #E6F3FF;
        }
        
        /* Success/info message styling */
        .stSuccess, .stInfo {
            padding: 1rem;
            border-radius: 4px;
            margin: 1rem 0;
            background-color: rgba(255, 255, 255, 0.05);
        }
        
        /* Divider styling */
        hr {
            border-color: rgba(255, 255, 255, 0.1) !important;
        }
        
        /* Text color for better readability */
        p, li {
            color: #E6F3FF !important;
        }

        /* Make the entire row highlighted when it contains bold text */
        .mystyle tr:has(td:first-child b) {
            background-color: #EBF8FF;  /* Light blue background */
            font-weight: bold;  /* Make all text in highlighted rows bold */
        }

        /* Keep the non-first cells in highlighted rows bold but original color */
        .mystyle tr:has(td:first-child b) td:not(:first-child) {
            color: #000000;  /* Keep the number color black */
            font-weight: bold;
        }

        /* Keep the first cell (with b tag) styled as before */
        .mystyle tr td:first-child b {
            display: block;
            width: 100%;
            background-color: #90CDF4;
            padding: 8px;
            margin: -8px;
            color: #2A4365;
        }
        </style>
    """, unsafe_allow_html=True)

    # Create tabs with better styling
    tab_calculator, tab_explanation = st.tabs(["📊 Calculator", "📖 Explanation"])

    ############################################################################
    #                           TAB 1: CALCULATOR
    ############################################################################
    with tab_calculator:
        st.title("RCF – CLN Calculator")
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # Add a brief introduction
        st.markdown("""
            This calculator helps determine the profitability of Revolving Credit Facilities (RCF) 
            by analyzing both drawn and undrawn portions, costs, and returns.
        """)

        # -----------------
        # Sidebar Inputs
        # -----------------
        st.sidebar.header("User Inputs")

        with st.sidebar.expander("General Inputs", expanded=True):
            st.markdown("""
                <small>These are the primary inputs that define the facility structure.</small>
            """, unsafe_allow_html=True)
            
            company_name = st.text_input(
                "Company Name", 
                value="Burger's Burgers",
                help="Enter the name of the company or facility"
            )

            rcf_limit = st.number_input(
                "RCF Limit (ZAR)",
                min_value=0.0, value=2_000_000_000.0, step=50_000.0,
                help="The total facility limit in South African Rand (ZAR)"
            )

            drawn_percentage = st.number_input(
                "Drawn Percentage (0.00 - 1.00)",
                min_value=0.0, max_value=1.0,
                value=0.35, step=0.05,
                help="The portion of the facility that is currently drawn down (e.g., 0.35 = 35%)"
            )

            cap_cost = st.number_input(
                "Capital Cost (for ROC calculation)",
                min_value=0.0, value=12.0, step=1.0,
                help="The cost of capital used in Return on Capital calculations"
            )

        with st.sidebar.expander("Total Cost (Drawn Portion) Inputs", expanded=True):
            st.markdown("""
                <small>These inputs determine the costs associated with the drawn portion of the facility.</small>
            """, unsafe_allow_html=True)
            
            margin_bps = st.number_input(
                "Margin (bps)", 
                value=250.0,
                help="The margin charged on the drawn portion in basis points"
            )
            
            funding_bps = st.number_input(
                "Funding (bps)", 
                value=-114.0,
                help="The funding cost in basis points (typically negative)"
            )
            
            credit_bps = st.number_input(
                "Credit (bps)", 
                value=-29.0,
                help="The credit cost in basis points (typically negative)"
            )
            
            capital_bps = st.number_input(
                "Capital (bps)", 
                value=-115.0,
                help="The capital cost in basis points (typically negative)"
            )

        with st.sidebar.expander("Commitment Fee (Undrawn) Inputs", expanded=True):
            st.markdown("""
                <small>These inputs determine the costs associated with the undrawn portion of the facility.</small>
            """, unsafe_allow_html=True)
            
            commitment_fee_bps = st.number_input(
                "Commitment Fee (bps)", 
                value=75.0,
                help="The fee charged on the undrawn portion in basis points"
            )
            
            commitment_fee_funding_bps = st.number_input(
                "Commitment Fee Funding (bps)", 
                value=-13.0,
                help="The funding cost for the undrawn portion in basis points"
            )
            
            commitment_fee_credit_bps = st.number_input(
                "Commitment Fee Credit (bps)", 
                value=-12.0,
                help="The credit cost for the undrawn portion in basis points"
            )
            
            commitment_fee_capital_bps = st.number_input(
                "Commitment Fee Capital (bps)", 
                value=-50.0,
                help="The capital cost for the undrawn portion in basis points"
            )

        # CLN Section
        with st.sidebar.expander("CLN Inputs", expanded=True):
            st.markdown("""
                <small>Credit Linked Note (CLN) parameters for credit risk transfer.</small>
            """, unsafe_allow_html=True)

            include_cln = st.checkbox(
                "Include CLN Issuance?",
                value=False,
                help="Enable to include CLN calculations"
            )

            if include_cln:
                cln_amount = st.number_input(
                    "CLN Amount (ZAR)",
                    min_value=0.0, max_value=rcf_limit,
                    value=rcf_limit * 0.15,  # Default to 15% of RCF limit
                    step=50_000.0,
                    help="Amount of credit risk to transfer (cannot exceed RCF limit)"
                )

                cln_cost_bps = st.number_input(
                    "CLN Cost (bps)",
                    min_value=-9999.0, max_value=9999.0,
                    value=-70.0,  # Changed from -50.0
                    help="The cost of issuing the CLN (typically negative)"
                )

                compare_mode = st.radio(
                    "Output Display Mode",
                    ("Show CLN Table Only", "Compare: No CLN vs. CLN", "Single Comparison Table"),
                    help="Choose how to display the CLN scenario results"
                )
            else:
                cln_amount = 0.0
                cln_cost_bps = 0.0
                compare_mode = "Show CLN Table Only"

        # In the sidebar, after the CLN section and before the helpful notes:
        with st.sidebar.expander("⚙️ Settings"):
            decimal_places = st.slider("Decimal Places", 0, 4, 2)
            show_percentages = st.checkbox("Show % Values", value=True)
            dark_mode = st.checkbox("Dark Mode", value=True)

        # Keep existing helpful notes section
        st.sidebar.markdown("---")
        st.sidebar.markdown("""
            <small>💡 **Tips:**
            - Hover over inputs for more information
            - Costs are typically entered as negative values
            - BPS = Basis Points (1% = 100 bps)
            </small>
        """, unsafe_allow_html=True)

        # Calculate Button with description
        calc_btn = st.sidebar.button(
            "Calculate",
            help="Click to calculate the RCF metrics based on the inputs provided"
        )

        if calc_btn:
            # Add a loading message
            with st.spinner('Calculating RCF metrics...'):
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
                net_spread_bps = margin_bps + total_cost_bps

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
                net_spread_commit_fees_zar = undrawn_amount * (net_commit_bps / 10_000)
                net_spread_commit_fees_bps = net_commit_bps

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
                blended_view_credit_bps = (credit_bps * drawn_percentage) + (
                            commitment_fee_credit_bps * undrawn_percentage)

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

            # Add explanatory text above the table
            st.markdown("""
                ### Results Explanation
                - **Bold rows** indicate major sections and totals
                - Negative values are shown in parentheses
                - The Blended View combines both drawn and undrawn portions
            """)

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

            st.subheader("NO CLN Output Table")
            
            # Add html2canvas library and download functionality
            html2canvas_js = """
            <script src="https://html2canvas.hertzen.com/dist/html2canvas.min.js"></script>
            <script>
            function downloadTableAsImage() {
                const table = document.querySelector('.rcf-table');
                html2canvas(table).then(canvas => {
                    const link = document.createElement('a');
                    link.download = 'table.png';
                    link.href = canvas.toDataURL();
                    link.click();
                });
            }
            </script>
            """

            # Define CSS
            custom_css = """
            <style>
            .rcf-table {
                width: 100%;
                border-collapse: collapse;
                font-family: -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", Roboto;
            }

            /* Column Headers */
            .rcf-table thead th {
                background-color: #4A5568;
                color: white;
                padding: 12px 16px;
                text-align: left;
                font-weight: 500;
                border: 1px solid #2D3748;
            }

            /* All cells */
            .rcf-table td {
                padding: 8px 16px;
                border: 1px solid #E2E8F0;
            }

            /* Section headers (blue background) */
            .rcf-table tr.section-header {
                background-color: #EBF8FF;
            }
            .rcf-table tr.section-header td {
                color: #2C5282;
                font-weight: 600;
            }

            /* Regular rows */
            .rcf-table tr:not(.section-header) {
                background-color: white;
            }

            /* Number columns */
            .rcf-table td:nth-child(2),
            .rcf-table td:nth-child(3) {
                text-align: right;
                font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
            }

            /* Negative numbers */
            .rcf-table td:nth-child(2),
            .rcf-table td:nth-child(3) {
                color: #2D3748;
            }

            /* Empty rows */
            .rcf-table tr:has(td:empty) {
                height: 8px;
                background-color: white;
            }
            </style>
            """

            # Build the table HTML
            df = pd.DataFrame(rows, columns=["Item", "ZAR", "BPS"])
            df["ZAR"] = df["ZAR"].apply(format_negatives)
            df["BPS"] = df["BPS"].apply(format_negatives)
            html_table = df.to_html(index=False, border=0, escape=False)
            html_table = html_table.replace('class="dataframe"', 'class="rcf-table"')
            html_table = html_table.replace('<tr>', '<tr class="data-row">')
            html_table = html_table.replace('<tr class="data-row"><td><b>', '<tr class="section-header"><td><b>')

            # Add download image button to HTML with full width styling
            screenshot_button = """
            <button onclick="downloadTableAsImage()" 
                    style="width: 100%; padding: 12px 20px; 
                    background-color: #2B6CB0; color: white; 
                    border: none; border-radius: 4px; 
                    cursor: pointer; font-family: -apple-system, system-ui;
                    font-size: 14px; font-weight: 500;
                    margin: 10px 0;">
                📸 Download as Image
            </button>
            """

            # Add CSS for Streamlit button to match
            st.markdown("""
                <style>
                .stDownloadButton button {
                    width: 100% !important;
                    padding: 12px 20px !important;
                    background-color: #2B6CB0 !important;
                    color: white !important;
                    border: none !important;
                    border-radius: 4px !important;
                    font-size: 14px !important;
                    font-weight: 500 !important;
                    margin: 0 !important;  /* Remove all margins */
                }
                .stDownloadButton {
                    margin: 0 !important;  /* Remove container margins too */
                    padding: 0 !important;  /* Remove container padding */
                }
                </style>
            """, unsafe_allow_html=True)

            # Add CSV download button at the top
            st.download_button(
                label="📊 Download CSV",
                data=df.to_csv(index=False).encode('utf-8'),
                file_name=f"{company_name}_rcf_cln_calculation.csv",
                mime='text/csv'
            )

            # Display table with image download button at bottom
            final_html = html2canvas_js + custom_css + html_table + screenshot_button
            components.html(final_html, height=1000, scrolling=True)

            # Add context after the table and buttons
            st.markdown("""
                <small>
                ℹ️ **Note:** The table above shows:
                - Drawn portion calculations (margin and costs)
                - Undrawn portion calculations (commitment fees)
                - Blended view combining both portions
                - Return on Capital (ROC) metrics
                </small>
            """, unsafe_allow_html=True)

            # CLN Calculations (if enabled)
            if include_cln and cln_amount > 0:
                # Ensure CLN amount doesn't exceed limit
                cln_amount = min(cln_amount, rcf_limit)
                cln_percentage = cln_amount / rcf_limit

                # CLN margin (same as base)
                cln_margin_bps = margin_bps
                cln_margin_zar = drawn_amount * (cln_margin_bps / 10_000)

                # Funding same as no cln
                cln_funding_bps = funding_bps
                cln_funding_zar = funding_zar

                # Credit, capital scaled by (1 - cln_percentage)
                cln_credit_bps = credit_bps * (1 - cln_percentage)
                cln_credit_zar = drawn_amount * (cln_credit_bps / 10_000)

                cln_capital_bps = capital_bps * (1 - cln_percentage)
                cln_capital_zar = drawn_amount * (cln_capital_bps / 10_000)

                # First calculate CLN specific costs
                cln_specific_cost_zar = cln_amount * (cln_cost_bps / 10_000)  # G17

                # Calculate CLN Total Cost
                cln_total_cost_bps = cln_funding_bps + cln_credit_bps + cln_capital_bps
                cln_total_cost_zar = drawn_amount * (cln_total_cost_bps / 10_000)

                # Calculate CLN Net Spread
                cln_net_spread_zar = cln_margin_zar + cln_total_cost_zar
                cln_net_spread_bps = cln_margin_bps + cln_total_cost_bps

                # Calculate CLN Commitment Fee components
                cln_commitment_fee_bps = commitment_fee_bps  # Same as No CLN
                cln_commitment_fee_zar = undrawn_amount * (cln_commitment_fee_bps / 10_000)

                cln_comm_fee_funding_bps = commitment_fee_funding_bps  # Same as No CLN
                cln_comm_fee_funding_zar = undrawn_amount * (cln_comm_fee_funding_bps / 10_000)

                # Scale commitment fee credit & capital
                cln_commit_fee_credit_bps = commitment_fee_credit_bps * (1 - cln_percentage)
                cln_commit_fee_credit_zar = undrawn_amount * (cln_commit_fee_credit_bps / 10_000)

                cln_commit_fee_capital_bps = commitment_fee_capital_bps * (1 - cln_percentage)
                cln_commit_fee_capital_zar = undrawn_amount * (cln_commit_fee_capital_bps / 10_000)

                # Calculate Net Spread for Commitment Fees
                cln_commit_fee_total_bps = (
                        cln_commitment_fee_bps  # Fee
                        + cln_comm_fee_funding_bps  # Funding
                        + cln_commit_fee_credit_bps  # Credit
                        + cln_commit_fee_capital_bps  # Capital
                )

                # Calculate Net Spread BPS and ZAR
                cln_net_commit_fee_bps = cln_commit_fee_total_bps
                cln_net_commit_fee_zar = undrawn_amount * (cln_net_commit_fee_bps / 10_000)

                # Calculate Blended View components
                cln_blended_margin_zar = cln_margin_zar + cln_commitment_fee_zar
                cln_blended_margin_bps = (cln_margin_bps * drawn_percentage) + (commitment_fee_bps * undrawn_percentage)

                cln_blended_funding_zar = cln_funding_zar + cln_comm_fee_funding_zar
                cln_blended_funding_bps = (cln_funding_bps * drawn_percentage) + (
                            cln_comm_fee_funding_bps * undrawn_percentage)

                cln_blended_credit_zar = cln_credit_zar + cln_commit_fee_credit_zar
                cln_blended_credit_bps = (cln_credit_bps * drawn_percentage) + (
                            cln_commit_fee_credit_bps * undrawn_percentage)

                cln_blended_capital_zar = cln_capital_zar + cln_commit_fee_capital_zar
                cln_blended_capital_bps = (cln_capital_bps * drawn_percentage) + (
                            cln_commit_fee_capital_bps * undrawn_percentage)

                # CLN Cost for Blended View
                blended_cln_cost_zar = cln_specific_cost_zar  # G22 = G17
                blended_cln_cost_bps = cln_cost_bps * cln_percentage  # H22 = H17 * CLN%

                # Now calculate net revenue
                cln_blended_netrev_zar = (
                        cln_blended_margin_zar  # Margin (positive)
                        + cln_blended_funding_zar  # Funding (negative)
                        + blended_cln_cost_zar  # CLN Cost (negative)
                        + cln_blended_credit_zar  # Credit (negative)
                        + cln_blended_capital_zar  # Capital (negative)
                )

                cln_blended_netrev_bps = (
                        cln_blended_margin_bps  # Margin (positive)
                        + cln_blended_funding_bps  # Funding (negative)
                        + blended_cln_cost_bps  # CLN Cost (negative)
                        + cln_blended_credit_bps  # Credit (negative)
                        + cln_blended_capital_bps  # Capital (negative)
                )

                # Calculate ROC for CLN scenario
                if cln_blended_capital_bps != 0:
                    cln_roc_bps = (
                            (cln_blended_margin_bps
                             + cln_blended_funding_bps
                             + blended_cln_cost_bps
                             + cln_blended_credit_bps)
                            / (-cln_blended_capital_bps)
                            * cap_cost
                    )
                else:
                    cln_roc_bps = 0

                # CLN rows definition with correct indentation
                cln_rows = [
                    {"Item": "<b>CLN Scenario</b>", "ZAR": "", "BPS": ""},
                    {"Item": "CLN Amount", "ZAR": cln_amount, "BPS": f"{cln_percentage * 100:.0f}%"},
                    {"Item": "<b>Margin</b>", "ZAR": cln_margin_zar, "BPS": cln_margin_bps},
                    {"Item": "<b>Total Cost</b>", "ZAR": cln_total_cost_zar, "BPS": cln_total_cost_bps},
                    {"Item": "Funding", "ZAR": cln_funding_zar, "BPS": cln_funding_bps},
                    {"Item": "Credit", "ZAR": cln_credit_zar, "BPS": cln_credit_bps},
                    {"Item": "Capital", "ZAR": cln_capital_zar, "BPS": cln_capital_bps},
                    {"Item": "<b>Net Spread</b>", "ZAR": cln_net_spread_zar, "BPS": cln_net_spread_bps},
                    {"Item": "", "ZAR": "", "BPS": ""},
                    {"Item": "<b>Commitment Fee</b>", "ZAR": cln_commitment_fee_zar, "BPS": cln_commitment_fee_bps},
                    {"Item": "Funding", "ZAR": cln_comm_fee_funding_zar, "BPS": cln_comm_fee_funding_bps},
                    {"Item": "Credit Cost", "ZAR": cln_commit_fee_credit_zar, "BPS": cln_commit_fee_credit_bps},
                    {"Item": "Capital Cost", "ZAR": cln_commit_fee_capital_zar, "BPS": cln_commit_fee_capital_bps},
                    {"Item": "<b>Net Spread</b>", "ZAR": cln_net_commit_fee_zar, "BPS": cln_net_commit_fee_bps},
                    {"Item": "", "ZAR": "", "BPS": ""},
                    {"Item": "<b>CLN Cost</b>", "ZAR": cln_specific_cost_zar, "BPS": cln_cost_bps},
                    {"Item": "", "ZAR": "", "BPS": ""},
                    {"Item": "<b>Blended View</b>", "ZAR": "", "BPS": ""},
                    {"Item": "Margin", "ZAR": cln_blended_margin_zar, "BPS": cln_blended_margin_bps},
                    {"Item": "Funding", "ZAR": cln_blended_funding_zar, "BPS": cln_blended_funding_bps},
                    {"Item": "CLN Cost", "ZAR": blended_cln_cost_zar, "BPS": blended_cln_cost_bps},
                    {"Item": "Credit", "ZAR": cln_blended_credit_zar, "BPS": cln_blended_credit_bps},
                    {"Item": "Capital", "ZAR": cln_blended_capital_zar, "BPS": cln_blended_capital_bps},
                    {"Item": "<b>Net Revenue</b>", "ZAR": cln_blended_netrev_zar, "BPS": cln_blended_netrev_bps},
                    {"Item": "<b>ROC (bps)</b>", "ZAR": "", "BPS": cln_roc_bps},
                    {"Item": "", "ZAR": "", "BPS": ""},
                    {"Item": "<b>Facility Amount</b>", "ZAR": rcf_limit, "BPS": "100%"},
                    {"Item": "<b>Drawn</b>", "ZAR": drawn_amount, "BPS": f"{drawn_percentage * 100:.0f}%"},
                    {"Item": "<b>Undrawn</b>", "ZAR": undrawn_amount, "BPS": f"{undrawn_percentage * 100:.0f}%"}
                ]

                # Then use the display mode check
                if compare_mode == "Show CLN Table Only":
                    st.subheader("CLN Scenario Results")
                    
                    # Add CSV download button ABOVE the table (full width)
                    st.download_button(
                        label="📊 Download CSV",
                        data=pd.DataFrame(cln_rows).to_csv(index=False).encode('utf-8'),
                        file_name=f"{company_name}_cln_scenario.csv",
                        mime='text/csv',
                        use_container_width=True
                    )
                    
                    # Display table
                    df_cln = pd.DataFrame(cln_rows)
                    display_table(df_cln)
                    
                    # Add image download button BELOW the table
                    html2canvas_js = """
                    <script src="https://html2canvas.hertzen.com/dist/html2canvas.min.js"></script>
                    <script>
                    function downloadTableImage() {
                        const table = document.querySelector('.rcf-table');
                        const options = {
                            scale: 2,
                            useCORS: true,
                            backgroundColor: '#ffffff'
                        };
                        
                        html2canvas(table, options).then(canvas => {
                            const image = canvas.toDataURL('image/png', 1.0);
                            const link = document.createElement('a');
                            link.href = image;
                            link.download = 'comparison_table.png';
                            document.body.appendChild(link);
                            link.click();
                            document.body.removeChild(link);
                        });
                    }
                    </script>
                    <div style='width: 100%; padding: 10px 0;'>
                        <button onclick="downloadTableImage()" 
                                style="width: 100%;
                                       background-color: rgb(43, 108, 176);
                                       color: white;
                                       padding: 0.6rem 0.6rem;
                                       border: none;
                                       border-radius: 0.25rem;
                                       cursor: pointer;
                                       font-weight: 500;
                                       font-size: 1rem;
                                       line-height: 1.4;
                                       transition: background-color 0.2s;">
                            📷 Download Image
                        </button>
                    </div>
                    """
                    components.html(html2canvas_js, height=70)
                elif compare_mode == "Compare: No CLN vs. CLN":
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("No CLN Scenario")
                        # Add CSV download button
                        st.download_button(
                            label="📊 Download No CLN CSV",
                            data=pd.DataFrame(rows).to_csv(index=False).encode('utf-8'),
                            file_name=f"{company_name}_no_cln.csv",
                            mime='text/csv',
                            use_container_width=True
                        )
                        # Display table
                        df_no_cln = pd.DataFrame(rows)
                        display_table(df_no_cln)
                        
                    with col2:
                        st.subheader("CLN Scenario")
                        # Add CSV download button
                        st.download_button(
                            label="📊 Download CLN CSV",
                            data=pd.DataFrame(cln_rows).to_csv(index=False).encode('utf-8'),
                            file_name=f"{company_name}_cln.csv",
                            mime='text/csv',
                            use_container_width=True
                        )
                        # Display table
                        df_cln = pd.DataFrame(cln_rows)
                        display_table(df_cln)

                    # Add image download button for both tables
                    html2canvas_js = """
                    <script src="https://html2canvas.hertzen.com/dist/html2canvas.min.js"></script>
                    <script>
                    function downloadTableImage() {
                        const tables = document.querySelectorAll('.rcf-table');
                        let combinedCanvas = document.createElement('canvas');
                        let ctx = combinedCanvas.getContext('2d');
                        let totalWidth = 0;
                        let maxHeight = 0;
                        
                        Promise.all(Array.from(tables).map(table => 
                            html2canvas(table, {
                                scale: 2,
                                useCORS: true,
                                backgroundColor: '#ffffff'
                            })
                        )).then(canvases => {
                            totalWidth = canvases.reduce((sum, canvas) => sum + canvas.width, 0);
                            maxHeight = Math.max(...canvases.map(canvas => canvas.height));
                            
                            combinedCanvas.width = totalWidth;
                            combinedCanvas.height = maxHeight;
                            
                            let xOffset = 0;
                            canvases.forEach(canvas => {
                                ctx.drawImage(canvas, xOffset, 0);
                                xOffset += canvas.width;
                            });
                            
                            const link = document.createElement('a');
                            link.href = combinedCanvas.toDataURL('image/png', 1.0);
                            link.download = 'comparison_tables.png';
                            document.body.appendChild(link);
                            link.click();
                            document.body.removeChild(link);
                        });
                    }
                    </script>
                    <div style='width: 100%; padding: 10px 0;'>
                        <button onclick="downloadTableImage()" 
                                style="width: 100%;
                                       background-color: rgb(43, 108, 176);
                                       color: white;
                                       padding: 0.6rem 0.6rem;
                                       border: none;
                                       border-radius: 0.25rem;
                                       cursor: pointer;
                                       font-weight: 500;
                                       font-size: 1rem;
                                       line-height: 1.4;
                                       transition: background-color 0.2s;">
                            📷 Download Image
                        </button>
                    </div>
                    """
                    components.html(html2canvas_js, height=70)
                elif compare_mode == "Single Comparison Table":
                    st.subheader("CLN Comparison Analysis")
                    
                    # Create the comparison table structure
                    comparison_rows = [
                        {"Item": f"{company_name}", "NO CLN_ZAR": "", "NO CLN_bps": "", f"R{cln_amount:,.0f} CLN_ZAR": "", f"R{cln_amount:,.0f} CLN_bps": "", "Differential": "", "bps": ""},
                        # Drawn portion
                        {"Item": "Margin", "NO CLN_ZAR": margin_zar, "NO CLN_bps": margin_bps, 
                         f"R{cln_amount:,.0f} CLN_ZAR": cln_margin_zar, f"R{cln_amount:,.0f} CLN_bps": cln_margin_bps, 
                         "Differential": cln_margin_zar - margin_zar, "bps": cln_margin_bps - margin_bps},
                        {"Item": "Total Cost", "NO CLN_ZAR": total_cost_zar, "NO CLN_bps": total_cost_bps, 
                         f"R{cln_amount:,.0f} CLN_ZAR": cln_total_cost_zar, f"R{cln_amount:,.0f} CLN_bps": cln_total_cost_bps, 
                         "Differential": cln_total_cost_zar - total_cost_zar, "bps": cln_total_cost_bps - total_cost_bps},
                        {"Item": "Funding", "NO CLN_ZAR": funding_zar, "NO CLN_bps": funding_bps, 
                         f"R{cln_amount:,.0f} CLN_ZAR": cln_funding_zar, f"R{cln_amount:,.0f} CLN_bps": cln_funding_bps, 
                         "Differential": cln_funding_zar - funding_zar, "bps": cln_funding_bps - funding_bps},
                        {"Item": "Credit", "NO CLN_ZAR": credit_zar, "NO CLN_bps": credit_bps, 
                         f"R{cln_amount:,.0f} CLN_ZAR": cln_credit_zar, f"R{cln_amount:,.0f} CLN_bps": cln_credit_bps, 
                         "Differential": cln_credit_zar - credit_zar, "bps": cln_credit_bps - credit_bps},
                        {"Item": "Capital", "NO CLN_ZAR": capital_zar, "NO CLN_bps": capital_bps, 
                         f"R{cln_amount:,.0f} CLN_ZAR": cln_capital_zar, f"R{cln_amount:,.0f} CLN_bps": cln_capital_bps, 
                         "Differential": cln_capital_zar - capital_zar, "bps": cln_capital_bps - capital_bps},
                        {"Item": "Net Spread", "NO CLN_ZAR": net_spread_zar, "NO CLN_bps": net_spread_bps, 
                         f"R{cln_amount:,.0f} CLN_ZAR": cln_net_spread_zar, f"R{cln_amount:,.0f} CLN_bps": cln_net_spread_bps, 
                         "Differential": cln_net_spread_zar - net_spread_zar, "bps": cln_net_spread_bps - net_spread_bps},
                        # Empty row
                        {"Item": "", "NO CLN_ZAR": "", "NO CLN_bps": "", f"R{cln_amount:,.0f} CLN_ZAR": "", f"R{cln_amount:,.0f} CLN_bps": "", "Differential": "", "bps": ""},
                        # Commitment Fee section
                        {"Item": "Commitment fee", "NO CLN_ZAR": commitment_fee_zar, "NO CLN_bps": commitment_fee_bps, 
                         f"R{cln_amount:,.0f} CLN_ZAR": cln_commitment_fee_zar, f"R{cln_amount:,.0f} CLN_bps": cln_commitment_fee_bps, 
                         "Differential": cln_commitment_fee_zar - commitment_fee_zar, "bps": cln_commitment_fee_bps - commitment_fee_bps},
                        {"Item": "Funding", "NO CLN_ZAR": comm_fee_funding_zar, "NO CLN_bps": commitment_fee_funding_bps,
                         f"R{cln_amount:,.0f} CLN_ZAR": cln_comm_fee_funding_zar, f"R{cln_amount:,.0f} CLN_bps": cln_comm_fee_funding_bps,
                         "Differential": cln_comm_fee_funding_zar - comm_fee_funding_zar, "bps": cln_comm_fee_funding_bps - commitment_fee_funding_bps},
                        {"Item": "Credit Cost", "NO CLN_ZAR": comm_fee_credit_zar, "NO CLN_bps": commitment_fee_credit_bps,
                         f"R{cln_amount:,.0f} CLN_ZAR": cln_commit_fee_credit_zar, f"R{cln_amount:,.0f} CLN_bps": cln_commit_fee_credit_bps,
                         "Differential": cln_commit_fee_credit_zar - comm_fee_credit_zar, "bps": cln_commit_fee_credit_bps - commitment_fee_credit_bps},
                        {"Item": "Capital Cost", "NO CLN_ZAR": comm_fee_capital_zar, "NO CLN_bps": commitment_fee_capital_bps,
                         f"R{cln_amount:,.0f} CLN_ZAR": cln_commit_fee_capital_zar, f"R{cln_amount:,.0f} CLN_bps": cln_commit_fee_capital_bps,
                         "Differential": cln_commit_fee_capital_zar - comm_fee_capital_zar, "bps": cln_commit_fee_capital_bps - commitment_fee_capital_bps},
                        {"Item": "Net Spread", "NO CLN_ZAR": net_spread_commit_fees_zar, "NO CLN_bps": net_spread_commit_fees_bps,
                         f"R{cln_amount:,.0f} CLN_ZAR": cln_net_commit_fee_zar, f"R{cln_amount:,.0f} CLN_bps": cln_net_commit_fee_bps,
                         "Differential": cln_net_commit_fee_zar - net_spread_commit_fees_zar, "bps": cln_net_commit_fee_bps - net_spread_commit_fees_bps},
                        # Empty row
                        {"Item": "", "NO CLN_ZAR": "", "NO CLN_bps": "", f"R{cln_amount:,.0f} CLN_ZAR": "", f"R{cln_amount:,.0f} CLN_bps": "", "Differential": "", "bps": ""},
                        # CLN Cost
                        {"Item": "CLN Cost", "NO CLN_ZAR": "-", "NO CLN_bps": "-",
                         f"R{cln_amount:,.0f} CLN_ZAR": cln_specific_cost_zar, f"R{cln_amount:,.0f} CLN_bps": cln_cost_bps,
                         "Differential": cln_specific_cost_zar, "bps": cln_cost_bps},
                        # Empty row
                        {"Item": "", "NO CLN_ZAR": "", "NO CLN_bps": "", f"R{cln_amount:,.0f} CLN_ZAR": "", f"R{cln_amount:,.0f} CLN_bps": "", "Differential": "", "bps": ""},
                        # Blended View
                        {"Item": "Blended View", "NO CLN_ZAR": "", "NO CLN_bps": "", f"R{cln_amount:,.0f} CLN_ZAR": "", f"R{cln_amount:,.0f} CLN_bps": "", "Differential": "", "bps": ""},
                        {"Item": "Margin", "NO CLN_ZAR": blended_view_margin_zar, "NO CLN_bps": blended_view_margin_bps,
                         f"R{cln_amount:,.0f} CLN_ZAR": cln_blended_margin_zar, f"R{cln_amount:,.0f} CLN_bps": cln_blended_margin_bps,
                         "Differential": cln_blended_margin_zar - blended_view_margin_zar, "bps": cln_blended_margin_bps - blended_view_margin_bps},
                        {"Item": "Funding", "NO CLN_ZAR": blended_view_funding_zar, "NO CLN_bps": blended_view_funding_bps,
                         f"R{cln_amount:,.0f} CLN_ZAR": cln_blended_funding_zar, f"R{cln_amount:,.0f} CLN_bps": cln_blended_funding_bps,
                         "Differential": cln_blended_funding_zar - blended_view_funding_zar, "bps": cln_blended_funding_bps - blended_view_funding_bps},
                        {"Item": "CLN Cost", "NO CLN_ZAR": "-", "NO CLN_bps": "-",
                         f"R{cln_amount:,.0f} CLN_ZAR": blended_cln_cost_zar, f"R{cln_amount:,.0f} CLN_bps": blended_cln_cost_bps,
                         "Differential": blended_cln_cost_zar, "bps": blended_cln_cost_bps},
                        {"Item": "Credit", "NO CLN_ZAR": blended_view_credit_zar, "NO CLN_bps": blended_view_credit_bps,
                         f"R{cln_amount:,.0f} CLN_ZAR": cln_blended_credit_zar, f"R{cln_amount:,.0f} CLN_bps": cln_blended_credit_bps,
                         "Differential": cln_blended_credit_zar - blended_view_credit_zar, "bps": cln_blended_credit_bps - blended_view_credit_bps},
                        {"Item": "Capital", "NO CLN_ZAR": blended_view_capital_zar, "NO CLN_bps": blended_view_capital_bps,
                         f"R{cln_amount:,.0f} CLN_ZAR": cln_blended_capital_zar, f"R{cln_amount:,.0f} CLN_bps": cln_blended_capital_bps,
                         "Differential": cln_blended_capital_zar - blended_view_capital_zar, "bps": cln_blended_capital_bps - blended_view_capital_bps},
                        {"Item": "Net Revenue", "NO CLN_ZAR": blended_view_net_revenue_zar, "NO CLN_bps": blended_view_net_revenue_bps,
                         f"R{cln_amount:,.0f} CLN_ZAR": cln_blended_netrev_zar, f"R{cln_amount:,.0f} CLN_bps": cln_blended_netrev_bps,
                         "Differential": cln_blended_netrev_zar - blended_view_net_revenue_zar, "bps": cln_blended_netrev_bps - blended_view_net_revenue_bps},
                        {"Item": "", "NO CLN_ZAR": "", "NO CLN_bps": "", f"R{cln_amount:,.0f} CLN_ZAR": "", f"R{cln_amount:,.0f} CLN_bps": "", "Differential": "", "bps": ""},
                        
                        # ROC
                        {"Item": "ROC", "NO CLN_ZAR": "", "NO CLN_bps": f"{blended_view_roc_bps:.2f}%",
                         f"R{cln_amount:,.0f} CLN_ZAR": "", f"R{cln_amount:,.0f} CLN_bps": "⚠" if cln_roc_bps > 999 else f"{cln_roc_bps:.2f}%",
                         "Differential": "", "bps": "⚠" if cln_roc_bps > 999 else f"{(cln_roc_bps - blended_view_roc_bps):.2f}%"},
                        {"Item": "", "NO CLN_ZAR": "", "NO CLN_bps": "", f"R{cln_amount:,.0f} CLN_ZAR": "", f"R{cln_amount:,.0f} CLN_bps": "", "Differential": "", "bps": ""},
                        
                        # Facility Information
                        {"Item": "Facility Amount", "NO CLN_ZAR": rcf_limit, "NO CLN_bps": "100%",
                         f"R{cln_amount:,.0f} CLN_ZAR": rcf_limit, f"R{cln_amount:,.0f} CLN_bps": "100%", "Differential": "", "bps": ""},
                        {"Item": "Drawn", "NO CLN_ZAR": drawn_amount, "NO CLN_bps": f"{drawn_percentage*100:.0f}%",
                         f"R{cln_amount:,.0f} CLN_ZAR": drawn_amount, f"R{cln_amount:,.0f} CLN_bps": f"{drawn_percentage*100:.0f}%", "Differential": "", "bps": ""},
                        {"Item": "Undrawn", "NO CLN_ZAR": undrawn_amount, "NO CLN_bps": f"{undrawn_percentage*100:.0f}%",
                         f"R{cln_amount:,.0f} CLN_ZAR": undrawn_amount, f"R{cln_amount:,.0f} CLN_bps": f"{undrawn_percentage*100:.0f}%", "Differential": "", "bps": ""},
                        {"Item": "", "NO CLN_ZAR": "", "NO CLN_bps": "", f"R{cln_amount:,.0f} CLN_ZAR": "", f"R{cln_amount:,.0f} CLN_bps": "", "Differential": "", "bps": ""},
                        
                        # CLN Note
                        {"Item": "CLN Note", "NO CLN_ZAR": "-", "NO CLN_bps": "0%",
                         f"R{cln_amount:,.0f} CLN_ZAR": cln_amount, f"R{cln_amount:,.0f} CLN_bps": f"{cln_percentage*100:.0f}%", "Differential": "", "bps": ""}
                    ]
                    
                    # Add CSV download button ABOVE the table (full width)
                    st.download_button(
                        label="📊 Download CSV",
                        data=pd.DataFrame(comparison_rows).to_csv(index=False).encode('utf-8'),
                        file_name=f"{company_name}_cln_comparison.csv",
                        mime='text/csv',
                        use_container_width=True
                    )
                    
                    # Display the table
                    df_comparison = pd.DataFrame(comparison_rows)
                    display_table(df_comparison)
                    
                    # Add image download button BELOW the table with fixed JavaScript
                    html2canvas_js = """
                    <script src="https://html2canvas.hertzen.com/dist/html2canvas.min.js"></script>
                    <script>
                    function downloadTableImage() {
                        const table = document.querySelector('.rcf-table');
                        const options = {
                            scale: 2,
                            useCORS: true,
                            backgroundColor: '#ffffff'
                        };
                        
                        html2canvas(table, options).then(canvas => {
                            const image = canvas.toDataURL('image/png', 1.0);
                            const link = document.createElement('a');
                            link.href = image;
                            link.download = 'comparison_table.png';
                            document.body.appendChild(link);
                            link.click();
                            document.body.removeChild(link);
                        });
                    }
                    </script>
                    <div style='width: 100%; padding: 10px 0;'>
                        <button onclick="downloadTableImage()" 
                                style="width: 100%;
                                       background-color: rgb(43, 108, 176);
                                       color: white;
                                       padding: 0.6rem 0.6rem;
                                       border: none;
                                       border-radius: 0.25rem;
                                       cursor: pointer;
                                       font-weight: 500;
                                       font-size: 1rem;
                                       line-height: 1.4;
                                       transition: background-color 0.2s;">
                            📷 Download Image
                        </button>
                    </div>
                    """
                    
                    components.html(html2canvas_js, height=70)

    ############################################################################
    #                           TAB 2: EXPLANATION
    ############################################################################
    with tab_explanation:
        st.title("Understanding the Calculations")
        
        # Add a subtle divider
        st.markdown("<hr style='margin: 2rem 0; border: none; border-top: 1px solid #f0f0f0;'>", unsafe_allow_html=True)

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
        st.latex(
            r"\text{Funding (ZAR)} = \text{Undrawn Amount} \times \frac{\text{Commitment Fee Funding (bps)}}{10,000}")
        
        st.markdown("2. **Credit Cost**")
        st.latex(
            r"\text{Credit (ZAR)} = \text{Undrawn Amount} \times \frac{\text{Commitment Fee Credit (bps)}}{10,000}")
        
        st.markdown("3. **Capital Cost**")
        st.latex(
            r"\text{Capital (ZAR)} = \text{Undrawn Amount} \times \frac{\text{Commitment Fee Capital (bps)}}{10,000}")

        # Blended View Calculations
        st.markdown("## Blended View")
        st.write("The blended view combines both drawn and undrawn portions:")
        
        st.markdown("### Net Revenue")
        st.latex(
            r"\text{Net Revenue (ZAR)} = \text{Margin} + \text{Funding} + \text{CLN} + \text{Credit} + \text{Capital}")
        st.write("Where each component combines both drawn and undrawn portions.")
        
        st.markdown("### Return on Capital (ROC)")
        st.write("ROC is calculated as:")
        st.latex(
            r"\text{ROC (bps)} = \frac{\text{Margin} + \text{Funding} + \text{CLN} + \text{Credit}}{-\text{Capital}} \times \text{Capital Cost}")
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
