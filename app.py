import streamlit as st
import sqlite3, hashlib, json
from datetime import date, timedelta

st.set_page_config(page_title="Wanderly Planner", page_icon="✈️", layout="wide")

DB_FILE = "wanderly.db"
DESTINATIONS = [
    {"name":"Goa","region":"Beach escape","emoji":"🏖️","cost":3500,"tags":["Relaxation","Adventure","Family"],"desc":"Golden beaches, sunsets, seafood and water sports.","places":["Baga Beach","Fort Aguada","Anjuna Flea Market"]},
    {"name":"Jaipur","region":"Royal heritage","emoji":"🏰","cost":2800,"tags":["Culture","Family","Nature"],"desc":"Pink City palaces, colourful markets and Rajasthani food.","places":["Hawa Mahal","Amber Fort","City Palace"]},
    {"name":"Manali","region":"Mountain retreat","emoji":"🏔️","cost":4200,"tags":["Adventure","Nature","Relaxation"],"desc":"Mountain views, pine forests and outdoor adventures.","places":["Solang Valley","Hadimba Temple","Old Manali"]},
    {"name":"Mumbai","region":"City & culture","emoji":"🌆","cost":2500,"tags":["Culture","Food","Family"],"desc":"Coastal promenades, historic landmarks and street food.","places":["Gateway of India","Marine Drive","Colaba Causeway"]},
    {"name":"Kerala","region":"Backwaters & nature","emoji":"🌴","cost":4000,"tags":["Nature","Relaxation","Family"],"desc":"Lush greenery, backwaters, beaches and local cuisine.","places":["Alleppey Backwaters","Munnar","Fort Kochi"]},
    {"name":"Rishikesh","region":"River & adventure","emoji":"🛶","cost":3000,"tags":["Adventure","Nature","Relaxation"],"desc":"Riverside views, yoga, rafting and peaceful cafés.","places":["Triveni Ghat","Ram Jhula","Neer Garh Waterfall"]},
]
HOTELS = [
    {"name":"Goa Beach Resort","city":"Goa","rating":4.5,"price":2500,"amenities":"Pool · Wi-Fi · Breakfast"},
    {"name":"Paradise Hotel","city":"Goa","rating":4.2,"price":2000,"amenities":"Wi-Fi · Restaurant · Parking"},
    {"name":"Pride Amber Vilas Resort","city":"Jaipur","rating":4.4,"price":2725,"amenities":"Pool · Spa · Restaurant"},
    {"name":"WelcomHeritage Traditional Haveli","city":"Jaipur","rating":4.6,"price":2843,"amenities":"Rooftop pool · Spa · Wi-Fi"},
    {"name":"Mountain View Stay","city":"Manali","rating":4.3,"price":2200,"amenities":"Mountain view · Wi-Fi · Café"},
    {"name":"Harbour City Hotel","city":"Mumbai","rating":4.1,"price":3200,"amenities":"Wi-Fi · Restaurant · City view"},
]

def db():
    con=sqlite3.connect(DB_FILE)
    con.execute("CREATE TABLE IF NOT EXISTS users (name TEXT, email TEXT UNIQUE, password TEXT)")
    con.execute("CREATE TABLE IF NOT EXISTS saved_trips (email TEXT, destination TEXT, days INTEGER, budget REAL, preference TEXT, created TEXT)")
    con.commit()
    return con

def hash_pw(p):
    return hashlib.sha256(p.encode()).hexdigest()

def money(n):
    return "₹{:,.0f}".format(n)

if "user" not in st.session_state: st.session_state.user=None
if "page" not in st.session_state: st.session_state.page="Home"

st.markdown("""
<style>
.stApp {background:linear-gradient(135deg,#07171d 0%,#102a33 55%,#173640 100%);color:#eff7f5}
h1,h2,h3,p,label,.stMarkdown {color:#eff7f5}
div[data-testid="stMetric"] {background:#153640;padding:16px;border:1px solid #28515c;border-radius:14px}
div.stButton>button {border-radius:24px;background:#f6b352;color:#07171d;border:0;font-weight:700}
div[data-testid="stForm"] {background:#102a33;padding:18px;border-radius:14px;border:1px solid #28515c}
.card {background:#102a33;border:1px solid #28515c;border-radius:16px;padding:18px;margin-bottom:12px;min-height:150px}
.small {color:#a9c2c7}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("# ✈️ Wanderly")
    st.caption("Travel smarter. Wander better.")
    if st.session_state.user:
        st.success("Signed in as "+st.session_state.user["name"])
        pages=["Home","Trip Planner","Explore","Budget Optimizer","Hotel Finder","My Trips"]
        selected=st.radio("Navigate",pages,index=pages.index(st.session_state.page) if st.session_state.page in pages else 0)
        st.session_state.page=selected
        if st.button("Log out",use_container_width=True):
            st.session_state.user=None; st.session_state.page="Home"; st.rerun()
    else:
        st.info("Create an account or log in to save your travel plans.")
        st.session_state.page="Home"
        auth_mode=st.radio("Account",["Login","Sign up"])
        with st.form("auth_form"):
            name=st.text_input("Full name") if auth_mode=="Sign up" else ""
            email=st.text_input("Email").strip().lower()
            password=st.text_input("Password",type="password")
            submitted=st.form_submit_button("Create account" if auth_mode=="Sign up" else "Login",use_container_width=True)
        if submitted:
            if not email or not password or (auth_mode=="Sign up" and not name):
                st.error("Please fill in all required fields.")
            else:
                con=db()
                if auth_mode=="Sign up":
                    try:
                        con.execute("INSERT INTO users VALUES (?,?,?)",(name,email,hash_pw(password))); con.commit()
                        st.session_state.user={"name":name,"email":email}; st.success("Account created!"); st.rerun()
                    except sqlite3.IntegrityError: st.error("This email already has an account. Please log in.")
                else:
                    row=con.execute("SELECT name,email FROM users WHERE email=? AND password=?",(email,hash_pw(password))).fetchone()
                    if row:
                        st.session_state.user={"name":row[0],"email":row[1]}; st.rerun()
                    else: st.error("Incorrect email or password.")
                con.close()

page=st.session_state.page
if not st.session_state.user:
    st.markdown("# ✈️ Wanderly Planner")
    st.markdown("### Your travel ideas, itinerary and budget in one place.")
    st.markdown("Create an account or log in using the panel on the left to access the full planner.")
    c1,c2,c3=st.columns(3)
    for col,icon,title,desc in [(c1,"🧭","Smart trip planning","Build a simple day-by-day itinerary."),(c2,"💰","Budget optimizer","Estimate expenses and split your budget."),(c3,"🏨","Hotel discovery","Browse sample stays by destination.")]:
        with col: st.markdown(f'<div class="card"><h2>{icon} {title}</h2><p>{desc}</p></div>',unsafe_allow_html=True)
    st.stop()

if page=="Home":
    st.markdown("# Travel smarter. <span style='color:#f6b352'>Wander better.</span>",unsafe_allow_html=True)
    st.write(f"Welcome back, **{st.session_state.user['name']}** — where will your next journey take you?")
    a,b,c=st.columns(3)
    a.metric("Destinations",len(DESTINATIONS)); b.metric("Sample stays",len(HOTELS)); c.metric("Planner","Ready")
    st.markdown("## Explore a few ideas")
    cols=st.columns(3)
    for i,d in enumerate(DESTINATIONS[:3]):
        with cols[i]:
            st.markdown(f'<div class="card"><div style="font-size:38px">{d["emoji"]}</div><h3>{d["name"]}</h3><p class="small">{d["region"]}</p><p>{d["desc"]}</p><b>From {money(d["cost"])} / person / day</b></div>',unsafe_allow_html=True)
            if st.button("Plan "+d["name"],key="home_"+d["name"]):
                st.session_state.prefill=d["name"]; st.session_state.page="Trip Planner"; st.rerun()
    st.info("Use the navigation menu to plan a trip, explore places, optimize a budget, find hotels, or view saved trips.")

elif page=="Trip Planner":
    st.markdown("# 🧭 Smart Trip Planner")
    st.write("Enter a few details to generate a sample itinerary and estimated budget.")
    with st.form("trip_form"):
        dest_names=[d["name"] for d in DESTINATIONS]
        default=dest_names.index(st.session_state.get("prefill","Goa")) if st.session_state.get("prefill","Goa") in dest_names else 0
        dest=st.selectbox("Destination",dest_names,index=default)
        start=st.date_input("Start date",value=date.today()+timedelta(days=7),min_value=date.today())
        days=st.slider("Number of days",1,14,3)
        travelers=st.number_input("Number of travellers",1,20,2)
        budget=st.number_input("Total budget (₹)",min_value=1000,value=20000,step=1000)
        pref=st.selectbox("Travel preference",["Adventure","Relaxation","Family","Nature","Culture","Food"])
        interests=st.multiselect("Interests",["Sightseeing","Local food","Shopping","Nature","Museums","Photography","Adventure"],default=["Sightseeing","Local food"])
        go=st.form_submit_button("✨ Generate my trip plan",use_container_width=True)
    if go:
        d=next(x for x in DESTINATIONS if x["name"]==dest)
        estimate=d["cost"]*days*travelers
        st.session_state.generated={"dest":dest,"start":str(start),"days":days,"travelers":travelers,"budget":budget,"pref":pref,"estimate":estimate,"places":d["places"]}
        con=db(); con.execute("INSERT INTO saved_trips VALUES (?,?,?,?,?,?)",(st.session_state.user["email"],dest,days,budget,pref,str(date.today()))); con.commit(); con.close()
    trip=st.session_state.get("generated")
    if trip:
        st.markdown("---"); st.markdown(f"## Your {trip['days']}-day plan for {trip['dest']}")
        x,y,z=st.columns(3); x.metric("Travellers",trip["travelers"]); y.metric("Your budget",money(trip["budget"])); z.metric("Estimated cost",money(trip["estimate"]))
        if trip["budget"]<trip["estimate"]: st.warning("Your budget may be tight. Try fewer days, fewer travellers, or increase the budget.")
        else: st.success("Your budget looks reasonable for this sample estimate.")
        places=trip["places"]
        for day in range(trip["days"]):
            p1=places[day%len(places)]
            p2=places[(day+1)%len(places)]
            st.markdown(f"**Day {day+1} — {date.fromisoformat(trip['start'])+timedelta(days=day)}**")
            st.write(f"• Morning: Visit {p1}.")
            st.write(f"• Afternoon: Explore {p2} and nearby attractions.")
            st.write("• Evening: Try local food and enjoy free time.")
        st.caption("This is a sample itinerary, not a live booking or real-time price quote.")

elif page=="Explore":
    st.markdown("# 🌍 Explore destinations")
    q=st.text_input("Search destination or travel style")
    matches=[d for d in DESTINATIONS if q.lower() in (d["name"]+" "+d["region"]+" "+d["desc"]+" "+" ".join(d["tags"])).lower()]
    cols=st.columns(3)
    for i,d in enumerate(matches):
        with cols[i%3]:
            st.markdown(f'<div class="card"><div style="font-size:38px">{d["emoji"]}</div><h3>{d["name"]}</h3><p class="small">{d["region"]}</p><p>{d["desc"]}</p><p><b>Highlights:</b> {", ".join(d["places"])}</p><p><b>From {money(d["cost"])} per person/day</b></p></div>',unsafe_allow_html=True)
            if st.button("Use destination",key="explore_"+d["name"]):
                st.session_state.prefill=d["name"]; st.session_state.page="Trip Planner"; st.rerun()
    if not matches: st.info("No matching destination. Try Goa, Jaipur, nature, adventure or family.")

elif page=="Budget Optimizer":
    st.markdown("# 💰 Smart Budget Optimizer")
    st.write("Adjust your budget to see a suggested expense split.")
    budget=st.number_input("Total trip budget (₹)",min_value=1000,value=20000,step=500)
    days=st.slider("Trip length (days)",1,30,4)
    travelers=st.number_input("Travellers",1,20,2,key="budget_travellers")
    mode=st.selectbox("Travel style",["Budget","Balanced","Comfort"])
    ratios={"Budget":[.35,.25,.20,.10,.10],"Balanced":[.40,.25,.20,.10,.05],"Comfort":[.45,.25,.18,.07,.05]}[mode]
    names=["Stay","Transport","Food","Activities","Emergency reserve"]
    vals=[round(budget*r) for r in ratios]; vals[-1]+=budget-sum(vals)
    st.metric("Budget per person per day",money(budget/(days*travelers)))
    st.progress(1.0)
    for n,v in zip(names,vals):
        st.write(f"**{n}: {money(v)}**")
        st.progress(v/budget)
    d=next((d for d in DESTINATIONS if d["cost"]*days*travelers<=budget),None)
    if d: st.success(f"Based on the sample estimate, {d['name']} could fit this budget.")
    else: st.info("Consider a shorter trip or a lower-cost destination to stretch your budget.")
    st.caption("Estimates are illustrative and do not use live travel prices.")

elif page=="Hotel Finder":
    st.markdown("# 🏨 Hotel Finder")
    city=st.selectbox("Choose a destination",["All"]+sorted(set(h["city"] for h in HOTELS)))
    max_price=st.slider("Maximum nightly price (₹)",1000,5000,3500,100)
    filtered=[h for h in HOTELS if (city=="All" or h["city"]==city) and h["price"]<=max_price]
    if not filtered: st.info("No sample hotels match those filters.")
    cols=st.columns(2)
    for i,h in enumerate(filtered):
        with cols[i%2]:
            st.markdown(f'<div class="card"><h3>🏨 {h["name"]}</h3><p>📍 {h["city"]} &nbsp; ⭐ {h["rating"]}</p><h2 style="color:#f6b352">{money(h["price"])} <small>/ night</small></h2><p>{h["amenities"]}</p></div>',unsafe_allow_html=True)
            st.caption("Sample listing for project demonstration. Availability is not checked.")

elif page=="My Trips":
    st.markdown("# 🧳 My Saved Trips")
    con=db()
    rows=con.execute("SELECT destination,days,budget,preference,created FROM saved_trips WHERE email=? ORDER BY rowid DESC",(st.session_state.user["email"],)).fetchall()
    con.close()
    if not rows: st.info("You haven't saved a trip yet. Open Trip Planner to create one.")
    else:
        for dest,days,budget,pref,created in rows:
            st.markdown(f'<div class="card"><h3>🗺️ {dest}</h3><p>{days} days · {pref} · Budget {money(budget)}</p><p class="small">Created on {created}</p></div>',unsafe_allow_html=True)

st.markdown("---")
st.caption("Wanderly Planner · Hackathon prototype · Sample destination, hotel and cost data only.")
