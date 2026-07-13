"""UI theme constants — dark theme with readable contrast."""

C_BG = "#0b1220"
C_PANEL = "#111827"
C_BORDER = "#334155"
C_TEXT = "#f1f5f9"
C_MUTED = "#cbd5e1"
C_ACCENT = "#3b82f6"
C_CODE_BG = "#020617"
C_CODE_FG = "#93c5fd"

CUSTOM_CSS = f"""
.gradio-container {{
    max-width: 1360px !important;
    font-family: Inter, Segoe UI, system-ui, sans-serif !important;
    background: {C_BG} !important;
    color: {C_TEXT} !important;
}}

.header-block {{
    border-bottom: 1px solid {C_BORDER};
    padding-bottom: 1rem;
    margin-bottom: 0.75rem;
}}
.header-block.hero-viral .eyebrow {{
    font-size: 0.7rem;
    letter-spacing: 0.12em;
    font-weight: 600;
    color: {C_ACCENT} !important;
    margin-bottom: 0.35rem;
}}
.header-block h1 {{
    font-size: 1.75rem;
    font-weight: 700;
    margin: 0;
    color: {C_TEXT} !important;
    letter-spacing: -0.02em;
}}
.header-block p {{
    margin: 0.45rem 0 0;
    color: {C_MUTED} !important;
    font-size: 1rem;
    max-width: 46rem;
    line-height: 1.45;
}}
.footer-viral {{
    color: {C_MUTED} !important;
    font-size: 0.78rem;
    margin-top: 1.25rem;
}}
.footer-viral a {{
    color: {C_ACCENT} !important;
}}

/* Markdown / prose readability */
.prose, .markdown, .md, [class*="prose"] {{
    color: {C_TEXT} !important;
}}
.prose *, .markdown *, .md * {{
    color: inherit;
}}
.prose h1, .prose h2, .prose h3, .prose h4,
.markdown h1, .markdown h2, .markdown h3, .markdown h4 {{
    color: {C_TEXT} !important;
}}
.prose p, .prose li, .prose td, .prose th,
.markdown p, .markdown li, .markdown td, .markdown th {{
    color: {C_TEXT} !important;
}}
.prose strong, .markdown strong {{
    color: #ffffff !important;
}}
.prose a, .markdown a {{
    color: {C_ACCENT} !important;
}}

/* Inline code and fenced code — fix white-on-white */
.prose code, .markdown code, code {{
    background: {C_CODE_BG} !important;
    color: {C_CODE_FG} !important;
    border: 1px solid {C_BORDER} !important;
    border-radius: 4px !important;
    padding: 0.1rem 0.35rem !important;
}}
.prose pre, .markdown pre, pre {{
    background: {C_CODE_BG} !important;
    color: {C_TEXT} !important;
    border: 1px solid {C_BORDER} !important;
    border-radius: 8px !important;
}}
.prose pre code, .markdown pre code, pre code {{
    background: transparent !important;
    border: none !important;
    color: {C_TEXT} !important;
}}

/* Tables */
.prose table, .markdown table {{
    border-color: {C_BORDER} !important;
}}
.prose th, .markdown th {{
    background: #1e293b !important;
    color: {C_TEXT} !important;
}}
.prose td, .markdown td {{
    color: {C_TEXT} !important;
    border-color: {C_BORDER} !important;
}}

/* Code / chatbot / inputs */
.cm-editor, .cm-content, .cm-line {{
    background: {C_CODE_BG} !important;
    color: {C_TEXT} !important;
}}
textarea, input, .svelte-input {{
    color: {C_TEXT} !important;
}}

/* Chatbot bubbles */
.bot, .user, [data-testid="bot"], [data-testid="user"] {{
    color: {C_TEXT} !important;
}}
.message, .chatbot, .bubble-message {{
    color: {C_TEXT} !important;
}}

footer {{ display: none !important; }}
"""


def build_theme():
    import gradio as gr

    return gr.themes.Base(
        primary_hue=gr.themes.colors.blue,
        neutral_hue=gr.themes.colors.slate,
        font=[gr.themes.GoogleFont("Inter"), "ui-sans-serif", "system-ui", "sans-serif"],
    ).set(
        body_background_fill=C_BG,
        body_background_fill_dark=C_BG,
        background_fill_primary=C_PANEL,
        background_fill_primary_dark=C_PANEL,
        background_fill_secondary="#0f172a",
        background_fill_secondary_dark="#0f172a",
        border_color_primary=C_BORDER,
        border_color_primary_dark=C_BORDER,
        body_text_color=C_TEXT,
        body_text_color_dark=C_TEXT,
        body_text_color_subdued=C_MUTED,
        body_text_color_subdued_dark=C_MUTED,
        block_background_fill=C_PANEL,
        block_background_fill_dark=C_PANEL,
        block_label_text_color=C_MUTED,
        block_label_text_color_dark=C_MUTED,
        block_title_text_color=C_TEXT,
        block_title_text_color_dark=C_TEXT,
        input_background_fill=C_CODE_BG,
        input_background_fill_dark=C_CODE_BG,
        input_border_color=C_BORDER,
        input_border_color_dark=C_BORDER,
        input_placeholder_color=C_MUTED,
        input_placeholder_color_dark=C_MUTED,
        button_primary_background_fill=C_ACCENT,
        button_primary_background_fill_dark=C_ACCENT,
        button_primary_text_color="#ffffff",
        button_primary_text_color_dark="#ffffff",
        button_secondary_text_color=C_TEXT,
        button_secondary_text_color_dark=C_TEXT,
        link_text_color=C_ACCENT,
        link_text_color_dark=C_ACCENT,
        code_background_fill=C_CODE_BG,
        code_background_fill_dark=C_CODE_BG,
    )


DARK_THEME = None  # built lazily to avoid import-time Gradio side effects
