import os
import subprocess
import tempfile

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

output_dir = "svg_icons"
os.makedirs(output_dir, exist_ok=True)

tex_template = r"""\documentclass[12pt, border=2pt]{standalone}
\usepackage{amsmath, amssymb, amsfonts, bm}
\usepackage{xcolor}
% Add this line so the generator knows how to color the SVG icon
\definecolor{colorA}{HTML}{DE4968} 
\begin{document}
\color{white} 
$\displaystyle REPLACE_ME $
\end{document}
"""

print(f"Generating SVGs in ./{output_dir}...")

with tempfile.TemporaryDirectory() as temp_dir:
    for category, snippets in snippet_categories.items():
        for label, snippet in snippets.items():
            safe_name = f"{category}_{label}".replace(" ", "_").replace("/", "over")
            
            tex_filepath = os.path.join(temp_dir, 'icon.tex')
            pdf_filepath = os.path.join(temp_dir, 'icon.pdf')
            svg_filepath = os.path.join(output_dir, f"{safe_name}.svg")
            
            with open(tex_filepath, 'w', encoding='utf-8') as f:
                f.write(tex_template.replace("REPLACE_ME", snippet))
            
            subprocess.run(
                ['pdflatex', '-interaction=nonstopmode', 'icon.tex'],
                cwd=temp_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            
            if os.path.exists(pdf_filepath):
                subprocess.run(['pdf2svg', pdf_filepath, svg_filepath])
                print(f"Created: {safe_name}.svg")

print("All SVGs generated successfully!")