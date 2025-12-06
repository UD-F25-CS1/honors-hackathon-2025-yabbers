from bakery import assert_equal
from dataclasses import dataclass
from drafter import *

set_site_information(
    author="m-yablons@udel.edu",
    description="""Carbon Footprints are something epople might have heard of, but don't know how it applies to them.
    This website lets you change that!""",
    sources=["https://ourworldindata.org/travel-carbon-footprint", 'https://ourworldindata.org/food-choice-vs-eating-local'],
    planning=["your_planning_document.pdf"],
    links=["https://github.com/m-yablons/your-repo"]
)
hide_debug_information()
set_website_title("Carbon Footprint Calculator")
set_website_framed(False)
add_website_css('''
body {
    background-color: lightgreen;
    font-size: 20px;
}
''')
    

@dataclass
class Food:
    name: str
    group: str
    amount: int
    emissions: int
    
@dataclass
class Travel:
    is_public: bool
    people: int
    method: str
    distance: float
    emission: int

@dataclass
class State:
    guess: int
    food: list[Food]
    travel: list[Travel]
    food_tons: float
    travel_tons: float
    emissions: float

@route
def index(state: State)-> Page:
    return Page(state, content =[
        Header("The Carbon Footprint Calculator"),
        "Hello there! A carbon footprint is a fancy way to say how much carbon emissions your activites put into the atmosphere, measured in metric tonnes.",
        "How many metric tonnes of carbon do you think you put into the atmosphere per year?",
        TextBox("guess"),
        "Your guess is currently set at: " + str(state.guess),
        Button("Enter my guess!", url='/setguess'),
        Button(text="Start calculating my carbon footprint", url = "/begin_calculating")
        ])
@route
def setguess(state:State, guess: str)-> Page:
    number_guess = int(guess)
    state.guess =number_guess
    return index(state)
@route
def begin_calculating(state: State, guess: str)-> Page:
    return Page(state, content=[
        "Alright! What do you want to start calculating?",
        Button(text= "My Food Footprint", url ="/food_info"),
        Button(text= "My Travel Footprint", url= "/travel_info"),
        Button(text= "Take me home", url='/index')
        ])
@route
def food_info(state: State)-> Page:
    return Page(state, content=[
        "Choose a basic food that you eat a lot.",
        "What is it's name?",
        TextBox("food_name", "Ex. Chicken, Milk, Corn"),
        "What food group is it? Please choose from Meat Protein, Plant proteins, Fish/Ocean protein, Dairy, Fruit, Vegetables, and Grain.",
        TextBox("group", "Ex. Dairy, Fruit, etc."),
        "How many kilograms of this do you eat every week?",
        TextBox("weekly_kg", "Ex. 12, 200"),
        Button(text="I'm done adding 1 food", url= '/add_food'),
        Button(text= "I have added all my weekly foods", url = '/food_emissions')
        ])
@route
def add_food(state: State, food_name: str, group: str, weekly_kg: str) -> Page:
    kg = int(weekly_kg)
    f_name = food_name.lower()
    group_name = group.lower()
    emission = 0
    if group_name=="meat protein":
        emission= 20
    elif group_name=="plant protein":
        emission= 2
    elif group_name=="fish/ocean protein":
        emission= 10
    elif "fish" in group_name:
        emission = 5
    elif group_name=="dairy":
        emission= 21
    elif group_name=="fruit":
        emission= 1
    elif group_name=="vegetables":
        emission= 1
    elif group_name=="grain":
        emission= 3
    if "beef" in f_name:
        emission = 60
    elif "lamb" in f_name:
        emission = 24
    elif "mutton" in f_name:
        emission = 24
    elif "cheese" in f_name:
        emission = 21
    elif "chocolate" in f_name:
        emission = 19
    elif "bacon" in f_name:
        emission = 7
    elif "pork" in f_name:
        emission = 7
    elif "chicken" in f_name:
        emission = 6
    elif "nuts" in f_name:
        emission = 0
    new_food= Food(food_name, group, kg, emission)
    state.food.append(new_food)
    return food_info(state)

@route
def travel_info(state: State)-> Page:
    return Page(state, content=[
        "Think about how much you travel in a year.",
        "What did you travel in?",
        TextBox("method", "Ex. Car, train, plane"),
        "Was it public?",
        CheckBox("public"),
        "How many people did you travel with?",
        TextBox("people", "0 to 999"),
        "How far did you travel?",
        TextBox("dist", "In kilometers!"),
        "How many times did you make that trip in a year?",
        TextBox("often", "5 days a week = 261"),
        Button(text= "Add the trip", url='/add_travel'),
        Button(text= "I have added all of my travels", url='/travel_emissions')
        ])
@route
def add_travel(state:State, method: str, public: str, people: str, dist: str, often: str)-> Page:
    p_trans = False
    e_factor = 0.0
    emission = 0
    if public:
        p_trans = True
    elif "car" in method.lower():
        e_factor = .171
    elif "plane" in method.lower():
        e_factor = .246
    elif "bus" in method.lower():
        e_factor = .097
    elif "train" in method.lower():
        e_factor = .029
    if int(people) >= 1:
        e_factor = e_factor / (int(people)+1)
    emission = e_factor * float(dist) * float(often)
    if p_trans == True:
        emission = emission *0.03
    new_travel = Travel(p_trans, int(people), method, float(dist), emission)
    state.travel.append(new_travel)
    return travel_info(state)
@route
def food_emissions(state:State)-> Page:
    m_kg = 0
    item_em = 0
    for food in state.food:
        item_em = food.amount * food.emissions
        m_kg = m_kg + item_em
    f_tons = m_kg * 0.001 * 52.1
    state.food_tons = f_tons
    return Page(state,content =[
        "Here is your food carbon footprint in metric tonnes per year: " + str(state.food_tons),
        Button(text="Add my travel footprint", url='/travel_info'),
        Button(text="See my total footprint", url ='/final_emissions')
        ])
@route
def travel_emissions(state:State)->Page:
    total_em = 0
    for trip in state.travel:
        total_em = total_em + trip.emission
    total_em = total_em * 0.001
    state.travel_tons = total_em
    return Page(state,content =[
        "Here is your travel carbon footprint in metric tonnes per year: " + str(total_em),
        Button(text="Add my food footprint", url='/food_info'),
        Button(text="See my total footprint", url ='/final_emissions')
        ])
@route
def final_emissions(state:State)-> Page:
    state.emissions = state.food_tons + state.travel_tons
    return Page(state, content =[
        "Your total emissions, in metric tonnes per year, is: " + str(state.emissions),
        "How does it compare to your guess of " + str(state.guess) + " metric tonnes?",
        Button(text="Return Home", url= '/index')
        ])


start_server(State(0,[],[],0.0,0.0,0.0))  

    
        
    
        
        
    
