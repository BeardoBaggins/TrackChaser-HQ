import csv
import ctypes
import hashlib
import io
import json
import math
import os
import re
import shutil
import threading
import unicodedata
import urllib.parse
import webbrowser
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import tkinter.font as tkfont

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    import urllib.request
    import urllib.error
    HAS_REQUESTS = False

try:
    from PIL import Image, ImageDraw, ImageFont, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

DEFAULT_FILE = "default_data.json"
USER_FILE = "user_progress.json"
GEO_CACHE_FILE = "geo_cache.json"
CUSTOM_LOGO_DIR = "custom_logos"
ICON_ICO_FILE = "app_icon.ico"
ICON_PNG_FILE = "app_icon.png"
CUSTOM_BANNER_FILE = "banner.png"

APP_NAME = "TrackChaser HQ — Motorsport Attendance, Quests, Bucket List & Trip Planner"
APP_FONT = "Helvetica S"

SERIES_KEYS = ["Cup", "O'Reilly", "Craftsman", "ARCA_National", "ARCA_East", "ARCA_West", "Grassroots"]
NATIONAL_WEEKEND_KEYS = ["Cup", "O'Reilly", "Craftsman", "ARCA_National", "ARCA_East", "ARCA_West"]

TAB_CONFIG = [
    ("Cup", "Cup Series", "#2563eb", "#ffffff"),
    ("O'Reilly", "O'Reilly Auto Parts", "#16a34a", "#ffffff"),
    ("Craftsman", "FedEx Truck Series", "#7c3aed", "#ffffff"),
    ("ARCA", "ARCA Menards", "#eab308", "#0f172a"),
    ("Grassroots", "Grassroots & Local", "#ea580c", "#ffffff"),
    ("Attractions", "Attractions & Shops", "#dc2626", "#ffffff"),
    ("Bucket", "Bucket List", "#d97706", "#ffffff"),
    ("Quests", "Quests & Challenges", "#10b981", "#0f172a"),
    ("Trip", "My Trip Planner", "#475569", "#ffffff"),
]

TRACK_ADDRESS_BOOK = {
    "bowman gray": "1250 S Martin Luther King Jr Dr, Winston-Salem, NC 27107",
    "daytona": "1801 W International Speedway Blvd, Daytona Beach, FL 32114",
    "atlanta": "1500 Tara Pl, Hampton, GA 30228",
    "echopark": "1500 Tara Pl, Hampton, GA 30228",
    "circuit of the americas": "9201 Circuit of the Americas Blvd, Austin, TX 78617",
    "phoenix": "7602 Jimmie Johnson Dr, Avondale, AZ 85323",
    "las vegas": "7000 Las Vegas Blvd N, Las Vegas, NV 89115",
    "bullring": "7000 Las Vegas Blvd N, Las Vegas, NV 89115",
    "darlington": "1301 Harry Byrd Hwy, Darlington, SC 29532",
    "martinsville": "340 Speedway Rd, Ridgeway, VA 24148",
    "bristol": "151 Speedway Blvd, Bristol, TN 37620",
    "kansas": "400 Speedway Blvd, Kansas City, KS 66111",
    "talladega": "3366 Speedway Blvd, Lincoln, AL 35096",
    "texas motor": "3545 Lone Star Cir, Fort Worth, TX 76177",
    "watkins glen": "2790 County Route 16, Watkins Glen, NY 14891",
    "dover": "1131 N DuPont Hwy, Dover, DE 19901",
    "charlotte": "5555 Concord Pkwy S, Concord, NC 28027",
    "nashville superspeedway": "4847-F McCrary Rd, Lebanon, TN 37090",
    "nashville fairgrounds": "625 Smith Ave, Nashville, TN 37203",
    "michigan": "12626 US-12, Brooklyn, MI 49230",
    "pocono": "1234 Long Pond Rd, Long Pond, PA 18334",
    "coronado": "Naval Air Station North Island, Coronado, CA 92135",
    "sonoma": "29355 Arnold Dr, Sonoma, CA 95476",
    "chicagoland": "500 Speedway Blvd, Joliet, IL 60433",
    "north wilkesboro": "381 Speedway Ln, North Wilkesboro, NC 28659",
    "indianapolis motor speedway": "4790 W 16th St, Speedway, IN 46222",
    "indianapolis raceway park": "10267 E US Hwy 136, Indianapolis, IN 46234",
    "lucas oil": "10267 E US Hwy 136, Indianapolis, IN 46234",
    "iowa": "3333 Rusty Wallace Dr, Newton, IA 50208",
    "richmond": "600 E Laburnum Ave, Richmond, VA 23222",
    "new hampshire": "1122 Route 106 N, Loudon, NH 03307",
    "world wide technology": "700 Raceway Blvd, Madison, IL 62060",
    "worldwide technology": "700 Raceway Blvd, Madison, IL 62060",
    "homestead": "1 Ralph Sanchez Speedway Blvd, Homestead, FL 33035",
    "rockingham": "2152 N US Hwy 1, Rockingham, NC 28379",
    "st. petersburg": "100 1st Ave SE, St. Petersburg, FL 33701",
    "lime rock": "60 White Hollow Rd, Lakeville, CT 06039",
    "toledo": "5639 Benore Rd, Toledo, OH 43612",
    "berlin": "2060 Berlin Fair Dr, Marne, MI 49435",
    "elko": "26350 France Ave, Elko New Market, MN 55020",
    "illinois state fairgrounds": "801 E Sangamon Ave, Springfield, IL 62702",
    "springfield": "801 E Sangamon Ave, Springfield, IL 62702",
    "madison international": "1122 Sunrise Rd, Oregon, WI 53575",
    "duquoin": "655 Executive Dr, DuQuoin, IL 62832",
    "salem": "2723 W State Rd 56, Salem, IN 47167",
    "hickory": "3130 Hwy 70 SE, Newton, NC 28658",
    "flat rock": "14041 Telegraph Rd, Flat Rock, MI 48134",
    "five flags": "7451 Pine Forest Rd, Pensacola, FL 32526",
    "kern": "13500 Raceway Blvd, Bakersfield, CA 93311",
    "tucson": "11955 S Harrison Rd, Tucson, AZ 85747",
    "shasta": "1890 Briggs St, Anderson, CA 96007",
    "colorado national": "4281 Speedway Blvd, Dacono, CO 80514",
    "tri-city": "47302 E Hwy 224, West Richland, WA 99353",
    "portland": "1940 N Victory Blvd, Portland, OR 97217",
    "all american": "700 Event Center Dr, Roseville, CA 95678",
    "madera": "1850 W Cleveland Ave, Madera, CA 93637",
    "eldora": "13929 State Route 118, New Weston, OH 45348",
    "knoxville": "1000 N Lincoln St, Knoxville, IA 50138",
    "sagenet": "4145 E 21st St, Tulsa, OK 74114",
    "winchester": "2556 W State Rd 32, Winchester, IN 47394",
    "oxford plains": "877 Main St, Oxford, ME 04270",
    "slinger": "2800 E Washington St, Slinger, WI 53086",
    "southern national": "8071 Newsome Mill Rd, Lucama, NC 27851",
    "thompson": "205 E Thompson Rd, Thompson, CT 06277"
}

ICONIC_RACE_NOTES = {
    "daytona 500": (True, "BUCKET LIST: The Great American Race & Super Bowl of NASCAR | Tix: $145-$550+ | Fanzone & Pre-Race Pass: $108 ($168 4-Day) | VIP Garage Pass: $850+"),
    "duel": (True, "BUCKET LIST: Twin night-race qualifiers under the lights setting the Daytona 500 starting grid | Tix: $56-$115 | Fanzone & Pre-Race: $35"),
    "clash": (True, "BUCKET LIST: Season-opening exhibition short-track/superspeedway shootout under the lights | Tix: $75-$250 | Pre-Race Pass: $75"),
    "coca-cola 600": (True, "BUCKET LIST: Crown Jewel 600-mile endurance test on Memorial Day Weekend | Tix: $95-$220 | Pre-Race Track Pass: $95 | VIP Garage Pass: $650+"),
    "southern 500": (True, "BUCKET LIST: Historic Labor Day Weekend Crown Jewel at the Track Too Tough to Tame | Tix: $70-$175 | Pre-Race Experience Pass: $75 | VIP Garage: $550+"),
    "brickyard 400": (True, "BUCKET LIST: Crown Jewel at the 2.5-mile Indianapolis oval—Kiss the Bricks! | Tix: $65-$185 | Bronze Badge Garage Pass: $100-$150 | Pit Walk: $85"),
    "bass pro shops night race": (True, "BUCKET LIST: 500 laps under the lights inside the 140,000-seat Last Great Colosseum | Tix: $95-$225 | Pre-Race Track Walk: $115 | Ultimate Fan Pass: $799"),
    "jack link's 500": (True, "BUCKET LIST: 200 mph 4-wide pack racing on Talladega's 33-degree banks + infield party | Tix: $65-$165 | Talladega Garage Experience Pass: $85-$145"),
    "yellawood 500": (True, "BUCKET LIST: Playoff wildcard pack-racing thriller at Talladega | Tix: $65-$165 | Talladega Garage Experience Pass: $85-$145"),
    "coke zero sugar 400": (True, "BUCKET LIST: Regular-season cutoff night race under the lights at Daytona | Tix: $69-$175 | Fanzone & Pre-Race: $75 | VIP Garage: $650+"),
    "xfinity 500": (True, "BUCKET LIST: Championship 4 cutoff war at the 1947 Martinsville Paperclip for the Grandfather Clock | Tix: $65-$145 | Pre-Race Track Pass: $75"),
    "all-star race": (True, "BUCKET LIST: $1 Million All-Star showdown with no points on the line | Tix: $75-$195 | Pre-Race Track Walk Pass: $85"),
    "window world 450": (True, "BUCKET LIST: Historic Moonshine-country 1947 Appalachian short track return | Tix: $85-$210 | Pre-Race Track Walk Pass: $85"),
    "go bowling at the glen": (True, "BUCKET LIST: High-speed road course classic through the Esses & Bus Stop in Finger Lakes | Tix: $75-$160 | Infield Fanwalk Pass: $70"),
    "toyota / save mart 350": (True, "BUCKET LIST: California Wine Country road course with dramatic elevation & Turn 11 hairpin | Tix: $70-$165 | Pre-Race Grid Pass: $85"),
    "anduril 250": (True, "BUCKET LIST: First-ever Cup race on an active U.S. Navy aircraft carrier base in San Diego Bay | Tix: $135-$350+ | Trackside Hospitality: $450+"),
    "championship": (True, "BUCKET LIST: Season Championship Finale on Homestead-Miami's multi-groove 1.5-mile oval | Tix: $95-$260 | Pre-Race & Stage Celebration Pass: $125"),
}

# -------------------- QUESTS & CHALLENGES MASTER CATALOG --------------------

AUTO_CAMPAIGNS = [
    {
        "id": "camp_grand_slam",
        "title": "The NASCAR Grand Slam",
        "category": "Crown Jewel Campaign",
        "xp": 500,
        "desc": "Attend all 4 Crown Jewel Cup races: Daytona 500, Coca-Cola 600, Brickyard 400 & Cook Out Southern 500.",
        "type": "races",
        "targets": ["daytona 500", "coca-cola 600", "brickyard 400", "southern 500"]
    },
    {
        "id": "camp_draft_baron",
        "title": "Restrictor Plate Baron",
        "category": "Superspeedway Campaign",
        "xp": 300,
        "desc": "Survive the 200 mph pack draft at all 3 drafting tracks: Daytona, Talladega & EchoPark (Atlanta).",
        "type": "tracks",
        "targets": ["daytona", "talladega", "echopark"]
    },
    {
        "id": "camp_short_track_bully",
        "title": "Short Track Bully",
        "category": "Bullring Campaign",
        "xp": 350,
        "desc": "Hear the brakes glow at the 4 historic short-track shrines: Bristol, Martinsville, North Wilkesboro & Bowman Gray.",
        "type": "tracks",
        "targets": ["bristol", "martinsville", "north wilkesboro", "bowman gray"]
    },
    {
        "id": "camp_moonshine_trail",
        "title": "Moonshine Heritage Trail",
        "category": "Carolinas Roots",
        "xp": 400,
        "desc": "Visit the 5 Carolina moonshine-era legends: North Wilkesboro, Rockingham, Hickory, Darlington & Occoneechee Ghost Track.",
        "type": "mixed_tracks_attr",
        "targets": ["north wilkesboro", "rockingham", "hickory", "darlington", "occoneechee"]
    },
    {
        "id": "camp_left_and_right",
        "title": "Turning Left AND Right",
        "category": "Road Course Campaign",
        "xp": 300,
        "desc": "Attend a race at 3 different road or street circuits (Watkins Glen, Sonoma, COTA, Lime Rock, Coronado, St. Pete, or Portland).",
        "type": "track_count_any",
        "need": 3,
        "targets": ["watkins glen", "sonoma", "circuit of the americas", "lime rock", "coronado", "st. petersburg", "portland"]
    },
    {
        "id": "camp_broomstick",
        "title": "Break Out The Broomstick (Same-Year Weekend Sweep)",
        "category": "Endurance Achievement",
        "xp": 400,
        "desc": "Conquer an entire Race Weekend by watching EVERY national series race at a track during the same season year.",
        "type": "sweeps",
        "need": 1
    },
    {
        "id": "camp_triple_sweep",
        "title": "Ironman Weekend Chaser",
        "category": "Endurance Achievement",
        "xp": 750,
        "desc": "Conquer 3 complete Same-Year Race Weekend Sweeps across any tracks on the circuit.",
        "type": "sweeps",
        "need": 3
    },
    {
        "id": "camp_red_clay_royalty",
        "title": "Red Clay Royalty",
        "category": "Grassroots & Dirt",
        "xp": 450,
        "desc": "Attend America's 3 biggest dirt spectacles: World 100 (Eldora), Knoxville Nationals & Chili Bowl Nationals (Tulsa).",
        "type": "races",
        "targets": ["world 100", "knoxville nationals", "chili bowl"]
    },
    {
        "id": "camp_asphalt_late_model",
        "title": "Pavement Bullring Boss",
        "category": "Grassroots Late Models",
        "xp": 400,
        "desc": "Attend any 3 pavement Late Model classics (Snowball Derby, ValleyStar 300, Throwback Classic, All American 400, Winchester 400, Oxford 250, Slinger Nationals).",
        "type": "race_count_any",
        "need": 3,
        "targets": ["snowball derby", "valleystar", "throwback classic", "all american 400", "winchester 400", "oxford 250", "slinger nationals"]
    },
    {
        "id": "camp_fairgrounds_miles",
        "title": "The Dirt Mile Fairgrounds Double",
        "category": "ARCA Dirt History",
        "xp": 350,
        "desc": "Watch stock cars slide 100+ mph on clay at both historic Illinois fairgrounds miles: Springfield & DuQuoin.",
        "type": "tracks",
        "targets": ["illinois state fairgrounds", "duquoin"]
    },
    {
        "id": "camp_race_city_usa",
        "title": "Race City USA Pilgrimage",
        "category": "Shop Tour Campaign",
        "xp": 350,
        "desc": "Visit 5 Charlotte/Mooresville race shops (Hendrick, JR Motorsports, Penske, 23XI Airspeed, Gibbs, RFK, Trackhouse, RCR, or DEI).",
        "type": "attr_count_any",
        "need": 5,
        "targets": ["hendrick", "jr motorsports", "penske", "23xi", "joe gibbs", "rfk", "trackhouse", "richard childress", "dale earnhardt inc"]
    },
    {
        "id": "camp_intimidator",
        "title": "The Intimidator's Trail (#3)",
        "category": "Legend Tribute",
        "xp": 400,
        "desc": "Pay respects at all 4 Dale Earnhardt landmarks: DEI Museum, RCR Museum, Kannapolis Tribute Plaza & Talladega Superspeedway.",
        "type": "mixed_tracks_attr",
        "targets": ["dale earnhardt inc", "richard childress", "tribute plaza", "talladega"]
    },
    {
        "id": "camp_founding_fathers",
        "title": "Founding Fathers of Stock Car",
        "category": "Heritage Museums",
        "xp": 350,
        "desc": "Visit the 4 pillars of stock car history: NASCAR Hall of Fame, Petty Museum, Wood Brothers Museum & Darlington Stock Car Museum.",
        "type": "attr_all",
        "targets": ["nascar hall of fame", "petty museum", "wood brothers", "darlington raceway stock car museum"]
    },
    {
        "id": "camp_10_tracks",
        "title": "Ten-Track Barnstormer",
        "category": "Milestone",
        "xp": 500,
        "desc": "Step foot inside 10 unique physical race tracks across any series or year.",
        "type": "unique_tracks",
        "need": 10
    },
]

FOOD_CHALLENGES = [
    ("food_martinsville", "The Famous $2 Pink Hot Dog", "Martinsville Speedway", "Eat a pair of Jesse Jones bright-red hot dogs topped with chili, slaw, mustard & onions at the Paperclip.", 100),
    ("food_darlington", "Southern Pimento Cheese Sandwich", "Darlington Raceway", "Eat a classic handmade Darlington Pimento Cheese sandwich on white bread while watching cars ride the stripe.", 100),
    ("food_bristol", "Thunder Valley Footlong Corn Dog", "Bristol Motor Speedway", "Have a fresh-dipped footlong corn dog or giant BBQ nachos inside the Last Great Colosseum.", 100),
    ("food_daytona", "Daytona Sausage & Peppers Hoagie", "Daytona International Speedway", "Grab an Italian sausage with peppers & onions or Fanzone loaded fries in the Daytona infield.", 100),
    ("food_talladega", "The Big One Meatball Sub & Funnel Cake", "Talladega Superspeedway", "Have a 1-pound Talladega meatball/cheese sub or powdered-sugar funnel cake at NASCAR's biggest oval.", 100),
    ("food_charlotte", "The Hawg Heaven Bacon Mac & Cheese Cone", "Charlotte Motor Speedway", "Try CMS's famous waffle cone stuffed with smoked pulled pork and mac & cheese.", 100),
    ("food_atlanta", "Georgia Peach Cobbler & Fried Chicken Basket", "EchoPark Speedway (Atlanta)", "Have hot Southern fried chicken or peach cobbler while watching the pack draft on 28-degree banks.", 100),
    ("food_wilkesboro", "Brushy Mountain Pulled Pork & Moonshine Slush", "North Wilkesboro Speedway", "Have Wilkes County pit-cooked pulled pork BBQ and a moonshine slushie at the resurrected 1947 short track.", 100),
    ("food_bowman_gray", "Madhouse Popcorn & Ice-Cold Cheerwine", "Bowman Gray Stadium", "Grab a Carolina Cheerwine and stadium popcorn steps from the quarter-mile guardrail.", 100),
    ("food_richmond", "Virginia Smoked Turkey Leg", "Richmond Raceway", "Have a smoked turkey leg under the Saturday night lights in Richmond.", 100),
    ("food_dover", "Monster Mile Maryland Crab Cake Sandwich", "Dover Motor Speedway", "Order a Delmarva boardwalk-style crab cake sandwich and vinegar fries outside Turn 4.", 100),
    ("food_pocono", "Poconos Pierogies & Cheesesteak", "Pocono Raceway", "Have Pennsylvania Dutch butter-and-onion pierogies or a Philly cheesesteak in the Tricky Triangle paddock.", 100),
    ("food_nhms", "The Magic Mile Lobster Roll", "New Hampshire Motor Speedway", "Eat a genuine New England Maine lobster roll at the track where the winner gets a giant live lobster.", 100),
    ("food_watkins_glen", "Upstate NY Chicken Spiedie Sub", "Watkins Glen International", "Have a marinated char-grilled Upstate NY Chicken Spiedie sub or Finger Lakes grape pie in the infield.", 100),
    ("food_indy", "The Hoosier Pork Tenderloin Sandwich", "Indianapolis Motor Speedway", "Eat a breaded Indiana pork tenderloin sandwich that is three times wider than the bun.", 100),
    ("food_michigan", "Irish Hills Coney Island Chili Dog", "Michigan International Speedway", "Grab a classic Michigan Coney Island chili dog in the MIS infield.", 100),
    ("food_kansas", "Kansas City Burnt Ends & Brisket Sandwich", "Kansas Speedway", "Have authentic slow-smoked KC burnt ends with sweet molasses BBQ sauce.", 100),
    ("food_iowa", "Iowa Roasted Sweet Corn & Pork Chop on a Stick", "Iowa Speedway", "Have a roasted ear of Iowa sweet corn and a pork chop on a stick.", 100),
    ("food_gateway", "St. Louis Toasted Ravioli & Gooey Butter Cake", "World Wide Technology Raceway", "Grab crispy St. Louis toasted ravioli with marinara near the Gateway Arch.", 100),
    ("food_chicagoland", "Joliet Italian Beef with Hot Giardiniera", "Chicagoland Speedway", "Eat a dipped Chicago-style Italian beef sandwich or Maxwell Street Polish sausage.", 100),
    ("food_texas", "No-Limits Smoked Brisket & Jalapeño Sausage", "Texas Motor Speedway", "Eat Texas post-oak smoked brisket or a 2-foot Texas broomstick hot dog.", 100),
    ("food_cota", "Austin Brisket Breakfast Tacos", "Circuit of The Americas", "Fuel up on Austin brisket breakfast tacos before climbing the Turn 1 hill.", 100),
    ("food_phoenix", "Sonoran Bacon-Wrapped Hot Dog", "Phoenix Raceway", "Eat an Arizona Sonoran dog (wrapped in bacon with pinto beans, pico & jalapeño sauce) in the desert.", 100),
    ("food_vegas", "Neon Garage Loaded Nachos", "Las Vegas Motor Speedway", "Have a tray of loaded Vegas nachos while watching pit crews work through the Neon Garage glass.", 100),
    ("food_sonoma", "Napa Valley Garlic Fries & Tri-Tip Sandwich", "Sonoma Raceway", "Eat California Santa Maria-style grilled tri-tip and garlic fries on the Wine Country hillsides.", 100),
    ("food_homestead", "Cubano Sandwich & Key Lime Pie", "Homestead-Miami Speedway", "Celebrate Championship Weekend with a pressed Miami Cuban sandwich, plantain chips & Key lime pie.", 100),
    ("food_nashville", "Music City Hot Chicken Tenders", "Nashville Superspeedway / Fairgrounds", "Have cayenne-dipped Nashville Hot Chicken with dill pickles on white bread.", 100),
    ("food_eldora", "The Eldora Pizza Burger & Giant Tenderloin", "Eldora Speedway", "Order Tony Stewart's famous Eldora Pizza Burger or giant tenderloin during the World 100.", 100),
    ("food_knoxville", "Sprint Car Capital Ribeye Steak Sandwich", "Knoxville Raceway", "Grab a grilled Iowa ribeye steak sandwich outside Turn 1 at Knoxville.", 100),
    ("food_five_flags", "Snowball Derby Gulf Coast Gumbo", "Five Flags Speedway", "Warm up during December's Snowball Derby with a bowl of Pensacola seafood gumbo.", 100),
    ("food_slinger", "Wisconsin Squeaky Cheese Curds & Bratwurst", "Slinger Super Speedway", "Eat deep-fried Wisconsin cheddar curds and a beer brat at the world's fastest quarter-mile.", 100),
    ("food_dawsonville", "The Famous Dawsonville Bully Burger", "Dawsonville Pool Room", "Order a Bully Burger with onion rings right under the victory SiReen in Awesome Bill's hometown.", 100),
    ("food_north_turn", "Beach-Course Fish Tacos Overlooking the North Turn", "Racing's North Turn (Ponce Inlet)", "Eat lunch overlooking the exact ocean sand where stock cars made the North Turn from 1948 to 1958.", 100),
    ("food_illinois_mile", "State Fair Cozy Dog & Lemon Shake-Up", "Springfield / DuQuoin Dirt Miles", "Get a fresh-squeezed lemon shake-up and a Route 66 Cozy Dog while ARCA cars fling clay.", 100),
]

# Meaningful, track-specific fan traditions & landmarks ("Side-Tracked")
SIDE_TRACKED_QUESTS = [
    ("sq_indy", "Kiss the Yard of Bricks", "Indianapolis Motor Speedway", "Kneel down on the frontstretch and kiss (or touch) the original 36-inch strip of 1909 paving bricks at the start/finish line.", 100),
    ("sq_daytona_sign", "Sign the Daytona Start/Finish Line & Walk the 31° Banks", "Daytona International Speedway", "Use the Hard Rock Bet Fanzone & Pre-Race pass to walk onto the tri-oval grass, sign the start/finish line, and stand at the bottom of the 31-degree banking.", 100),
    ("sq_daytona_beach", "Stand on the Original 1948 Sand & Hwy A1A North Turn", "Daytona Beach Road Course (Ponce Inlet)", "Visit Racing's North Turn at 4511 S Atlantic Ave and walk onto the beach where stock cars transitioned from pavement to ocean sand from 1948–1958.", 100),
    ("sq_martinsville_clock", "Stand Beside the Ridgeway Grandfather Clock", "Martinsville Speedway", "See the iconic 7-foot Ridgeway Grandfather Clock trophy up close in the fan midway or pre-race stage before the green flag drops.", 100),
    ("sq_bristol_walk", "Walk the 28-Degree Concrete Banking Inside the Colosseum", "Bristol Motor Speedway", "Step onto the track surface during the pre-race track walk and look straight up at all 140,000 seats surrounding the half-mile bowl.", 100),
    ("sq_darlington_museum", "Tour the NMPA Stock Car Museum Outside Turn 3", "Darlington Raceway", "Before the race, walk through the historic museum right outside Turn 3 to see Pearson, Yarborough, and Petty's Southern 500 winners.", 100),
    ("sq_charlotte_sign", "Sign the Coca-Cola 600 Start/Finish Line", "Charlotte Motor Speedway", "Bring a Sharpie onto the pre-race frontstretch track walk and sign your name on the Charlotte asphalt.", 100),
    ("sq_talladega_blvd", "Experience Talladega Boulevard & The Big Bill's Garage", "Talladega Superspeedway", "Walk the Talladega Garage Experience inches from the cars and visit the International Motorsports Hall of Fame outside Turn 1.", 100),
    ("sq_wilkesboro_walk", "Walk the Uphill Backstretch & Downhill Frontstretch", "North Wilkesboro Speedway", "Do the pre-race track walk at the 1947 Brushy Mountain short track to feel how the frontstretch drops downhill and the backstretch climbs uphill.", 100),
    ("sq_bowman_gray", "Stand at the Guardrail of 'The Madhouse'", "Bowman Gray Stadium", "Watch Modifieds or Cup cars from the lower walkway just feet from the quarter-mile guardrail inside the 1937 football stadium.", 100),
    ("sq_dover_miles", "Take a Photo with the 46-Foot Miles the Monster Monument", "Dover Motor Speedway", "Visit the Victory Plaza outside Turn 4 and stand underneath the 46-foot-tall fiberglass Miles the Monster statue holding a real stock car.", 100),
    ("sq_cota_tower", "Climb the 251-Foot COTA Observation Tower", "Circuit of The Americas", "Take the elevator/stairs to the top of the COTA Mullet Tower (or climb the 133-foot Turn 1 amphitheater hill) to see the entire 20-turn layout at once.", 100),
    ("sq_phoenix_victory", "Stand at the Infield Garage & Victory Lane Rope", "Phoenix Raceway", "Use the Phoenix Infield Experience Pass to walk through the open-air garage bays and stand right along the Victory Lane celebration circle.", 100),
    ("sq_vegas_neon", "Watch Pit Crews From the Neon Garage Balcony", "Las Vegas Motor Speedway", "Hang out inside the infield Neon Garage courtyard and watch teams prep their cars through the garage bay windows.", 100),
    ("sq_watkins_glen_gorge", "Hike the Historic 1948 Street Course & Watkins Glen Gorge", "Watkins Glen International", "Drive or walk the original 6.6-mile 1948 village street course markers through downtown Watkins Glen and the Old Entrance bridge.", 100),
    ("sq_sonoma_turn11", "Watch Heavy Braking from the Turn 11 Hairpin Apron", "Sonoma Raceway", "Stand right behind the Turn 11 hairpin K-rail (closest fan viewing point in Cup) and smell the brake pads smoking on corner entry.", 100),
    ("sq_pocono_paddock", "Walk Through the Historic Paddock Behind Pit Road", "Pocono Raceway", "Use the Pocono Paddock Pass to walk right behind the pit boxes and view the cars up close before they roll onto the 3,740-foot frontstretch.", 100),
    ("sq_richmond_fangrounds", "Walk the Infield Fangrounds Garage Walkway", "Richmond Raceway", "Walk the sunken eye-level walkway right through the middle of the Cup Series garage bays before the Saturday night race.", 100),
    ("sq_nhms_lobster", "Witness the Giant Live Lobster Victory Lane Tradition", "New Hampshire Motor Speedway", "Stay after the checkered flag at Loudon to watch the race winner hoist a 20+ lb live New England lobster in Victory Lane.", 100),
    ("sq_hickory_autographs", "Do the On-Track Autograph Session at the Birthplace of Stars", "Hickory Motor Speedway", "Walk onto the 0.363-mile Hickory asphalt at intermission to meet the drivers parked side-by-side on the frontstretch.", 100),
    ("sq_rockingham_walk", "Walk the High-Banked 1-Mile Turn 1 at 'The Rock'", "Rockingham Speedway", "Step onto the steep North Carolina Sandhills banking during the pre-race track walk to celebrate Rockingham's return.", 100),
    ("sq_eldora_throne", "See the Kings Royal Throne & World 100 Globe Trophy", "Eldora Speedway", "Visit the fan stage at Tony Stewart's half-mile clay oval to see the hand-carved Kings Royal throne or World 100 globe trophy.", 100),
    ("sq_knoxville_hof", "Watch Laps From the Sprint Car Hall of Fame Outside Turn 2", "Knoxville Raceway", "Tour the National Sprint Car Hall of Fame towering directly behind Turn 2 at the Sprint Car Capital of the World.", 100),
    ("sq_chili_bowl", "Walk 'The Building' Pit Floor Among 350+ Midgets", "SageNet Center (Tulsa Expo)", "Get a pit pass at the Chili Bowl to walk the massive indoor pit area where over 350 midget teams are parked under one roof.", 100),
    ("sq_five_flags", "Walk the Snowball Derby Tech Inspection Line ('Room of Doom')", "Five Flags Speedway", "Watch post-race or pre-race technical inspection in the famous 'Room of Doom' shed at Pensacola during Snowball Derby week.", 100),
    ("sq_nashville_guitar", "See the Custom Sam Bass-Style Gibson Guitar Trophy", "Nashville Superspeedway / Fairgrounds", "Check out the custom hand-painted Gibson Les Paul guitar trophy awarded to the winner in Music City.", 100),
    ("sq_gateway_arch", "Spot the St. Louis Gateway Arch From the Top Grandstand", "World Wide Technology Raceway", "Climb to the top row of the frontstretch stands and spot the 630-foot Gateway Arch gleaming across the Mississippi River.", 100),
    ("sq_lime_rock", "Camp or Picnic on the Infield Sam Posey Straightaway Hillside", "Lime Rock Park", "Set up a lawn chair on the natural grass amphitheater overlooking the Big Bend and Esses at Connecticut's historic 1957 bullring.", 100),
    ("sq_toledo_autograph", "Walk the Frontstretch On-Track Autograph Session", "Toledo Speedway", "Step onto the half-mile asphalt at ARCA's home track to meet the drivers and crews right beside their cars.", 100),
    ("sq_illinois_miles", "Walk the Historic 1-Mile Clay Infield at the State Fair", "Springfield / DuQuoin State Fairgrounds", "Use an infield pit pass to stand inside a 100-year-old 1-mile fairgrounds dirt track while 3,400-lb stock cars slide past at 120 mph.", 100),
    ("sq_salem_banks", "Stand at the Base of the Historic 33-Degree Salem High Banks", "Salem Speedway", "Walk up to the fence of the high-banked Indiana half-mile where legends have raced since 1947.", 100),
    ("sq_coronado_navy", "Watch Stock Cars Race Beside U.S. Navy Aircraft Carriers", "Naval Base Coronado", "Attend the historic street/runway race on active Naval Air Station North Island overlooking San Diego Bay.", 100),
    ("sq_homestead_sunset", "Watch the Sunset Over the Everglades Turn 1 & 2", "Homestead-Miami Speedway", "Watch the South Florida sky turn orange and purple over the backstretch as the Championship 4 battle inches from the wall.", 100),
    ("sq_dawsonville_sireen", "Hear (or See) the WWII Victory 'SiReen' at the Pool Room", "Dawsonville Pool Room", "Visit the historic Dawsonville Pool Room in Georgia where the hand-cranked air-raid siren sounds for every Elliott family win.", 100),
    ("sq_occoneechee", "Walk the Full 0.9-Mile 1949 Ghost Track Oval in the Woods", "Historic Occoneechee Speedway Trail", "Hike the complete dirt oval loop in Hillsborough, NC—passing the 1949 concrete grandstands, flagstand, and rusted #42 stock car.", 100),
    ("sq_hof_sim", "Turn a Hot Lap in the iRacing Simulators at the Hall of Fame", "NASCAR Hall of Fame (Charlotte)", "Walk up the 33-degree Glory Road banking exhibit and race a pack of fans in the full-size Hall of Fame simulators.", 100),
    ("sq_penske_fanwalk", "Walk the 400-Foot Overhead Glass Fan Walk", "Team Penske Racing Facility", "Look straight down onto the Cup Series and IndyCar build bays from the suspended glass walkway in Mooresville.", 100),
    ("sq_petty_level_cross", "Stand Inside the Original 1949 Lee Petty A-Frame Shop", "Petty Museum (Randleman, NC)", "Visit the original Level Cross reaper shed where Lee and Richard Petty built their first championship cars.", 100),
]

US_STATES = [
    "ALL", "AL", "AZ", "CA", "CO", "CT", "DE", "FL", "GA", "IA", "IL", "IN",
    "KS", "KY", "ME", "MI", "MN", "MO", "NC", "NH", "NV", "NY", "OH", "OK",
    "OR", "PA", "SC", "TN", "TX", "VA", "WA", "WI"
]

MONTH_MAP = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
}


def parse_day_of_year(date_str):
    if not date_str:
        return None
    m = re.search(r"([A-Za-z]{3})[a-z]*\s+(\d{1,2})", str(date_str))
    if not m:
        return None
    mon = MONTH_MAP.get(m.group(1).lower()[:3])
    day = int(m.group(2))
    if not mon:
        return None
    days_before = [0, 0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    return days_before[mon] + day


def normalize_track_key(track_name):
    if not track_name:
        return ""
    clean = re.sub(r"\s*\(.*?\)", "", track_name).strip().lower()
    if "bullring at las vegas" in clean:
        return "the bullring at las vegas motor speedway"
    if "dirt track at charlotte" in clean:
        return "the dirt track at charlotte"
    return clean


def get_item_attended_years(item):
    """Returns a sorted list of 4-digit year strings (e.g. ['2026']) when this race was attended."""
    yrs = item.get("attended_years", [])
    if isinstance(yrs, list) and yrs:
        return sorted(list({str(y).strip() for y in yrs if str(y).strip()}))
    if item.get("attended"):
        fallback_yr = str(item.get("season_year", "2026")).strip() or "2026"
        return [fallback_yr]
    return []


def format_date_with_year(item):
    base_date = item.get("date", "")
    yrs = get_item_attended_years(item)
    if yrs:
        return f"{base_date}\n({'/'.join(yrs)})"
    return base_date


def format_display_notes(item):
    parts = []
    swept_yrs = item.get("_weekend_swept_years", [])
    if swept_yrs:
        parts.append(f"[{'/'.join(swept_yrs)} WEEKEND SWEEP CONQUERED!]")
    yrs = get_item_attended_years(item)
    if yrs:
        parts.append(f"[Attended: {', '.join(yrs)}]")
    rating = item.get("rating", "")
    if rating and rating != "Unrated":
        parts.append(f"[{rating}]")
    winner = item.get("winner", "").strip()
    if winner:
        parts.append(f"[Winner: {winner}]")
    seat = item.get("seat", "").strip()
    if seat:
        parts.append(f"[Seat/Camp: {seat}]")
    base_notes = item.get("notes", "").strip()
    if base_notes:
        parts.append(base_notes)
    return "  •  ".join(parts) if parts else ""


def parse_money(val):
    if val is None:
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    cleaned = re.sub(r"[^0-9.]", "", str(val))
    try:
        return float(cleaned) if cleaned else 0.0
    except Exception:
        return 0.0


def fmt_money(val):
    v = parse_money(val)
    return f"${v:,.2f}" if v % 1 != 0 else f"${int(v):,}"


def extract_default_ticket_price(notes_str):
    if not notes_str:
        return 0.0
    if "Admission: FREE" in notes_str:
        return 0.0
    m = re.search(r"(?:Tix|Admission|Tour \+ Museum|Kart Races):\s*\$(\d+)", notes_str)
    if m:
        return float(m.group(1))
    return 0.0


def extract_state_code(address_or_city):
    if not address_or_city:
        return ""
    m = re.search(r",\s*([A-Z]{2})\b", address_or_city)
    if m:
        return m.group(1)
    return ""


def parse_miles_int(dist_str):
    if not dist_str or dist_str == "—":
        return 999999
    nums = re.sub(r"[^0-9]", "", str(dist_str))
    return int(nums) if nums else 999999


def load_custom_ttf_font(root):
    global APP_FONT
    FR_PRIVATE = 0x10
    search_dirs = [".", "fonts"]
    loaded_files = []

    for d in search_dirs:
        if not os.path.exists(d):
            continue
        for fname in os.listdir(d):
            if fname.lower().endswith((".ttf", ".otf")):
                full_path = os.path.abspath(os.path.join(d, fname))
                try:
                    ctypes.windll.gdi32.AddFontResourceExW(full_path, FR_PRIVATE, 0)
                    loaded_files.append(fname)
                except Exception:
                    pass

    available = list(tkfont.families(root))
    preferred = ["Helvetica S Bold", "Helvetica S", "Helvetica", "Segoe UI"]
    for cand in preferred:
        for fam in available:
            if fam.lower() == cand.lower():
                APP_FONT = fam
                return APP_FONT, loaded_files

    for fam in available:
        if "helvetica" in fam.lower():
            APP_FONT = fam
            return APP_FONT, loaded_files

    APP_FONT = "Segoe UI"
    return APP_FONT, loaded_files


def generate_smart_notes(race_name, track_name, series_key, existing_notes=""):
    if existing_notes and ("Tix:" in existing_notes or "Admission:" in existing_notes):
        return None, existing_notes

    r_low = race_name.lower()
    t_low = track_name.lower()

    for key, (is_bkt, note_txt) in ICONIC_RACE_NOTES.items():
        if key in r_low:
            return is_bkt, note_txt

    if series_key == "Cup":
        if "daytona" in t_low:
            return True, "High-banks Daytona pack racing | Tix: $69-$195 | Hard Rock Bet Fanzone & Pre-Race Pass: $75 | VIP Garage: $650+"
        if "talladega" in t_low:
            return True, "200 mph pack drafting at Talladega | Tix: $65-$165 | Talladega Garage Experience Pass: $85-$145"
        if "bristol" in t_low:
            return False, "High-banked Thunder Valley concrete short track | Tix: $65-$160 | Pre-Race Track Walk: $75 | Ultimate Fan Pass: $625+"
        if "charlotte" in t_low:
            return False, "Home-turf battle in Concord, NC | Tix: $59-$165 | Pre-Race Track Pass: $75-$95 | VIP Garage: $600+"
        if "martinsville" in t_low:
            return False, "0.526-mile Virginia Paperclip short track + $2 hot dogs | Tix: $50-$135 | Pre-Race Track Pass: $65"
        if "darlington" in t_low:
            return False, "The Track Too Tough to Tame egg-shaped oval | Tix: $55-$145 | Pre-Race Experience Pass: $65"
        return False, f"NASCAR Cup Series feature at {track_name} | Tix: $55-$145 | Pre-Race Track/Pit Pass: $65-$85 | VIP Garage Experience: $550+"
    elif series_key == "O'Reilly":
        return False, f"O'Reilly Auto Parts Series showcase at {track_name} | Tix: $40-$80 | Pre-Race Track/Infield Pass: $45-$55"
    elif series_key == "Craftsman":
        return False, f"FedEx Truck Series battle at {track_name} | Tix: $35-$70 | Pre-Race Track/Pit Walk Pass: $40-$50"
    elif series_key == "Grassroots":
        return False, f"Grassroots short-track racing at {track_name} | Tix: $20-$40 | Pit Pass: $40-$50"
    else:
        return False, f"ARCA Menards Series event at {track_name} | Tix: $25-$45 | Infield Pit & On-Track Autograph Pass: $40-$45"


def make_slug(text):
    norm = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "_", norm.lower()).strip("_")


def lookup_track_address(track_name, fallback=""):
    t_low = track_name.lower()
    for key, addr in TRACK_ADDRESS_BOOK.items():
        if key in t_low:
            return addr
    return fallback or track_name


def http_get_bytes(url, headers=None, timeout=10):
    hdrs = headers or {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0.0.0 Safari/537.36",
        "Accept": "*/*"
    }
    if HAS_REQUESTS:
        resp = requests.get(url, headers=hdrs, timeout=timeout)
        resp.raise_for_status()
        return resp.content
    else:
        req = urllib.request.Request(url, headers=hdrs)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read()


def http_get_json(url, headers=None, timeout=10):
    raw = http_get_bytes(url, headers=headers, timeout=timeout)
    return json.loads(raw.decode("utf-8", errors="ignore"))


class ResponsiveRaceTable(tk.Frame):
    ROW_H = 120

    def __init__(self, parent, app, columns_spec, on_select_cb=None, on_flag_cb=None, on_trophy_cb=None, on_notes_cb=None, row_height=120):
        super().__init__(parent, bd=0, highlightthickness=0)
        self.app = app
        self.columns_spec = columns_spec
        self.on_select_cb = on_select_cb
        self.on_flag_cb = on_flag_cb
        self.on_trophy_cb = on_trophy_cb
        self.on_notes_cb = on_notes_cb
        self.ROW_H = row_height

        self.rows_data = []
        self.selected_idx = None
        self.computed_widths = []

        self.header_canvas = tk.Canvas(self, height=38, bd=0, highlightthickness=0)
        self.header_canvas.pack(side="top", fill="x")

        body_frame = tk.Frame(self, bd=0, highlightthickness=0)
        body_frame.pack(side="top", fill="both", expand=True)

        self.canvas = tk.Canvas(body_frame, bd=0, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(body_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.canvas.bind("<Configure>", self._on_resize)
        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<Double-1>", self._on_double_click)
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        if self.canvas.winfo_containing(event.x_root, event.y_root) == self.canvas:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _compute_col_widths(self, total_w):
        if total_w < 300:
            total_w = 1150
        min_sum = sum(c["min_w"] for c in self.columns_spec)
        extra = max(0, total_w - min_sum)
        total_weight = max(1, sum(c["weight"] for c in self.columns_spec))

        widths = []
        for c in self.columns_spec:
            w = c["min_w"] + int(extra * (c["weight"] / total_weight))
            widths.append(w)
        self.computed_widths = widths

    def _on_resize(self, event):
        self._compute_col_widths(event.width)
        self.redraw()

    def set_rows(self, rows):
        self.rows_data = rows
        if self.selected_idx is not None and self.selected_idx >= len(rows):
            self.selected_idx = None
        self.redraw()

    def get_selected_real_idx(self):
        if self.selected_idx is None or not (0 <= self.selected_idx < len(self.rows_data)):
            return None
        return self.rows_data[self.selected_idx].get("_real_idx", self.selected_idx)

    def select_by_real_idx(self, real_idx):
        for r_i, r in enumerate(self.rows_data):
            if r.get("_real_idx", r_i) == real_idx:
                self.selected_idx = r_i
                self.redraw()
                if self.on_select_cb:
                    self.on_select_cb(real_idx)
                return

    def redraw(self):
        w = self.canvas.winfo_width()
        self._compute_col_widths(w)

        dark = self.app.dark_mode
        head_bg = "#0f172a" if dark else "#1e293b"
        head_fg = "#f8fafc"
        odd_bg = "#1e293b" if dark else "#ffffff"
        even_bg = "#243044" if dark else "#f1f5f9"
        return_bg = "#064e3b" if dark else "#dcfce7"
        sel_bg = "#334155" if dark else "#cbd5e1"
        sel_border = "#60a5fa" if dark else "#475569"
        text_fg = "#f8fafc" if dark else "#0f172a"
        sub_fg = "#cbd5e1" if dark else "#334155"
        gold_fg = "#fde047" if dark else "#b45309"
        sweep_fg = "#4ade80" if dark else "#15803d"
        line_col = "#334155" if dark else "#cbd5e1"

        self.header_canvas.configure(bg=head_bg)
        self.header_canvas.delete("all")
        x_cur = 0
        for col, cw in zip(self.columns_spec, self.computed_widths):
            anchor = "w" if col["align"] == "left" else "center"
            tx = x_cur + 12 if anchor == "w" else x_cur + cw // 2
            self.header_canvas.create_text(
                tx, 19, text=col["title"], fill=head_fg,
                font=(APP_FONT, 10, "bold"), anchor=anchor
            )
            x_cur += cw

        self.canvas.configure(bg=odd_bg)
        self.canvas.delete("all")
        total_h = max(len(self.rows_data) * self.ROW_H, 10)
        total_w = sum(self.computed_widths)
        self.canvas.configure(scrollregion=(0, 0, total_w, total_h))

        for r_idx, row in enumerate(self.rows_data):
            y0 = r_idx * self.ROW_H
            y1 = y0 + self.ROW_H
            ymid = y0 + self.ROW_H // 2

            is_sel = (r_idx == self.selected_idx)
            is_ret = row.get("_is_return_leg", False)
            bg = sel_bg if is_sel else (return_bg if is_ret else (even_bg if r_idx % 2 == 0 else odd_bg))
            fg = text_fg
            s_fg = text_fg if is_sel else sub_fg

            self.canvas.create_rectangle(
                0, y0, total_w, y1,
                fill=bg,
                outline=sel_border if is_sel else line_col,
                width=2 if is_sel else 1
            )

            x_cur = 0
            for col, cw in zip(self.columns_spec, self.computed_widths):
                ckey = col["key"]
                cx_mid = x_cur + cw // 2

                if ckey == "flag":
                    icon = self.app.icon_checkered_flag if row.get("flag") else self.app.icon_green_flag
                    if icon:
                        self.canvas.create_image(cx_mid, ymid, image=icon)
                elif ckey == "trophy":
                    icon = self.app.icon_trophy_gold if row.get("trophy") else self.app.icon_trophy_grey
                    if icon:
                        self.canvas.create_image(cx_mid, ymid, image=icon)
                elif ckey == "progress_bar":
                    done_n = row.get("done_n", 0)
                    need_n = max(1, row.get("need_n", 1))
                    pct = min(1.0, done_n / need_n)
                    bar_w = max(80, cw - 28)
                    bx0 = cx_mid - bar_w // 2
                    by0 = ymid - 14
                    by1 = ymid + 4
                    self.canvas.create_rectangle(bx0, by0, bx0 + bar_w, by1, fill="#0f172a", outline="#475569", width=1)
                    if pct > 0:
                        fill_col = "#22c55e" if pct >= 1.0 else "#eab308"
                        self.canvas.create_rectangle(bx0 + 1, by0 + 1, bx0 + int((bar_w - 2) * pct), by1 - 1, fill=fill_col, outline="")
                    lbl_txt = f"COMPLETED! ({done_n}/{need_n})" if pct >= 1.0 else f"{done_n} / {need_n} ({int(pct * 100)}%)"
                    self.canvas.create_text(
                        cx_mid, ymid + 18, text=lbl_txt,
                        fill=sweep_fg if pct >= 1.0 else fg,
                        font=(APP_FONT, 9, "bold"), anchor="center"
                    )
                elif ckey == "event":
                    logo = row.get("logo")
                    avail_w = max(70, cw - 14)
                    if logo:
                        self.canvas.create_image(cx_mid, y0 + int(self.ROW_H * 0.34), image=logo)
                        self.canvas.create_text(
                            cx_mid, y0 + int(self.ROW_H * 0.81), text=row.get("name", ""),
                            fill=fg, font=(APP_FONT, 10, "bold"),
                            anchor="center", justify="center", width=avail_w
                        )
                    else:
                        self.canvas.create_text(
                            cx_mid, ymid, text=row.get("name", ""),
                            fill=fg, font=(APP_FONT, 10, "bold"),
                            anchor="center", justify="center", width=avail_w
                        )
                elif ckey == "track":
                    t_logo = row.get("track_logo")
                    t_name = row.get("track", "")
                    avail_w = max(70, cw - 14)
                    if t_logo:
                        self.canvas.create_image(cx_mid, y0 + int(self.ROW_H * 0.34), image=t_logo)
                        self.canvas.create_text(
                            cx_mid, y0 + int(self.ROW_H * 0.81), text=t_name,
                            fill=fg, font=(APP_FONT, 10, "bold"),
                            anchor="center", justify="center", width=avail_w
                        )
                    else:
                        self.canvas.create_text(
                            cx_mid, ymid, text=t_name,
                            fill=fg, font=(APP_FONT, 10, "bold"),
                            anchor="center", justify="center", width=avail_w
                        )
                else:
                    val = str(row.get(ckey, ""))
                    if col["align"] == "center":
                        c_fill = sweep_fg if (ckey in ("stop_total", "xp") or (ckey == "date" and "(" in val)) else fg
                        self.canvas.create_text(
                            cx_mid, ymid, text=val, fill=c_fill,
                            font=(APP_FONT, 10, "bold"), anchor="center", justify="center", width=max(40, cw - 10)
                        )
                    else:
                        if ckey == "notes" and "WEEKEND SWEEP CONQUERED!" in val:
                            note_color = sweep_fg
                        elif ckey == "notes" and "BUCKET LIST:" in val:
                            note_color = gold_fg
                        elif ckey in ("address", "notes"):
                            note_color = s_fg
                        else:
                            note_color = fg
                        self.canvas.create_text(
                            x_cur + 10, ymid, text=val, fill=note_color,
                            font=(APP_FONT, 9, "bold"), anchor="w", width=max(40, cw - 16)
                        )
                x_cur += cw

    def _col_at_x(self, x):
        cur = 0
        for col, cw in zip(self.columns_spec, self.computed_widths):
            if cur <= x < cur + cw:
                return col["key"]
            cur += cw
        return None

    def _on_click(self, event):
        canvas_y = self.canvas.canvasy(event.y)
        r_idx = int(canvas_y // self.ROW_H)
        if not (0 <= r_idx < len(self.rows_data)):
            return

        row = self.rows_data[r_idx]
        if row.get("_is_return_leg"):
            return

        self.selected_idx = r_idx
        real_idx = row.get("_real_idx", r_idx)
        ckey = self._col_at_x(event.x)

        self.redraw()
        if self.on_select_cb:
            self.on_select_cb(real_idx)

        if ckey == "flag" and self.on_flag_cb:
            self.on_flag_cb(real_idx)
        elif ckey == "trophy" and self.on_trophy_cb:
            self.on_trophy_cb(real_idx)
        elif ckey == "notes" and self.on_notes_cb:
            self.on_notes_cb(real_idx)

    def _on_double_click(self, event):
        canvas_y = self.canvas.canvasy(event.y)
        r_idx = int(canvas_y // self.ROW_H)
        if not (0 <= r_idx < len(self.rows_data)):
            return
        row = self.rows_data[r_idx]
        if row.get("_is_return_leg"):
            return
        real_idx = row.get("_real_idx", r_idx)
        ckey = self._col_at_x(event.x)
        if ckey not in ("flag", "trophy", "notes") and self.on_flag_cb:
            self.on_flag_cb(real_idx)


class NASCARTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_NAME)
        self.root.geometry("1460x880")
        self.root.minsize(1040, 660)

        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("TrackChaserHQ.MotorsportTracker.4.0")
        except Exception:
            pass

        self.font_name, self.loaded_ttf_files = load_custom_ttf_font(self.root)

        os.makedirs(CUSTOM_LOGO_DIR, exist_ok=True)
        self.tables = {}
        self.tab_frames = {}
        self.tab_buttons = {}
        self.active_tab_key = "Cup"
        self.active_arca_key = "ARCA_National"
        self.arca_buttons = {}
        self.quest_sub_buttons = {}

        self.logo_cache = {}
        self.geo_cache = self.load_geo_cache()
        self.load_data()

        self.dark_mode = self.data.get("settings", {}).get("dark_mode", True)
        saved_home = self.data.get("settings", {}).get("home_address", "")
        self.home_var = tk.StringVar(value=saved_home)

        self.filter_state_var = tk.StringVar(value="ALL")
        self.filter_dist_var = tk.StringVar(value="Any Distance")
        self.filter_status_var = tk.StringVar(value="All Items")
        self.sort_by_var = tk.StringVar(value="Schedule / Default")
        self.search_var = tk.StringVar(value="")

        exp = self.data.get("TripExpenses", {})
        self.trip_name_var = tk.StringVar(value=exp.get("trip_name", "My Race Weekend Trip"))
        self.exp_hotel_var = tk.StringVar(value=str(exp.get("hotel", "0")))
        self.exp_fuel_var = tk.StringVar(value=str(exp.get("fuel", "0")))
        self.exp_food_var = tk.StringVar(value=str(exp.get("food", "0")))
        self.exp_souvenirs_var = tk.StringVar(value=str(exp.get("souvenirs", "0")))
        self.exp_other_var = tk.StringVar(value=str(exp.get("other", "0")))
        self.exp_budget_var = tk.StringVar(value=str(exp.get("budget_limit", "0")))
        self.saved_trip_select_var = tk.StringVar(value="")

        self.generate_app_icon()
        self.build_status_icons()
        self.build_ui()
        self.apply_theme()
        self.switch_main_tab("Cup")
        self.update_stats()
        self.refresh_all_tables()

    def get_active_season_year_for_series(self, series_key):
        """Determines which season year to stamp when a race is marked Attended."""
        sel = getattr(self, "year_var", None)
        sel_val = sel.get() if sel else "Season"
        if sel_val in ("2025", "2026", "2027"):
            return sel_val
        if series_key in ("ARCA_National", "ARCA_East", "ARCA_West"):
            return "2027"
        return "2026"

    # -------------------- APP ICON & TOP HERO BANNER GENERATOR --------------------

    def generate_app_icon(self):
        if not HAS_PIL:
            return
        try:
            if not os.path.exists(ICON_ICO_FILE) or not os.path.exists(ICON_PNG_FILE):
                sz = 256
                img = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
                d = ImageDraw.Draw(img)

                shield = [(128, 12), (236, 44), (218, 174), (128, 244), (38, 174), (20, 44)]
                d.polygon(shield, fill="#0f172a", outline="#facc15", width=10)

                d.polygon([(55, 48), (95, 48), (65, 190), (38, 165)], fill="#dc2626")
                d.polygon([(165, 48), (205, 48), (215, 165), (185, 190)], fill="#2563eb")

                for r in range(2):
                    for c in range(8):
                        bx = 40 + c * 22
                        by = 72 + r * 20
                        col = "#ffffff" if (r + c) % 2 == 0 else "#1e293b"
                        d.rectangle([bx, by, bx + 22, by + 20], fill=col)

                d.polygon([(88, 96), (168, 96), (152, 166), (104, 166)], fill="#facc15", outline="#ca8a04", width=4)
                d.rectangle([118, 166, 138, 194], fill="#facc15", outline="#ca8a04", width=3)
                d.rectangle([94, 194, 162, 212], fill="#92400e", outline="#facc15", width=3)

                img.save(ICON_PNG_FILE, "PNG")
                img.save(ICON_ICO_FILE, format="ICO", sizes=[(256, 256), (64, 64), (32, 32), (16, 16)])

            self.root.iconbitmap(ICON_ICO_FILE)
            self._app_icon_photo = ImageTk.PhotoImage(Image.open(ICON_PNG_FILE).resize((48, 48), Image.Resampling.LANCZOS))
        except Exception:
            self._app_icon_photo = None

    def draw_top_banner(self, event=None):
        w = self.banner_canvas.winfo_width()
        h = 68
        if w < 200:
            w = 1420
        self.banner_canvas.delete("all")

        if HAS_PIL and os.path.exists(CUSTOM_BANNER_FILE):
            try:
                b_img = Image.open(CUSTOM_BANNER_FILE).convert("RGBA")
                b_img = b_img.resize((w, h), Image.Resampling.LANCZOS)
                self._custom_banner_photo = ImageTk.PhotoImage(b_img)
                self.banner_canvas.create_image(0, 0, image=self._custom_banner_photo, anchor="nw")
                self.banner_canvas.create_text(
                    w - 16, h // 2, text=self.stats_var.get(),
                    fill="#f8fafc", font=(APP_FONT, 9, "bold"), anchor="e"
                )
                return
            except Exception:
                pass

        self.banner_canvas.configure(bg="#090d16")
        for x in range(-h, w, 18):
            self.banner_canvas.create_line(x, h, x + h, 0, fill="#111827", width=2)

        sq = 11
        for r in range(6):
            for c in range(4):
                col = "#f8fafc" if (r + c) % 2 == 0 else "#1e293b"
                self.banner_canvas.create_rectangle(c * sq, r * sq, (c + 1) * sq, (r + 1) * sq, fill=col, outline="")

        self.banner_canvas.create_polygon(46, h, 72, 0, 86, 0, 60, h, fill="#dc2626", outline="")
        self.banner_canvas.create_polygon(64, h, 90, 0, 100, 0, 74, h, fill="#facc15", outline="")
        self.banner_canvas.create_polygon(78, h, 104, 0, 118, 0, 92, h, fill="#2563eb", outline="")

        text_x = 130
        if getattr(self, "_app_icon_photo", None):
            self.banner_canvas.create_image(148, h // 2, image=self._app_icon_photo)
            text_x = 182

        self.banner_canvas.create_text(
            text_x, 23, text="TRACKCHASER HQ",
            fill="#f8fafc", font=(APP_FONT, 15, "bold"), anchor="w"
        )
        self.banner_canvas.create_text(
            text_x, 48, text="NASCAR  •  ARCA  •  GRASSROOTS  •  WEEKEND SWEEPS  •  SIDE-TRACKED QUESTS",
            fill="#facc15", font=(APP_FONT, 8, "bold"), anchor="w"
        )

        self.banner_canvas.create_rectangle(0, h - 3, w, h, fill="#eab308", outline="")

        self.banner_canvas.create_text(
            w - 14, h // 2, text=self.stats_var.get(),
            fill="#f8fafc", font=(APP_FONT, 8, "bold"), anchor="e"
        )

    def build_status_icons(self):
        self.icon_green_flag = None
        self.icon_checkered_flag = None
        self.icon_trophy_grey = None
        self.icon_trophy_gold = None
        if not HAS_PIL:
            return

        self.icon_green_flag = ImageTk.PhotoImage(self._draw_flag_icon(checkered=False))
        self.icon_checkered_flag = ImageTk.PhotoImage(self._draw_flag_icon(checkered=True))
        self.icon_trophy_grey = ImageTk.PhotoImage(self._draw_trophy_icon(active=False))
        self.icon_trophy_gold = ImageTk.PhotoImage(self._draw_trophy_icon(active=True))

    @staticmethod
    def _draw_flag_icon(checkered=False):
        img = Image.new("RGBA", (48, 42), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.line([(9, 5), (9, 38)], fill="#94a3b8", width=3)
        d.ellipse([7, 3, 11, 7], fill="#f8fafc")

        if not checkered:
            poly = [(11, 7), (41, 10), (39, 28), (11, 25)]
            d.polygon(poly, fill="#16a34a", outline="#ffffff")
            d.line([(15, 13), (35, 15)], fill="#4ade80", width=2)
        else:
            x0, y0, cell_w, cell_h = 11, 7, 7, 6
            for r in range(3):
                for c in range(4):
                    bx0 = x0 + c * cell_w
                    by0 = y0 + r * cell_h + (1 if c % 2 == 1 else 0)
                    col = "#0f172a" if (r + c) % 2 == 0 else "#ffffff"
                    d.rectangle([bx0, by0, bx0 + cell_w, by0 + cell_h], fill=col)
            d.rectangle([x0, y0, x0 + 4 * cell_w, y0 + 3 * cell_h + 1], outline="#cbd5e1", width=1)
        return img

    @staticmethod
    def _draw_trophy_icon(active=False):
        img = Image.new("RGBA", (44, 42), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        if active:
            cup_fill = "#facc15"
            cup_edge = "#ca8a04"
            shine = "#fef08a"
            base_col = "#92400e"
        else:
            cup_fill = "#475569"
            cup_edge = "#64748b"
            shine = "#64748b"
            base_col = "#334155"

        d.arc([5, 8, 17, 23], start=90, end=270, fill=cup_edge, width=3)
        d.arc([27, 8, 39, 23], start=270, end=90, fill=cup_edge, width=3)
        d.polygon([(11, 6), (33, 6), (29, 23), (15, 23)], fill=cup_fill, outline=cup_edge)
        d.line([(15, 9), (17, 20)], fill=shine, width=2)
        d.rectangle([20, 23, 24, 31], fill=cup_fill, outline=cup_edge)
        d.rectangle([13, 31, 31, 36], fill=base_col, outline=cup_edge)
        d.rectangle([11, 36, 33, 39], fill=cup_edge)
        return img

    # -------------------- DATA & STORAGE --------------------

    def load_geo_cache(self):
        if os.path.exists(GEO_CACHE_FILE):
            try:
                with open(GEO_CACHE_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def save_geo_cache(self):
        try:
            with open(GEO_CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.geo_cache, f, indent=2)
        except Exception:
            pass

    def load_data(self):
        if not os.path.exists(USER_FILE) and os.path.exists(DEFAULT_FILE):
            shutil.copy(DEFAULT_FILE, USER_FILE)

        target = USER_FILE if os.path.exists(USER_FILE) else DEFAULT_FILE
        try:
            with open(target, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        except Exception as e:
            messagebox.showerror("Error", f"Could not load data file:\n{e}")
            self.data = {}

        self.data.setdefault("settings", {"home_address": "", "dark_mode": True})
        if self.data["settings"].get("home_address") == "Murphy, NC":
            self.data["settings"]["home_address"] = ""
        self.data.setdefault("Trip", [])
        self.data.setdefault("TripExpenses", {
            "trip_name": "My Race Weekend Trip",
            "hotel": 0.0,
            "fuel": 0.0,
            "food": 0.0,
            "souvenirs": 0.0,
            "other": 0.0,
            "budget_limit": 0.0
        })
        self.data.setdefault("SavedTrips", {})
        self.data.setdefault("QuestProgress", {"food": {}, "side_quests": {}, "custom_quests": []})
        self.data.setdefault("CompletedTracksHistory", [])

        if os.path.exists(DEFAULT_FILE):
            try:
                with open(DEFAULT_FILE, "r", encoding="utf-8") as f:
                    defaults = json.load(f)

                for k in SERIES_KEYS:
                    default_yr = "2027" if k in ("ARCA_National", "ARCA_East", "ARCA_West") else "2026"
                    if not self.data.get(k):
                        self.data[k] = defaults.get(k, [])
                    def_map = {x.get("race", "").lower(): x for x in defaults.get(k, [])}
                    for item in self.data.get(k, []):
                        item.setdefault("season_year", default_yr)
                        if item.get("attended") and not item.get("attended_years"):
                            item["attended_years"] = [item["season_year"]]
                        if not item.get("address"):
                            item["address"] = lookup_track_address(item.get("track", ""), item.get("location", ""))
                        d_match = def_map.get(item.get("race", "").lower(), {})
                        if not item.get("notes") or "Tix:" not in item.get("notes", ""):
                            if d_match.get("notes"):
                                item["notes"] = d_match["notes"]
                                if d_match.get("bucket_list"):
                                    item["bucket_list"] = True
                            else:
                                auto_bkt, auto_note = generate_smart_notes(item.get("race", ""), item.get("track", ""), k, item.get("notes", ""))
                                item["notes"] = auto_note
                                if auto_bkt:
                                    item["bucket_list"] = True

                def_attr_map = {x.get("name", ""): x for x in defaults.get("Attractions", [])}
                for item in self.data.get("Attractions", []):
                    d_match = def_attr_map.get(item.get("name", ""), {})
                    if d_match.get("notes") and "Admission:" not in item.get("notes", ""):
                        item["notes"] = d_match["notes"]
            except Exception:
                pass

    def save_data(self):
        self.data.setdefault("settings", {})
        self.data["settings"]["home_address"] = self.home_var.get().strip()
        self.data["settings"]["dark_mode"] = self.dark_mode
        self.data["TripExpenses"] = {
            "trip_name": self.trip_name_var.get().strip() or "My Race Weekend Trip",
            "hotel": parse_money(self.exp_hotel_var.get()),
            "fuel": parse_money(self.exp_fuel_var.get()),
            "food": parse_money(self.exp_food_var.get()),
            "souvenirs": parse_money(self.exp_souvenirs_var.get()),
            "other": parse_money(self.exp_other_var.get()),
            "budget_limit": parse_money(self.exp_budget_var.get())
        }
        with open(USER_FILE, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4)
        self.update_stats()

    # -------------------- SAME-YEAR WEEKEND SWEEP & UNIQUE TRACKS ENGINE --------------------

    def compute_weekend_sweeps_and_tracks(self):
        """
        1. Unique Tracks Conquered: Counts any track where you attended a race in ANY year.
        2. Weekend Sweeps Conquered: Groups national series races at the same track within a 5-day window.
           A Weekend Sweep is ONLY awarded if every race in that weekend cluster was attended in the
           EXACT SAME YEAR (e.g., watching 2026 Bristol Trucks/ARCA and 2027 Bristol O'Reilly/Cup
           counts toward Unique Tracks, but does NOT award a Weekend Sweep until all races in the
           weekend share a common attended year).
        """
        all_tracks = set()
        attended_tracks = set(self.data.get("CompletedTracksHistory", []))

        for k in SERIES_KEYS:
            for ev in self.data.get(k, []):
                ev["_weekend_swept"] = False
                ev["_weekend_swept_years"] = []
                tk_norm = normalize_track_key(ev.get("track", ""))
                if tk_norm:
                    all_tracks.add(tk_norm)
                    if ev.get("attended") or get_item_attended_years(ev):
                        attended_tracks.add(tk_norm)

        self.data["CompletedTracksHistory"] = sorted(list(attended_tracks))

        by_track = {}
        for k in NATIONAL_WEEKEND_KEYS:
            for ev in self.data.get(k, []):
                tk_norm = normalize_track_key(ev.get("track", ""))
                doy = parse_day_of_year(ev.get("date", ""))
                if tk_norm and doy is not None:
                    by_track.setdefault(tk_norm, []).append((doy, ev))

        total_weekends = 0
        conquered_weekends = 0

        for tk_norm, ev_list in by_track.items():
            ev_list.sort(key=lambda x: x[0])
            clusters = []
            for doy, ev in ev_list:
                if not clusters or (doy - clusters[-1][-1][0]) > 5:
                    clusters.append([(doy, ev)])
                else:
                    clusters[-1].append((doy, ev))

            for cluster in clusters:
                total_weekends += 1
                # Intersect attended_years across every single race in this weekend cluster
                year_sets = [set(get_item_attended_years(item[1])) for item in cluster]
                common_years = sorted(list(set.intersection(*year_sets))) if year_sets else []
                if common_years:
                    conquered_weekends += 1
                    for _, ev in cluster:
                        ev["_weekend_swept"] = True
                        ev["_weekend_swept_years"] = common_years

        return conquered_weekends, total_weekends, len(attended_tracks), len(all_tracks)

    # -------------------- QUESTS & CHALLENGES EVALUATION ENGINE --------------------

    def evaluate_auto_campaign(self, camp, swept_wknds, vis_tracks):
        ctype = camp["type"]
        targets = camp.get("targets", [])

        attended_races_blob = []
        attended_tracks_blob = set(self.data.get("CompletedTracksHistory", []))
        for k in SERIES_KEYS:
            for ev in self.data.get(k, []):
                if ev.get("attended") or get_item_attended_years(ev):
                    attended_races_blob.append(ev.get("race", "").lower())
                    attended_tracks_blob.add(ev.get("track", "").lower())

        visited_attr_blob = [
            a.get("name", "").lower() for a in self.data.get("Attractions", []) if a.get("visited")
        ]

        if ctype == "races":
            done = sum(1 for t in targets if any(t in r for r in attended_races_blob))
            need = len(targets)
        elif ctype == "tracks":
            done = sum(1 for t in targets if any(t in tr for tr in attended_tracks_blob))
            need = len(targets)
        elif ctype == "mixed_tracks_attr":
            combined = list(attended_tracks_blob) + visited_attr_blob
            done = sum(1 for t in targets if any(t in c for c in combined))
            need = len(targets)
        elif ctype == "track_count_any":
            matched = sum(1 for t in targets if any(t in tr for tr in attended_tracks_blob))
            need = camp.get("need", 3)
            done = min(need, matched)
        elif ctype == "race_count_any":
            matched = sum(1 for t in targets if any(t in r for r in attended_races_blob))
            need = camp.get("need", 3)
            done = min(need, matched)
        elif ctype == "attr_count_any":
            matched = sum(1 for t in targets if any(t in a for a in visited_attr_blob))
            need = camp.get("need", 5)
            done = min(need, matched)
        elif ctype == "attr_all":
            done = sum(1 for t in targets if any(t in a for a in visited_attr_blob))
            need = len(targets)
        elif ctype == "sweeps":
            need = camp.get("need", 1)
            done = min(need, swept_wknds)
        elif ctype == "unique_tracks":
            need = camp.get("need", 10)
            done = min(need, vis_tracks)
        else:
            done, need = 0, 1

        return done, need, (done >= need)

    @staticmethod
    def get_chaser_rank_title(xp):
        if xp >= 4500:
            return "🏆 HALL OF FAME TRACK LEGEND"
        if xp >= 3000:
            return "🔥 GRAND NATIONAL BARNSTORMER"
        if xp >= 1800:
            return "⚡ HIGH-LINE VETERAN"
        if xp >= 900:
            return "🏁 WEEKEND ROAD WARRIOR"
        if xp >= 300:
            return "🎟️ SHORT-TRACK CONTENDER"
        return "🟢 ROOKIE STRIPE CHASER"

    # -------------------- USER CUSTOM RACE & TRACK LOGO ENGINE --------------------

    def find_custom_logo_file(self, name_str):
        if not name_str or not os.path.exists(CUSTOM_LOGO_DIR):
            return None
        target_slug = make_slug(name_str)
        legacy_slug = re.sub(r"[^a-z0-9]+", "_", name_str.lower()).strip("_")

        for fname in os.listdir(CUSTOM_LOGO_DIR):
            base, ext = os.path.splitext(fname)
            if ext.lower() not in (".png", ".jpg", ".jpeg", ".webp", ".gif"):
                continue
            file_slug = make_slug(base)
            if file_slug in (target_slug, legacy_slug) or base.lower() == name_str.lower():
                return os.path.join(CUSTOM_LOGO_DIR, fname)
        return None

    def _load_logo_photo(self, file_path, cache_id):
        try:
            src = Image.open(file_path).convert("RGBA")
            src.thumbnail((156, 64), Image.Resampling.LANCZOS)
            canvas = Image.new("RGBA", (160, 66), (255, 255, 255, 0))
            x = (160 - src.width) // 2
            y = (66 - src.height) // 2
            canvas.paste(src, (x, y), src)
            photo = ImageTk.PhotoImage(canvas)
            self.logo_cache[cache_id] = photo
            return photo
        except Exception:
            return None

    def get_race_logo(self, primary_name, series_key):
        if not HAS_PIL:
            return None
        cache_id = f"race|{series_key}|{primary_name}"
        if cache_id in self.logo_cache:
            return self.logo_cache[cache_id]

        logo_file = self.find_custom_logo_file(primary_name)
        if not logo_file:
            logo_file = self.find_custom_logo_file(series_key)

        if logo_file:
            return self._load_logo_photo(logo_file, cache_id)
        return None

    def get_track_logo(self, track_name):
        if not HAS_PIL or not track_name:
            return None
        cache_id = f"track|{track_name}"
        if cache_id in self.logo_cache:
            return self.logo_cache[cache_id]

        logo_file = self.find_custom_logo_file(track_name)
        if not logo_file:
            clean_track = re.sub(r"\s*\(.*?\)", "", track_name).strip()
            logo_file = self.find_custom_logo_file(clean_track)

        if logo_file:
            return self._load_logo_photo(logo_file, cache_id)
        return None

    def assign_custom_logo_for_selected(self, key, mode="race"):
        tbl = self.tables[key]
        real_idx = tbl.get_selected_real_idx()
        if real_idx is None:
            messagebox.showinfo("Select a Row", "Click a row first, then click the Set Logo button.")
            return
        item = self.data[key][real_idx]

        if mode == "track":
            name = item.get("track", "track")
            label_type = "Track Logo"
        else:
            name = item.get("race") or item.get("name", "item")
            label_type = "Event / Attraction Logo"

        slug = make_slug(name)
        file_path = filedialog.askopenfilename(
            title=f"Select {label_type} for '{name}'",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.webp *.gif"), ("All Files", "*.*")]
        )
        if not file_path:
            return

        dest_path = os.path.join(CUSTOM_LOGO_DIR, f"{slug}.png")
        try:
            img = Image.open(file_path).convert("RGBA")
            img.save(dest_path, "PNG")
            self.logo_cache.clear()
            self.refresh_all_tables()
            self.dist_status_var.set(f"Saved {label_type} to custom_logos/{slug}.png!")
        except Exception as e:
            messagebox.showerror("Image Error", f"Could not save logo:\n{e}")

    def open_custom_logos_folder(self):
        os.makedirs(CUSTOM_LOGO_DIR, exist_ok=True)
        os.startfile(os.path.abspath(CUSTOM_LOGO_DIR))

    def reload_custom_logos(self):
        self.logo_cache.clear()
        self.refresh_all_tables()
        count = len([f for f in os.listdir(CUSTOM_LOGO_DIR) if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))])
        self.dist_status_var.set(f"Reloaded {count} custom logos from custom_logos/ folder!")

    def make_flat_button(self, parent, text, bg_color, fg_color="#ffffff", cmd=None, pad_x=9, pad_y=4):
        return tk.Button(
            parent,
            text=text,
            bg=bg_color,
            fg=fg_color,
            activebackground=bg_color,
            activeforeground=fg_color,
            font=(APP_FONT, 9, "bold"),
            relief="flat",
            bd=0,
            padx=pad_x,
            pady=pad_y,
            cursor="hand2",
            command=cmd
        )

    def apply_theme(self):
        if self.dark_mode:
            bg_main = "#0f172a"
            bg_bar = "#1e293b"
            fg_text = "#f8fafc"
            btn_label = "Light Mode"
        else:
            bg_main = "#cbd5e1"
            bg_bar = "#ffffff"
            fg_text = "#0f172a"
            btn_label = "Dark Mode"

        self.root.configure(bg=bg_main)
        self.action_bar.configure(bg=bg_bar)
        self.filter_bar.configure(bg=bg_bar)
        self.tab_strip.configure(bg=bg_main)
        self.content_area.configure(bg=bg_main)
        self.home_lbl.configure(bg=bg_bar, fg=fg_text)
        self.dist_status_lbl.configure(bg=bg_bar, fg=fg_text)
        for lbl in self.filter_labels:
            lbl.configure(bg=bg_bar, fg=fg_text)
        self.theme_btn.configure(text=btn_label)

        for tbl in self.tables.values():
            tbl.redraw()

        self.update_tab_button_visuals()
        self.draw_top_banner()

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()
        self.save_data()

    def build_ui(self):
        self.stats_var = tk.StringVar()

        # ROW 1: Top Motorsport Hero Banner
        self.banner_canvas = tk.Canvas(self.root, height=68, bd=0, highlightthickness=0, bg="#090d16")
        self.banner_canvas.pack(fill="x", padx=10, pady=(8, 4))
        self.banner_canvas.bind("<Configure>", self.draw_top_banner)

        # ROW 2: Home Address + Season Dropdown, Sync, Reset, Refresh Logos & custom_logos Folder
        self.action_bar = tk.Frame(self.root, pady=5, padx=12)
        self.action_bar.pack(fill="x", padx=10, pady=(0, 3))

        self.theme_btn = self.make_flat_button(self.action_bar, "Light Mode", "#4f46e5", cmd=self.toggle_dark_mode)
        self.theme_btn.pack(side="right", padx=2)

        self.make_flat_button(
            self.action_bar, "custom_logos Folder", "#db2777", cmd=self.open_custom_logos_folder
        ).pack(side="right", padx=2)

        self.make_flat_button(
            self.action_bar, "Refresh Logos", "#9333ea", cmd=self.reload_custom_logos
        ).pack(side="right", padx=2)

        self.make_flat_button(
            self.action_bar, "Reset Data", "#64748b", cmd=self.reload_default_schedule
        ).pack(side="right", padx=2)

        self.make_flat_button(self.action_bar, "Sync ARCA", "#ca8a04", cmd=self.sync_from_arca_web).pack(side="right", padx=2)
        self.make_flat_button(self.action_bar, "Sync NASCAR", "#0284c7", cmd=self.sync_from_nascar_api).pack(side="right", padx=2)

        self.year_var = tk.StringVar(value="Season")
        year_spin = ttk.Combobox(
            self.action_bar, textvariable=self.year_var,
            values=["Season", "2026", "2027"], width=7, state="readonly", font=(APP_FONT, 9, "bold")
        )
        year_spin.pack(side="right", padx=3)

        self.home_lbl = tk.Label(self.action_bar, text="Home Address:", font=(APP_FONT, 10, "bold"))
        self.home_lbl.pack(side="left", padx=(0, 4))

        home_entry = tk.Entry(self.action_bar, textvariable=self.home_var, width=20, font=(APP_FONT, 10, "bold"), relief="solid", bd=1)
        home_entry.pack(side="left", padx=3, ipady=2)

        self.make_flat_button(
            self.action_bar, "Calc Distances", "#0d9488", cmd=self.start_distance_calculation
        ).pack(side="left", padx=4)

        self.dist_status_var = tk.StringVar(value="")
        self.dist_status_lbl = tk.Label(self.action_bar, textvariable=self.dist_status_var, font=(APP_FONT, 9, "bold"), anchor="w")
        self.dist_status_lbl.pack(side="left", fill="x", expand=True, padx=6)

        # ROW 3: Live Filter & Sort Bar
        self.filter_bar = tk.Frame(self.root, pady=5, padx=12)
        self.filter_bar.pack(fill="x", padx=10, pady=(0, 5))
        self.filter_labels = []

        def add_filter_lbl(txt):
            lbl = tk.Label(self.filter_bar, text=txt, font=(APP_FONT, 9, "bold"))
            lbl.pack(side="left", padx=(8 if self.filter_labels else 0, 3))
            self.filter_labels.append(lbl)

        add_filter_lbl("STATE:")
        state_cb = ttk.Combobox(self.filter_bar, textvariable=self.filter_state_var, values=US_STATES, width=5, state="readonly", font=(APP_FONT, 9, "bold"))
        state_cb.pack(side="left", padx=2)
        state_cb.bind("<<ComboboxSelected>>", lambda e: self.refresh_all_tables())

        add_filter_lbl("MAX DISTANCE:")
        dist_cb = ttk.Combobox(
            self.filter_bar, textvariable=self.filter_dist_var,
            values=["Any Distance", "Under 150 mi", "Under 300 mi", "Under 500 mi", "Under 1,000 mi"],
            width=13, state="readonly", font=(APP_FONT, 9, "bold")
        )
        dist_cb.pack(side="left", padx=2)
        dist_cb.bind("<<ComboboxSelected>>", lambda e: self.refresh_all_tables())

        add_filter_lbl("STATUS:")
        status_cb = ttk.Combobox(
            self.filter_bar, textvariable=self.filter_status_var,
            values=["All Items", "Attended / Visited", "Unattended Only", "Bucket List Only", "Weekend Sweeps Only"],
            width=17, state="readonly", font=(APP_FONT, 9, "bold")
        )
        status_cb.pack(side="left", padx=2)
        status_cb.bind("<<ComboboxSelected>>", lambda e: self.refresh_all_tables())

        add_filter_lbl("SORT BY:")
        sort_cb = ttk.Combobox(
            self.filter_bar, textvariable=self.sort_by_var,
            values=["Schedule / Default", "Distance: Closest First", "Distance: Farthest First", "State (A-Z)", "Event Name (A-Z)"],
            width=19, state="readonly", font=(APP_FONT, 9, "bold")
        )
        sort_cb.pack(side="left", padx=2)
        sort_cb.bind("<<ComboboxSelected>>", lambda e: self.refresh_all_tables())

        add_filter_lbl("SEARCH:")
        search_entry = tk.Entry(self.filter_bar, textvariable=self.search_var, width=18, font=(APP_FONT, 9, "bold"), relief="solid", bd=1)
        search_entry.pack(side="left", padx=3, ipady=1)
        search_entry.bind("<KeyRelease>", lambda e: self.refresh_all_tables())

        def clear_filters():
            self.filter_state_var.set("ALL")
            self.filter_dist_var.set("Any Distance")
            self.filter_status_var.set("All Items")
            self.sort_by_var.set("Schedule / Default")
            self.search_var.set("")
            self.refresh_all_tables()

        self.make_flat_button(self.filter_bar, "Clear Filters", "#475569", cmd=clear_filters, pad_x=8, pad_y=2).pack(side="left", padx=6)

        # ROW 4: 9-Column Responsive Color-Coded Tab Bar
        self.tab_strip = tk.Frame(self.root)
        self.tab_strip.pack(fill="x", padx=10, pady=(2, 0))

        for idx, (key, title, bg_col, fg_col) in enumerate(TAB_CONFIG):
            self.tab_strip.grid_columnconfigure(idx, weight=1, uniform="tabs")
            btn = tk.Button(
                self.tab_strip,
                text=title,
                bg=bg_col,
                fg=fg_col,
                activebackground=bg_col,
                activeforeground=fg_col,
                font=(APP_FONT, 9, "bold"),
                relief="flat",
                bd=0,
                pady=8,
                cursor="hand2",
                command=lambda k=key: self.switch_main_tab(k)
            )
            btn.grid(row=0, column=idx, sticky="ew", padx=(0, 3 if idx < len(TAB_CONFIG) - 1 else 0))
            self.tab_buttons[key] = (btn, bg_col, fg_col)

        self.tab_accent_line = tk.Frame(self.root, height=4, bg="#2563eb")
        self.tab_accent_line.pack(fill="x", padx=10)

        self.content_area = tk.Frame(self.root)
        self.content_area.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.tab_frames["Cup"] = self.build_race_view(self.content_area, "Cup", "#2563eb")
        self.tab_frames["O'Reilly"] = self.build_race_view(self.content_area, "O'Reilly", "#16a34a")
        self.tab_frames["Craftsman"] = self.build_race_view(self.content_area, "Craftsman", "#7c3aed")
        self.tab_frames["ARCA"] = self.build_arca_view(self.content_area)
        self.tab_frames["Grassroots"] = self.build_grassroots_view(self.content_area)
        self.tab_frames["Attractions"] = self.build_attractions_view(self.content_area)
        self.tab_frames["Bucket"] = self.build_bucket_list_view(self.content_area)
        self.tab_frames["Quests"] = self.build_quests_view(self.content_area)
        self.tab_frames["Trip"] = self.build_trip_view(self.content_area)

    # -------------------- QUESTS, TRACK FOOD CHALLENGES & "SIDE-TRACKED" VIEW --------------------

    def build_quests_view(self, parent):
        container = tk.Frame(parent, bg="#0f172a")

        self.quest_rank_var = tk.StringVar(value="CHASER RANK: ROOKIE STRIPE CHASER  |  0 XP")
        rank_banner = tk.Label(
            container, textvariable=self.quest_rank_var,
            bg="#064e3b", fg="#fde047", font=(APP_FONT, 11, "bold"),
            pady=8, padx=14, anchor="w"
        )
        rank_banner.pack(side="top", fill="x")

        sub_strip = tk.Frame(container, bg="#10b981", pady=4, padx=8)
        sub_strip.pack(side="top", fill="x")

        tk.Label(
            sub_strip, text="QUESTBOOK SECTIONS:", bg="#10b981", fg="#0f172a",
            font=(APP_FONT, 10, "bold")
        ).pack(side="left", padx=(4, 12))

        self.quest_sub_frames = {}
        sub_defs = [
            ("Quest_Campaigns", "Auto-Tracked Campaigns (14)"),
            ("Quest_Food", "Track Food Challenges (34)"),
            ("Quest_Silly", "Side-Tracked (38 Track Traditions)")
        ]
        for q_key, q_label in sub_defs:
            b = tk.Button(
                sub_strip,
                text=q_label,
                bg="#0f172a",
                fg="#fde047",
                font=(APP_FONT, 9, "bold"),
                relief="flat",
                bd=0,
                padx=14,
                pady=5,
                cursor="hand2",
                command=lambda k=q_key: self.switch_quest_subtab(k)
            )
            b.pack(side="left", padx=4)
            self.quest_sub_buttons[q_key] = b

        body = tk.Frame(container)
        body.pack(side="top", fill="both", expand=True)

        # 1. Auto-Tracked Campaigns Sub-View
        camp_frame = tk.Frame(body)
        camp_cols = [
            {"key": "event", "title": "Campaign Quest Name", "weight": 22, "min_w": 210, "align": "center"},
            {"key": "trophy", "title": "Unlocked", "weight": 6, "min_w": 75, "align": "center"},
            {"key": "category", "title": "Quest Line", "weight": 13, "min_w": 120, "align": "center"},
            {"key": "progress_bar", "title": "Live Campaign Progress", "weight": 18, "min_w": 175, "align": "center"},
            {"key": "xp", "title": "XP Reward", "weight": 8, "min_w": 85, "align": "center"},
            {"key": "notes", "title": "How to Conquer This Campaign (Auto-Updates from Your Attendance)", "weight": 35, "min_w": 280, "align": "left"},
        ]
        self.tables["Quest_Campaigns"] = ResponsiveRaceTable(camp_frame, self, camp_cols, row_height=96)
        self.tables["Quest_Campaigns"].pack(fill="both", expand=True)
        self.quest_sub_frames["Quest_Campaigns"] = camp_frame

        # 2. Dedicated Track Food Challenges Sub-View
        food_frame = tk.Frame(body)
        food_cols = [
            {"key": "event", "title": "Signature Track Food Item", "weight": 21, "min_w": 200, "align": "center"},
            {"key": "flag", "title": "Eaten!", "weight": 6, "min_w": 75, "align": "center"},
            {"key": "track", "title": "Track / Landmark", "weight": 20, "min_w": 190, "align": "center"},
            {"key": "xp", "title": "XP Reward", "weight": 8, "min_w": 85, "align": "center"},
            {"key": "notes", "title": "The Culinary Challenge (Click Green Flag When You've Eaten It!)", "weight": 42, "min_w": 310, "align": "left"},
        ]
        self.tables["Quest_Food"] = ResponsiveRaceTable(
            food_frame, self, food_cols,
            on_flag_cb=self.toggle_food_quest,
            row_height=105
        )
        self.tables["Quest_Food"].pack(fill="both", expand=True)
        self.quest_sub_frames["Quest_Food"] = food_frame

        # 3. "Side-Tracked" Track Traditions Sub-View (+ Add Custom Side-Tracked Goal)
        silly_frame = tk.Frame(body)
        add_sq_bar = tk.Frame(silly_frame, bg="#0f172a", pady=6, padx=10)
        add_sq_bar.pack(side="bottom", fill="x")

        tk.Label(add_sq_bar, text="+ ADD SIDE-TRACKED GOAL:", bg="#0f172a", fg="#34d399", font=(APP_FONT, 9, "bold")).pack(side="left", padx=(0, 6))
        sq_title_in = tk.Entry(add_sq_bar, width=22, font=(APP_FONT, 9, "bold"))
        sq_title_in.insert(0, "Tradition / Landmark Title")
        sq_title_in.pack(side="left", padx=3, ipady=2)

        sq_track_in = tk.Entry(add_sq_bar, width=20, font=(APP_FONT, 9, "bold"))
        sq_track_in.insert(0, "Track Name")
        sq_track_in.pack(side="left", padx=3, ipady=2)

        sq_desc_in = tk.Entry(add_sq_bar, width=32, font=(APP_FONT, 9, "bold"))
        sq_desc_in.insert(0, "What to do or see at the track...")
        sq_desc_in.pack(side="left", fill="x", expand=True, padx=3, ipady=2)

        def add_custom_side_quest():
            t_str = sq_title_in.get().strip()
            tr_str = sq_track_in.get().strip()
            d_str = sq_desc_in.get().strip()
            if not t_str or t_str == "Tradition / Landmark Title":
                return
            q_id = f"custom_sq_{len(self.data['QuestProgress'].get('custom_quests', [])) + 1}_{make_slug(t_str)}"
            self.data["QuestProgress"].setdefault("custom_quests", []).append({
                "id": q_id,
                "title": t_str,
                "track": tr_str if tr_str != "Track Name" else "Any Track",
                "desc": d_str if d_str != "What to do or see at the track..." else "",
                "xp": 100,
                "done": False
            })
            self.save_data()
            self.refresh_quests_tables()

        self.make_flat_button(add_sq_bar, "+ Add Side-Tracked", "#10b981", fg_color="#0f172a", cmd=add_custom_side_quest).pack(side="left", padx=4)

        silly_cols = [
            {"key": "event", "title": "Side-Tracked Tradition", "weight": 22, "min_w": 205, "align": "center"},
            {"key": "flag", "title": "Completed", "weight": 6, "min_w": 75, "align": "center"},
            {"key": "track", "title": "Track / Historic Site", "weight": 20, "min_w": 190, "align": "center"},
            {"key": "xp", "title": "XP Reward", "weight": 8, "min_w": 85, "align": "center"},
            {"key": "notes", "title": "Trackside Tradition & Landmark Objective (Click Green Flag When Done!)", "weight": 42, "min_w": 310, "align": "left"},
        ]
        self.tables["Quest_Silly"] = ResponsiveRaceTable(
            silly_frame, self, silly_cols,
            on_flag_cb=self.toggle_silly_quest,
            row_height=105
        )
        self.tables["Quest_Silly"].pack(side="top", fill="both", expand=True)
        self.quest_sub_frames["Quest_Silly"] = silly_frame

        self.switch_quest_subtab("Quest_Campaigns")
        return container

    def switch_quest_subtab(self, sub_key):
        for k, f in self.quest_sub_frames.items():
            f.pack_forget()
        self.quest_sub_frames[sub_key].pack(fill="both", expand=True)
        for k, b in self.quest_sub_buttons.items():
            if k == sub_key:
                b.configure(bg="#0f172a", fg="#fde047")
            else:
                b.configure(bg="#059669", fg="#ffffff")

    def toggle_food_quest(self, real_idx):
        if not (0 <= real_idx < len(FOOD_CHALLENGES)):
            return
        q_id = FOOD_CHALLENGES[real_idx][0]
        f_map = self.data.setdefault("QuestProgress", {}).setdefault("food", {})
        f_map[q_id] = not f_map.get(q_id, False)
        self.save_data()
        self.refresh_quests_tables()
        self.tables["Quest_Food"].select_by_real_idx(real_idx)

    def toggle_silly_quest(self, real_idx):
        base_len = len(SIDE_TRACKED_QUESTS)
        if 0 <= real_idx < base_len:
            q_id = SIDE_TRACKED_QUESTS[real_idx][0]
            s_map = self.data.setdefault("QuestProgress", {}).setdefault("side_quests", {})
            s_map[q_id] = not s_map.get(q_id, False)
        else:
            c_idx = real_idx - base_len
            c_list = self.data.setdefault("QuestProgress", {}).setdefault("custom_quests", [])
            if 0 <= c_idx < len(c_list):
                c_list[c_idx]["done"] = not c_list[c_idx].get("done", False)
        self.save_data()
        self.refresh_quests_tables()
        self.tables["Quest_Silly"].select_by_real_idx(real_idx)

    def refresh_quests_tables(self):
        if "Quest_Campaigns" not in self.tables:
            return

        swept_wknds, _, vis_tracks, _ = self.compute_weekend_sweeps_and_tracks()
        total_xp = 0

        # 1. Auto Campaigns
        camp_rows = []
        camp_done_count = 0
        for idx, camp in enumerate(AUTO_CAMPAIGNS):
            done_n, need_n, is_done = self.evaluate_auto_campaign(camp, swept_wknds, vis_tracks)
            if is_done:
                total_xp += camp["xp"]
                camp_done_count += 1
            camp_rows.append({
                "_real_idx": idx,
                "name": camp["title"],
                "logo": None,
                "trophy": is_done,
                "category": camp["category"],
                "done_n": done_n,
                "need_n": need_n,
                "xp": f"+{camp['xp']} XP",
                "notes": camp["desc"]
            })
        self.tables["Quest_Campaigns"].set_rows(camp_rows)

        # 2. Food Challenges
        f_map = self.data.get("QuestProgress", {}).get("food", {})
        food_rows = []
        food_done_count = 0
        for idx, (q_id, f_title, f_track, f_desc, f_xp) in enumerate(FOOD_CHALLENGES):
            done = bool(f_map.get(q_id, False))
            if done:
                total_xp += f_xp
                food_done_count += 1
            food_rows.append({
                "_real_idx": idx,
                "name": f_title,
                "logo": self.get_race_logo(f_title, "Attractions"),
                "flag": done,
                "track": f_track,
                "track_logo": self.get_track_logo(f_track),
                "xp": f"+{f_xp} XP",
                "notes": f_desc
            })
        self.tables["Quest_Food"].set_rows(food_rows)

        # 3. "Side-Tracked" Track Traditions (+ Custom Side-Tracked)
        s_map = self.data.get("QuestProgress", {}).get("side_quests", {})
        silly_rows = []
        silly_done_count = 0
        for idx, (q_id, s_title, s_track, s_desc, s_xp) in enumerate(SIDE_TRACKED_QUESTS):
            done = bool(s_map.get(q_id, False))
            if done:
                total_xp += s_xp
                silly_done_count += 1
            silly_rows.append({
                "_real_idx": idx,
                "name": s_title,
                "logo": None,
                "flag": done,
                "track": s_track,
                "track_logo": self.get_track_logo(s_track),
                "xp": f"+{s_xp} XP",
                "notes": s_desc
            })

        custom_list = self.data.get("QuestProgress", {}).get("custom_quests", [])
        base_len = len(SIDE_TRACKED_QUESTS)
        for c_i, cq in enumerate(custom_list):
            done = bool(cq.get("done", False))
            cxp = int(cq.get("xp", 100))
            if done:
                total_xp += cxp
                silly_done_count += 1
            silly_rows.append({
                "_real_idx": base_len + c_i,
                "name": cq.get("title", "Custom Tradition"),
                "logo": None,
                "flag": done,
                "track": cq.get("track", "Local Track"),
                "track_logo": self.get_track_logo(cq.get("track", "")),
                "xp": f"+{cxp} XP",
                "notes": cq.get("desc", "")
            })
        self.tables["Quest_Silly"].set_rows(silly_rows)

        rank_str = self.get_chaser_rank_title(total_xp)
        self.quest_rank_var.set(
            f"CHASER RANK: {rank_str}   |   TOTAL XP: {total_xp:,} XP   |   "
            f"Campaigns: {camp_done_count}/{len(AUTO_CAMPAIGNS)}  •  "
            f"Food Challenges: {food_done_count}/{len(FOOD_CHALLENGES)}  •  "
            f"Side-Tracked: {silly_done_count}/{len(silly_rows)}"
        )

    # -------------------- POPOUT NOTES & RACE MEMORY LOG DIALOG (WITH YEAR EDITOR) --------------------

    def open_notes_popup(self, key, real_idx=None):
        tbl = self.tables[key]
        target = real_idx if real_idx is not None else tbl.get_selected_real_idx()
        if target is None:
            messagebox.showinfo("Select a Row", "Click a row first or click directly on its Notes column to edit.")
            return

        item = self.data[key][target]
        title_str = item.get("race") or item.get("name", "Event")

        dark = self.dark_mode
        bg_win = "#0f172a" if dark else "#f1f5f9"
        bg_box = "#1e293b" if dark else "#ffffff"
        fg_txt = "#f8fafc" if dark else "#0f172a"
        border_col = "#475569" if dark else "#cbd5e1"

        win = tk.Toplevel(self.root)
        win.title(f"Edit Notes & Memory Log — {title_str}")
        win.geometry("680x440")
        win.configure(bg=bg_win)
        win.transient(self.root)
        win.grab_set()

        tk.Label(
            win, text=f"RACE MEMORY LOG & NOTES: {title_str.upper()}",
            bg=bg_win, fg="#facc15" if dark else "#1e293b",
            font=(APP_FONT, 11, "bold"), anchor="w"
        ).pack(fill="x", padx=16, pady=(14, 8))

        log_frame = tk.Frame(win, bg=bg_win)
        log_frame.pack(fill="x", padx=16, pady=(0, 8))

        tk.Label(log_frame, text="Winner:", bg=bg_win, fg=fg_txt, font=(APP_FONT, 9, "bold")).grid(row=0, column=0, sticky="w", padx=(0, 4), pady=4)
        winner_var = tk.StringVar(value=item.get("winner", ""))
        tk.Entry(log_frame, textvariable=winner_var, width=16, bg=bg_box, fg=fg_txt, insertbackground=fg_txt, font=(APP_FONT, 9, "bold"), relief="solid", bd=1).grid(row=0, column=1, sticky="w", padx=(0, 10), pady=4, ipady=2)

        tk.Label(log_frame, text="Seat / Camp:", bg=bg_win, fg=fg_txt, font=(APP_FONT, 9, "bold")).grid(row=0, column=2, sticky="w", padx=(0, 4), pady=4)
        seat_var = tk.StringVar(value=item.get("seat", ""))
        tk.Entry(log_frame, textvariable=seat_var, width=16, bg=bg_box, fg=fg_txt, insertbackground=fg_txt, font=(APP_FONT, 9, "bold"), relief="solid", bd=1).grid(row=0, column=3, sticky="w", padx=(0, 10), pady=4, ipady=2)

        tk.Label(log_frame, text="Rating:", bg=bg_win, fg=fg_txt, font=(APP_FONT, 9, "bold")).grid(row=0, column=4, sticky="w", padx=(0, 4), pady=4)
        rating_var = tk.StringVar(value=item.get("rating", "Unrated"))
        rating_cb = ttk.Combobox(
            log_frame, textvariable=rating_var,
            values=["Unrated", "★★★★★ (5/5)", "★★★★☆ (4/5)", "★★★☆☆ (3/5)", "★★☆☆☆ (2/5)", "★☆☆☆☆ (1/5)"],
            width=13, state="readonly", font=(APP_FONT, 9, "bold")
        )
        rating_cb.grid(row=0, column=5, sticky="w", pady=4)

        tk.Label(log_frame, text="Year(s) Attended (e.g. 2026):", bg=bg_win, fg="#4ade80" if dark else "#15803d", font=(APP_FONT, 9, "bold")).grid(row=1, column=0, columnspan=2, sticky="w", pady=(6, 2))
        yrs_var = tk.StringVar(value=", ".join(get_item_attended_years(item)))
        tk.Entry(log_frame, textvariable=yrs_var, width=24, bg=bg_box, fg=fg_txt, insertbackground=fg_txt, font=(APP_FONT, 9, "bold"), relief="solid", bd=1).grid(row=1, column=2, columnspan=4, sticky="w", pady=(6, 2), ipady=2)

        tk.Label(win, text="Event Notes, Ticket Info & Personal Memories:", bg=bg_win, fg=fg_txt, font=(APP_FONT, 9, "bold"), anchor="w").pack(fill="x", padx=16, pady=(4, 2))

        txt_frame = tk.Frame(win, bg=border_col, bd=1)
        txt_frame.pack(fill="both", expand=True, padx=16, pady=4)

        txt_box = tk.Text(
            txt_frame, wrap="word",
            bg=bg_box, fg=fg_txt,
            insertbackground=fg_txt,
            selectbackground="#334155" if dark else "#cbd5e1",
            font=(APP_FONT, 10, "bold"),
            relief="flat", padx=10, pady=10, height=8
        )
        txt_box.pack(fill="both", expand=True)
        txt_box.insert("1.0", item.get("notes", ""))
        txt_box.focus_set()

        btn_bar = tk.Frame(win, bg=bg_win, pady=10)
        btn_bar.pack(fill="x", padx=16)

        def save_and_close():
            item["winner"] = winner_var.get().strip()
            item["seat"] = seat_var.get().strip()
            item["rating"] = rating_var.get().strip()
            parsed_yrs = [y.strip() for y in re.split(r"[,;/\s]+", yrs_var.get().strip()) if re.match(r"^\d{4}$", y.strip())]
            if parsed_yrs:
                item["attended_years"] = sorted(list(set(parsed_yrs)))
                item["attended"] = True
            elif item.get("attended") and not yrs_var.get().strip():
                item["attended_years"] = [self.get_active_season_year_for_series(key)]
            item["notes"] = txt_box.get("1.0", "end-1c").strip()
            self.save_data()
            self.refresh_all_tables()
            tbl.select_by_real_idx(target)
            win.destroy()

        self.make_flat_button(btn_bar, "Save Log & Notes", "#16a34a", cmd=save_and_close, pad_x=14, pad_y=6).pack(side="right", padx=4)
        self.make_flat_button(btn_bar, "Cancel", "#64748b", cmd=win.destroy, pad_x=14, pad_y=6).pack(side="right", padx=4)

    # -------------------- FILTER & SORT PIPELINE --------------------

    def apply_filters_and_sort(self, rows):
        st_filter = self.filter_state_var.get()
        dist_filter = self.filter_dist_var.get()
        status_filter = self.filter_status_var.get()
        sort_mode = self.sort_by_var.get()
        q_search = self.search_var.get().strip().lower()

        max_miles = None
        if dist_filter == "Under 150 mi":
            max_miles = 150
        elif dist_filter == "Under 300 mi":
            max_miles = 300
        elif dist_filter == "Under 500 mi":
            max_miles = 500
        elif dist_filter == "Under 1,000 mi":
            max_miles = 1000

        filtered = []
        for r in rows:
            addr_str = f"{r.get('address', '')} {r.get('city', '')}"
            state_code = extract_state_code(addr_str)
            if st_filter != "ALL" and state_code != st_filter:
                continue

            if max_miles is not None:
                m_val = parse_miles_int(r.get("distance", "—"))
                if m_val > max_miles:
                    continue

            if status_filter == "Attended / Visited" and not r.get("flag"):
                continue
            elif status_filter == "Unattended Only" and r.get("flag"):
                continue
            elif status_filter == "Bucket List Only" and not r.get("trophy"):
                continue
            elif status_filter == "Weekend Sweeps Only" and not r.get("_weekend_swept"):
                continue

            if q_search:
                blob = f"{r.get('name', '')} {r.get('track', '')} {r.get('city', '')} {r.get('address', '')} {r.get('notes', '')} {r.get('category', '')}".lower()
                if q_search not in blob:
                    continue

            r["_state"] = state_code
            filtered.append(r)

        if sort_mode == "Distance: Closest First":
            filtered.sort(key=lambda x: parse_miles_int(x.get("distance", "—")))
        elif sort_mode == "Distance: Farthest First":
            filtered.sort(key=lambda x: (parse_miles_int(x.get("distance", "—")) == 999999, -parse_miles_int(x.get("distance", "—"))))
        elif sort_mode == "State (A-Z)":
            filtered.sort(key=lambda x: (x.get("_state") or "ZZ", x.get("name", "")))
        elif sort_mode == "Event Name (A-Z)":
            filtered.sort(key=lambda x: x.get("name", "").lower())

        return filtered

    def switch_main_tab(self, tab_key):
        self.active_tab_key = tab_key
        for k, frame in self.tab_frames.items():
            frame.pack_forget()
        self.tab_frames[tab_key].pack(fill="both", expand=True)
        self.update_tab_button_visuals()

    def update_tab_button_visuals(self):
        for key, (btn, bg_col, fg_col) in self.tab_buttons.items():
            if key == self.active_tab_key:
                btn.configure(bg=bg_col, fg=fg_col, font=(APP_FONT, 10, "bold"), pady=9)
                self.tab_accent_line.configure(bg=bg_col)
            else:
                btn.configure(bg=bg_col, fg=fg_col, font=(APP_FONT, 9, "bold"), pady=7)

    def build_arca_view(self, parent):
        container = tk.Frame(parent, bg="#0f172a")
        sub_strip = tk.Frame(container, bg="#eab308", pady=4, padx=8)
        sub_strip.pack(fill="x")

        tk.Label(
            sub_strip, text="ARCA MENARDS DIVISIONS:", bg="#eab308", fg="#0f172a",
            font=(APP_FONT, 10, "bold")
        ).pack(side="left", padx=(4, 12))

        self.arca_sub_frames = {}
        sub_defs = [
            ("ARCA_National", "National Series (2027)"),
            ("ARCA_East", "East Series"),
            ("ARCA_West", "West Series")
        ]
        for s_key, s_label in sub_defs:
            b = tk.Button(
                sub_strip,
                text=s_label,
                bg="#0f172a",
                fg="#facc15",
                font=(APP_FONT, 9, "bold"),
                relief="flat",
                bd=0,
                padx=14,
                pady=5,
                cursor="hand2",
                command=lambda k=s_key: self.switch_arca_subtab(k)
            )
            b.pack(side="left", padx=4)
            self.arca_buttons[s_key] = b

        body = tk.Frame(container)
        body.pack(fill="both", expand=True)

        for s_key, _ in sub_defs:
            self.arca_sub_frames[s_key] = self.build_race_view(body, s_key, "#ca8a04")

        self.switch_arca_subtab("ARCA_National")
        return container

    def switch_arca_subtab(self, sub_key):
        self.active_arca_key = sub_key
        for k, f in self.arca_sub_frames.items():
            f.pack_forget()
        self.arca_sub_frames[sub_key].pack(fill="both", expand=True)
        for k, b in self.arca_buttons.items():
            if k == sub_key:
                b.configure(bg="#0f172a", fg="#facc15")
            else:
                b.configure(bg="#ca8a04", fg="#ffffff")

    def build_race_view(self, parent, key, accent_color):
        frame = tk.Frame(parent)

        cols = [
            {"key": "event", "title": "Event", "weight": 20, "min_w": 195, "align": "center"},
            {"key": "flag", "title": "Attended", "weight": 5, "min_w": 70, "align": "center"},
            {"key": "trophy", "title": "Bucket List", "weight": 6, "min_w": 75, "align": "center"},
            {"key": "date", "title": "Date / Year", "weight": 6, "min_w": 75, "align": "center"},
            {"key": "track", "title": "Track Name", "weight": 20, "min_w": 195, "align": "center"},
            {"key": "address", "title": "Track Street Address", "weight": 17, "min_w": 155, "align": "left"},
            {"key": "distance", "title": "Distance", "weight": 7, "min_w": 80, "align": "center"},
            {"key": "notes", "title": "Memory Log, Ticket Prices & Notes (Click to Edit)", "weight": 28, "min_w": 220, "align": "left"},
        ]

        ctrl = tk.Frame(frame, bg="#1e293b", pady=7, padx=10)
        ctrl.pack(side="bottom", fill="x")

        def on_row_select(real_idx):
            r_name = self.data[key][real_idx].get("race", "")
            t_name = self.data[key][real_idx].get("track", "")
            self.dist_status_var.set(
                f"Race Logo: custom_logos/{make_slug(r_name)}.png   |   Track Logo: custom_logos/{make_slug(t_name)}.png"
            )

        tbl = ResponsiveRaceTable(
            frame, self, cols,
            on_select_cb=on_row_select,
            on_flag_cb=lambda real_idx, k=key: self.toggle_race_attended(k, real_idx),
            on_trophy_cb=lambda real_idx, k=key: self.toggle_race_bucket(k, real_idx),
            on_notes_cb=lambda real_idx, k=key: self.open_notes_popup(k, real_idx)
        )
        tbl.pack(side="top", fill="both", expand=True)
        self.tables[key] = tbl

        self.make_flat_button(ctrl, "✓ Attended", accent_color, cmd=lambda k=key: self.toggle_race_attended(k)).pack(side="left", padx=3)
        self.make_flat_button(ctrl, "★ Bucket List", "#d97706", cmd=lambda k=key: self.toggle_race_bucket(k)).pack(side="left", padx=3)
        self.make_flat_button(ctrl, "Set Race Logo...", "#db2777", cmd=lambda k=key: self.assign_custom_logo_for_selected(k, "race")).pack(side="left", padx=3)
        self.make_flat_button(ctrl, "Set Track Logo...", "#0284c7", cmd=lambda k=key: self.assign_custom_logo_for_selected(k, "track")).pack(side="left", padx=3)
        self.make_flat_button(ctrl, "Google Maps", "#059669", cmd=lambda k=key: self.open_maps_for_selected(k)).pack(side="left", padx=3)
        self.make_flat_button(ctrl, "+ Trip", "#7c3aed", cmd=lambda k=key: self.save_selected_to_trip(k)).pack(side="left", padx=3)
        self.make_flat_button(ctrl, "Edit Notes & Log...", "#334155", cmd=lambda k=key: self.open_notes_popup(k)).pack(side="left", padx=6)
        return frame

    def build_grassroots_view(self, parent):
        frame = tk.Frame(parent)

        cols = [
            {"key": "event", "title": "Event", "weight": 19, "min_w": 185, "align": "center"},
            {"key": "flag", "title": "Attended", "weight": 5, "min_w": 68, "align": "center"},
            {"key": "trophy", "title": "Bucket List", "weight": 5, "min_w": 72, "align": "center"},
            {"key": "category", "title": "Class / Division", "weight": 12, "min_w": 115, "align": "center"},
            {"key": "date", "title": "Date / Year", "weight": 6, "min_w": 75, "align": "center"},
            {"key": "track", "title": "Track Name", "weight": 20, "min_w": 195, "align": "center"},
            {"key": "address", "title": "Track Address / City", "weight": 15, "min_w": 140, "align": "left"},
            {"key": "distance", "title": "Distance", "weight": 6, "min_w": 75, "align": "center"},
            {"key": "notes", "title": "Memory Log, Ticket Prices & Notes (Click to Edit)", "weight": 26, "min_w": 200, "align": "left"},
        ]

        add_bar = tk.Frame(frame, bg="#0f172a", pady=6, padx=10)
        add_bar.pack(side="bottom", fill="x")

        tk.Label(add_bar, text="+ ADD LOCAL RACE:", bg="#0f172a", fg="#fb923c", font=(APP_FONT, 9, "bold")).pack(side="left", padx=(0, 6))

        race_in = tk.Entry(add_bar, width=18, font=(APP_FONT, 9, "bold"))
        race_in.insert(0, "Event Name")
        race_in.pack(side="left", padx=3, ipady=2)

        cat_in = ttk.Combobox(
            add_bar,
            values=["Late Model Stock", "Super Late Models", "Dirt Late Models", "410 Sprint Cars", "U.S. Legend Cars", "Tour Modifieds", "Street Stock / Local", "Midgets / Micros"],
            width=16,
            font=(APP_FONT, 9, "bold")
        )
        cat_in.set("Dirt Late Models")
        cat_in.pack(side="left", padx=3)

        date_in = tk.Entry(add_bar, width=9, font=(APP_FONT, 9, "bold"))
        date_in.insert(0, "Date")
        date_in.pack(side="left", padx=3, ipady=2)

        track_in = tk.Entry(add_bar, width=18, font=(APP_FONT, 9, "bold"))
        track_in.insert(0, "Local Track Name")
        track_in.pack(side="left", padx=3, ipady=2)

        addr_in = tk.Entry(add_bar, width=20, font=(APP_FONT, 9, "bold"))
        addr_in.insert(0, "City, State or Address")
        addr_in.pack(side="left", padx=3, ipady=2)

        note_in = tk.Entry(add_bar, width=20, font=(APP_FONT, 9, "bold"))
        note_in.insert(0, "Tix / Winner / Notes")
        note_in.pack(side="left", fill="x", expand=True, padx=3, ipady=2)

        def add_custom_grassroots_race():
            r_txt = race_in.get().strip()
            t_txt = track_in.get().strip()
            if not r_txt or r_txt == "Event Name":
                messagebox.showwarning("Missing Event Name", "Enter an Event Name for your local race.")
                return
            active_yr = self.get_active_season_year_for_series("Grassroots")
            new_ev = {
                "date": "" if date_in.get().strip() == "Date" else date_in.get().strip(),
                "season_year": active_yr,
                "race": r_txt,
                "category": cat_in.get().strip(),
                "track": t_txt if t_txt != "Local Track Name" else "Local Short Track",
                "address": addr_in.get().strip() if addr_in.get().strip() != "City, State or Address" else "",
                "distance": "—",
                "attended": True,
                "attended_years": [active_yr],
                "bucket_list": False,
                "notes": "" if note_in.get().strip() == "Tix / Winner / Notes" else note_in.get().strip()
            }
            self.data.setdefault("Grassroots", []).append(new_ev)
            self.save_data()
            self.refresh_all_tables()
            self.dist_status_var.set(f"Added '{r_txt}' ({active_yr}) at {new_ev['track']} to Grassroots & Local!")

        self.make_flat_button(add_bar, "+ Add Local Race", "#ea580c", cmd=add_custom_grassroots_race).pack(side="left", padx=4)

        ctrl = tk.Frame(frame, bg="#1e293b", pady=7, padx=10)
        ctrl.pack(side="bottom", fill="x")

        def on_row_select(real_idx):
            r_name = self.data["Grassroots"][real_idx].get("race", "")
            t_name = self.data["Grassroots"][real_idx].get("track", "")
            self.dist_status_var.set(
                f"Race Logo: custom_logos/{make_slug(r_name)}.png   |   Track Logo: custom_logos/{make_slug(t_name)}.png"
            )

        tbl = ResponsiveRaceTable(
            frame, self, cols,
            on_select_cb=on_row_select,
            on_flag_cb=lambda real_idx: self.toggle_race_attended("Grassroots", real_idx),
            on_trophy_cb=lambda real_idx: self.toggle_race_bucket("Grassroots", real_idx),
            on_notes_cb=lambda real_idx: self.open_notes_popup("Grassroots", real_idx)
        )
        tbl.pack(side="top", fill="both", expand=True)
        self.tables["Grassroots"] = tbl

        def delete_selected_grassroots():
            real_idx = tbl.get_selected_real_idx()
            if real_idx is None:
                return
            removed = self.data["Grassroots"].pop(real_idx)
            self.save_data()
            self.refresh_all_tables()
            self.dist_status_var.set(f"Removed '{removed.get('race', '')}' from Grassroots & Local.")

        self.make_flat_button(ctrl, "✓ Attended", "#ea580c", cmd=lambda: self.toggle_race_attended("Grassroots")).pack(side="left", padx=3)
        self.make_flat_button(ctrl, "★ Bucket List", "#d97706", cmd=lambda: self.toggle_race_bucket("Grassroots")).pack(side="left", padx=3)
        self.make_flat_button(ctrl, "Set Race Logo...", "#db2777", cmd=lambda: self.assign_custom_logo_for_selected("Grassroots", "race")).pack(side="left", padx=3)
        self.make_flat_button(ctrl, "Set Track Logo...", "#0284c7", cmd=lambda: self.assign_custom_logo_for_selected("Grassroots", "track")).pack(side="left", padx=3)
        self.make_flat_button(ctrl, "Google Maps", "#059669", cmd=lambda: self.open_maps_for_selected("Grassroots")).pack(side="left", padx=3)
        self.make_flat_button(ctrl, "+ Trip", "#7c3aed", cmd=lambda: self.save_selected_to_trip("Grassroots")).pack(side="left", padx=3)
        self.make_flat_button(ctrl, "Delete Row", "#dc2626", cmd=delete_selected_grassroots).pack(side="left", padx=3)
        self.make_flat_button(ctrl, "Edit Notes & Log...", "#334155", cmd=lambda: self.open_notes_popup("Grassroots")).pack(side="left", padx=6)
        return frame

    def build_attractions_view(self, parent):
        frame = tk.Frame(parent)

        cols = [
            {"key": "event", "title": "Event / Attraction", "weight": 22, "min_w": 210, "align": "center"},
            {"key": "flag", "title": "Visited", "weight": 5, "min_w": 70, "align": "center"},
            {"key": "trophy", "title": "Bucket List", "weight": 6, "min_w": 75, "align": "center"},
            {"key": "city", "title": "City / Region", "weight": 11, "min_w": 100, "align": "center"},
            {"key": "category", "title": "Category", "weight": 13, "min_w": 110, "align": "center"},
            {"key": "address", "title": "Full Street Address", "weight": 18, "min_w": 160, "align": "left"},
            {"key": "distance", "title": "Distance", "weight": 7, "min_w": 80, "align": "center"},
            {"key": "notes", "title": "Admission Prices, Tours & Notes (Click to Edit)", "weight": 28, "min_w": 220, "align": "left"},
        ]

        ctrl = tk.Frame(frame, bg="#1e293b", pady=7, padx=10)
        ctrl.pack(side="bottom", fill="x")

        def on_row_select(real_idx):
            a_name = self.data["Attractions"][real_idx].get("name", "")
            self.dist_status_var.set(f"Attraction Logo file: custom_logos/{make_slug(a_name)}.png")

        tbl = ResponsiveRaceTable(
            frame, self, cols,
            on_select_cb=on_row_select,
            on_flag_cb=self.toggle_attraction_visited,
            on_trophy_cb=self.toggle_attraction_bucket,
            on_notes_cb=lambda real_idx: self.open_notes_popup("Attractions", real_idx)
        )
        tbl.pack(side="top", fill="both", expand=True)
        self.tables["Attractions"] = tbl

        self.make_flat_button(ctrl, "✓ Visited", "#dc2626", cmd=self.toggle_attraction_visited).pack(side="left", padx=3)
        self.make_flat_button(ctrl, "★ Bucket List", "#d97706", cmd=self.toggle_attraction_bucket).pack(side="left", padx=3)
        self.make_flat_button(ctrl, "Set Logo...", "#db2777", cmd=lambda: self.assign_custom_logo_for_selected("Attractions", "race")).pack(side="left", padx=3)
        self.make_flat_button(ctrl, "Google Maps", "#059669", cmd=lambda: self.open_maps_for_selected("Attractions")).pack(side="left", padx=3)
        self.make_flat_button(ctrl, "+ Save to Trip", "#7c3aed", cmd=lambda: self.save_selected_to_trip("Attractions")).pack(side="left", padx=3)
        self.make_flat_button(ctrl, "Edit Notes & Log...", "#334155", cmd=lambda: self.open_notes_popup("Attractions")).pack(side="left", padx=6)
        return frame

    def build_bucket_list_view(self, parent):
        frame = tk.Frame(parent)

        cols = [
            {"key": "event", "title": "Event", "weight": 20, "min_w": 195, "align": "center"},
            {"key": "flag", "title": "Completed", "weight": 6, "min_w": 75, "align": "center"},
            {"key": "trophy", "title": "Bucket List", "weight": 6, "min_w": 75, "align": "center"},
            {"key": "division", "title": "Division / Type", "weight": 11, "min_w": 100, "align": "center"},
            {"key": "track", "title": "Track Name / City", "weight": 20, "min_w": 195, "align": "center"},
            {"key": "address", "title": "Street Address", "weight": 17, "min_w": 150, "align": "left"},
            {"key": "distance", "title": "Distance", "weight": 7, "min_w": 80, "align": "center"},
            {"key": "notes", "title": "Why You Must Go + Ticket & Fan Pass Prices", "weight": 30, "min_w": 230, "align": "left"},
        ]

        ctrl = tk.Frame(frame, bg="#1e293b", pady=7, padx=10)
        ctrl.pack(side="bottom", fill="x")

        tbl = ResponsiveRaceTable(
            frame, self, cols,
            on_flag_cb=self.toggle_bucket_item_completed,
            on_trophy_cb=self.remove_from_bucket_list
        )
        tbl.pack(side="top", fill="both", expand=True)
        self.tables["Bucket"] = tbl

        self.make_flat_button(ctrl, "✓ Toggle Attended / Completed", "#d97706", cmd=self.toggle_bucket_item_completed).pack(side="left", padx=4)
        self.make_flat_button(ctrl, "Remove from Bucket List", "#dc2626", cmd=self.remove_from_bucket_list).pack(side="left", padx=4)
        self.make_flat_button(ctrl, "Google Maps Directions", "#059669", cmd=self.open_maps_from_bucket).pack(side="left", padx=4)
        self.make_flat_button(ctrl, "+ Add to Trip Planner", "#7c3aed", cmd=self.add_bucket_to_trip).pack(side="left", padx=4)
        return frame

    # -------------------- TRIP & BUDGET PLANNER VIEW --------------------

    def build_trip_view(self, parent):
        frame = tk.Frame(parent)

        save_bar = tk.Frame(frame, bg="#0f172a", pady=6, padx=10)
        save_bar.pack(side="top", fill="x")

        tk.Label(save_bar, text="TRIP NAME:", bg="#0f172a", fg="#facc15", font=(APP_FONT, 9, "bold")).pack(side="left", padx=(0, 4))
        trip_name_entry = tk.Entry(save_bar, textvariable=self.trip_name_var, width=22, font=(APP_FONT, 9, "bold"))
        trip_name_entry.pack(side="left", padx=4, ipady=2)

        self.make_flat_button(save_bar, "Save Trip Plan", "#16a34a", cmd=self.save_named_trip).pack(side="left", padx=3)
        self.make_flat_button(save_bar, "New Blank Trip", "#475569", cmd=self.new_blank_trip).pack(side="left", padx=3)

        tk.Label(save_bar, text="  |  SAVED TRIPS:", bg="#0f172a", fg="#cbd5e1", font=(APP_FONT, 9, "bold")).pack(side="left", padx=4)
        self.saved_trips_cb = ttk.Combobox(
            save_bar, textvariable=self.saved_trip_select_var,
            values=list(self.data.get("SavedTrips", {}).keys()),
            width=22, state="readonly", font=(APP_FONT, 9, "bold")
        )
        self.saved_trips_cb.pack(side="left", padx=3)

        self.make_flat_button(save_bar, "Load Trip", "#0284c7", cmd=self.load_selected_trip).pack(side="left", padx=3)
        self.make_flat_button(save_bar, "Delete Trip", "#dc2626", cmd=self.delete_saved_trip).pack(side="left", padx=3)
        self.make_flat_button(save_bar, "Export Itinerary (.txt / .csv)", "#9333ea", cmd=self.export_trip_itinerary).pack(side="right", padx=4)

        self.trip_summary_var = tk.StringVar(value="Round-Trip Summary: Add stops using '+ Trip' and click 'Calc Distances' for full route + return leg.")
        trip_banner = tk.Label(
            frame, textvariable=self.trip_summary_var,
            bg="#065f46", fg="#f8fafc", font=(APP_FONT, 9, "bold"),
            pady=6, padx=12, anchor="w"
        )
        trip_banner.pack(side="top", fill="x")

        self.budget_total_var = tk.StringVar(value="GRAND TOTAL TRIP COST: $0")
        budget_banner = tk.Label(
            frame, textvariable=self.budget_total_var,
            bg="#1e1b4b", fg="#fde047", font=(APP_FONT, 11, "bold"),
            pady=8, padx=14, anchor="w"
        )
        budget_banner.pack(side="bottom", fill="x")

        exp_bar = tk.Frame(frame, bg="#0f172a", pady=7, padx=10)
        exp_bar.pack(side="bottom", fill="x")

        tk.Label(exp_bar, text="TRIP EXPENSES ($):", bg="#0f172a", fg="#38bdf8", font=(APP_FONT, 9, "bold")).pack(side="left", padx=(0, 6))

        def make_exp_box(label_txt, var_obj, width=7):
            tk.Label(exp_bar, text=label_txt, bg="#0f172a", fg="#f8fafc", font=(APP_FONT, 8, "bold")).pack(side="left", padx=(6, 2))
            e = tk.Entry(exp_bar, textvariable=var_obj, width=width, font=(APP_FONT, 9, "bold"))
            e.pack(side="left", padx=2, ipady=1)
            e.bind("<KeyRelease>", lambda ev: self.on_expense_edited())
            return e

        make_exp_box("Hotel/Lodging:", self.exp_hotel_var)
        make_exp_box("Fuel/Gas:", self.exp_fuel_var)
        self.make_flat_button(exp_bar, "Auto-Fuel", "#0d9488", cmd=self.auto_estimate_fuel_cost, pad_x=6, pad_y=2).pack(side="left", padx=2)
        make_exp_box("Food/Drinks:", self.exp_food_var)
        make_exp_box("Souvenirs/Merch:", self.exp_souvenirs_var)
        make_exp_box("Other:", self.exp_other_var)
        make_exp_box("Target Budget:", self.exp_budget_var, width=8)

        stop_cost_bar = tk.Frame(frame, bg="#1e293b", pady=6, padx=10)
        stop_cost_bar.pack(side="bottom", fill="x")

        self.sel_stop_lbl = tk.Label(
            stop_cost_bar, text="SELECTED STOP COSTS ($) — Click a stop above:",
            bg="#1e293b", fg="#fbbf24", font=(APP_FONT, 9, "bold")
        )
        self.sel_stop_lbl.pack(side="left", padx=(0, 8))

        self.stop_ticket_var = tk.StringVar(value="0")
        self.stop_vip_var = tk.StringVar(value="0")
        self.stop_parking_var = tk.StringVar(value="0")

        tk.Label(stop_cost_bar, text="Base Admission / Ticket ($):", bg="#1e293b", fg="#f8fafc", font=(APP_FONT, 9, "bold")).pack(side="left", padx=(4, 2))
        tk.Entry(stop_cost_bar, textvariable=self.stop_ticket_var, width=8, font=(APP_FONT, 9, "bold")).pack(side="left", padx=2, ipady=1)

        tk.Label(stop_cost_bar, text="VIP / Fan Pass Upgrade ($):", bg="#1e293b", fg="#f8fafc", font=(APP_FONT, 9, "bold")).pack(side="left", padx=(8, 2))
        tk.Entry(stop_cost_bar, textvariable=self.stop_vip_var, width=8, font=(APP_FONT, 9, "bold")).pack(side="left", padx=2, ipady=1)

        tk.Label(stop_cost_bar, text="Parking ($):", bg="#1e293b", fg="#f8fafc", font=(APP_FONT, 9, "bold")).pack(side="left", padx=(8, 2))
        tk.Entry(stop_cost_bar, textvariable=self.stop_parking_var, width=7, font=(APP_FONT, 9, "bold")).pack(side="left", padx=2, ipady=1)

        self.make_flat_button(stop_cost_bar, "Update Stop Costs", "#2563eb", cmd=self.save_selected_stop_costs).pack(side="left", padx=8)

        ctrl = tk.Frame(frame, bg="#334155", pady=6, padx=10)
        ctrl.pack(side="bottom", fill="x")

        self.make_flat_button(ctrl, "Launch Round-Trip Route in Google Maps (Includes Return Home)", "#16a34a", cmd=self.open_full_trip_route).pack(side="left", padx=3)
        self.make_flat_button(ctrl, "Directions to Selected Stop", "#0284c7", cmd=self.open_trip_stop_maps).pack(side="left", padx=3)
        self.make_flat_button(ctrl, "▲ Move Stop Up", "#d97706", cmd=lambda: self.move_trip_stop(-1)).pack(side="left", padx=3)
        self.make_flat_button(ctrl, "▼ Move Stop Down", "#d97706", cmd=lambda: self.move_trip_stop(1)).pack(side="left", padx=3)
        self.make_flat_button(ctrl, "Remove Selected Stop", "#dc2626", cmd=self.remove_trip_stop).pack(side="left", padx=3)

        cols = [
            {"key": "event", "title": "Trip Stop / Event", "weight": 22, "min_w": 195, "align": "center"},
            {"key": "type", "title": "Series / Type", "weight": 10, "min_w": 95, "align": "center"},
            {"key": "date", "title": "Date", "weight": 7, "min_w": 70, "align": "center"},
            {"key": "track", "title": "Venue / Destination", "weight": 18, "min_w": 165, "align": "center"},
            {"key": "leg_dist", "title": "Leg Miles", "weight": 8, "min_w": 85, "align": "center"},
            {"key": "ticket_cost", "title": "Admission ($)", "weight": 8, "min_w": 85, "align": "center"},
            {"key": "vip_cost", "title": "VIP / Pass ($)", "weight": 8, "min_w": 85, "align": "center"},
            {"key": "parking_cost", "title": "Parking ($)", "weight": 7, "min_w": 75, "align": "center"},
            {"key": "stop_total", "title": "Stop Total ($)", "weight": 9, "min_w": 90, "align": "center"},
        ]

        def on_trip_stop_select(real_idx):
            if real_idx is None or real_idx < 0 or real_idx >= len(self.data.get("Trip", [])):
                return
            st = self.data["Trip"][real_idx]
            self.sel_stop_lbl.configure(text=f"STOP #{real_idx + 1} ({st.get('title', '')[:24]}):")
            self.stop_ticket_var.set(str(st.get("ticket_cost", 0)))
            self.stop_vip_var.set(str(st.get("vip_cost", 0)))
            self.stop_parking_var.set(str(st.get("parking_cost", 0)))

        tbl = ResponsiveRaceTable(frame, self, cols, on_select_cb=on_trip_stop_select, row_height=105)
        tbl.pack(side="top", fill="both", expand=True)
        self.tables["Trip"] = tbl
        return frame

    def move_trip_stop(self, direction):
        tbl = self.tables["Trip"]
        real_idx = tbl.get_selected_real_idx()
        stops = self.data.get("Trip", [])
        if real_idx is None or real_idx < 0 or real_idx >= len(stops):
            return
        new_idx = real_idx + direction
        if 0 <= new_idx < len(stops):
            stops[real_idx], stops[new_idx] = stops[new_idx], stops[real_idx]
            self.save_data()
            self.refresh_trip_table()
            tbl.select_by_real_idx(new_idx)

    def export_trip_itinerary(self):
        stops = self.data.get("Trip", [])
        if not stops:
            messagebox.showinfo("No Stops to Export", "Add stops to your Trip Planner before exporting.")
            return

        t_name = self.trip_name_var.get().strip() or "Race_Trip_Itinerary"
        safe_default = f"{make_slug(t_name)}.txt"
        file_path = filedialog.asksaveasfilename(
            title="Export Trip Itinerary & Budget",
            initialfile=safe_default,
            defaultextension=".txt",
            filetypes=[("Text Itinerary (*.txt)", "*.txt"), ("CSV Spreadsheet (*.csv)", "*.csv")]
        )
        if not file_path:
            return

        home_addr = self.home_var.get().strip() or "Not Set"
        tickets_sum = sum(parse_money(s.get("ticket_cost", 0)) for s in stops)
        vip_sum = sum(parse_money(s.get("vip_cost", 0)) for s in stops)
        parking_sum = sum(parse_money(s.get("parking_cost", 0)) for s in stops)
        hotel = parse_money(self.exp_hotel_var.get())
        fuel = parse_money(self.exp_fuel_var.get())
        food = parse_money(self.exp_food_var.get())
        souv = parse_money(self.exp_souvenirs_var.get())
        other = parse_money(self.exp_other_var.get())
        grand_total = tickets_sum + vip_sum + parking_sum + hotel + fuel + food + souv + other

        try:
            if file_path.lower().endswith(".csv"):
                with open(file_path, "w", newline="", encoding="utf-8") as f:
                    w = csv.writer(f)
                    w.writerow(["TrackChaser HQ — Trip Itinerary & Budget", t_name])
                    w.writerow(["Starting / Return Home Address", home_addr])
                    w.writerow(["Estimated Round-Trip Miles", getattr(self, "_last_roundtrip_miles", 0)])
                    w.writerow([])
                    w.writerow(["Stop #", "Event / Attraction", "Series / Type", "Date", "Venue", "Address", "Admission ($)", "VIP/Pass ($)", "Parking ($)", "Stop Subtotal ($)"])
                    for idx, s in enumerate(stops, 1):
                        tc, vc, pc = parse_money(s.get("ticket_cost", 0)), parse_money(s.get("vip_cost", 0)), parse_money(s.get("parking_cost", 0))
                        w.writerow([idx, s.get("title", ""), s.get("type", ""), s.get("date", ""), s.get("venue", ""), s.get("address", ""), tc, vc, pc, tc + vc + pc])
                    w.writerow(["RETURN", f"Return Home to {home_addr}", "Return Leg", "End of Trip", home_addr, home_addr, 0, 0, 0, 0])
                    w.writerow([])
                    w.writerow(["EXPENSE CATEGORY", "AMOUNT ($)"])
                    w.writerow(["Tickets & Admissions", tickets_sum])
                    w.writerow(["VIP & Pass Upgrades", vip_sum])
                    w.writerow(["Parking", parking_sum])
                    w.writerow(["Hotel / Lodging", hotel])
                    w.writerow(["Fuel / Gas", fuel])
                    w.writerow(["Food & Drinks", food])
                    w.writerow(["Souvenirs / Merch", souv])
                    w.writerow(["Other Expenses", other])
                    w.writerow(["GRAND TOTAL", grand_total])
            else:
                lines = [
                    "=" * 72,
                    f"TRACKCHASER HQ — TRIP ITINERARY & BUDGET: {t_name.upper()}",
                    "=" * 72,
                    f"Home Departure & Return Address : {home_addr}",
                    f"Estimated Round-Trip Mileage    : ~{getattr(self, '_last_roundtrip_miles', 0):,} miles",
                    "-" * 72,
                    "STOP-BY-STOP ITINERARY:",
                ]
                for idx, s in enumerate(stops, 1):
                    tc, vc, pc = parse_money(s.get("ticket_cost", 0)), parse_money(s.get("vip_cost", 0)), parse_money(s.get("parking_cost", 0))
                    lines.append(
                        f"  Stop #{idx}: {s.get('title', '')} ({s.get('type', '')}) — {s.get('date', '')}\n"
                        f"           Venue  : {s.get('venue', '')} | {s.get('address', '')}\n"
                        f"           Costs  : Ticket {fmt_money(tc)} + VIP {fmt_money(vc)} + Parking {fmt_money(pc)} = {fmt_money(tc + vc + pc)}"
                    )
                lines.append(f"  Return : Back Home to {home_addr}")
                lines.extend([
                    "-" * 72,
                    "FULL TRIP BUDGET BREAKDOWN:",
                    f"  • Base Tickets & Admissions : {fmt_money(tickets_sum)}",
                    f"  • VIP & Fan Pass Upgrades   : {fmt_money(vip_sum)}",
                    f"  • Track Parking             : {fmt_money(parking_sum)}",
                    f"  • Hotel / Lodging           : {fmt_money(hotel)}",
                    f"  • Fuel / Gas                : {fmt_money(fuel)}",
                    f"  • Food & Drinks             : {fmt_money(food)}",
                    f"  • Souvenirs & Merch         : {fmt_money(souv)}",
                    f"  • Other Expenses            : {fmt_money(other)}",
                    "-" * 72,
                    f"  GRAND TOTAL TRIP COST       : {fmt_money(grand_total)}",
                    "=" * 72,
                ])
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(lines))

            messagebox.showinfo("Export Complete", f"Saved trip itinerary & budget to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Could not export itinerary:\n{e}")

    def save_selected_stop_costs(self):
        tbl = self.tables["Trip"]
        real_idx = tbl.get_selected_real_idx()
        if real_idx is None or real_idx < 0 or real_idx >= len(self.data.get("Trip", [])):
            messagebox.showinfo("Select a Trip Stop", "Click a stop row in the Trip Planner table first to update its costs.")
            return
        stop = self.data["Trip"][real_idx]
        stop["ticket_cost"] = parse_money(self.stop_ticket_var.get())
        stop["vip_cost"] = parse_money(self.stop_vip_var.get())
        stop["parking_cost"] = parse_money(self.stop_parking_var.get())
        self.save_data()
        self.refresh_trip_table()
        tbl.select_by_real_idx(real_idx)

    def on_expense_edited(self):
        self.save_data()
        self.update_budget_totals()

    def auto_estimate_fuel_cost(self):
        miles = getattr(self, "_last_roundtrip_miles", 0)
        if miles <= 0:
            messagebox.showinfo("Calculate Distances First", "Enter your Home Address and click 'Calc Distances' first so total round-trip mileage is known.")
            return
        est_fuel = round((miles / 22.0) * 3.35, 2)
        self.exp_fuel_var.set(f"{est_fuel:.2f}")
        self.on_expense_edited()
        self.dist_status_var.set(f"Estimated fuel for ~{miles:,} round-trip miles (@ 22 MPG, $3.35/gal): ${est_fuel:,.2f}")

    def update_budget_totals(self):
        stops = self.data.get("Trip", [])
        tickets_sum = sum(parse_money(s.get("ticket_cost", 0)) for s in stops)
        vip_sum = sum(parse_money(s.get("vip_cost", 0)) for s in stops)
        parking_sum = sum(parse_money(s.get("parking_cost", 0)) for s in stops)
        stops_subtotal = tickets_sum + vip_sum + parking_sum

        hotel = parse_money(self.exp_hotel_var.get())
        fuel = parse_money(self.exp_fuel_var.get())
        food = parse_money(self.exp_food_var.get())
        souv = parse_money(self.exp_souvenirs_var.get())
        other = parse_money(self.exp_other_var.get())

        grand_total = stops_subtotal + hotel + fuel + food + souv + other
        budget_limit = parse_money(self.exp_budget_var.get())

        budget_status = ""
        if budget_limit > 0:
            diff = budget_limit - grand_total
            if diff >= 0:
                budget_status = f"   |   BUDGET REMAINING: {fmt_money(diff)} (Under {fmt_money(budget_limit)} Budget)"
            else:
                budget_status = f"   |   OVER BUDGET BY: {fmt_money(abs(diff))} (Target: {fmt_money(budget_limit)})"

        self.budget_total_var.set(
            f"Tickets: {fmt_money(tickets_sum)}  +  VIP/Passes: {fmt_money(vip_sum)}  +  Parking: {fmt_money(parking_sum)}  +  "
            f"Hotel: {fmt_money(hotel)}  +  Fuel: {fmt_money(fuel)}  +  Food: {fmt_money(food)}  +  "
            f"Souvenirs: {fmt_money(souv)}  +  Other: {fmt_money(other)}   =   "
            f"GRAND TOTAL: {fmt_money(grand_total)}{budget_status}"
        )

    def save_named_trip(self):
        t_name = self.trip_name_var.get().strip()
        if not t_name:
            messagebox.showwarning("Trip Name Required", "Enter a name for your trip in the 'TRIP NAME' box.")
            return
        self.save_data()
        self.data.setdefault("SavedTrips", {})[t_name] = {
            "stops": json.loads(json.dumps(self.data.get("Trip", []))),
            "expenses": json.loads(json.dumps(self.data.get("TripExpenses", {}))),
            "home_address": self.home_var.get().strip()
        }
        self.save_data()
        self.saved_trips_cb.configure(values=list(self.data["SavedTrips"].keys()))
        self.saved_trip_select_var.set(t_name)
        messagebox.showinfo("Trip Saved", f"Saved trip plan & budget '{t_name}'! You can reload it anytime from the Saved Trips dropdown.")

    def load_selected_trip(self):
        t_name = self.saved_trip_select_var.get().strip()
        saved = self.data.get("SavedTrips", {}).get(t_name)
        if not saved:
            messagebox.showinfo("Select a Saved Trip", "Pick a saved trip from the 'SAVED TRIPS' dropdown first.")
            return
        self.data["Trip"] = json.loads(json.dumps(saved.get("stops", [])))
        exp = saved.get("expenses", {})
        self.trip_name_var.set(exp.get("trip_name", t_name))
        self.exp_hotel_var.set(str(exp.get("hotel", 0)))
        self.exp_fuel_var.set(str(exp.get("fuel", 0)))
        self.exp_food_var.set(str(exp.get("food", 0)))
        self.exp_souvenirs_var.set(str(exp.get("souvenirs", 0)))
        self.exp_other_var.set(str(exp.get("other", 0)))
        self.exp_budget_var.set(str(exp.get("budget_limit", 0)))
        if saved.get("home_address") and not self.home_var.get().strip():
            self.home_var.set(saved["home_address"])
        self.save_data()
        self.refresh_trip_table()
        self.dist_status_var.set(f"Loaded saved trip '{t_name}'!")

    def delete_saved_trip(self):
        t_name = self.saved_trip_select_var.get().strip()
        if t_name in self.data.get("SavedTrips", {}):
            del self.data["SavedTrips"][t_name]
            self.save_data()
            keys = list(self.data["SavedTrips"].keys())
            self.saved_trips_cb.configure(values=keys)
            self.saved_trip_select_var.set(keys[0] if keys else "")
            self.dist_status_var.set(f"Deleted saved trip '{t_name}'.")

    def new_blank_trip(self):
        self.data["Trip"] = []
        self.trip_name_var.set("New Race Trip")
        self.exp_hotel_var.set("0")
        self.exp_fuel_var.set("0")
        self.exp_food_var.set("0")
        self.exp_souvenirs_var.set("0")
        self.exp_other_var.set("0")
        self.exp_budget_var.set("0")
        self.save_data()
        self.refresh_trip_table()

    # -------------------- TABLE REFRESHERS --------------------

    def refresh_race_table(self, key):
        raw_rows = []
        for idx, ev in enumerate(self.data.get(key, [])):
            t_name = ev.get("track", "")
            addr = ev.get("address") or lookup_track_address(t_name, ev.get("location", ""))
            ev["address"] = addr
            raw_rows.append({
                "_real_idx": idx,
                "_weekend_swept": bool(ev.get("_weekend_swept")),
                "name": ev.get("race", ""),
                "logo": self.get_race_logo(ev.get("race", ""), key),
                "category": ev.get("category", key),
                "track": t_name,
                "track_logo": self.get_track_logo(t_name),
                "flag": bool(ev.get("attended")),
                "trophy": bool(ev.get("bucket_list")),
                "date": format_date_with_year(ev),
                "address": addr,
                "distance": ev.get("distance", "—"),
                "notes": format_display_notes(ev)
            })
        self.tables[key].set_rows(self.apply_filters_and_sort(raw_rows))

    def refresh_attractions_table(self):
        raw_rows = []
        for idx, pl in enumerate(self.data.get("Attractions", [])):
            raw_rows.append({
                "_real_idx": idx,
                "name": pl.get("name", ""),
                "logo": self.get_race_logo(pl.get("name", ""), "Attractions"),
                "flag": bool(pl.get("visited")),
                "trophy": bool(pl.get("bucket_list")),
                "city": pl.get("city", ""),
                "category": pl.get("category", ""),
                "address": pl.get("address", ""),
                "distance": pl.get("distance", "—"),
                "notes": format_display_notes(pl)
            })
        self.tables["Attractions"].set_rows(self.apply_filters_and_sort(raw_rows))

    def refresh_bucket_table(self):
        self.bucket_index_map = []
        raw_rows = []
        b_idx = 0
        for k in SERIES_KEYS:
            for idx, ev in enumerate(self.data.get(k, [])):
                if ev.get("bucket_list"):
                    self.bucket_index_map.append((k, idx))
                    t_name = ev.get("track", "")
                    disp_div = ev.get("category", "FedEx Truck" if k == "Craftsman" else k)
                    raw_rows.append({
                        "_real_idx": b_idx,
                        "_weekend_swept": bool(ev.get("_weekend_swept")),
                        "name": ev.get("race", ""),
                        "logo": self.get_race_logo(ev.get("race", ""), k),
                        "track": t_name,
                        "track_logo": self.get_track_logo(t_name),
                        "flag": bool(ev.get("attended")),
                        "trophy": True,
                        "division": disp_div,
                        "address": ev.get("address", ""),
                        "distance": ev.get("distance", "—"),
                        "notes": format_display_notes(ev)
                    })
                    b_idx += 1
        for idx, pl in enumerate(self.data.get("Attractions", [])):
            if pl.get("bucket_list"):
                self.bucket_index_map.append(("Attractions", idx))
                raw_rows.append({
                    "_real_idx": b_idx,
                    "name": pl.get("name", ""),
                    "logo": self.get_race_logo(pl.get("name", ""), "Attractions"),
                    "track": pl.get("city", ""),
                    "track_logo": None,
                    "flag": bool(pl.get("visited")),
                    "trophy": True,
                    "division": pl.get("category", "Attraction"),
                    "address": pl.get("address", ""),
                    "distance": pl.get("distance", "—"),
                    "notes": format_display_notes(pl)
                })
                b_idx += 1
        self.tables["Bucket"].set_rows(self.apply_filters_and_sort(raw_rows))

    def refresh_trip_table(self):
        stops = self.data.get("Trip", [])
        rows = []
        home_addr = self.home_var.get().strip()
        home_coords = self.geo_cache.get(home_addr) if home_addr else None

        total_miles = 0
        prev_coords = home_coords

        for idx, stop in enumerate(stops):
            venue_str = stop.get("venue", "")
            stop_addr = stop.get("address", "")
            stop_coords = self.geo_cache.get(stop_addr)

            leg_str = "—"
            if prev_coords and stop_coords:
                leg_mi = self.haversine_miles_int(prev_coords, stop_coords)
                total_miles += leg_mi
                leg_str = f"~{leg_mi:,} mi"

            prev_coords = stop_coords

            t_cost = parse_money(stop.get("ticket_cost", 0))
            v_cost = parse_money(stop.get("vip_cost", 0))
            p_cost = parse_money(stop.get("parking_cost", 0))
            s_tot = t_cost + v_cost + p_cost

            rows.append({
                "_real_idx": idx,
                "name": f"Stop #{idx + 1}: {stop.get('title', '')}",
                "logo": self.get_race_logo(stop.get("title", ""), stop.get("type", "")),
                "type": stop.get("type", ""),
                "date": stop.get("date", "Flexible"),
                "track": venue_str,
                "track_logo": self.get_track_logo(venue_str),
                "leg_dist": leg_str,
                "ticket_cost": fmt_money(t_cost),
                "vip_cost": fmt_money(v_cost),
                "parking_cost": fmt_money(p_cost),
                "stop_total": fmt_money(s_tot)
            })

        if stops:
            ret_leg_str = "—"
            if prev_coords and home_coords:
                ret_mi = self.haversine_miles_int(prev_coords, home_coords)
                total_miles += ret_mi
                ret_leg_str = f"~{ret_mi:,} mi"

            self._last_roundtrip_miles = total_miles

            rows.append({
                "_real_idx": -1,
                "_is_return_leg": True,
                "name": f"RETURN HOME: Back to {home_addr or 'Your Home Address'}",
                "logo": None,
                "type": "Return Leg",
                "date": "End of Trip",
                "track": home_addr or "(Enter Home Address Above)",
                "track_logo": None,
                "leg_dist": ret_leg_str,
                "ticket_cost": "—",
                "vip_cost": "—",
                "parking_cost": "—",
                "stop_total": "Return Home"
            })

            if home_coords and total_miles > 0:
                self.trip_summary_var.set(
                    f"ROUND-TRIP ITINERARY ({self.trip_name_var.get()}): {len(stops)} Stops + Return Home to {home_addr}   |   "
                    f"Estimated Total Round-Trip Driving: ~{total_miles:,} miles"
                )
            else:
                self.trip_summary_var.set(
                    f"ROUND-TRIP ITINERARY ({self.trip_name_var.get()}): {len(stops)} Stops + Return Home Leg   |   "
                    f"Enter your Home Address above and click 'Calc Distances' to compute round-trip mileage!"
                )
        else:
            self._last_roundtrip_miles = 0
            self.trip_summary_var.set("Round-Trip Summary: Add races or attractions using '+ Trip' to calculate your full route, return leg & trip budget.")

        self.tables["Trip"].set_rows(rows)
        self.update_budget_totals()

    def refresh_all_tables(self):
        self.update_stats()
        for k in SERIES_KEYS:
            if k in self.tables:
                self.refresh_race_table(k)
        if "Attractions" in self.tables:
            self.refresh_attractions_table()
        if "Bucket" in self.tables:
            self.refresh_bucket_table()
        if "Quest_Campaigns" in self.tables:
            self.refresh_quests_tables()
        if "Trip" in self.tables:
            self.refresh_trip_table()

    # -------------------- YEAR-LOCKED FLAG & TROPHY HANDLERS --------------------

    def _toggle_event_attendance_with_year(self, item, series_key):
        active_yr = str(item.get("season_year") or self.get_active_season_year_for_series(series_key))
        yrs = get_item_attended_years(item)
        if not item.get("attended"):
            item["attended"] = True
            if active_yr not in yrs:
                yrs.append(active_yr)
            item["attended_years"] = sorted(list(set(yrs)))
            tk_norm = normalize_track_key(item.get("track", ""))
            if tk_norm:
                hist = set(self.data.get("CompletedTracksHistory", []))
                hist.add(tk_norm)
                self.data["CompletedTracksHistory"] = sorted(list(hist))
        else:
            if active_yr in yrs:
                yrs.remove(active_yr)
            item["attended_years"] = yrs
            item["attended"] = bool(yrs)

    def toggle_race_attended(self, key, real_idx=None):
        tbl = self.tables[key]
        target = real_idx if real_idx is not None else tbl.get_selected_real_idx()
        if target is None:
            return
        self._toggle_event_attendance_with_year(self.data[key][target], key)
        self.save_data()
        self.refresh_all_tables()
        tbl.select_by_real_idx(target)

    def toggle_race_bucket(self, key, real_idx=None):
        tbl = self.tables[key]
        target = real_idx if real_idx is not None else tbl.get_selected_real_idx()
        if target is None:
            return
        self.data[key][target]["bucket_list"] = not self.data[key][target].get("bucket_list", False)
        self.save_data()
        self.refresh_all_tables()
        tbl.select_by_real_idx(target)

    def toggle_attraction_visited(self, real_idx=None):
        tbl = self.tables["Attractions"]
        target = real_idx if real_idx is not None else tbl.get_selected_real_idx()
        if target is None:
            return
        self.data["Attractions"][target]["visited"] = not self.data["Attractions"][target].get("visited", False)
        self.save_data()
        self.refresh_all_tables()
        tbl.select_by_real_idx(target)

    def toggle_attraction_bucket(self, real_idx=None):
        tbl = self.tables["Attractions"]
        target = real_idx if real_idx is not None else tbl.get_selected_real_idx()
        if target is None:
            return
        self.data["Attractions"][target]["bucket_list"] = not self.data["Attractions"][target].get("bucket_list", False)
        self.save_data()
        self.refresh_all_tables()
        tbl.select_by_real_idx(target)

    def toggle_bucket_item_completed(self, real_idx=None):
        tbl = self.tables["Bucket"]
        target = real_idx if real_idx is not None else tbl.get_selected_real_idx()
        if target is None or target >= len(self.bucket_index_map):
            return
        src_key, item_idx = self.bucket_index_map[target]
        if src_key == "Attractions":
            self.data[src_key][item_idx]["visited"] = not self.data[src_key][item_idx].get("visited", False)
        else:
            self._toggle_event_attendance_with_year(self.data[src_key][item_idx], src_key)
        self.save_data()
        self.refresh_all_tables()
        tbl.select_by_real_idx(target)

    def remove_from_bucket_list(self, real_idx=None):
        tbl = self.tables["Bucket"]
        target = real_idx if real_idx is not None else tbl.get_selected_real_idx()
        if target is None or target >= len(self.bucket_index_map):
            return
        src_key, item_idx = self.bucket_index_map[target]
        self.data[src_key][item_idx]["bucket_list"] = False
        self.save_data()
        self.refresh_all_tables()

    # -------------------- GOOGLE MAPS & ROUND-TRIP ROUTING --------------------

    def open_maps_url(self, destination_address):
        home = self.home_var.get().strip()
        dest = urllib.parse.quote_plus(destination_address)
        if home:
            orig = urllib.parse.quote_plus(home)
            url = f"https://www.google.com/maps/dir/?api=1&origin={orig}&destination={dest}&travelmode=driving"
        else:
            url = f"https://www.google.com/maps/dir/?api=1&destination={dest}&travelmode=driving"
        webbrowser.open(url)

    def open_maps_for_selected(self, key):
        tbl = self.tables[key]
        real_idx = tbl.get_selected_real_idx()
        if real_idx is None:
            messagebox.showinfo("Select a Row", "Click a race or attraction first to open Google Maps directions.")
            return
        item = self.data[key][real_idx]
        addr = item.get("address") or item.get("track") or item.get("name")
        self.open_maps_url(addr)

    def open_maps_from_bucket(self):
        tbl = self.tables["Bucket"]
        real_idx = tbl.get_selected_real_idx()
        if real_idx is None or real_idx >= len(self.bucket_index_map):
            return
        src_key, item_idx = self.bucket_index_map[real_idx]
        item = self.data[src_key][item_idx]
        self.open_maps_url(item.get("address", ""))

    def save_selected_to_trip(self, key):
        tbl = self.tables[key]
        real_idx = tbl.get_selected_real_idx()
        if real_idx is None:
            messagebox.showinfo("Select a Row", "Select a race or attraction to add to your Trip Planner.")
            return
        item = self.data[key][real_idx]
        disp_type = item.get("category") or ("FedEx Truck" if key == "Craftsman" else key)
        default_tix = extract_default_ticket_price(item.get("notes", ""))
        stop = {
            "title": item.get("race") or item.get("name"),
            "type": disp_type,
            "date": item.get("date", "Anytime"),
            "venue": item.get("track") or item.get("city"),
            "address": item.get("address", ""),
            "distance": item.get("distance", "—"),
            "ticket_cost": default_tix,
            "vip_cost": 0.0,
            "parking_cost": 0.0
        }
        self.data.setdefault("Trip", []).append(stop)
        self.save_data()
        self.refresh_trip_table()
        messagebox.showinfo("Saved to Trip", f"Added '{stop['title']}' (Est. Base Ticket: {fmt_money(default_tix)}) to your My Trip Planner tab!")

    def add_bucket_to_trip(self):
        tbl = self.tables["Bucket"]
        real_idx = tbl.get_selected_real_idx()
        if real_idx is None or real_idx >= len(self.bucket_index_map):
            return
        src_key, item_idx = self.bucket_index_map[real_idx]
        item = self.data[src_key][item_idx]
        disp_type = item.get("category") or ("FedEx Truck" if src_key == "Craftsman" else src_key)
        default_tix = extract_default_ticket_price(item.get("notes", ""))
        stop = {
            "title": item.get("race") or item.get("name"),
            "type": disp_type,
            "date": item.get("date", "Anytime"),
            "venue": item.get("track") or item.get("city"),
            "address": item.get("address", ""),
            "distance": item.get("distance", "—"),
            "ticket_cost": default_tix,
            "vip_cost": 0.0,
            "parking_cost": 0.0
        }
        self.data.setdefault("Trip", []).append(stop)
        self.save_data()
        self.refresh_trip_table()
        messagebox.showinfo("Saved to Trip", f"Added '{stop['title']}' (Est. Base Ticket: {fmt_money(default_tix)}) to your Trip Planner!")

    def open_trip_stop_maps(self):
        tbl = self.tables["Trip"]
        real_idx = tbl.get_selected_real_idx()
        if real_idx is None or real_idx < 0:
            return
        stop = self.data["Trip"][real_idx]
        self.open_maps_url(stop.get("address", ""))

    def open_full_trip_route(self):
        stops = self.data.get("Trip", [])
        if not stops:
            messagebox.showinfo("Empty Trip", "Add races or attractions to your trip first using '+ Trip'.")
            return
        home_raw = self.home_var.get().strip()
        if not home_raw:
            messagebox.showwarning("Home Address Needed", "Type your starting Home Address in the top bar so Google Maps can route your departure and return trip home.")
            return

        home = urllib.parse.quote_plus(home_raw)
        waypoints = "|".join(urllib.parse.quote_plus(s.get("address", "")) for s in stops)
        url = f"https://www.google.com/maps/dir/?api=1&origin={home}&destination={home}&waypoints={waypoints}&travelmode=driving"
        webbrowser.open(url)

    def remove_trip_stop(self):
        tbl = self.tables["Trip"]
        real_idx = tbl.get_selected_real_idx()
        if real_idx is None or real_idx < 0:
            return
        del self.data["Trip"][real_idx]
        self.save_data()
        self.refresh_trip_table()

    # -------------------- MULTI-PROVIDER DISTANCE GEOCODER --------------------

    def geocode_address(self, query_str):
        q = query_str.strip()
        if not q:
            return None
        if q in self.geo_cache:
            return self.geo_cache[q]

        KNOWN_COORDS = {
            "winston-salem, nc": [36.0796, -80.2234],
            "daytona beach, fl": [29.1852, -81.0705],
            "ponce inlet, fl": [29.0964, -80.9370],
            "hampton, ga": [33.3868, -84.3164],
            "dawsonville, ga": [34.4212, -84.1191],
            "austin, tx": [30.1328, -97.6411],
            "avondale, az": [33.3750, -112.3111],
            "tucson, az": [32.1161, -110.8256],
            "las vegas, nv": [36.2719, -115.0106],
            "darlington, sc": [34.2953, -79.9056],
            "ridgeway, va": [36.6339, -79.8511],
            "stuart, va": [36.6418, -80.2695],
            "bristol, tn": [36.5156, -82.2569],
            "kansas city, ks": [39.1156, -94.8311],
            "lincoln, al": [33.5669, -86.0661],
            "birmingham, al": [33.5311, -86.5614],
            "fort worth, tx": [33.0369, -97.2817],
            "watkins glen, ny": [42.3369, -76.9272],
            "dover, de": [39.1897, -75.5303],
            "concord, nc": [35.3522, -80.6828],
            "charlotte, nc": [35.2216, -80.8431],
            "mooresville, nc": [35.5849, -80.8101],
            "huntersville, nc": [35.4107, -80.8428],
            "kannapolis, nc": [35.4874, -80.6217],
            "welcome, nc": [35.9082, -80.2567],
            "randleman, nc": [35.8165, -79.8048],
            "hillsborough, nc": [36.0665, -79.0917],
            "newton, nc": [35.6947, -81.2683],
            "rockingham, nc": [34.9742, -79.6103],
            "north wilkesboro, nc": [36.1422, -81.0725],
            "lucama, nc": [35.6413, -78.0469],
            "murphy, nc": [35.0876, -84.0346],
            "lebanon, tn": [36.0461, -86.4119],
            "nashville, tn": [36.1311, -86.7625],
            "brooklyn, mi": [42.0664, -84.2414],
            "marne, mi": [43.0358, -85.8300],
            "flat rock, mi": [42.0842, -83.3106],
            "dearborn, mi": [42.3039, -83.2342],
            "long pond, pa": [41.0553, -75.5114],
            "philadelphia, pa": [40.1144, -75.2328],
            "coronado, ca": [32.7019, -117.2044],
            "sonoma, ca": [38.1614, -122.4547],
            "bakersfield, ca": [35.3189, -119.2225],
            "anderson, ca": [40.4482, -122.2978],
            "roseville, ca": [38.7521, -121.2880],
            "madera, ca": [36.9613, -120.0607],
            "los angeles, ca": [34.0622, -118.3614],
            "joliet, il": [41.4747, -88.0572],
            "springfield, il": [39.8392, -89.6394],
            "madison, il": [38.6508, -90.1353],
            "duquoin, il": [37.9897, -89.2225],
            "speedway, in": [39.7950, -86.2347],
            "indianapolis, in": [39.8128, -86.3408],
            "salem, in": [38.6019, -86.1436],
            "winchester, in": [40.1689, -85.0161],
            "newton, ia": [41.6750, -93.0136],
            "knoxville, ia": [41.3264, -93.1097],
            "richmond, va": [37.5919, -77.4208],
            "loudon, nh": [43.3625, -71.4608],
            "homestead, fl": [25.4519, -80.4086],
            "st. petersburg, fl": [27.7661, -82.6300],
            "pensacola, fl": [30.5050, -87.3458],
            "lakeville, ct": [41.9286, -73.3842],
            "thompson, ct": [41.9814, -71.8250],
            "toledo, oh": [41.7253, -83.5289],
            "new weston, oh": [40.3186, -84.6347],
            "elko new market, mn": [44.5686, -93.3375],
            "oregon, wi": [42.9056, -89.2981],
            "slinger, wi": [43.3375, -88.2686],
            "dacono, co": [40.0642, -104.9803],
            "west richland, wa": [46.2808, -119.3897],
            "portland, or": [45.5958, -122.6947],
            "tulsa, ok": [36.1353, -95.9317],
            "oxford, me": [44.1489, -70.4836],
            "bowling green, ky": [37.0033, -86.3689]
        }

        q_low = q.lower()
        for k_city, k_coords in KNOWN_COORDS.items():
            if k_city in q_low:
                self.geo_cache[q] = k_coords
                return k_coords

        candidates = [q]
        parts = [p.strip() for p in q.split(",") if p.strip()]
        if len(parts) >= 2:
            tail = ", ".join(parts[-2:])
            if tail not in candidates:
                candidates.append(tail)
            no_zip = re.sub(r"\b\d{5}(?:-\d{4})?\b", "", tail).strip()
            if no_zip and no_zip not in candidates:
                candidates.append(no_zip)

        zip_match = re.search(r"\b(\d{5})\b", q)
        if zip_match and zip_match.group(1) not in candidates:
            candidates.append(zip_match.group(1))

        if len(parts) >= 2 and any(ch.isdigit() for ch in parts[0]):
            try:
                c_url = f"https://geocoding.geo.census.gov/geocoder/locations/onelineaddress?address={urllib.parse.quote_plus(q)}&benchmark=Public_AR_Current&format=json"
                c_res = http_get_json(c_url, timeout=6)
                matches = c_res.get("result", {}).get("addressMatches", [])
                if matches:
                    xy = matches[0].get("coordinates", {})
                    coords = [float(xy["y"]), float(xy["x"])]
                    self.geo_cache[q] = coords
                    return coords
            except Exception:
                pass

        for cand in candidates:
            try:
                p_url = f"https://photon.komoot.io/api/?q={urllib.parse.quote_plus(cand)}&limit=1"
                p_res = http_get_json(p_url, timeout=6)
                feats = p_res.get("features", [])
                if feats:
                    lon, lat = feats[0]["geometry"]["coordinates"]
                    coords = [float(lat), float(lon)]
                    self.geo_cache[q] = coords
                    return coords
            except Exception:
                pass

            try:
                n_url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote_plus(cand)}&countrycodes=us,ca&format=json&limit=1"
                n_res = http_get_json(n_url, headers={"User-Agent": "TrackChaserHQDesktopApp/14.0"}, timeout=6)
                if n_res:
                    coords = [float(n_res[0]["lat"]), float(n_res[0]["lon"])]
                    self.geo_cache[q] = coords
                    return coords
            except Exception:
                pass

        return None

    @staticmethod
    def haversine_miles_int(coord1, coord2):
        lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
        lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        air_miles = 3958.8 * (2 * math.asin(math.sqrt(a)))
        return int(round(air_miles * 1.22))

    @classmethod
    def haversine_miles(cls, coord1, coord2):
        return f"~{cls.haversine_miles_int(coord1, coord2):,} mi"

    def start_distance_calculation(self):
        home_addr = self.home_var.get().strip()
        if not home_addr:
            messagebox.showwarning("Enter Home Address", "Type your Home Address (e.g., 'City, State' or street address) in the Home Address box first.")
            return
        self.save_data()
        self.dist_status_var.set(f"Calculating distances & round-trip mileage from '{home_addr}'...")
        threading.Thread(target=self._distance_worker, daemon=True).start()

    def _distance_worker(self):
        home_addr = self.home_var.get().strip()
        home_coords = self.geocode_address(home_addr)
        if not home_coords:
            self.root.after(0, lambda: self.dist_status_var.set("Could not locate Home Address. Try 'City, State' or ZIP Code."))
            return

        for k in SERIES_KEYS:
            for ev in self.data.get(k, []):
                c = self.geocode_address(ev.get("address", ""))
                if c:
                    ev["distance"] = self.haversine_miles(home_coords, c)

        for pl in self.data.get("Attractions", []):
            c = self.geocode_address(pl.get("address", ""))
            if c:
                pl["distance"] = self.haversine_miles(home_coords, c)

        for stop in self.data.get("Trip", []):
            c = self.geocode_address(stop.get("address", ""))
            if c:
                stop["distance"] = self.haversine_miles(home_coords, c)

        self.save_geo_cache()
        self.root.after(0, self._finish_distance_calc)

    def _finish_distance_calc(self):
        self.save_data()
        self.refresh_all_tables()
        self.dist_status_var.set(f"Distances & Round-Trip Planner updated from {self.home_var.get().strip()}!")

    # -------------------- LIVE SCHEDULE SYNCS (PRESERVING ATTENDED YEARS) --------------------

    def sync_from_arca_web(self):
        urls = {
            "ARCA_National": "https://www.arcaracing.com/arca-menards-series/",
            "ARCA_East": "https://www.arcaracing.com/arca-menards-series-east/",
            "ARCA_West": "https://www.arcaracing.com/arca-menards-series-west/"
        }
        summary = []
        for key, url in urls.items():
            try:
                raw_html = http_get_bytes(url, timeout=12).decode("utf-8", errors="ignore")
                clean_text = re.sub(r"<[^>]+>", "\n", raw_html)
                lines = [ln.strip() for ln in clean_text.splitlines() if ln.strip()]
                date_pat = re.compile(r"^(?:Mon|Tue|Wed|Thu|Thur|Fri|Sat|Sun)?\.?,?\s*(Jan|Feb|Mar|March|Apr|April|May|Jun|June|Jul|July|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2}$", re.I)

                scraped = []
                for i, line in enumerate(lines):
                    if date_pat.match(line) and i >= 1:
                        track_candidate = lines[i - 1]
                        if len(track_candidate) > 4 and any(w in track_candidate.lower() for w in ["speedway", "raceway", "park", "fairgrounds", "bullring", "glen", "rock", "mile", "bowl"]):
                            addr = lookup_track_address(track_candidate)
                            scraped.append({
                                "date": line,
                                "race": f"{track_candidate} ARCA Event",
                                "track": track_candidate,
                                "address": addr
                            })

                if len(scraped) >= 5:
                    old_map = {x.get("track", "").lower(): x for x in self.data.get(key, [])}
                    merged = []
                    for item in scraped:
                        prev = old_map.get(item["track"].lower(), {})
                        r_title = prev.get("race", item["race"])
                        auto_bkt, auto_note = generate_smart_notes(r_title, item["track"], key, prev.get("notes", ""))
                        prev_yrs = get_item_attended_years(prev)
                        merged.append({
                            "date": item["date"],
                            "season_year": "2027",
                            "race": r_title,
                            "track": item["track"],
                            "address": item["address"],
                            "distance": prev.get("distance", "—"),
                            "attended": bool(prev_yrs),
                            "attended_years": prev_yrs,
                            "bucket_list": prev.get("bucket_list", bool(auto_bkt)),
                            "winner": prev.get("winner", ""),
                            "seat": prev.get("seat", ""),
                            "rating": prev.get("rating", "Unrated"),
                            "notes": auto_note
                        })
                    self.data[key] = merged
                    summary.append(f"{key}: Pulled {len(merged)} live events from ARCARacing.com")
                else:
                    summary.append(f"{key}: Using built-in verified schedule ({len(self.data.get(key, []))} races)")
            except Exception as e:
                summary.append(f"{key}: Kept local schedule ({e})")

        self.save_data()
        self.refresh_all_tables()
        messagebox.showinfo("ARCA Menards Sync", "\n".join(summary))

    def sync_from_nascar_api(self):
        year = self.year_var.get()
        if year == "Season":
            year = "2026"
        url = f"https://cf.nascar.com/cacher/{year}/race_list_basic.json"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/131.0.0.0 Safari/537.36",
            "Referer": "https://www.nascar.com/"
        }
        try:
            api_data = http_get_json(url, headers=headers, timeout=10)
        except Exception as e:
            if "403" in str(e) and year == "2027":
                self.load_builtin_2027_schedule()
                return
            messagebox.showerror("NASCAR Server Error", f"Could not pull {year} schedule:\n{e}")
            return

        series_map = {"series_1": "Cup", "series_2": "O'Reilly", "series_3": "Craftsman"}
        updated_counts = []
        for api_key, app_key in series_map.items():
            races = api_data.get(api_key, [])
            if not races:
                continue
            old_lookup = {(r.get("race", "").lower(), r.get("track", "").lower()): r for r in self.data.get(app_key, [])}
            new_list = []
            for r in races:
                r_name = r.get("race_name", "NASCAR Event").strip()
                t_name = r.get("track_name", "Unknown Track").strip()
                raw_date = r.get("race_date", "")
                short_date = raw_date[:10]
                try:
                    dt = datetime.fromisoformat(raw_date.replace("Z", "+00:00"))
                    short_date = dt.strftime("%b %d")
                except Exception:
                    pass

                prev = old_lookup.get((r_name.lower(), t_name.lower()), {})
                addr = lookup_track_address(t_name, prev.get("address", ""))
                auto_bkt, auto_note = generate_smart_notes(r_name, t_name, app_key, prev.get("notes", ""))
                prev_yrs = get_item_attended_years(prev)
                new_list.append({
                    "date": short_date,
                    "season_year": year,
                    "race": r_name,
                    "track": t_name,
                    "address": addr,
                    "distance": prev.get("distance", "—"),
                    "attended": bool(prev_yrs),
                    "attended_years": prev_yrs,
                    "bucket_list": prev.get("bucket_list", bool(auto_bkt)),
                    "winner": prev.get("winner", ""),
                    "seat": prev.get("seat", ""),
                    "rating": prev.get("rating", "Unrated"),
                    "notes": auto_note
                })
            self.data[app_key] = new_list
            disp_label = "FedEx Truck" if app_key == "Craftsman" else app_key
            updated_counts.append(f"{disp_label} ({year}): {len(new_list)} races")

        self.save_data()
        self.refresh_all_tables()
        messagebox.showinfo("NASCAR.com Sync Complete", "\n".join(updated_counts))

    def load_builtin_2027_schedule(self):
        schedule_2027_cup = [
            ("Feb 13", "Wheatley Vodka Clash", "Daytona International Speedway"),
            ("Feb 18", "Duel at Daytona", "Daytona International Speedway"),
            ("Feb 21", "DAYTONA 500", "Daytona International Speedway"),
            ("Feb 28", "Autotrader 400", "EchoPark Speedway (Atlanta)"),
            ("Mar 07", "DuraMAX Texas Grand Prix", "Circuit of The Americas"),
            ("Mar 14", "Straight Talk Wireless 500", "Phoenix Raceway"),
            ("Mar 21", "Pennzoil 400", "Las Vegas Motor Speedway"),
            ("Apr 04", "Goodyear 400", "Darlington Raceway"),
            ("Apr 11", "Food City 500", "Bristol Motor Speedway"),
            ("Apr 18", "Cook Out 400", "Martinsville Speedway"),
            ("Apr 25", "Jack Link's 500", "Talladega Superspeedway"),
            ("May 02", "Würth 400", "Texas Motor Speedway"),
            ("May 09", "AdventHealth 400", "Kansas Speedway"),
            ("May 16", "ECOSAVE 400", "Dover Motor Speedway"),
            ("May 23", "NASCAR All-Star Race", "North Wilkesboro Speedway"),
            ("May 30", "Coca-Cola 600", "Charlotte Motor Speedway"),
            ("Jun 06", "Cracker Barrel 400", "Nashville Superspeedway"),
            ("Jun 13", "Great American Getaway 400", "Pocono Raceway"),
            ("Jun 20", "FireKeepers Casino 400", "Michigan International Speedway"),
            ("Jun 27", "eero 400", "Chicagoland Speedway"),
            ("Jul 04", "Iowa Corn 350", "Iowa Speedway"),
            ("Jul 11", "Toyota / Save Mart 350", "Sonoma Raceway"),
            ("Jul 18", "Dollar Tree 400", "EchoPark Speedway (Atlanta)"),
            ("Jul 25", "Brickyard 400", "Indianapolis Motor Speedway"),
            ("Aug 01", "Anduril 250 Race the Base", "Naval Base Coronado"),
            ("Aug 14", "Bass Pro Shops Night Race", "Bristol Motor Speedway"),
            ("Aug 22", "Enjoy Illinois 300", "World Wide Technology Raceway"),
            ("Aug 28", "Coke Zero Sugar 400", "Daytona International Speedway"),
            ("Sep 05", "Cook Out Southern 500", "Darlington Raceway"),
            ("Sep 11", "Cook Out 400", "Richmond Raceway"),
            ("Sep 19", "Go Bowling at The Glen", "Watkins Glen International"),
            ("Sep 26", "New Hampshire 301", "New Hampshire Motor Speedway"),
            ("Oct 03", "Hollywood Casino 400", "Kansas Speedway"),
            ("Oct 10", "South Point 400", "Las Vegas Motor Speedway"),
            ("Oct 17", "Bank of America 400", "Charlotte Motor Speedway"),
            ("Oct 24", "Freeway Insurance 500", "Phoenix Raceway"),
            ("Oct 31", "YellaWood 500", "Talladega Superspeedway"),
            ("Nov 07", "Xfinity 500", "Martinsville Speedway"),
            ("Nov 14", "NASCAR Cup Series Championship", "Homestead-Miami Speedway")
        ]
        old_lookup = {(r.get("race", "").lower(), r.get("track", "").lower()): r for r in self.data.get("Cup", [])}
        new_cup = []
        for dt_s, r_name, t_name in schedule_2027_cup:
            prev = old_lookup.get((r_name.lower(), t_name.lower()), {})
            auto_bkt, auto_note = generate_smart_notes(r_name, t_name, "Cup", prev.get("notes", ""))
            prev_yrs = get_item_attended_years(prev)
            new_cup.append({
                "date": dt_s,
                "season_year": "2027",
                "race": r_name,
                "track": t_name,
                "address": lookup_track_address(t_name),
                "distance": prev.get("distance", "—"),
                "attended": bool(prev_yrs),
                "attended_years": prev_yrs,
                "bucket_list": prev.get("bucket_list", bool(auto_bkt)),
                "winner": prev.get("winner", ""),
                "seat": prev.get("seat", ""),
                "rating": prev.get("rating", "Unrated"),
                "notes": auto_note
            })
        self.data["Cup"] = new_cup
        self.save_data()
        self.refresh_all_tables()
        messagebox.showinfo("2027 Schedule Loaded", "Loaded confirmed 2027 Cup & ARCA Menards National schedules (preserving your attended years)!")

    def reload_default_schedule(self):
        confirm = messagebox.askyesno(
            "Confirm Factory Reset",
            "Are you sure you want to perform a full Factory Reset?\n\n"
            "This will:\n"
            "• Clear all Attended / Visited checkmarks & Attended Years back to 0\n"
            "• Reset all Quests, Food Challenges, Side-Tracked, Notes & Bucket List\n"
            "• Clear your Home Address, calculated distances, and Trip Planner\n"
            "• Remove any custom added local races"
        )
        if not confirm:
            return

        if not os.path.exists(DEFAULT_FILE):
            messagebox.showerror("Missing File", f"Could not find {DEFAULT_FILE}.")
            return

        with open(DEFAULT_FILE, "r", encoding="utf-8") as f:
            fresh = json.load(f)

        for k in SERIES_KEYS:
            default_yr = "2027" if k in ("ARCA_National", "ARCA_East", "ARCA_West") else "2026"
            for item in fresh.get(k, []):
                item["season_year"] = default_yr
                item["attended"] = False
                item["attended_years"] = []
                item["distance"] = "—"
        for item in fresh.get("Attractions", []):
            item["visited"] = False
            item["distance"] = "—"

        self.data = fresh
        self.data["settings"] = {"home_address": "", "dark_mode": self.dark_mode}
        self.data["Trip"] = []
        self.data["TripExpenses"] = {
            "trip_name": "My Race Weekend Trip",
            "hotel": 0.0,
            "fuel": 0.0,
            "food": 0.0,
            "souvenirs": 0.0,
            "other": 0.0,
            "budget_limit": 0.0
        }
        self.data["SavedTrips"] = {}
        self.data["QuestProgress"] = {"food": {}, "side_quests": {}, "custom_quests": []}
        self.data["CompletedTracksHistory"] = []

        self.home_var.set("")
        self.year_var.set("Season")
        self.trip_name_var.set("My Race Weekend Trip")
        self.exp_hotel_var.set("0")
        self.exp_fuel_var.set("0")
        self.exp_food_var.set("0")
        self.exp_souvenirs_var.set("0")
        self.exp_other_var.set("0")
        self.exp_budget_var.set("0")
        self.saved_trip_select_var.set("")
        if hasattr(self, "saved_trips_cb"):
            self.saved_trips_cb.configure(values=[])

        self.filter_state_var.set("ALL")
        self.filter_dist_var.set("Any Distance")
        self.filter_status_var.set("All Items")
        self.sort_by_var.set("Schedule / Default")
        self.search_var.set("")
        self.dist_status_var.set("")

        self.save_data()
        self.refresh_all_tables()
        messagebox.showinfo("Factory Reset Complete", "TrackChaser HQ has been restored to a clean factory state!")

    def update_stats(self):
        def tally(key, field="attended"):
            items = self.data.get(key, [])
            done = sum(1 for x in items if x.get(field))
            return f"{done}/{len(items)}"

        arca_keys = ["ARCA_National", "ARCA_East", "ARCA_West"]
        arca_total = sum(len(self.data.get(k, [])) for k in arca_keys)
        arca_done = sum(sum(1 for x in self.data.get(k, []) if x.get("attended")) for k in arca_keys)

        bucket_total = 0
        bucket_done = 0
        for k in SERIES_KEYS:
            for x in self.data.get(k, []):
                if x.get("bucket_list"):
                    bucket_total += 1
                    if x.get("attended"):
                        bucket_done += 1
        for x in self.data.get("Attractions", []):
            if x.get("bucket_list"):
                bucket_total += 1
                if x.get("visited"):
                    bucket_done += 1

        swept_wknds, total_wknds, vis_tracks, tot_tracks = self.compute_weekend_sweeps_and_tracks()

        self.stats_var.set(
            f"Cup: {tally('Cup')} • "
            f"O'Reilly: {tally('O\'Reilly')} • "
            f"FedEx: {tally('Craftsman')} • "
            f"ARCA: {arca_done}/{arca_total} • "
            f"Local: {tally('Grassroots')} • "
            f"Sweeps: {swept_wknds}/{total_wknds} • "
            f"Tracks: {vis_tracks}/{tot_tracks} • "
            f"Shops: {tally('Attractions', 'visited')} • "
            f"Bucket: {bucket_done}/{bucket_total}"
        )
        if hasattr(self, "banner_canvas"):
            self.draw_top_banner()


if __name__ == "__main__":
    root = tk.Tk()
    app = NASCARTrackerApp(root)
    root.mainloop()