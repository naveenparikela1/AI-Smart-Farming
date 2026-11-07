import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import date, timedelta
from database import (
    init_db, authenticate, create_user, get_user, update_profile,
    list_farms, add_farm, delete_farm, list_crops, add_crop, delete_crop,
    list_expenses, add_expense, delete_expense, list_activities, add_activity,
    delete_activity, list_harvests, add_harvest, delete_harvest,
    list_sales, add_sale, delete_sale, list_reminders, add_reminder,
    complete_reminder, delete_reminder, dashboard_totals
)

st.set_page_config(page_title="SmartFarm | Smart Farming Dashboard", page_icon="🌱", layout="wide")
init_db()

# AI SMART FARMING THEME
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
:root { --bg:#08120f; --panel:#101e19; --panel2:#14251e; --line:#263b31; --muted:#9aada2; --text:#edf5ef; --lime:#b7ef68; --green:#4ca878; }
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
.stApp { background:radial-gradient(ellipse at 82% 0%,#173528 0%,#0b1712 38%,#07100d 100%); color:var(--text); }
header[data-testid="stHeader"] { background:rgba(7,16,13,.78); }
.block-container { max-width:1440px; padding-top:2rem; padding-bottom:3rem; }
section[data-testid="stSidebar"] { background:linear-gradient(180deg,#10221a 0%,#09130f 100%); border-right:1px solid #263b31; }
section[data-testid="stSidebar"] > div { padding-top:1.4rem; }
section[data-testid="stSidebar"] * { color:var(--text); }
h1,h2,h3 { color:var(--text)!important; font-family:'Manrope',sans-serif!important; letter-spacing:-.7px; }
h1 { font-size:2.1rem!important; font-weight:800!important; }
h2 { font-size:1.45rem!important; font-weight:700!important; }
h3 { font-size:1.08rem!important; font-weight:700!important; }
p, .stCaption { color:var(--muted); }
div[data-testid="stMetric"] { background:linear-gradient(145deg,#172a21,#102018); border:1px solid #2b4537; border-radius:18px; padding:18px 20px; box-shadow:0 12px 30px #0002; min-height:118px; }
[data-testid="stMetricLabel"] { color:#a9bdb0!important; font-size:.83rem!important; }
[data-testid="stMetricValue"] { color:var(--lime)!important; font-family:'Manrope',sans-serif!important; font-weight:800!important; }
[data-testid="stMetricDelta"] { font-size:.75rem!important; }
.stButton > button, .stFormSubmitButton > button { background:linear-gradient(135deg,#c4f27b,#8bd45a); color:#102016; border:0; border-radius:11px; min-height:42px; font-weight:700; transition:all .2s ease; }
.stButton > button:hover, .stFormSubmitButton > button:hover { background:#d6ff9c; color:#102016; border:0; transform:translateY(-1px); }
.stButton > button[kind="secondary"] { background:#1b3026; color:#dce9df; border:1px solid #385442; }
input,textarea,[data-baseweb="select"] > div { background-color:#13251d!important; border-color:#355242!important; border-radius:10px!important; color:var(--text)!important; }
[data-testid="stDataFrame"],[data-testid="stTable"] { border:1px solid #2b4537; border-radius:14px; overflow:hidden; }
[data-testid="stExpander"] { background:#112119; border:1px solid #2b4537; border-radius:14px; }
div[data-testid="stAlert"] { border-radius:13px; }
hr { border-color:#2b4537; }
div[data-testid="stVerticalBlockBorderWrapper"] > div { border-color:#2b4537!important; border-radius:16px!important; background:rgba(17,33,25,.72); }
div[data-testid="stRadio"] label { background:transparent; border-radius:9px; }
.stProgress > div > div > div > div { background:var(--lime); }
a { color:var(--lime)!important; }
.login-wrap { max-width:480px; margin:5vh auto; padding:2.2rem; border:1px solid #2b4537; border-radius:24px; background:linear-gradient(145deg,#14271e,#0d1a14); box-shadow:0 24px 80px #0005; }
.brand-pill { display:inline-block; padding:7px 12px; border:1px solid #42634d; border-radius:999px; color:#c4f27b; background:#1b3324; font-size:12px; letter-spacing:1.5px; font-weight:700; }
.hero-panel { padding:26px 28px; border:1px solid #355242; border-radius:22px; background:linear-gradient(120deg,rgba(40,81,55,.85),rgba(16,34,25,.92)); margin:8px 0 22px 0; }
.hero-panel p { color:#c1d2c6; margin-bottom:0; }
.section-kicker { color:#b7ef68; font-size:11px; font-weight:800; letter-spacing:2px; text-transform:uppercase; }
.insight-panel { padding:18px 20px; border-radius:16px; border:1px solid #365342; background:#14271e; min-height:120px; }

.insight-panel strong { color:#c4f27b; }
.landing-shell { max-width:1240px; margin:0 auto; }
.landing-nav { display:flex; align-items:center; justify-content:space-between; padding:8px 0 24px; }
.landing-hero { min-height:490px; display:flex; flex-direction:column; justify-content:center; padding:58px 6%; border:1px solid #46624d; border-radius:28px; overflow:hidden; background-image:linear-gradient(90deg,rgba(5,18,12,.94) 0%,rgba(5,18,12,.76) 48%,rgba(5,18,12,.12) 100%),url('https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=1800&q=85'); background-position:center; background-size:cover; box-shadow:0 25px 70px #0005; }
.landing-hero h1 { max-width:690px; font-size:clamp(2.6rem,5.5vw,4.7rem)!important; line-height:1.06!important; margin:18px 0!important; }
.landing-hero p { max-width:560px; color:#e0eadf; font-size:1.08rem; line-height:1.7; }
.landing-kicker { color:#c4f27b; text-transform:uppercase; letter-spacing:2.5px; font-size:.76rem; font-weight:800; }
.landing-feature { overflow:hidden; border:1px solid #2b4537; border-radius:18px; background:linear-gradient(145deg,#14271e,#0d1a14); min-height:275px; }
.landing-feature img { width:100%; height:145px; object-fit:cover; display:block; }
.landing-feature-copy { padding:17px 18px 20px; }
.landing-feature-copy h3 { margin:0 0 7px; }
.landing-feature-copy p { font-size:.9rem; line-height:1.55; margin:0; }
.landing-stat { border:1px solid #2b4537; border-radius:16px; padding:20px; background:#112119; }
.landing-stat strong { color:#c4f27b; font-size:1.25rem; display:block; }
.landing-cta { text-align:center; padding:42px 20px; border:1px solid #355242; border-radius:22px; background:linear-gradient(120deg,#1b3928,#102018); }
.landing-footer { text-align:center; color:#8fa397; padding:28px 0 10px; font-size:.82rem; }
@media(max-width:700px) { .landing-hero{min-height:440px;padding:32px 24px;background-position:58% center;} .landing-hero h1{font-size:2.5rem!important;} }

@media(max-width:700px) { .block-container{padding:1rem!important;} h1{font-size:1.7rem!important;} .hero-panel{padding:20px;} }
</style>
""", unsafe_allow_html=True)

TEXT = {
    "English": {
        "app": "SmartFarm", "dashboard": "Dashboard", "farms": "My Farms", "crops": "Crops",
        "expenses": "Expenses", "activities": "Activities", "harvest": "Harvest & Sales",
        "reminders": "Reminders", "settings": "Settings", "logout": "Log out",
        "welcome": "Your farm, organised.", "sample": "Data is saved in your local SQLite database.",
        "area": "Total area", "active": "Active crop cycles", "expense": "Total expenses",
        "harvested": "Harvest recorded", "revenue": "Sales revenue", "costs": "Selling costs",
        "profit": "Estimated profit", "add": "Add", "save": "Save", "delete": "Delete",
        "village": "Village", "farm_name": "Farm name", "acres": "Area (acres)",
        "soil": "Soil type", "irrigation": "Irrigation method", "crop": "Crop name",
        "variety": "Variety", "farm": "Farm", "planting": "Transplanting date",
        "expected": "Expected harvest date", "stage": "Growth stage", "category": "Category",
        "amount": "Amount (₹)", "description": "Description", "date": "Date",
        "type": "Activity", "quantity": "Quantity (kg)", "grade": "Grade",
        "price": "Price per quintal (₹)", "buyer": "Buyer", "market": "Market / location",
        "transport": "Transport cost (₹)", "other": "Other selling costs (₹)",
        "title": "Reminder", "due": "Due date", "profile": "Profile", "name": "Name",
        "language": "Language", "phone": "Phone number", "password": "Password",
        "login": "Log in", "register": "Create account", "no_account": "New here? Create an account",
        "have_account": "Already registered? Log in", "bad_login": "Incorrect phone number or password.",
        "phone_exists": "An account with this phone number already exists.",
        "required": "Please complete the required fields.", "done": "Mark complete",
        "overdue": "Overdue", "pending": "Pending", "completed": "Completed",
        "no_data": "No records yet. Use the form above to add your first record.",
        "farm_deleted": "Farm deleted.", "crop_deleted": "Crop deleted.",
        "expense_deleted": "Expense deleted.", "activity_deleted": "Activity deleted.",
        "harvest_deleted": "Harvest record deleted.", "sale_deleted": "Sale deleted.",
        "reminder_deleted": "Reminder deleted.", "profile_saved": "Profile updated.",
        "profit_note": "Estimated profit = sales revenue − recorded expenses − selling costs. This is not an audited accounting figure.",
        "expense_link": "Link expense to a crop cycle (optional)", "linked": "Linked crop",
        "all_farms": "All farms", "select_farm": "Select a farm",
        "soil_red": "Red soil", "soil_black": "Black soil", "soil_sandy": "Sandy",
        "soil_loamy": "Loamy", "soil_clay": "Clay", "soil_other": "Other",
        "irr_drip": "Drip", "irr_furrow": "Furrow", "irr_sprinkler": "Sprinkler",
        "irr_rainfed": "Rainfed", "irr_other": "Other",
        "stage_vegetative": "Vegetative growth", "stage_flowering": "Flowering",
        "stage_fruiting": "Fruiting", "stage_harvest": "Harvesting",
        "exp_seeds": "Seeds", "exp_fertilizers": "Fertilisers", "exp_pesticides": "Pesticides",
        "exp_labour": "Labour", "exp_irrigation": "Irrigation", "exp_transport": "Transport",
        "exp_other": "Other", "act_spraying": "Spraying", "act_irrigation": "Irrigation",
        "act_weeding": "Weeding", "act_fertilising": "Fertilising", "act_other": "Other",
        "rem_irrigation": "Irrigation", "rem_soil_test": "Soil test",
        "rem_inspection": "Field inspection", "rem_other": "Other",
    },
    "తెలుగు": {
        "app": "స్మార్ట్‌ఫార్మ్", "dashboard": "డాష్‌బోర్డ్", "farms": "నా పొలాలు", "crops": "పంటలు",
        "expenses": "ఖర్చులు", "activities": "పనులు", "harvest": "కోత & అమ్మకాలు",
        "reminders": "రిమైండర్లు", "settings": "సెట్టింగ్స్", "logout": "లాగ్ అవుట్",
        "welcome": "మీ పొలం వివరాలు ఒకేచోట.", "sample": "మీ వివరాలు స్థానిక SQLite డేటాబేస్‌లో భద్రపరచబడతాయి.",
        "area": "మొత్తం విస్తీర్ణం", "active": "కొనసాగుతున్న పంటలు", "expense": "మొత్తం ఖర్చులు",
        "harvested": "నమోదైన కోత", "revenue": "అమ్మకాల ఆదాయం", "costs": "అమ్మకం ఖర్చులు",
        "profit": "అంచనా లాభం", "add": "జోడించండి", "save": "సేవ్ చేయండి", "delete": "తొలగించండి",
        "village": "గ్రామం", "farm_name": "పొలం పేరు", "acres": "విస్తీర్ణం (ఎకరాలు)",
        "soil": "నేల రకం", "irrigation": "నీటిపారుదల విధానం", "crop": "పంట పేరు",
        "variety": "రకం", "farm": "పొలం", "planting": "నాటిన తేదీ",
        "expected": "అంచనా కోత తేదీ", "stage": "పంట దశ", "category": "వర్గం",
        "amount": "మొత్తం (₹)", "description": "వివరణ", "date": "తేదీ",
        "type": "పని", "quantity": "పరిమాణం (కిలోలు)", "grade": "గ్రేడ్",
        "price": "క్వింటాలుకు ధర (₹)", "buyer": "కొనుగోలుదారు", "market": "మార్కెట్ / ప్రాంతం",
        "transport": "రవాణా ఖర్చు (₹)", "other": "ఇతర అమ్మకం ఖర్చులు (₹)",
        "title": "రిమైండర్", "due": "గడువు తేదీ", "profile": "ప్రొఫైల్", "name": "పేరు",
        "language": "భాష", "phone": "ఫోన్ నంబర్", "password": "పాస్‌వర్డ్",
        "login": "లాగిన్", "register": "ఖాతా సృష్టించండి", "no_account": "కొత్తవారా? ఖాతా సృష్టించండి",
        "have_account": "ఖాతా ఉందా? లాగిన్ అవ్వండి", "bad_login": "ఫోన్ నంబర్ లేదా పాస్‌వర్డ్ తప్పు.",
        "phone_exists": "ఈ ఫోన్ నంబర్‌తో ఖాతా ఇప్పటికే ఉంది.",
        "required": "అవసరమైన వివరాలను నమోదు చేయండి.", "done": "పూర్తయినట్లు గుర్తించండి",
        "overdue": "గడువు దాటింది", "pending": "పెండింగ్", "completed": "పూర్తయింది",
        "no_data": "ఇంకా వివరాలు లేవు. మొదటి వివరాన్ని జోడించండి.",
        "farm_deleted": "పొలం తొలగించబడింది.", "crop_deleted": "పంట తొలగించబడింది.",
        "expense_deleted": "ఖర్చు తొలగించబడింది.", "activity_deleted": "పని తొలగించబడింది.",
        "harvest_deleted": "కోత వివరాలు తొలగించబడ్డాయి.", "sale_deleted": "అమ్మకం తొలగించబడింది.",
        "reminder_deleted": "రిమైండర్ తొలగించబడింది.", "profile_saved": "ప్రొఫైల్ నవీకరించబడింది.",
        "profit_note": "అంచనా లాభం = అమ్మకాల ఆదాయం − నమోదైన ఖర్చులు − అమ్మకం ఖర్చులు. ఇది ఆడిట్ చేసిన లెక్క కాదు.",
        "expense_link": "ఖర్చును పంటకు అనుసంధానించండి (ఐచ్ఛికం)", "linked": "అనుసంధానించిన పంట",
        "all_farms": "అన్ని పొలాలు", "select_farm": "పొలాన్ని ఎంచుకోండి",
        "soil_red": "ఎర్ర నేల", "soil_black": "నల్ల నేల", "soil_sandy": "ఇసుక నేల",
        "soil_loamy": "ఒండ్రు నేల", "soil_clay": "బంకమట్టి", "soil_other": "ఇతర",
        "irr_drip": "డ్రిప్", "irr_furrow": "కాలువల ద్వారా", "irr_sprinkler": "స్ప్రింక్లర్",
        "irr_rainfed": "వర్షాధారం", "irr_other": "ఇతర",
        "stage_vegetative": "ఆకుపెరుగుదల", "stage_flowering": "పూత దశ",
        "stage_fruiting": "కాయ దశ", "stage_harvest": "కోత దశ",
        "exp_seeds": "విత్తనాలు", "exp_fertilizers": "ఎరువులు", "exp_pesticides": "పురుగుమందులు",
        "exp_labour": "కూలీలు", "exp_irrigation": "నీటిపారుదల", "exp_transport": "రవాణా",
        "exp_other": "ఇతర", "act_spraying": "మందు పిచికారీ", "act_irrigation": "నీటి పారుదల",
        "act_weeding": "కలుపు తీయడం", "act_fertilising": "ఎరువులు వేయడం", "act_other": "ఇతర",
        "rem_irrigation": "నీటి పారుదల", "rem_soil_test": "నేల పరీక్ష",
        "rem_inspection": "పొలం పరిశీలన", "rem_other": "ఇతర",
    }
}

def tr(key):
    lang = st.session_state.get("language", "English")
    return TEXT.get(lang, TEXT["English"]).get(key, TEXT["English"].get(key, key))

def money(value):
    return f"₹{value:,.2f}"

def show_table(rows, columns=None):
    if rows:
        df = pd.DataFrame(rows)
        if columns:
            df = df[columns]
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info(tr("no_data"))

def landing_page():
    """Public marketing page shown before authentication."""
    st.markdown("<div class='landing-shell'>", unsafe_allow_html=True)
    nav1, nav2, nav3 = st.columns([5,1,1])
    with nav1:
        st.markdown("<div class='brand-pill'>🌱 SMARTFARM AI</div>", unsafe_allow_html=True)
    with nav2:
        if st.button("Log in", key="landing_login", use_container_width=True):
            st.session_state.auth_mode = "login"
            st.session_state.show_auth = True
            st.rerun()
    with nav3:
        if st.button("Get started", key="landing_register", use_container_width=True):
            st.session_state.auth_mode = "register"
            st.session_state.show_auth = True
            st.rerun()

    st.markdown("""
    <section class='landing-hero'>
      <div class='landing-kicker'>A smarter way to manage every acre</div>
      <h1>Grow better.<br>Manage smarter.</h1>
      <p>Bring your farm records, crop cycles, expenses, harvests and daily activities together in one simple workspace.</p>
    </section>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:34px'></div><div class='landing-kicker'>YOUR FARM, ONE WORKSPACE</div>", unsafe_allow_html=True)
    st.markdown("## Everything your farm needs, in one place")
    st.markdown("From the first planting record to harvest and sales, keep the important details organised.")
    feature_data = [
        ("https://images.unsplash.com/photo-1464226184884-fa280b87c399?auto=format&fit=crop&w=900&q=80", "Farm management", "Organise farm profiles, land area, soil types and irrigation details."),
        ("https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=900&q=80", "Crop tracking", "Track crop cycles, varieties, planting dates and growth stages."),
        ("https://images.unsplash.com/photo-1560493676-04071c5f467b?auto=format&fit=crop&w=900&q=80", "Harvest & sales", "Record harvest quantities, buyers, market prices and selling costs."),
    ]
    cols = st.columns(3)
    for col, (src, title, desc) in zip(cols, feature_data):
        with col:
            st.markdown(f"<div class='landing-feature'><img src='{src}' alt='{title}'><div class='landing-feature-copy'><h3>{title}</h3><p>{desc}</p></div></div>", unsafe_allow_html=True)

    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
    more = st.columns(3)
    extras = [
        ("📊", "Understand your finances", "See recorded expenses, sales revenue and estimated profit."),
        ("🗓️", "Stay on schedule", "Create reminders for irrigation, soil tests and field inspections."),
        ("🌐", "Your language, your way", "Use the workspace in English or Telugu."),
    ]
    for col, (ico, title, desc) in zip(more, extras):
        with col:
            st.markdown(f"<div class='landing-stat'><strong>{ico} {title}</strong><p>{desc}</p></div>", unsafe_allow_html=True)

    st.markdown("<div style='height:34px'></div><div class='landing-cta'><div class='landing-kicker'>READY TO GET ORGANISED?</div><h2>Make every farm decision easier.</h2><p>Start building a clear record of your farm, one activity at a time.</p></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        if st.button("Create your free account →", key="landing_bottom_register", use_container_width=True):
            st.session_state.auth_mode = "register"
            st.session_state.show_auth = True
            st.rerun()
    st.markdown("<div class='landing-footer'>🌱 SMARTFARM AI · Practical tools for better farm management</div></div>", unsafe_allow_html=True)

def login_screen():
    st.markdown("<div class='login-wrap'>", unsafe_allow_html=True)
    st.markdown("<div class='brand-pill'>🌱 SMARTFARM INTELLIGENCE</div>", unsafe_allow_html=True)
    st.title("Grow smarter. Farm better.")
    st.caption("Your farm operations, insights and records in one place.")
    st.session_state.setdefault("auth_mode", "login")
    mode = st.radio("Account", ["login", "register"], horizontal=True,
                    format_func=lambda x: tr("login") if x == "login" else tr("register"),
                    index=0 if st.session_state.auth_mode == "login" else 1)
    st.session_state.auth_mode = mode
    with st.form("auth_form"):
        name = st.text_input(tr("name"), placeholder="Your name") if mode == "register" else ""
        phone = st.text_input(tr("phone"), placeholder="10-digit phone number")
        password = st.text_input(tr("password"), type="password")
        submitted = st.form_submit_button(tr("register") if mode == "register" else tr("login"), use_container_width=True)
    if submitted:
        if not phone.strip() or not password:
            st.error(tr("required"))
        elif mode == "register":
            if not name.strip():
                st.error(tr("required"))
            else:
                ok, msg = create_user(name.strip(), phone.strip(), password)
                if ok:
                    st.success("Account created. Please log in.")
                    st.session_state.auth_mode = "login"
                    st.rerun()
                else:
                    st.error(tr(msg))
        else:
            user = authenticate(phone.strip(), password)
            if user:
                st.session_state.user_id = user["id"]
                st.session_state.user_name = user["name"]
                st.rerun()
            else:
                st.error(tr("bad_login"))
    st.markdown("</div>", unsafe_allow_html=True)


def add_satellite_tiles(map_obj):
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Tiles © Esri — Source: Esri, Maxar, Earthstar Geographics, and the GIS User Community",
        name="Satellite imagery",
        overlay=False,
        control=True,
    ).add_to(map_obj)
    folium.LayerControl(collapsed=True).add_to(map_obj)
    return map_obj

def farm_map(farms, height=460, key="farm_overview_map"):
    located = [f for f in farms if f.get("latitude") is not None and f.get("longitude") is not None]
    if not located:
        st.info("No farm coordinates saved yet. Open **My Farms** and pin a location to see it on the satellite map.")
        return
    center = [located[0]["latitude"], located[0]["longitude"]]
    m = folium.Map(location=center, zoom_start=13, control_scale=True, tiles=None)
    add_satellite_tiles(m)
    for farm in located:
        folium.Marker(
            [farm["latitude"], farm["longitude"]],
            tooltip=farm["name"],
            popup=f"{farm['name']} · {farm['area']:.2f} acres",
            icon=folium.Icon(color="green", icon="leaf", prefix="fa"),
        ).add_to(m)
    st_folium(m, height=height, use_container_width=True, returned_objects=[], key=key)

def farm_location_picker():
    st.caption("Click the map to pin the centre of your farm. You can zoom in for a more accurate location.")
    m = folium.Map(location=[17.05, 79.27], zoom_start=11, control_scale=True, tiles=None)
    add_satellite_tiles(m)
    picked = st.session_state.get("farm_pick_latlon")
    if picked:
        folium.Marker(picked, tooltip="Selected farm location", icon=folium.Icon(color="green", icon="map-pin", prefix="fa")).add_to(m)
    result = st_folium(m, height=340, use_container_width=True, returned_objects=["last_clicked"], key="farm_location_picker")
    clicked = result.get("last_clicked") if result else None
    if clicked:
        st.session_state["farm_pick_latlon"] = [clicked["lat"], clicked["lng"]]
    picked = st.session_state.get("farm_pick_latlon")
    if picked:
        st.success(f"Selected coordinates: {picked[0]:.6f}, {picked[1]:.6f}")
    else:
        st.info("No location selected yet. Click anywhere on the satellite map.")
    return picked

def farm_options(user_id):
    return list_farms(user_id)

def crop_options(user_id):
    return list_crops(user_id)

def dashboard(user_id):
    totals = dashboard_totals(user_id)
    farms = list_farms(user_id)
    crops = list_crops(user_id)
    expenses = list_expenses(user_id)
    reminders = list_reminders(user_id)
    st.markdown("<div class='section-kicker'>FARM OVERVIEW · FIELD INTELLIGENCE</div>", unsafe_allow_html=True)
    st.title(f"Good to see you, {st.session_state.user_name} 👋")
    st.markdown("<div class='hero-panel'><div class='section-kicker'>SMART FARMING CONTROL CENTRE</div><h2 style='margin:.45rem 0 .3rem 0'>A clearer view of every acre.</h2><p>Track operations, understand performance and keep your next farm activity on schedule.</p></div>", unsafe_allow_html=True)

    cards = [
        (tr("area"), f"{totals['area']:.2f} ac"),
        (tr("active"), str(totals["active_crops"])),
        (tr("expense"), money(totals["expenses"])),
        (tr("revenue"), money(totals["revenue"])),
        (tr("harvested"), f"{totals['harvest_kg']:,.1f} kg"),
        (tr("profit"), money(totals["profit"])),
        (tr("reminders"), str(totals["pending_reminders"])),
        ("Farms registered", str(len(farms))),
    ]
    cols = st.columns(4)
    for i, (label, value) in enumerate(cards):
        with cols[i % 4]:
            st.metric(label, value)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    left, right = st.columns([1.35, 1])
    with left:
        st.subheader("📊 Financial performance")
        if expenses:
            df = pd.DataFrame(expenses)
            chart = df.groupby("category", as_index=False)["amount"].sum().sort_values("amount", ascending=False)
            st.bar_chart(chart.set_index("category"), color="#9bd96b")
        else:
            st.info("Your expense chart will appear once you record farm spending.")
    with right:
        st.subheader("🌿 Crop portfolio")
        if crops:
            for crop in crops[:5]:
                st.markdown(f"**{crop['crop']} · {crop['variety']}**")
                st.caption(f"{crop['farm_name']} · {tr('stage_'+crop['stage'])}")
                st.progress({"vegetative":25,"flowering":50,"fruiting":75,"harvest":100}.get(crop["stage"],10))
        else:
            st.info("Add your first crop cycle to start tracking crop progress.")

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
    st.subheader("🛰️ Satellite farm locations")
    st.caption("Satellite basemap with saved farm pins. This view shows location imagery, not live crop-health measurements.")
    farm_map(farms, height=430, key="dashboard_satellite_farms")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    c1, c2 = st.columns([1,1])
    with c1:
        st.subheader("⏰ Upcoming reminders")
        pending = [r for r in reminders if not r["is_done"]]
        if pending:
            for item in pending[:5]:
                with st.container(border=True):
                    st.markdown(f"**{item['title']}**")
                    st.caption(f"{item['category'].replace('_',' ').title()} · Due {item['due_date']}")
        else:
            st.info("No pending reminders. You're up to date.")
    with c2:
        st.subheader("🚜 Your farms")
        if farms:
            for farm in farms[:4]:
                with st.container(border=True):
                    st.markdown(f"**{farm['name']}**")
                    st.caption(f"{farm['village'] or 'Location not added'} · {farm['area']:.2f} acres · {farm['soil'].title()} soil")
        else:
            st.info("Create a farm profile to organise your land and crop cycles.")

    st.caption(tr("profit_note"))

def farms_page(uid):
    st.title(f"🚜 {tr('farms')}")
    with st.expander(f"➕ {tr('add')} {tr('farms')}", expanded=False):
        st.markdown("#### Pin your farm on satellite imagery")
        picked_location = farm_location_picker()
        with st.form("farm_add"):
            c1, c2 = st.columns(2)
            name = c1.text_input(tr("farm_name"))
            village = c2.text_input(tr("village"))
            area = c1.number_input(tr("acres"), min_value=0.01, step=0.25)
            soil = c2.selectbox(tr("soil"), ["red","black","sandy","loamy","clay","other"], format_func=lambda x: tr("soil_"+x))
            irrigation = c1.selectbox(tr("irrigation"), ["drip","furrow","sprinkler","rainfed","other"], format_func=lambda x: tr("irr_"+x))
            if st.form_submit_button(tr("save")):
                if name.strip():
                    lat = picked_location[0] if picked_location else None
                    lon = picked_location[1] if picked_location else None
                    add_farm(uid, name.strip(), village.strip(), area, soil, irrigation, lat, lon)
                    st.session_state.pop("farm_pick_latlon", None)
                    st.success("Farm saved with its map pin." if picked_location else "Farm saved. You can add its map pin later.")
                    st.rerun()
                st.error(tr("required"))
    rows = list_farms(uid)
    if rows:
        for row in rows:
            with st.container(border=True):
                c1, c2 = st.columns([5,1])
                c1.markdown(f"**{row['name']}** · {row['village'] or '—'}")
                c1.write(f"{row['area']:.2f} acres · {tr('soil_'+row['soil'])} · {tr('irr_'+row['irrigation'])}")
                if row.get("latitude") is not None and row.get("longitude") is not None:
                    c1.caption(f"📍 {row['latitude']:.5f}, {row['longitude']:.5f} · Satellite pin saved")
                if c2.button(tr("delete"), key=f"farm_del_{row['id']}"):
                    delete_farm(uid, row["id"])
                    st.rerun()
    else:
        st.info(tr("no_data"))

def crops_page(uid):
    st.title(f"🌶️ {tr('crops')}")
    farms = farm_options(uid)
    if not farms:
        st.warning("Add a farm before adding a crop cycle.")
        return
    with st.expander(f"➕ {tr('add')} {tr('crops')}"):
        with st.form("crop_add"):
            farm_map = {f"{x['name']} ({x['village']})": x["id"] for x in farms}
            farm_label = st.selectbox(tr("farm"), list(farm_map))
            c1,c2 = st.columns(2)
            crop = c1.text_input(tr("crop"), value="Chilli")
            variety = c2.text_input(tr("variety"), value="Teja")
            area = c1.number_input(tr("acres"), min_value=0.01, step=0.25)
            stage = c2.selectbox(tr("stage"), ["vegetative","flowering","fruiting","harvest"], format_func=lambda x: tr("stage_"+x))
            planted = c1.date_input(tr("planting"), value=date.today())
            expected = c2.date_input(tr("expected"), value=date.today()+timedelta(days=120))
            if st.form_submit_button(tr("save")):
                add_crop(uid, farm_map[farm_label], crop, variety, area, stage, planted.isoformat(), expected.isoformat())
                st.success("Crop cycle saved.")
                st.rerun()
    rows = list_crops(uid)
    if rows:
        for r in rows:
            with st.container(border=True):
                a,b = st.columns([5,1])
                a.markdown(f"**{r['crop']} — {r['variety']}**")
                a.write(f"{r['farm_name']} · {r['area']:.2f} acres · {tr('stage_'+r['stage'])}")
                a.caption(f"{tr('planting')}: {r['planting_date']} · {tr('expected')}: {r['expected_harvest']}")
                if b.button(tr("delete"), key=f"crop_del_{r['id']}"):
                    delete_crop(uid, r["id"]); st.rerun()
    else:
        st.info(tr("no_data"))

def expenses_page(uid):
    st.title(f"💸 {tr('expenses')}")
    crops = crop_options(uid)
    with st.expander(f"➕ {tr('add')} {tr('expenses')}"):
        with st.form("expense_add"):
            c1,c2 = st.columns(2)
            cat = c1.selectbox(tr("category"), ["seeds","fertilizers","pesticides","labour","irrigation","transport","other"], format_func=lambda x: tr("exp_"+x))
            amount = c2.number_input(tr("amount"), min_value=0.01, step=100.0)
            spent = c1.date_input(tr("date"), value=date.today())
            desc = c2.text_input(tr("description"))
            crop_map = {"—": None}
            crop_map.update({f"{x['crop']} / {x['variety']} · {x['farm_name']}": x["id"] for x in crops})
            linked = st.selectbox(tr("linked"), list(crop_map))
            if st.form_submit_button(tr("save")):
                add_expense(uid, cat, amount, spent.isoformat(), desc, crop_map[linked])
                st.success("Expense saved."); st.rerun()
    rows = list_expenses(uid)
    if rows:
        st.metric(tr("expense"), money(sum(x["amount"] for x in rows)))
        for r in rows:
            c1,c2 = st.columns([6,1])
            c1.write(f"**{money(r['amount'])}** · {tr('exp_'+r['category'])} · {r['spent_on']}")
            c1.caption(f"{r['description'] or '—'} · {r['crop_name'] or 'Not linked'}")
            if c2.button(tr("delete"), key=f"exp_del_{r['id']}"):
                delete_expense(uid,r["id"]); st.rerun()
    else: st.info(tr("no_data"))

def activities_page(uid):
    st.title(f"🧑‍🌾 {tr('activities')}")
    crops = crop_options(uid)
    with st.expander(f"➕ {tr('add')} {tr('activities')}"):
        with st.form("activity_add"):
            typ = st.selectbox(tr("type"), ["spraying","irrigation","weeding","fertilising","other"], format_func=lambda x: tr("act_"+x))
            d = st.date_input(tr("date"))
            crop_map = {"—": None}
            crop_map.update({f"{x['crop']} / {x['variety']}":x["id"] for x in crops})
            crop = st.selectbox(tr("crop"), list(crop_map))
            note = st.text_input(tr("description"))
            if st.form_submit_button(tr("save")):
                add_activity(uid,typ,d.isoformat(),note,crop_map[crop]); st.success("Activity saved."); st.rerun()
    rows=list_activities(uid)
    if rows: show_table(rows,["activity_type","activity_date","crop_name","notes"])
    else: st.info(tr("no_data"))
    for r in rows:
        if st.button(f"{tr('delete')} #{r['id']}",key=f"actdel{r['id']}"):
            delete_activity(uid,r["id"]); st.rerun()

def harvest_sales_page(uid):
    st.title(f"⚖️ {tr('harvest')}")
    crops = crop_options(uid)
    crop_map = {f"{x['crop']} / {x['variety']} · {x['farm_name']}":x["id"] for x in crops}
    if not crop_map:
        st.warning("Add a crop cycle before recording harvest or sales.")
        return
    left,right=st.columns(2)
    with left:
        st.subheader("Harvest")
        with st.form("harvest_add"):
            crop=st.selectbox(tr("crop"),list(crop_map),key="harv_crop")
            qty=st.number_input(tr("quantity"),min_value=0.1,step=10.0,key="harv_qty")
            grade=st.text_input(tr("grade"),value="A")
            d=st.date_input(tr("date"),key="harv_date")
            if st.form_submit_button(tr("save")):
                add_harvest(uid,crop_map[crop],qty,grade,d.isoformat()); st.success("Harvest saved."); st.rerun()
        rows=list_harvests(uid)
        show_table(rows,["harvest_date","crop_name","quantity_kg","grade"] if rows else None)
        for r in rows:
            if st.button(f"{tr('delete')} #{r['id']}",key=f"hdel{r['id']}"):
                delete_harvest(uid,r["id"]); st.rerun()
    with right:
        st.subheader("Sales")
        with st.form("sale_add"):
            crop=st.selectbox(tr("crop"),list(crop_map),key="sale_crop")
            qty=st.number_input(tr("quantity"),min_value=0.1,step=10.0,key="sale_qty")
            price=st.number_input(tr("price"),min_value=0.01,step=100.0)
            buyer=st.text_input(tr("buyer")); market=st.text_input(tr("market"))
            transport=st.number_input(tr("transport"),min_value=0.0,step=50.0)
            other=st.number_input(tr("other"),min_value=0.0,step=50.0)
            d=st.date_input(tr("date"),key="sale_date")
            if st.form_submit_button(tr("save")):
                add_sale(uid,crop_map[crop],qty,price,buyer,market,transport,other,d.isoformat())
                st.success("Sale saved."); st.rerun()
        rows=list_sales(uid)
        show_table(rows,["sale_date","crop_name","quantity_kg","price_per_quintal","buyer","market","transport_cost","other_cost"] if rows else None)
        for r in rows:
            if st.button(f"{tr('delete')} #{r['id']}",key=f"sdel{r['id']}"):
                delete_sale(uid,r["id"]); st.rerun()

def reminders_page(uid):
    st.title(f"⏰ {tr('reminders')}")
    with st.expander(f"➕ {tr('add')} {tr('reminders')}"):
        with st.form("reminder_add"):
            title=st.text_input(tr("title"))
            category=st.selectbox(tr("category"),["irrigation","soil_test","inspection","other"],format_func=lambda x:tr("rem_"+x))
            due=st.date_input(tr("due"),value=date.today()+timedelta(days=1))
            if st.form_submit_button(tr("save")):
                if title.strip():
                    add_reminder(uid,title.strip(),category,due.isoformat()); st.success("Reminder saved."); st.rerun()
                st.error(tr("required"))
    rows=list_reminders(uid)
    if rows:
        for r in rows:
            with st.container(border=True):
                a,b,c=st.columns([5,2,1])
                status = tr("completed") if r["is_done"] else (tr("overdue") if r["due_date"] < date.today().isoformat() else tr("pending"))
                a.markdown(f"**{r['title']}** · {tr('rem_'+r['category'])}")
                a.caption(f"{tr('due')}: {r['due_date']} · {status}")
                if not r["is_done"] and b.button(tr("done"),key=f"done{r['id']}"):
                    complete_reminder(uid,r["id"]); st.rerun()
                if c.button("✕",key=f"rdel{r['id']}"):
                    delete_reminder(uid,r["id"]); st.rerun()
    else: st.info(tr("no_data"))

def settings_page(uid):
    st.title(f"⚙️ {tr('settings')}")
    user=get_user(uid)
    with st.form("profile_form"):
        name=st.text_input(tr("name"),value=user["name"])
        phone=st.text_input(tr("phone"),value=user["phone"],disabled=True)
        lang=st.selectbox(tr("language"),["English","తెలుగు"],index=0 if user["language"]=="English" else 1)
        if st.form_submit_button(tr("save")):
            update_profile(uid,name,lang)
            st.session_state.user_name=name
            st.session_state.language=lang
            st.success(tr("profile_saved")); st.rerun()
    st.caption("Your data is stored in smartfarm.db on the server running this app. Back up the database file regularly.")

def main():
    if "user_id" not in st.session_state:
        st.session_state.setdefault("language","English")
        if st.session_state.get("show_auth", False):
            c1, c2 = st.columns([5,1])
            with c2:
                if st.button("← Back to home", use_container_width=True):
                    st.session_state.show_auth = False
                    st.rerun()
            login_screen()
        else:
            landing_page()
        return
    user=get_user(st.session_state.user_id)
    if not user:
        st.session_state.pop("user_id",None)
        st.rerun()
    st.session_state.language=user["language"]
    with st.sidebar:
        st.markdown("<div class='brand-pill'>🌱 SMARTFARM</div>", unsafe_allow_html=True)
        st.markdown("### Farm intelligence")
        st.caption(f"Welcome back, **{user['name']}**")
        st.divider()
        page=st.radio("WORKSPACE",
            ["dashboard","farms","crops","expenses","activities","harvest","reminders","settings"],
            format_func=lambda x: {
                "dashboard":"◫  Overview","farms":"▦  My Farms","crops":"♧  Crop Management",
                "expenses":"₹  Expenses","activities":"☷  Activities","harvest":"⚖  Harvest & Sales",
                "reminders":"◷  Reminders","settings":"⚙  Settings"
            }.get(x,x), label_visibility="visible")
        st.divider()
        language=st.selectbox(tr("language"),["English","తెలుగు"],index=0 if user["language"]=="English" else 1)
        if language != user["language"]:
            update_profile(user["id"],user["name"],language)
            st.session_state.language=language
            st.rerun()
        st.caption("SMARTFARM · FIELD OPERATIONS")
        if st.button("↪  "+tr("logout"),use_container_width=True):
            for k in ["user_id","user_name"]:
                st.session_state.pop(k,None)
            st.rerun()
    uid=user["id"]
    if page=="dashboard": dashboard(uid)
    elif page=="farms": farms_page(uid)
    elif page=="crops": crops_page(uid)
    elif page=="expenses": expenses_page(uid)
    elif page=="activities": activities_page(uid)
    elif page=="harvest": harvest_sales_page(uid)
    elif page=="reminders": reminders_page(uid)
    elif page=="settings": settings_page(uid)

if __name__=="__main__":
    main()
