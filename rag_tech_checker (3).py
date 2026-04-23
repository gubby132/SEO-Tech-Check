import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="SEO RAG Tech Checker", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Mono', monospace;
    background-color: #0d0d14;
    color: #e8e8f0;
}
h1, h2, h3 { font-family: 'Syne', sans-serif; }
.stApp { background-color: #0d0d14; }
.block-container { padding: 2rem 3rem; max-width: 1400px; }

.hero {
    background: linear-gradient(135deg, #1a0a2e 0%, #0d0d14 60%);
    border: 1px solid #3d2060;
    border-radius: 12px;
    padding: 2rem 2.5rem;
    margin-bottom: 2rem;
}
.hero h1 {
    font-size: 2.2rem;
    font-weight: 800;
    background: linear-gradient(90deg, #e040fb, #ff4081);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 0 0.4rem 0;
}
.hero p { color: #9090b0; font-size: 0.85rem; margin: 0; }

.upload-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
    margin-bottom: 1.5rem;
}
.upload-box {
    background: #110920;
    border: 1px dashed #3d2060;
    border-radius: 10px;
    padding: 1.2rem 1.5rem;
}
.upload-box-label {
    font-family: 'Syne', sans-serif;
    font-size: 0.7rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #e040fb;
    margin-bottom: 0.5rem;
}
.upload-note { font-size: 0.78rem; color: #505070; margin-top: 0.4rem; }

.rag-col {
    background: #110920;
    border: 1px solid #2a1a40;
    border-radius: 10px;
    overflow: hidden;
    height: fit-content;
}
.col-header {
    font-family: 'Syne', sans-serif;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    background: #1e0d38;
    color: #e040fb;
    padding: 0.8rem 1.2rem;
    border-bottom: 1px solid #2a1a40;
}
.section-header {
    font-family: 'Syne', sans-serif;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    background: #0f0f22;
    color: #6060a0;
    padding: 0.5rem 1.2rem;
    border-bottom: 1px solid #1a1a30;
    border-top: 1px solid #1a1a30;
}
.rag-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.6rem 1.2rem;
    border-bottom: 1px solid #1a1a2e;
    gap: 0.5rem;
}
.rag-row:last-child { border-bottom: none; }
.rag-row:hover { background: #13132a; }
.rag-label { font-size: 0.82rem; color: #c0c0d8; flex: 1; }

.pill {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 80px;
    padding: 0.25rem 0;
    border-radius: 4px;
    font-weight: 600;
    font-size: 0.72rem;
    letter-spacing: 0.08em;
    flex-shrink: 0;
}
.pill-R { background: #c0392b; color: #fff; }
.pill-G { background: #27ae60; color: #fff; }
.pill-blank { background: #1e1e35; color: #404060; border: 1px solid #2a2a45; }

.score-box {
    background: #110920;
    border: 1px solid #2a1a40;
    border-radius: 10px;
    padding: 1.5rem 2rem;
    margin-top: 1.5rem;
    display: flex;
    gap: 3rem;
    align-items: center;
}
.score-item { text-align: center; }
.score-num { font-family: 'Syne', sans-serif; font-size: 2.5rem; font-weight: 800; line-height: 1; }
.score-pass { color: #27ae60; }
.score-fail { color: #c0392b; }
.score-na { color: #404060; }
.score-label { font-size: 0.75rem; color: #6060a0; margin-top: 0.3rem; letter-spacing: 0.1em; text-transform: uppercase; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <h1>SEO RAG Tech Checker</h1>
    <p>Upload both Screaming Frog exports below to generate a full RAG status table. Internal All is required; Issues Overview unlocks Images, Structured Data and Open Graph checks.</p>
</div>
""", unsafe_allow_html=True)

# ── Uploads ───────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown('<p style="font-family:Syne,sans-serif;font-size:0.7rem;letter-spacing:0.12em;text-transform:uppercase;color:#e040fb;margin-bottom:0.3rem;">Internal All Export (required)</p>', unsafe_allow_html=True)
    uploaded_internal = st.file_uploader("Internal All", type=["csv"], label_visibility="collapsed", key="internal")
    st.markdown('<p class="upload-note">Screaming Frog: Internal tab → Export. Ensure Crawl Depth is a visible column.</p>', unsafe_allow_html=True)

with col2:
    st.markdown('<p style="font-family:Syne,sans-serif;font-size:0.7rem;letter-spacing:0.12em;text-transform:uppercase;color:#e040fb;margin-bottom:0.3rem;">Issues Overview Export (optional)</p>', unsafe_allow_html=True)
    uploaded_issues = st.file_uploader("Issues Overview", type=["csv"], label_visibility="collapsed", key="issues")
    st.markdown('<p class="upload-note">Screaming Frog: Issues tab → Export. Enables Images, Structured Data and Open Graph checks.</p>', unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def html_only(df):
    df = df.copy()
    df["Content Type"] = df["Content Type"].astype(str)
    return df[df["Content Type"].str.contains("text/html", na=False)]

def load_issues_lookup(issues_df):
    """Return dict of issue name -> URL count from issues overview export."""
    issues_df.columns = [c.strip().strip('"').lstrip('\ufeff') for c in issues_df.columns]
    issue_col = next((c for c in issues_df.columns if c.lower() in ["issue name", "issuename"]), None)
    urls_col = next((c for c in issues_df.columns if c.lower() in ["urls", "url count", "count"]), None)
    if not issue_col or not urls_col:
        return {}
    issues_df[urls_col] = pd.to_numeric(issues_df[urls_col], errors="coerce").fillna(0)
    return dict(zip(issues_df[issue_col].str.strip(), issues_df[urls_col]))


# ── Assessment functions (internal_df) ────────────────────────────────────────
def assess_site_hierarchy(df, _=None):
    df = html_only(df)
    if "Crawl Depth" not in df.columns:
        return None, "Crawl Depth column not found - ensure it is visible before exporting"
    df = df.copy()
    df["Crawl Depth"] = pd.to_numeric(df["Crawl Depth"], errors="coerce")
    deep = df[df["Crawl Depth"] > 4]
    total = len(df)
    if total == 0:
        return None, ""
    pct = len(deep) / total
    if pct == 0:
        return "G", "All pages within crawl depth 4"
    return "R", f"{len(deep)} pages beyond crawl depth 4 ({pct:.0%})"

def assess_url_structure(df, _=None):
    html_urls = html_only(df)["Address"].dropna().astype(str)
    issues = []
    spaces = html_urls[html_urls.str.contains("%20| ", regex=True)]
    uppercase = html_urls[html_urls.apply(
        lambda u: any(c.isupper() for c in u.split("://", 1)[-1].split("/", 1)[-1] if c.isalpha())
    )]
    underscores = html_urls[html_urls.str.contains(r'/[^?#]*_[^?#]*', regex=True)]
    params = html_urls[html_urls.str.contains(r'\?', regex=True)]
    long_urls = html_urls[html_urls.str.len() > 115]
    if len(spaces): issues.append(f"{len(spaces)} URLs with spaces")
    if len(uppercase): issues.append(f"{len(uppercase)} URLs with uppercase")
    if len(underscores): issues.append(f"{len(underscores)} URLs with underscores")
    if len(params): issues.append(f"{len(params)} parameterised URLs")
    if len(long_urls): issues.append(f"{len(long_urls)} URLs over 115 chars")
    if not issues:
        return "G", "No URL structure issues detected"
    return "R", " · ".join(issues)

def assess_security(df, _=None):
    http = df[df["Address"].str.startswith("http://", na=False)]
    if len(http) > 0:
        return "R", f"{len(http)} pages on HTTP"
    return "G", "All pages on HTTPS"

def assess_robots(df, _=None):
    df = html_only(df).copy()
    df["Meta Robots 1"] = df["Meta Robots 1"].astype(str)
    noindex = df[df["Meta Robots 1"].str.contains("noindex", na=False, case=False)]
    if len(noindex) > 0:
        return "R", f"{len(noindex)} pages with noindex directive"
    return "G", "No unexpected noindex directives"

def assess_sitemaps(df, _=None):
    return None, "Requires manual check"

def assess_breadcrumbs(df, _=None):
    return None, "Requires manual assessment"

def assess_canonical_issues(df, _=None):
    df = html_only(df)
    if "Canonical Link Element 1" not in df.columns:
        return None, "Canonical column not found"
    missing = df[df["Canonical Link Element 1"].isna() | (df["Canonical Link Element 1"].astype(str).str.strip() == "")]
    mismatch = df[
        df["Canonical Link Element 1"].notna() &
        (df["Canonical Link Element 1"].astype(str).str.strip() != "") &
        (df["Canonical Link Element 1"].astype(str).str.strip() != df["Address"].astype(str).str.strip())
    ]
    issues = []
    if len(missing): issues.append(f"{len(missing)} missing canonical")
    if len(mismatch): issues.append(f"{len(mismatch)} canonical mismatches")
    if not issues:
        return "G", "Canonicals present and self-referencing"
    return "R", " · ".join(issues)

def assess_page_duplication(df, _=None):
    df = html_only(df)
    if "Hash" not in df.columns:
        return None, "Hash column not found"
    dupes = df[df["Hash"].duplicated(keep=False) & df["Hash"].notna() & (df["Hash"].astype(str).str.strip() != "")]
    if len(dupes) > 0:
        return "R", f"{len(dupes)} pages with duplicate content"
    return "G", "No duplicate pages detected"

def assess_www_non_www(df, _=None):
    redirects = df[df["Status Code"].astype(str).str.startswith("3")]
    non_www_to_www = redirects[
        ~redirects["Address"].str.contains("://www.", na=False) &
        redirects["Redirect URL"].astype(str).str.contains("://www.", na=False)
    ]
    if len(non_www_to_www) > 0:
        return "G", "Non-www redirects to www correctly"
    non_www = df[
        ~df["Address"].str.contains("://www.", na=False) &
        df["Address"].str.startswith("https://", na=False)
    ]
    if len(non_www) > 1:
        return "R", "Both www and non-www versions may be accessible"
    return "G", "Single www version detected"

def assess_http_https(df, _=None):
    http_pages = df[df["Address"].str.startswith("http://", na=False)]
    if len(http_pages) > 0:
        return "R", f"{len(http_pages)} HTTP URLs in crawl"
    return "G", "All URLs use HTTPS"

def assess_cwv(df, _=None):
    return None, "Requires PageSpeed Insights or GSC data"

def assess_js_rendering(df, _=None):
    return None, "Requires manual assessment"

def assess_mobile_friendly(df, _=None):
    return None, "Requires Google Mobile-Friendly Test or GSC"

def assess_page_speed(df, _=None):
    return None, "Requires PageSpeed Insights data"

def assess_error_messages(df, _=None):
    df_html = html_only(df)
    errors_4xx = df_html[df_html["Status Code"].astype(str).str.startswith("4")]
    errors_5xx = df_html[df_html["Status Code"].astype(str).str.startswith("5")]
    issues = []
    if len(errors_4xx): issues.append(f"{len(errors_4xx)} 4xx errors")
    if len(errors_5xx): issues.append(f"{len(errors_5xx)} 5xx errors")
    if not issues:
        return "G", "No 4xx or 5xx errors"
    return "R", " · ".join(issues)

def assess_internal_redirects(df, _=None):
    df_html = html_only(df)
    redirects = df_html[df_html["Status Code"].astype(str).str.startswith("3")]
    if len(redirects) > 0:
        return "R", f"{len(redirects)} internal redirects detected"
    return "G", "No internal redirects"

def assess_response_codes(df, _=None):
    df_html = html_only(df)
    non_200 = df_html[~df_html["Status Code"].astype(str).str.startswith("2")]
    if len(non_200) > 0:
        counts = non_200["Status Code"].value_counts().to_dict()
        summary = " · ".join([f"{v}x {k}" for k, v in counts.items()])
        return "R", summary
    return "G", "All pages return 2xx"

def assess_duplicate_sites(df, _=None):
    return None, "Requires manual check"

def assess_duplicate_content(df, _=None):
    df = html_only(df)
    if "No. Near Duplicates" not in df.columns:
        return None, "Near Duplicates column not found"
    dupes = df[pd.to_numeric(df["No. Near Duplicates"], errors="coerce") > 0]
    if len(dupes) > 0:
        return "R", f"{len(dupes)} pages with near-duplicate content"
    return "G", "No near-duplicate content detected"

def assess_page_titles(df, _=None):
    df = html_only(df)
    if "Title 1" not in df.columns:
        return None, "Title 1 column not found in export"
    issues = []
    missing = df[df["Title 1"].isna() | (df["Title 1"].astype(str).str.strip() == "")]
    dupes = df[df["Title 1"].duplicated(keep=False) & df["Title 1"].notna() & (df["Title 1"].astype(str).str.strip() != "")]
    if "Title 1 Length" in df.columns:
        long_t = df[pd.to_numeric(df["Title 1 Length"], errors="coerce") > 60]
        if len(long_t): issues.append(f"{len(long_t)} over 60 chars")
    if len(missing): issues.append(f"{len(missing)} missing")
    if len(dupes): issues.append(f"{len(dupes)} duplicate")
    if not issues:
        return "G", "Page titles look good"
    return "R", " · ".join(issues)

def assess_meta_descriptions(df, _=None):
    df = html_only(df)
    if "Meta Description 1" not in df.columns:
        return None, "Meta Description 1 column not found in export"
    issues = []
    missing = df[df["Meta Description 1"].isna() | (df["Meta Description 1"].astype(str).str.strip() == "")]
    dupes = df[df["Meta Description 1"].duplicated(keep=False) & df["Meta Description 1"].notna() & (df["Meta Description 1"].astype(str).str.strip() != "")]
    if "Meta Description 1 Length" in df.columns:
        long_m = df[pd.to_numeric(df["Meta Description 1 Length"], errors="coerce") > 155]
        if len(long_m): issues.append(f"{len(long_m)} over 155 chars")
    if len(missing): issues.append(f"{len(missing)} missing")
    if len(dupes): issues.append(f"{len(dupes)} duplicate")
    if not issues:
        return "G", "Meta descriptions look good"
    return "R", " · ".join(issues)

def assess_headings(df, _=None):
    df = html_only(df)
    issues = []
    if "H1-1" not in df.columns:
        return None, "H1-1 column not found in export"
    missing_h1 = df[df["H1-1"].isna() | (df["H1-1"].astype(str).str.strip() == "")]
    dupes_h1 = df[df["H1-1"].duplicated(keep=False) & df["H1-1"].notna() & (df["H1-1"].astype(str).str.strip() != "")]
    if len(missing_h1): issues.append(f"{len(missing_h1)} missing H1")
    if len(dupes_h1): issues.append(f"{len(dupes_h1)} duplicate H1s")
    if "H1-2" in df.columns:
        multi_h1 = df[df["H1-2"].notna() & (df["H1-2"].astype(str).str.strip() != "")]
        if len(multi_h1): issues.append(f"{len(multi_h1)} multiple H1s")
    if not issues:
        return "G", "Heading structure looks good"
    return "R", " · ".join(issues)

def assess_links(df, _=None):
    df = html_only(df)
    if "Inlinks" not in df.columns:
        return None, "Inlinks column not found"
    orphans = df[pd.to_numeric(df["Inlinks"], errors="coerce") == 0]
    if len(orphans) > 0:
        return "R", f"{len(orphans)} orphan pages (0 inlinks)"
    return "G", "No orphan pages detected"

def assess_indexation(df, _=None):
    df = html_only(df).copy()
    df["Indexability"] = df["Indexability"].astype(str)
    non_indexable = df[df["Indexability"].str.lower() == "non-indexable"]
    if len(non_indexable) > 0:
        reasons = non_indexable["Indexability Status"].value_counts().to_dict()
        summary = " · ".join([f"{v}x {k}" for k, v in reasons.items()])
        return "R", summary
    return "G", "All pages indexable"


# ── Assessment functions (issues_lookup) ──────────────────────────────────────
def assess_images(df, issues_lookup):
    if not issues_lookup:
        return None, "Upload Issues Overview export to enable this check"
    issues = []
    alt_missing = int(issues_lookup.get("Images: Missing Alt Text", 0))
    oversized = int(issues_lookup.get("Images: Over 100 KB", 0))
    missing_size = int(issues_lookup.get("Images: Missing Size Attributes", 0))
    if alt_missing: issues.append(f"{alt_missing} images missing alt text")
    if oversized: issues.append(f"{oversized} images over 100KB")
    if missing_size: issues.append(f"{missing_size} missing size attributes")
    if not issues:
        return "G", "No image issues detected"
    return "R", " · ".join(issues)

def assess_structured_data(df, issues_lookup):
    if not issues_lookup:
        return None, "Upload Issues Overview export to enable this check"
    # SF doesn't report structured data errors directly in issues - manual check needed
    return None, "Requires manual assessment or schema validator"

def assess_open_graph(df, issues_lookup):
    if not issues_lookup:
        return None, "Upload Issues Overview export to enable this check"
    # OG tags not directly in SF issues export
    return None, "Requires manual assessment or OG tag crawl configuration in SF"


# ── Layout ────────────────────────────────────────────────────────────────────
COLUMNS = [
    {
        "title": "Structure & Indexation",
        "sections": [
            {
                "label": "Structure",
                "items": [
                    ("Site Hierarchy", assess_site_hierarchy),
                    ("URL Structure", assess_url_structure),
                    ("Security", assess_security),
                ]
            },
            {
                "label": "Indexation",
                "items": [
                    ("Robots.txt / Noindex", assess_robots),
                    ("Sitemaps", assess_sitemaps),
                    ("Breadcrumbs", assess_breadcrumbs),
                    ("Canonical Issues", assess_canonical_issues),
                ]
            },
            {
                "label": "On Site Duplication",
                "items": [
                    ("Page Level Duplication", assess_page_duplication),
                    ("www. vs non-www.", assess_www_non_www),
                    ("http vs https", assess_http_https),
                ]
            },
        ]
    },
    {
        "title": "Technical Optimisation",
        "sections": [
            {
                "label": "Technical",
                "items": [
                    ("Core Web Vitals", assess_cwv),
                    ("JavaScript Rendering", assess_js_rendering),
                    ("Mobile Friendly", assess_mobile_friendly),
                    ("Page Speed", assess_page_speed),
                    ("Error Messages", assess_error_messages),
                    ("Internal Redirects", assess_internal_redirects),
                    ("Response Code Handling", assess_response_codes),
                ]
            },
            {
                "label": "Off Site Duplication",
                "items": [
                    ("Duplicate Sites", assess_duplicate_sites),
                    ("Duplicate Content", assess_duplicate_content),
                ]
            },
        ]
    },
    {
        "title": "On Page & Markup",
        "sections": [
            {
                "label": "On Page Elements",
                "items": [
                    ("Page Titles", assess_page_titles),
                    ("Meta Descriptions", assess_meta_descriptions),
                    ("Headings", assess_headings),
                    ("Images", assess_images),
                    ("Links", assess_links),
                    ("Indexation", assess_indexation),
                ]
            },
            {
                "label": "Markup",
                "items": [
                    ("Structured Data", assess_structured_data),
                    ("Open Graph Protocol", assess_open_graph),
                ]
            },
        ]
    },
]

# ── Run ───────────────────────────────────────────────────────────────────────
if uploaded_internal:
    try:
        df = pd.read_csv(uploaded_internal, low_memory=False)
    except Exception as e:
        st.error(f"Could not read Internal All file: {e}")
        st.stop()

    df.columns = [c.strip().strip('"').lstrip('\ufeff') for c in df.columns]

    issues_lookup = {}
    if uploaded_issues:
        try:
            issues_df = pd.read_csv(uploaded_issues, low_memory=False)
            issues_lookup = load_issues_lookup(issues_df)
        except Exception as e:
            st.warning(f"Could not read Issues Overview file: {e}")

    status_line = f"Internal All: {len(df):,} rows loaded"
    if issues_lookup:
        status_line += f" · Issues Overview: {len(issues_lookup)} issues loaded"
    else:
        status_line += " · Issues Overview: not uploaded (Images check disabled)"
    st.markdown(f'<p style="font-size:0.78rem;color:#505070;margin-bottom:1rem;">{status_line}</p>', unsafe_allow_html=True)

    all_results = []
    for col in COLUMNS:
        for section in col["sections"]:
            for name, fn in section["items"]:
                status, note = fn(df, issues_lookup)
                all_results.append({
                    "column": col["title"],
                    "section": section["label"],
                    "name": name,
                    "status": status,
                    "note": note,
                })

    passes = sum(1 for r in all_results if r["status"] == "G")
    fails = sum(1 for r in all_results if r["status"] == "R")
    na = sum(1 for r in all_results if r["status"] is None)
    total_assessed = passes + fails

    result_lookup = {r["name"]: r for r in all_results}

    def pill_html(status):
        if status == "R":
            return '<span class="pill pill-R">FAIL</span>'
        elif status == "G":
            return '<span class="pill pill-G">PASS</span>'
        else:
            return '<span class="pill pill-blank">N/A</span>'

    cols = st.columns(3)
    for col_idx, col_cfg in enumerate(COLUMNS):
        with cols[col_idx]:
            html = f'<div class="rag-col"><div class="col-header">{col_cfg["title"]}</div>'
            for section in col_cfg["sections"]:
                html += f'<div class="section-header">{section["label"]}</div>'
                for name, _ in section["items"]:
                    r = result_lookup[name]
                    html += f'<div class="rag-row"><span class="rag-label">{name}</span>{pill_html(r["status"])}</div>'
            html += '</div>'
            st.markdown(html, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="score-box">
        <div class="score-item">
            <div class="score-num score-pass">{passes}</div>
            <div class="score-label">Tests Passed</div>
        </div>
        <div class="score-item">
            <div class="score-num score-fail">{fails}</div>
            <div class="score-label">Tests Failed</div>
        </div>
        <div class="score-item">
            <div class="score-num score-na">{na}</div>
            <div class="score-label">Manual Review</div>
        </div>
        <div class="score-item">
            <div class="score-num" style="color:#9090b0">{passes}/{total_assessed}</div>
            <div class="score-label">Score (assessed only)</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("View detailed notes"):
        for r in all_results:
            status_label = r["status"] if r["status"] else "N/A"
            st.markdown(f"**{r['name']}** ({status_label}) — {r['note']}")

    st.markdown("<br>", unsafe_allow_html=True)
    export_rows = [{
        "Section": r["section"],
        "Element": r["name"],
        "Status": r["status"] if r["status"] else "",
        "Notes": r["note"],
    } for r in all_results]

    csv_buf = io.StringIO()
    pd.DataFrame(export_rows).to_csv(csv_buf, index=False)
    st.download_button(
        label="Download RAG table as CSV",
        data=csv_buf.getvalue(),
        file_name="rag_tech_check.csv",
        mime="text/csv",
    )

else:
    st.markdown("""
    <div style="border:1px dashed #2a2a45;border-radius:10px;padding:3rem;text-align:center;color:#404060;margin-top:1rem;">
        <p style="font-family:'Syne',sans-serif;font-size:1.1rem;margin:0;">Upload the Internal All CSV above to generate your RAG table</p>
    </div>
    """, unsafe_allow_html=True)
