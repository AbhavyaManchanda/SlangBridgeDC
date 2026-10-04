"""
Custom CSS styling for DC Roommate Slang Bridge Streamlit UI.
Theme: Infosys Mysore DC Aesthetic (Campus Blue, Emerald Green, Slate Dark/Light).
"""

CUSTOM_CSS = """
<style>
/* Main container layout */
.main .block-container {
    padding-top: 1.8rem;
    padding-bottom: 3rem;
    max-width: 1100px;
}

/* Header & Banner */
.dc-hero-banner {
    background: linear-gradient(135deg, #0b1f3a 0%, #102a4e 50%, #004b87 100%);
    border: 1px solid #1e3a64;
    border-radius: 14px;
    padding: 24px 28px;
    margin-bottom: 24px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
    color: #ffffff;
}

.dc-hero-title {
    font-size: 2.1rem;
    font-weight: 800;
    letter-spacing: -0.5px;
    margin: 0 0 6px 0;
    color: #ffffff;
    display: flex;
    align-items: center;
    gap: 12px;
}

.dc-hero-subtitle {
    font-size: 1.05rem;
    color: #94a3b8;
    margin: 0 0 14px 0;
    line-height: 1.5;
}

.dc-badge-row {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.dc-pill-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(255, 255, 255, 0.12);
    border: 1px solid rgba(255, 255, 255, 0.18);
    padding: 4px 12px;
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 600;
    color: #e2e8f0;
}

.dc-pill-badge.active {
    background: rgba(16, 185, 129, 0.2);
    border-color: rgba(16, 185, 129, 0.4);
    color: #34d399;
}

.dc-pill-badge.offline {
    background: rgba(59, 130, 246, 0.2);
    border-color: rgba(59, 130, 246, 0.4);
    color: #60a5fa;
}

/* Three Core Output Cards (Direct Meaning, The Vibe/Tone, On-Campus Context) */
.output-card {
    border-radius: 12px;
    padding: 18px 20px;
    margin-bottom: 16px;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.output-card:hover {
    transform: translateY(-1px);
}

/* 1. Direct Meaning Card */
.card-meaning {
    background: #0f1f38;
    border: 1px solid #1e3b6d;
    border-left: 5px solid #38bdf8;
}

.card-title-meaning {
    color: #38bdf8;
    font-size: 0.95rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.card-body-meaning {
    color: #f1f5f9;
    font-size: 1.15rem;
    font-weight: 500;
    line-height: 1.5;
}

/* 2. The Vibe / Tone Card */
.card-vibe {
    background: #1a162b;
    border: 1px solid #3c2a63;
    border-left: 5px solid #c084fc;
}

.card-title-vibe {
    color: #c084fc;
    font-size: 0.95rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.card-body-vibe {
    color: #f1f5f9;
    font-size: 1.05rem;
    line-height: 1.5;
}

/* 3. On-Campus Context Card */
.card-context {
    background: #0d2822;
    border: 1px solid #134e40;
    border-left: 5px solid #34d399;
}

.card-title-context {
    color: #34d399;
    font-size: 0.95rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.card-body-context {
    color: #f1f5f9;
    font-size: 1.02rem;
    line-height: 1.55;
}

/* Roommate Reply Box */
.card-reply {
    background: #1e293b;
    border: 1px dashed #475569;
    border-radius: 10px;
    padding: 14px 18px;
    margin-top: 14px;
}

.card-title-reply {
    color: #fbbf24;
    font-size: 0.85rem;
    font-weight: 700;
    text-transform: uppercase;
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    gap: 6px;
}

.card-body-reply {
    color: #f8fafc;
    font-size: 1.0rem;
    font-style: italic;
}

/* Slang Tag Pills */
.slang-tag {
    display: inline-block;
    background: #1e293b;
    color: #38bdf8;
    border: 1px solid #334155;
    padding: 3px 10px;
    border-radius: 6px;
    font-size: 0.8rem;
    font-weight: 600;
    margin-right: 6px;
    margin-bottom: 6px;
}

/* Quick Chip Buttons */
div[data-testid="stHorizontalBlock"] button {
    border-radius: 20px !important;
    font-size: 0.82rem !important;
    padding: 4px 12px !important;
    white-space: nowrap !important;
}

/* Model Info Pill */
.model-info-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.78rem;
    color: #64748b;
    margin-top: 12px;
    padding-top: 10px;
    border-top: 1px solid #1e293b;
}

/* Audio Uploader Box Enhancement */
.audio-card-box {
    background: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 16px;
}

/* Privacy Callout */
.privacy-badge {
    background: #022c22;
    border: 1px solid #065f46;
    color: #6ee7b7;
    padding: 8px 14px;
    border-radius: 8px;
    font-size: 0.85rem;
    margin-top: 10px;
    display: flex;
    align-items: center;
    gap: 8px;
}
</style>
"""
