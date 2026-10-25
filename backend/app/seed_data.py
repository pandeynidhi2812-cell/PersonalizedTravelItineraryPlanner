"""Sample (dummy) data used to seed the database. Prices are in INR and are illustrative only."""

# (id, name, email, password, role, home_city, travel_style)
USERS = [
    (1, "Admin User",   "admin@travelplanner.com", "Admin@123", "admin",    "Bhopal",    "mid"),
    (2, "Aarav Sharma", "aarav@example.com",       "Aarav@123", "traveler", "Indore",    "budget"),
    (3, "Priya Nair",   "priya@example.com",       "Priya@123", "traveler", "Mumbai",    "premium"),
    (4, "Rohan Mehta",  "rohan@example.com",       "Rohan@123", "traveler", "Pune",      "mid"),
    (5, "Meera Iyer",   "meera@example.com",       "Meera@123", "traveler", "Bengaluru", "mid"),
    (6, "Karan Singh",  "karan@example.com",       "Karan@123", "traveler", "Delhi",     "mid"),
    (7, "Sneha Reddy",  "sneha@example.com",       "Sneha@123", "traveler", "Hyderabad", "premium"),
]

# (id, name, state, tagline, description, best_season, avg_daily_budget, tags)
DESTINATIONS = [
    (1, "Goa", "Goa", "Beaches, forts and slow evenings",
     "Sun, sand and Portuguese heritage. North Goa buzzes with beach shacks and nightlife, while the south stays calm and scenic.",
     "Nov - Feb", 4500, ["beach", "nightlife", "food", "relaxation"]),
    (2, "Jaipur", "Rajasthan", "The Pink City of palaces and bazaars",
     "Hill forts, royal palaces and colourful markets make Jaipur a compact, culture-rich city break.",
     "Oct - Mar", 4000, ["culture", "shopping", "heritage", "food"]),
    (3, "Manali", "Himachal Pradesh", "Snow, pine and adrenaline",
     "A Himalayan valley town known for adventure sports, cafes in Old Manali and high mountain passes.",
     "Mar - Jun, Dec - Jan", 4200, ["adventure", "nature", "mountains"]),
    (4, "Munnar", "Kerala", "Tea hills above the clouds",
     "Rolling tea estates, misty viewpoints and quiet lakes, ideal for slow, scenic holidays.",
     "Sep - May", 3800, ["nature", "relaxation", "romantic"]),
    (5, "Udaipur", "Rajasthan", "The city of lakes",
     "Lakeside palaces, sunset boat rides and old-world havelis make Udaipur India's most romantic city.",
     "Oct - Mar", 5000, ["romantic", "culture", "lakes"]),
    (6, "Rishikesh", "Uttarakhand", "Rapids, yoga and the Ganges",
     "The yoga capital of the world doubles as India's rafting hub, with evening aartis on the river.",
     "Sep - Nov, Feb - May", 3200, ["adventure", "spiritual", "relaxation"]),
    (7, "Varanasi", "Uttar Pradesh", "The oldest living city",
     "Ghats, temples, narrow lanes and street food. Varanasi is best experienced at dawn on the river.",
     "Oct - Mar", 3000, ["culture", "spiritual", "food"]),
]

# (destination_id, name, tags, entry_fee_per_person, duration_min, best_slot, area, description)
ATTRACTIONS = [
    (1, "Fort Aguada", ["sightseeing", "culture", "romantic"], 50, 90, "evening", "Candolim",
     "17th-century Portuguese fort with a lighthouse and wide sea views at sunset."),
    (1, "Baga Beach Water Sports", ["adventure", "nightlife"], 1200, 120, "morning", "Baga",
     "Parasailing, jet-ski and banana-boat rides, followed by the lively beach strip."),
    (1, "Basilica of Bom Jesus and Old Goa", ["culture", "sightseeing"], 0, 90, "morning", "Old Goa",
     "UNESCO-listed churches holding centuries of Goan Catholic history."),
    (1, "Palolem Beach", ["relaxation", "nature", "romantic"], 0, 180, "afternoon", "Palolem",
     "A crescent bay in South Goa with calm water, kayaks and quiet shacks."),

    (2, "Amber Fort", ["sightseeing", "culture"], 550, 150, "morning", "Amer",
     "Hilltop fort-palace with mirror work, courtyards and elephant-era ramps."),
    (2, "City Palace and Hawa Mahal", ["culture", "sightseeing"], 700, 150, "afternoon", "Old City",
     "Royal residence museum plus the honeycomb facade of the Palace of Winds."),
    (2, "Johari Bazaar Walk", ["shopping", "food"], 0, 120, "evening", "Old City",
     "Jewellery, block-print textiles and lassi stalls along Jaipur's oldest market street."),
    (2, "Nahargarh Fort Sunset", ["romantic", "sightseeing", "nature"], 200, 90, "evening", "Nahargarh",
     "Ridge-top fort with a panoramic view over the city as the lights come on."),

    (3, "Solang Valley Adventure", ["adventure", "nature"], 1500, 180, "morning", "Solang",
     "Paragliding, zorbing and cable car rides against a snow-line backdrop."),
    (3, "Hadimba Temple and Old Manali", ["culture", "sightseeing", "food"], 50, 120, "morning", "Old Manali",
     "Wooden cedar-forest temple followed by cafes along the Manalsu river."),
    (3, "Rohtang Pass Excursion", ["nature", "adventure", "sightseeing"], 1000, 300, "morning", "Rohtang",
     "High-altitude pass with snow play (permit required, closed in winter)."),
    (3, "Vashisht Hot Springs", ["relaxation", "nature"], 0, 90, "evening", "Vashisht",
     "Natural sulphur springs and an old stone temple in a quiet village."),

    (4, "Eravikulam National Park", ["nature", "sightseeing"], 200, 150, "morning", "Rajamala",
     "Home of the Nilgiri tahr with rolling grasslands above the tea line."),
    (4, "Tea Museum and Plantation Walk", ["culture", "nature"], 125, 90, "afternoon", "Munnar Town",
     "See how tea is processed and walk between the estate rows."),
    (4, "Mattupetty Dam Boating", ["relaxation", "romantic", "nature"], 400, 90, "afternoon", "Mattupetty",
     "Calm reservoir boat ride surrounded by shola forest."),
    (4, "Top Station Viewpoint", ["sightseeing", "nature", "romantic"], 50, 90, "afternoon", "Top Station",
     "The highest point in Munnar with sweeping views over the Western Ghats."),

    (5, "City Palace Udaipur", ["culture", "sightseeing"], 400, 120, "morning", "Lake Pichola",
     "Sprawling palace complex of courtyards, balconies and royal galleries."),
    (5, "Lake Pichola Sunset Boat Ride", ["romantic", "relaxation", "sightseeing"], 500, 75, "evening", "Lake Pichola",
     "Glide past Jag Mandir and the Lake Palace as the sun goes down."),
    (5, "Sajjangarh Monsoon Palace", ["sightseeing", "nature"], 300, 90, "afternoon", "Sajjangarh",
     "Hilltop palace with a long view across Udaipur's lakes."),
    (5, "Bagore Ki Haveli Dance Show", ["culture"], 100, 75, "evening", "Gangaur Ghat",
     "Traditional Rajasthani folk dance in a restored 18th-century haveli."),

    (6, "White Water Rafting", ["adventure"], 1200, 180, "morning", "Shivpuri",
     "Grade II-III rapids on the Ganges with a cliff-jump stop."),
    (6, "Laxman Jhula and Ram Jhula Walk", ["sightseeing", "culture"], 0, 90, "afternoon", "Tapovan",
     "Cross the iconic suspension bridges and browse the riverside lanes."),
    (6, "Ganga Aarti at Triveni Ghat", ["culture", "romantic"], 0, 60, "evening", "Triveni Ghat",
     "Lamps, bells and chanting on the riverbank every evening."),
    (6, "Beatles Ashram and Yoga Session", ["relaxation", "culture"], 150, 120, "morning", "Tapovan",
     "Explore the graffiti-covered ashram ruins and join a guided yoga class."),

    (7, "Dawn Boat Ride on the Ganges", ["culture", "sightseeing", "romantic"], 600, 90, "morning", "Dashashwamedh Ghat",
     "Watch the ghats wake up from the water at sunrise."),
    (7, "Kashi Vishwanath Corridor", ["culture"], 0, 90, "morning", "Godowlia",
     "Walk the redeveloped corridor to one of India's most visited Shiva temples."),
    (7, "Ganga Aarti at Dashashwamedh Ghat", ["culture", "sightseeing"], 0, 60, "evening", "Dashashwamedh Ghat",
     "The grand evening ritual with priests, fire lamps and drums."),
    (7, "Sarnath Buddhist Site", ["culture", "sightseeing", "nature"], 100, 120, "afternoon", "Sarnath",
     "Where the Buddha gave his first sermon, with stupas and a museum."),
    (1, "Dudhsagar Falls Day Trip", ["nature", "adventure"], 400, 240, "morning", "Mollem",
     "Jeep safari to a four-tier waterfall inside the Mollem forest."),
    (2, "Jal Mahal and Panna Meena Kund", ["sightseeing", "culture"], 100, 90, "afternoon", "Amer",
     "Photo stop at the lake palace and a geometric 16th-century stepwell."),
    (3, "Mall Road and Tibetan Market", ["shopping", "food"], 0, 120, "evening", "Mall Road",
     "Woollens, handicrafts and momos along the town's main promenade."),
    (4, "Kolukkumalai Sunrise Jeep Safari", ["adventure", "nature"], 1800, 240, "morning", "Suryanelli",
     "Early-morning jeep ride to one of the highest tea estates in the world."),
    (5, "Saheliyon Ki Bari Gardens", ["relaxation", "nature"], 50, 75, "afternoon", "Fateh Sagar",
     "Fountain gardens built for the royal women of the court."),
    (6, "Neelkanth Mahadev Temple and Waterfall", ["nature", "culture"], 100, 150, "afternoon", "Neelkanth",
     "Forest-hill temple with a short trek to a cool waterfall."),
    (7, "Assi Ghat Morning Yoga and Chai", ["relaxation", "food", "culture"], 0, 90, "morning", "Assi Ghat",
     "Start the day with sunrise yoga followed by a kulhad of chai."),
]

# (destination_id, name, cuisine, tier, cost_per_person, rating, description)
RESTAURANTS = [
    (1, "Shack Sunset Kitchen", "Goan Seafood", "budget", 350, 4.2, "Beachside fish thali and prawn curry."),
    (1, "Vindaloo Junction", "Goan", "budget", 300, 4.0, "Home-style Goan plates and cold beer."),
    (1, "Casa Konkan Table", "Indo-Portuguese", "mid", 750, 4.5, "Courtyard dining with a changing seasonal menu."),
    (1, "The Tidewater Grill", "Fine Dining", "premium", 1800, 4.7, "Sea-view tasting menu with local catch."),

    (2, "Chaat Gali Corner", "Rajasthani Street Food", "budget", 200, 4.3, "Pyaaz kachori, mirchi vada and lassi."),
    (2, "Dal Baati Darbar", "Rajasthani", "budget", 320, 4.1, "Unlimited dal baati churma thali."),
    (2, "Rawat Haveli Kitchen", "North Indian", "mid", 700, 4.4, "Laal maas and gatte ki sabzi in a heritage setting."),
    (2, "Suvarna Mahal Dining", "Royal Rajasthani", "premium", 2200, 4.6, "Palace-style multi-course dinner with live music."),

    (3, "Maggi Point Cafe", "Cafe", "budget", 220, 4.0, "Hot noodles and chai with a river view."),
    (3, "Siddu and Trout House", "Himachali", "budget", 380, 4.4, "Steamed siddu with ghee and river trout."),
    (3, "Pine Ridge Bistro", "Continental", "mid", 800, 4.3, "Wood-fired pizza and mountain-view terrace."),
    (3, "Cedar Hearth Restaurant", "Multi-cuisine", "premium", 1600, 4.6, "Fireplace dining and curated mountain menu."),

    (4, "Appam Stop", "Kerala", "budget", 220, 4.2, "Appam with vegetable stew and fish curry."),
    (4, "Hill Station Mess", "South Indian", "budget", 250, 4.0, "Banana-leaf meals at local prices."),
    (4, "Spice Garden Kitchen", "Kerala", "mid", 650, 4.5, "Estate-fresh spices in every dish."),
    (4, "Cloud Peak Dining", "Fine Dining", "premium", 1700, 4.6, "Valley-view tasting menu."),

    (5, "Lakeside Chai Wala", "Street Snacks", "budget", 180, 4.1, "Kachori, samosa and masala chai by the water."),
    (5, "Thali House Udaipur", "Rajasthani", "budget", 300, 4.2, "Generous vegetarian thali."),
    (5, "Ambrai Ghat Terrace", "North Indian", "mid", 900, 4.5, "Rooftop dining facing the lit-up palace."),
    (5, "Jharokha Royal Dining", "Royal Rajasthani", "premium", 2500, 4.8, "Candle-lit dinner on a lakeside terrace."),

    (6, "Ganga Beach Cafe", "Cafe", "budget", 250, 4.3, "Sit on the sand with a pot of masala tea."),
    (6, "Tapovan Thali Hub", "Vegetarian", "budget", 200, 4.0, "Simple, filling sattvic meals."),
    (6, "Yogi Roots Kitchen", "Organic", "mid", 550, 4.4, "Healthy bowls and fresh juices."),
    (6, "Himalaya View Deck", "Multi-cuisine", "premium", 1400, 4.5, "River-facing deck with a curated menu."),

    (7, "Kachori Gali Stall", "Street Food", "budget", 150, 4.5, "Kachori-sabzi and jalebi at dawn."),
    (7, "Banarasi Chaat Bhandar", "Street Food", "budget", 180, 4.4, "Tamatar chaat and malaiyo in winter."),
    (7, "Ghat Side Rasoi", "North Indian", "mid", 500, 4.2, "River-view thali and lassi."),
    (7, "Kashi Heritage Table", "Fine Dining", "premium", 1500, 4.5, "Banarasi tasting menu in a restored haveli."),
]

# (destination_id, name, tier, price_per_night, rating, amenities)
HOTELS = [
    (1, "Palm Hostel Goa", "budget", 1200, 4.0, ["Wi-Fi", "Breakfast", "Shared kitchen"]),
    (1, "Coco Shore Resort", "mid", 3800, 4.3, ["Wi-Fi", "Breakfast included", "Pool"]),
    (1, "The Azure Bay Resort and Spa", "premium", 11000, 4.8, ["Wi-Fi", "Breakfast included", "Pool", "Spa", "Beach access"]),

    (2, "Pink City Backpackers", "budget", 1000, 4.0, ["Wi-Fi", "Breakfast", "Rooftop"]),
    (2, "Haveli Heritage Stay", "mid", 3500, 4.4, ["Wi-Fi", "Breakfast included", "Courtyard"]),
    (2, "Rajputana Palace Hotel", "premium", 13000, 4.8, ["Wi-Fi", "Breakfast included", "Pool", "Spa"]),

    (3, "Snowline Hostel", "budget", 900, 4.0, ["Wi-Fi", "Breakfast", "Bonfire"]),
    (3, "Pinewood Cottages", "mid", 3200, 4.3, ["Wi-Fi", "Breakfast included", "Heater"]),
    (3, "Himalayan Crest Resort", "premium", 9500, 4.7, ["Wi-Fi", "Breakfast included", "Spa", "Valley view"]),

    (4, "Tea Trail Homestay", "budget", 1100, 4.2, ["Wi-Fi", "Breakfast", "Garden"]),
    (4, "Misty Hills Resort", "mid", 3400, 4.4, ["Wi-Fi", "Breakfast included", "Plantation view"]),
    (4, "Cloud Nine Plantation Villa", "premium", 10500, 4.8, ["Wi-Fi", "Breakfast included", "Private deck", "Spa"]),

    (5, "Lakeview Dorm Udaipur", "budget", 1100, 4.1, ["Wi-Fi", "Breakfast", "Lake view roof"]),
    (5, "Mewar Heritage Inn", "mid", 4000, 4.4, ["Wi-Fi", "Breakfast included", "Courtyard"]),
    (5, "Lake Palace Suites", "premium", 15000, 4.9, ["Wi-Fi", "Breakfast included", "Pool", "Spa", "Lake view"]),

    (6, "Raft and Rest Camp", "budget", 800, 4.0, ["Breakfast", "Riverside", "Campfire"]),
    (6, "Ganga Yoga Retreat", "mid", 2800, 4.3, ["Wi-Fi", "Breakfast included", "Yoga hall"]),
    (6, "Himalaya Wellness Resort", "premium", 8500, 4.7, ["Wi-Fi", "Breakfast included", "Spa", "Pool"]),

    (7, "Ghat Backpackers", "budget", 700, 4.0, ["Wi-Fi", "Breakfast", "Terrace"]),
    (7, "Kashi Courtyard Inn", "mid", 2600, 4.3, ["Wi-Fi", "Breakfast included", "Ghat view"]),
    (7, "Ganga Haveli Palace", "premium", 9000, 4.7, ["Wi-Fi", "Breakfast included", "Spa", "River view"]),
]

# (destination_id, mode, cost_per_day, unit, notes)   unit: per_person | per_vehicle (4 seats)
TRANSPORTS = [
    (1, "Scooter rental", 450, "per_person", "Most popular way to hop between beaches."),
    (1, "Private cab", 2800, "per_vehicle", "Full-day cab with driver."),
    (2, "Auto-rickshaw and metro", 400, "per_person", "Short hops through the old city."),
    (2, "Private cab", 2500, "per_vehicle", "Day cab with driver for forts and palaces."),
    (3, "Shared taxi and local bus", 350, "per_person", "Cheap links between valley villages."),
    (3, "Private cab", 3200, "per_vehicle", "Needed for Rohtang and Solang runs."),
    (4, "Local jeep and auto", 400, "per_person", "Shared jeeps to viewpoints."),
    (4, "Private cab", 2600, "per_vehicle", "Day cab across the tea estates."),
    (5, "Auto-rickshaw", 350, "per_person", "Short rides around the lakes."),
    (5, "Private cab", 2400, "per_vehicle", "Day cab with driver."),
    (6, "Shared tuk-tuk", 250, "per_person", "Cheap hops between Tapovan and the ghats."),
    (6, "Private cab", 2200, "per_vehicle", "Day cab with driver."),
    (7, "E-rickshaw", 250, "per_person", "Works in the narrow lanes near the ghats."),
    (7, "Private cab", 2300, "per_vehicle", "Day cab with driver for Sarnath."),
]

# (user_id, destination_id, rating, comment)
REVIEWS = [
    (2, 1, 5, "Perfect weekend. The north-to-south routing saved a lot of time."),
    (3, 5, 5, "The sunset boat ride was the highlight of our honeymoon."),
    (5, 3, 4, "Great adventure mix. Pack warm clothes even in May."),
    (6, 2, 5, "Johari Bazaar in the evening is worth the whole trip."),
    (7, 4, 4, "Quiet, green and relaxing. Eravikulam tickets sell out early."),
    (4, 6, 5, "Rafting was a blast and the yoga session was the perfect reset."),
    (1, 7, 5, "The dawn boat ride is unforgettable."),
]

# (title, owner_user_id, destination_id, start, end, travelers, budget, style, pace, interests)
TRIPS = [
    ("Goa Solo Weekend",           2, 1, "2026-11-20", "2026-11-22", 1,   9000, "budget",  "relaxed",  ["food", "sightseeing"]),
    ("Udaipur Romantic Escape",    3, 5, "2026-12-05", "2026-12-08", 2,  85000, "premium", "relaxed",  ["romantic", "culture"]),
    ("Manali Friends Adventure",   5, 3, "2026-12-26", "2026-12-30", 5,  95000, "mid",     "packed",   ["adventure", "nature"]),
    ("Jaipur Culture Break",       6, 2, "2026-11-13", "2026-11-15", 2,  25000, "mid",     "balanced", ["shopping", "culture", "food"]),
    ("Munnar Slow Retreat",        7, 4, "2027-01-10", "2027-01-12", 2,  30000, "mid",     "relaxed",  ["nature", "relaxation"]),
    ("Rishikesh Rapids and Yoga",  4, 6, "2026-11-27", "2026-11-30", 4,  32000, "budget",  "balanced", ["adventure", "relaxation"]),
    ("Varanasi Heritage Walk",     1, 7, "2026-12-12", "2026-12-14", 3,  28000, "mid",     "balanced", ["culture", "food"]),
]

# (trip_index (1-based), user_id, role, interests)
TRIP_MEMBERS = [
    (2, 4, "editor", ["scenic", "romantic"]),
    (3, 6, "editor", ["adventure"]),
    (3, 7, "editor", ["nature", "relaxation"]),
    (3, 2, "editor", ["food"]),
    (3, 4, "editor", ["adventure", "nightlife"]),
    (6, 5, "editor", ["relaxation"]),
    (6, 6, "editor", ["adventure"]),
]
