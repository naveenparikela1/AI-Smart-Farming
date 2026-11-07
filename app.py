import streamlit as st
import pandas as pd
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
.stApp {
    background: radial-gradient(ellipse at top right, #132b36 0%, #07111f 48%, #050b14 100%);
    color: #eaf2f8;
}
header[data-testid="stHeader"] {
    background: rgba(7,17,31,0.85);
}
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #101f32, #07111f);
    border-right: 1px solid #263b4d;
}
section[data-testid="stSidebar"] * {
    color: #eaf2f8;
}
h1, h2, h3 {
    color: #eaf2f8 !important;
    letter-spacing: -0.5px;
}
.stMetric {
    background: linear-gradient(145deg, #14283a, #0c1928);
    border: 1px solid #294456;
    border-radius: 16px;
    padding: 18px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.20);
}
[data-testid="stMetricValue"] {
    color: #a3ff12;
    font-weight: 700;
}
[data-testid="stMetricLabel"] {
    color: #a9bdca;
}
.stButton > button, .stFormSubmitButton > button {
    background: linear-gradient(90deg, #a3ff12, #72d600);
    color: #07111f;
    border: none;
    border-radius: 10px;
    font-weight: 700;
    min-height: 42px;
}
.stButton > button:hover, .stFormSubmitButton > button:hover {
    background: #c0ff55;
    color: #07111f;
    border: none;
}
input, textarea, [data-baseweb="select"] > div {
    background-color: #102235 !important;
    border-color: #345064 !important;
    border-radius: 9px !important;
}
div[data-testid="stDataFrame"] {
    border: 1px solid #294456;
    border-radius: 12px;
    overflow: hidden;
}
div[data-testid="stAlert"] {
    border-radius: 12px;
}
hr {
    border-color: #294456;
}
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

def login_screen():
    st.markdown("<div class='login-wrap'>", unsafe_allow_html=True)
    st.title("🌱 SmartFarm")
    st.caption("Smart Farming Dashboard")
    st.session_state.setdefault("auth_mode", "login")
    mode = st.radio("Account", ["login", "register"], horizontal=True,
                    format_func=lambda x: tr("login") if x == "login" else tr("register"),
                    index=0 if st.session_state.auth_mode == "login" else 1)
    st.session_state.auth_mode = mode
    with st.form("auth_form"):
        name = st.text_input(tr("name")) if mode == "register" else ""
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

def farm_options(user_id):
    return list_farms(user_id)

def crop_options(user_id):
    return list_crops(user_id)

def dashboard(user_id):
    st.title(f"🌱 {tr('dashboard')}")
    st.subheader(f"{tr('welcome')} {st.session_state.user_name}")
    st.caption(tr("sample"))
    totals = dashboard_totals(user_id)
    cards = [
        (tr("area"), f"{totals['area']:.2f} acres"),
        (tr("active"), str(totals["active_crops"])),
        (tr("expense"), money(totals["expenses"])),
        (tr("harvested"), f"{totals['harvest_kg']:,.1f} kg"),
        (tr("revenue"), money(totals["revenue"])),
        (tr("costs"), money(totals["selling_costs"])),
        (tr("profit"), money(totals["profit"])),
        (tr("reminders"), str(totals["pending_reminders"])),
    ]
    cols = st.columns(4)
    for i, (label, value) in enumerate(cards):
        with cols[i % 4]:
            st.metric(label, value)
    st.info(tr("profit_note"))
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Expense breakdown")
        exp = list_expenses(user_id)
        if exp:
            df = pd.DataFrame(exp)
            chart = df.groupby("category", as_index=False)["amount"].sum()
            st.bar_chart(chart.set_index("category"))
        else:
            st.info(tr("no_data"))
    with c2:
        st.subheader("Recent reminders")
        rem = list_reminders(user_id)
        show_table(rem[:6], ["title", "due_date", "status"] if rem else None)

def farms_page(uid):
    st.title(f"🚜 {tr('farms')}")
    with st.expander(f"➕ {tr('add')} {tr('farms')}", expanded=False):
        with st.form("farm_add"):
            c1, c2 = st.columns(2)
            name = c1.text_input(tr("farm_name"))
            village = c2.text_input(tr("village"))
            area = c1.number_input(tr("acres"), min_value=0.01, step=0.25)
            soil = c2.selectbox(tr("soil"), ["red","black","sandy","loamy","clay","other"], format_func=lambda x: tr("soil_"+x))
            irrigation = c1.selectbox(tr("irrigation"), ["drip","furrow","sprinkler","rainfed","other"], format_func=lambda x: tr("irr_"+x))
            if st.form_submit_button(tr("save")):
                if name.strip():
                    add_farm(uid, name.strip(), village.strip(), area, soil, irrigation)
                    st.success("Farm saved.")
                    st.rerun()
                st.error(tr("required"))
    rows = list_farms(uid)
    if rows:
        for row in rows:
            with st.container(border=True):
                c1, c2 = st.columns([5,1])
                c1.markdown(f"**{row['name']}** · {row['village'] or '—'}")
                c1.write(f"{row['area']:.2f} acres · {tr('soil_'+row['soil'])} · {tr('irr_'+row['irrigation'])}")
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
        login_screen()
        return
    user=get_user(st.session_state.user_id)
    st.session_state.language=user["language"]
    with st.sidebar:
        st.markdown("# 🌱 SmartFarm")
        st.caption(f"Signed in as **{user['name']}**")
        page=st.radio("Navigation",
            ["dashboard","farms","crops","expenses","activities","harvest","reminders","settings"],
            format_func=lambda x: tr(x), label_visibility="collapsed")
        st.divider()
        language=st.selectbox(tr("language"),["English","తెలుగు"],index=0 if user["language"]=="English" else 1)
        if language != user["language"]:
            update_profile(user["id"],user["name"],language)
            st.session_state.language=language
            st.rerun()
        if st.button(tr("logout"),use_container_width=True):
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
