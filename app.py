import streamlit as st
import subprocess
import tempfile
import shutil
import os

def generate_latex_pdf(equation: str, output_filepath: str,
                       color: str = "black", fontsize: float = 8.0, font_package: str = "lmodern"):
    """
    Generates a cropped PDF from a LaTeX equation.
    """
    color_def = ""
    color_cmd = f"\\color{{{color}}}"
    if color.startswith("#"):
        hex_val = color.lstrip("#")
        color_def = f"\\definecolor{{mycolor}}{{HTML}}{{{hex_val}}}"
        color_cmd = "\\color{mycolor}"

    tex_template = f"""\\documentclass[10pt, border=1pt]{{standalone}}
\\usepackage{{{font_package}}}
\\usepackage{{amsmath, amssymb}}
\\usepackage{{bm}}
\\usepackage{{xcolor}}
\\definecolor{{gpred}}{{HTML}}{{DE4968}}
\\definecolor{{gpyellow}}{{HTML}}{{F8CD6C}}
\\definecolor{{gporange}}{{HTML}}{{F1A376}}
{color_def}

\\begin{{document}}
\\fontsize{{{fontsize}pt}}{{{fontsize * 1.2:.2f}pt}}\\selectfont
{color_cmd}
$\\displaystyle {equation} $
\\end{{document}}
"""

    with tempfile.TemporaryDirectory() as temp_dir:
        tex_filepath = os.path.join(temp_dir, 'equation.tex')
        with open(tex_filepath, 'w', encoding='utf-8') as f:
            f.write(tex_template)
        
        try:
            subprocess.run(
                ['pdflatex', '-interaction=nonstopmode', 'equation.tex'],
                cwd=temp_dir,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        except subprocess.CalledProcessError as e:
            st.error("LaTeX compilation failed! Check your syntax.")
            with st.expander("Show Error Log"):
                st.code(e.stdout.decode('utf-8'))
            return False

        temp_pdf_path = os.path.join(temp_dir, 'equation.pdf')
        if os.path.exists(temp_pdf_path):
            shutil.copy(temp_pdf_path, output_filepath)
            return True
        return False

# --- Web App UI ---

st.title("LaTeX to PDF Generator")

# 1. Inputs
col1, col2, col3 = st.columns(3)
with col1:
    user_color = st.color_picker("Pick a Text Color", "#DE4968")
with col2:
    user_fontsize = st.slider("Font Size (pt)", min_value=4.0, max_value=48.0, value=12.0, step=0.5)
with col3:
    font_options = {
        "Computer Modern (Default)": "lmodern",
        "Times / MathPTMX": "mathptmx",
        "Palatino": "mathpazo"
    }
    selected_font_label = st.selectbox("Font Type", list(font_options.keys()))
    user_font_package = font_options[selected_font_label]

user_equation = st.text_area(
    "LaTeX Equation (without $ signs)", 
    r"\bm{x}_{n+1} = \underset{\bm{x}}{\operatorname{argmax}}\,\alpha"
)

# 2. Live Preview
st.subheader("Live Web Preview")
st.latex(user_equation)
st.caption("Note: Preview uses standard web fonts. PDF export will use your selected LaTeX font and color.")

# 3. Export & Download
if st.button("Render PDF"):
    with st.spinner("Compiling LaTeX..."):
        # We save to a temporary file first
        temp_out = os.path.join(tempfile.gettempdir(), "final_equation.pdf")
        
        success = generate_latex_pdf(
            equation=user_equation, 
            output_filepath=temp_out, 
            color=user_color, 
            fontsize=user_fontsize,
            font_package=user_font_package
        )

        if success:
            st.success("PDF generated successfully!")
            
            # Read the PDF into memory so Streamlit can trigger the browser download
            with open(temp_out, "rb") as pdf_file:
                pdf_bytes = pdf_file.read()
            
            st.download_button(
                label="📥 Save PDF to Downloads",
                data=pdf_bytes,
                file_name="equation.pdf",
                mime="application/pdf"
            )