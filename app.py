import streamlit as st
import subprocess
import tempfile
import shutil
import os
import base64
from st_clickable_images import clickable_images

def generate_latex_pdf(equation: str, output_filepath: str,
                       palette: dict, bg_color: str, base_text_color: str,
                       fontsize: float = 8.0, font_package: str = "lmodern"):
    color_defs = ""
    for name, hex_val in palette.items():
        clean_hex = hex_val.lstrip("#")
        color_defs += f"\\definecolor{{{name}}}{{HTML}}{{{clean_hex}}}\n"

    bg_hex = bg_color.lstrip("#")
    text_hex = base_text_color.lstrip("#")
    color_defs += f"\\definecolor{{pagebg}}{{HTML}}{{{bg_hex}}}\n"
    color_defs += f"\\definecolor{{maintext}}{{HTML}}{{{text_hex}}}\n"

    tex_template = f"""\\documentclass[10pt, border=5pt]{{standalone}}
\\usepackage{{{font_package}}}
\\usepackage{{amsmath, amssymb, amsfonts}}
\\usepackage{{bm}}
\\usepackage{{xcolor}}
{color_defs}
\\begin{{document}}
\\pagecolor{{pagebg}}
\\color{{maintext}}
\\fontsize{{{fontsize}pt}}{{{fontsize * 1.2:.2f}pt}}\\selectfont
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
                cwd=temp_dir, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
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
st.set_page_config(layout="wide")
st.title("Advanced LaTeX to PDF Editor")

# Sidebar
st.sidebar.header("🎨 Colors & Canvas")

# Place canvas settings side-by-side
col1, col2 = st.sidebar.columns(2)
user_bg_color = col1.color_picker("Canvas", "#1A1A1A")
user_base_text = col2.color_picker("Text", "#FFFFFF")

st.sidebar.markdown("**Custom Highlight Palette**")

# Place highlight colors in a 2x2 grid
col3, col4 = st.sidebar.columns(2)
c1 = col3.color_picker("`colorA`", "#DE4968")
c2 = col4.color_picker("`colorB`", "#F8CD6C")

col5, col6 = st.sidebar.columns(2)
c3 = col5.color_picker("`colorC`", "#F1A376")
c4 = col6.color_picker("`colorD`", "#4D89F8")

user_palette = {"colorA": c1, "colorB": c2, "colorC": c3, "colorD": c4}

st.sidebar.header("⚙️ Typography")
user_fontsize = st.sidebar.slider("Font Size (pt)", 4.0, 48.0, 12.0, 0.5)
font_options = {"Computer Modern": "lmodern", "Times": "mathptmx", "Palatino": "mathpazo"}
user_font_package = font_options[st.sidebar.selectbox("Font Type", list(font_options.keys()))]
# --- Dictionary Re-Added Here ---
snippet_categories = {
    "Calculus & Structures": {
        "a/b": r"\frac{a}{b}", "xᵃ": r"x^{a}", "xₐ": r"x_{a}", "xₐᵇ": r"x_{a}^{b}",
        "√x": r"\sqrt{x}", "ⁿ√x": r"\sqrt[n]{x}",
        "∫": r"\int", "∫ₐᵇ": r"\int_{a}^{b}", "∬": r"\iint", "∮": r"\oint",
        "∑": r"\sum", "∑ₐᵇ": r"\sum_{i=a}^{b}", "∏": r"\prod", "∏ₐᵇ": r"\prod_{i=a}^{b}",
        "⋂": r"\bigcap", "⋃": r"\bigcup", "lim": r"\lim_{x \to \infty}",
        "∂": r"\partial", "∂f/∂x": r"\frac{\partial f}{\partial x}", "∂²f/∂x²": r"\frac{\partial^2 f}{\partial x^2}", "d/dx": r"\frac{\mathrm{d}}{\mathrm{d}x}"
    },
    "Greek": {
        "α": r"\alpha", "β": r"\beta", "γ": r"\gamma", "δ": r"\delta", "ϵ": r"\epsilon", "ε": r"\varepsilon",
        "ζ": r"\zeta", "η": r"\eta", "θ": r"\theta", "ϑ": r"\vartheta", "ι": r"\iota", "κ": r"\kappa",
        "λ": r"\lambda", "μ": r"\mu", "ν": r"\nu", "ξ": r"\xi", "π": r"\pi", "ϖ": r"\varpi",
        "ρ": r"\rho", "ϱ": r"\varrho", "σ": r"\sigma", "ς": r"\varsigma", "τ": r"\tau", "υ": r"\upsilon",
        "ϕ": r"\phi", "φ": r"\varphi", "χ": r"\chi", "ψ": r"\psi", "ω": r"\omega",
        "Γ": r"\Gamma", "Δ": r"\Delta", "Θ": r"\Theta", "Λ": r"\Lambda", "Ξ": r"\Xi",
        "Π": r"\Pi", "Σ": r"\Sigma", "Υ": r"\Upsilon", "Φ": r"\Phi", "Ψ": r"\Psi", "Ω": r"\Omega"
    },
    "Operators": {
        "±": r"\pm", "∓": r"\mp", "×": r"\times", "÷": r"\div", "·": r"\cdot", "∘": r"\circ", "∗": r"\ast", "⋆": r"\star",
        "∩": r"\cap", "∪": r"\cup", "⊎": r"\uplus", "⊓": r"\sqcap", "⊔": r"\sqcup",
        "∧": r"\wedge", "∨": r"\vee", "◁": r"\triangleleft", "▷": r"\triangleright",
        "⊕": r"\oplus", "⊖": r"\ominus", "⊗": r"\otimes", "⊘": r"\oslash", "⊙": r"\odot",
        "†": r"\dagger", "‡": r"\ddagger", "≀": r"\wr", "∖": r"\setminus", "△": r"\bigtriangleup", "▽": r"\bigtriangledown"
    },
    "Relations": {
        "=": r"=", "<": r"<", ">": r">", "≈": r"\approx", "≠": r"\neq", "≡": r"\equiv", "≤": r"\leq", "≥": r"\geq",
        "∼": r"\sim", "≃": r"\simeq", "≅": r"\cong", "≪": r"\ll", "≫": r"\gg", "≐": r"\doteq", "∝": r"\propto",
        "≺": r"\prec", "≻": r"\succ", "preceq": r"\preceq", "succeq": r"\succeq", "asymp": r"\asymp", "bowtie": r"\bowtie",
        "⊢": r"\vdash", "⊣": r"\dashv", "⊧": r"\models", "⊥": r"\perp", "∥": r"\parallel", "∣": r"\mid",
        "∈": r"\in", "∉": r"\notin", "∋": r"\ni",
        "⊂": r"\subset", "⊃": r"\supset", "⊆": r"\subseteq", "⊇": r"\supseteq", 
        "⊄": r"\not\subset", "⊅": r"\not\supset", "⊈": r"\not\subseteq", "⊉": r"\not\supseteq",
        "⊏": r"\sqsubset", "⊐": r"\sqsupset", "⊑": r"\sqsubseteq", "⊒": r"\sqsupseteq"
    },
    "Sets & Logic": {
        "∀": r"\forall", "∃": r"\exists", "∄": r"\nexists", "∞": r"\infty", "∅": r"\emptyset",
        "ℝ": r"\mathbb{R}", "ℂ": r"\mathbb{C}", "ℕ": r"\mathbb{N}", "ℤ": r"\mathbb{Z}", "ℚ": r"\mathbb{Q}", "ℙ": r"\mathbb{P}", "𝕀": r"\mathbb{I}",
        "ℜ": r"\Re", "ℑ": r"\Im", "℘": r"\wp", "ℓ": r"\ell", "∠": r"\angle", "∴": r"\therefore", "∵": r"\because",
        "Bold": r"\mathbf{text}", "Italic": r"\mathit{text}", "Callig": r"\mathcal{A}", "Fraktur": r"\mathfrak{R}",
        "Bold Math": r"\bm{x}", "Color": r"\textcolor{colorA}{text}"
    },
    "Arrows": {
        "→": r"\rightarrow", "←": r"\leftarrow", "↔": r"\leftrightarrow", 
        "⇒": r"\Rightarrow", "⇐": r"\Leftarrow", "⇔": r"\Leftrightarrow",
        "⟶": r"\longrightarrow", "⟵": r"\longleftarrow", "⟷": r"\longleftrightarrow",
        "↦": r"\mapsto", "⟼": r"\longmapsto",
        "↑": r"\uparrow", "↓": r"\downarrow", "↕": r"\updownarrow",
        "⇑": r"\Uparrow", "⇓": r"\Downarrow", "⇕": r"\Updownarrow",
        "↗": r"\nearrow", "↘": r"\searrow", "↙": r"\swarrow", "↖": r"\nwarrow",
        "⇀": r"\rightharpoonup", "⇁": r"\rightharpoondown", "↼": r"\leftharpoonup", "↽": r"\leftharpoondown",
        "⇌": r"\rightleftharpoons", "x→": r"\xrightarrow{\text{text}}"
    },
    "Brackets & Matrices": {
        "( )": r"\left( \dots \right)", "[ ]": r"\left[ \dots \right]", "{ }": r"\left\{ \dots \right\}",
        "| |": r"\left| \dots \right|", "‖ ‖": r"\left\| \dots \right\|", "⟨ ⟩": r"\left\langle \dots \right\rangle",
        "⌊ ⌋": r"\left\lfloor \dots \right\rfloor", "⌈ ⌉": r"\left\lceil \dots \right\rceil",
        "[ ] Mat": r"\begin{bmatrix} a & b \\ c & d \end{bmatrix}",
        "( ) Mat": r"\begin{pmatrix} a & b \\ c & d \end{pmatrix}",
        "| | Mat": r"\begin{vmatrix} a & b \\ c & d \end{vmatrix}",
        "‖ ‖ Mat": r"\begin{Vmatrix} a & b \\ c & d \end{Vmatrix}",
        "Cases": r"\begin{cases} x & x > 0 \\ 0 & \text{else} \end{cases}",
        "Binom": r"\binom{n}{r}",
        "…": r"\dots", "⋯": r"\cdots", "⋮": r"\vdots", "⋱": r"\ddots"
    },
    "Accents & Decor": {
        "a'": r"a'", "a''": r"a''", "a°": r"a^{\circ}",
        "ȧ": r"\dot{a}", "ä": r"\ddot{a}", 
        "â": r"\hat{a}", "ǎ": r"\check{a}", 
        "à": r"\grave{a}", "á": r"\acute{a}", 
        "ã": r"\tilde{a}", "ă": r"\breve{a}", 
        "ā": r"\bar{a}", "a⃗": r"\vec{a}",
        "abc (wide ~)": r"\widetilde{abc}", "abc (wide ^)": r"\widehat{abc}",
        "abc (over ¯)": r"\overline{abc}", "abc (under _)": r"\underline{abc}",
        "abc (overbrace)": r"\overbrace{abc}^{x}", "abc (underbrace)": r"\underbrace{abc}_{x}",
        "abc (over →)": r"\overrightarrow{abc}", "abc (over ←)": r"\overleftarrow{abc}"
    }
}

# Session State Initialization
if "equation_text" not in st.session_state:
    st.session_state.equation_text = r"\textcolor{colorA}{\bm{x}_{n+1}} = \underset{\bm{x}}{\operatorname{argmax}}\,\textcolor{colorC}{\alpha} + \textcolor{colorB}{\sum_{i=1}^n \beta_i}"

# --- Quick Insert Panel ---
st.subheader("Symbol & Structure Toolbar") # Removed the emoji

def load_svg(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            svg_content = f.read()
        b64 = base64.b64encode(svg_content.encode("utf-8")).decode("utf-8")
        return f"data:image/svg+xml;base64,{b64}"
    except FileNotFoundError:
        return ""

tabs = st.tabs(list(snippet_categories.keys()))

for i, (category_name, snippets) in enumerate(snippet_categories.items()):
    with tabs[i]:
        svg_images = []
        titles = []
        raw_snippets = []
        
        for label, snippet in snippets.items():
            safe_name = f"{category_name}_{label}".replace(" ", "_").replace("/", "over")
            svg_path = os.path.join("svg_icons", f"{safe_name}.svg")
            
            svg_data = load_svg(svg_path)
            if svg_data:
                svg_images.append(svg_data)
                titles.append(label)
                raw_snippets.append(snippet)
        
        if svg_images:
            clicked = clickable_images(
                svg_images,
                titles=titles,
                div_style={"display": "flex", "flex-wrap": "wrap", "gap": "10px"},
                img_style={
                    "cursor": "pointer", 
                    "padding": "10px", 
                    "border-radius": "5px", 
                    "background-color": "#2D2D2D", 
                    "height": "50px"
                },
                key=f"grid_{category_name}"
            )
            
            # --- THE CLICK FIX ---
            # Track the last clicked index to prevent infinite loops and freezing
            click_key = f"last_click_{category_name}"
            if click_key not in st.session_state:
                st.session_state[click_key] = -1

            # Only append text if an image was actually clicked AND it's a new click
            if clicked > -1 and clicked != st.session_state[click_key]:
                st.session_state.equation_text += f" {raw_snippets[clicked]} "
                st.session_state[click_key] = clicked
                # Removed the st.rerun() command so the text area updates smoothly

# --- Main Area: Equation Input ---
# Removed st.write("---") to tighten the gap between buttons and the text box
user_equation = st.text_area("LaTeX Editor", key="equation_text", height=150)

# Live Preview
st.subheader("Live Preview")
preview_equation = user_equation
for color_name, hex_code in user_palette.items():
    preview_equation = preview_equation.replace(
        f"\\textcolor{{{color_name}}}", 
        f"\\textcolor{{{hex_code}}}"
    )
preview_equation = f"\\color{{{user_base_text}}} {preview_equation}"

st.markdown(f"""
<div style="background-color: {user_bg_color}; padding: 30px; border-radius: 8px; text-align: center; overflow-x: auto; font-size: 1.5em;">

$$
{preview_equation}
$$

</div>
""", unsafe_allow_html=True)

# Export & Download
if st.button("Render PDF", type="primary"):
    with st.spinner("Compiling LaTeX engine..."):
        temp_out = os.path.join(tempfile.gettempdir(), "final_equation.pdf")
        success = generate_latex_pdf(
            equation=user_equation, output_filepath=temp_out, 
            palette=user_palette, bg_color=user_bg_color,
            base_text_color=user_base_text, fontsize=user_fontsize, font_package=user_font_package
        )

        if success:
            st.success("PDF generated successfully!")
            with open(temp_out, "rb") as pdf_file:
                st.download_button(
                    label="📥 Save PDF to Downloads", data=pdf_file.read(),
                    file_name="equation.pdf", mime="application/pdf"
                )