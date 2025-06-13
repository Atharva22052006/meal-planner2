from flask import Flask, render_template, request, session, redirect, url_for
from crewai import Agent, Task, Crew, LLM
import os

# Ensure the API key is set
os.environ['GEMINI_API_KEY'] = 'AIzaSyBiQlLfzp23CWnPnf91BegFX9DVgJjOqx0'
llm = LLM(model="gemini/gemini-2.0-flash")

# Define the agents and tasks within the Flask app or import them
# For simplicity, I will copy the agent and task definitions here
# It's better to import if crewai.py is a module, but given the __name__ == "__main__" block,
# copying might be safer or refactoring crewai.py into functions.
# For now, I will copy the definitions.

## Agents
user_profiler = Agent(
    role="Indian Reality Checker",
    goal="Analyze user's real food constraints in Indian context",
    backstory="You've survived Mumbai tiffins and Delhi hostel messes.",
    llm=llm,
    verbose=True
)

nutrition_calculator = Agent(
    role="Jugaad Nutritionist",
    goal="Calculate nutrition with Indian food constraints",
    backstory="Expert in hitting protein targets with dal and street food.",
    llm=llm,
    verbose=True
)

meal_designer = Agent(
    role="Street Food Architect",
    goal="Create practical Indian meal plans",
    backstory="Planned meals for students and professionals across India.",
    llm=llm,
    verbose=True
)

output_structurer = Agent(
    role="Master sentence structure examiner",
    goal="takes the output and structures it according to the context. If any information is missing it searches the information and adds it",
    backstory="Cannot tolerate incorrect structures whenever sees wrong structure you fix it",
    llm=llm,
    verbose=True
)

## Formatting rules (from crewai.py)
Result_instructions = """
- Create a 3 times a day meal plan, i.e, Breakfast, Lunch and Dinner.
- Make sure that the data provided by the user is being used.
- Make sure the area they are living in has the food available
- Along with the user goal, You also have to make sure that the suggested nutrients should be hit everyday for all the days
- Make sure to return all the micros and macros of the foods returned
- Make a plan for 7 days
- Include all the micros and macros
- At the end provide me a listed value for all the micros and micros for every meal every day. This list should not be in table format
- Jump straight to the meal plan no unnecessary before talks.
- Make sure to add note that all the micros and macros are approx and can vary based on the specific ingredients and preparation methods and also that the price is approx and can vary depending on the region
"""

Pricing = """
- If the pricing is less than Rs 150 and the Hostel/PG does not provide them food tell the user the money spent is too less.
- Make sure that the meal contains pricing at which they will be bought.
- Use the pricing for the item used in the area where the user is living
"""

Hostel_PG_Considerations = """
- If the hostel/PG provides food then make the meal plan by not including price for the times where the food is provided
- If the meal is provided by hostel/pg for all the times just provide the extra things the user has to eat to hit the nutrition goal.
- Even if the mess provides food consider approx food eaten and do not exclude it in the final count.
"""

nutritional_list = """
- Provide each and every food item with all the micros and micros on it
- Make sure to provide the list day wise and it should also have type of dinner in it.
- This list should not be in the table format
- The format will be again Day 1 then inside that a list of breakfast lunch and dinner and for every food item there make another nested list that gives the macros micros and all the nutritional information with price
"""

Diet_Plan = """
- While providing the 7 day plan do not return the micros and macros they should just be on the table not on the 7 day meal plan
- Do not provide suggestions at the end
- Make sure that the meal plan is not in one single line have nested list
- Provide just the total calories and nutrients for the entire day at the end of that particular day and not after all the days are completed
- Should start with days and it should be written Day 1, Day 2, Day 3, etc, no other format
"""

Food_pricing = """
- The typical 3 wheat roti and sabji comes for rs. 70
"""

Sample_output = """
<Sample Output>
Intro

Day 1
-Breakfast
 -item 1 (Price)
 -item 2 (Price)
 -item 3 (Price)
-Lunch
 -item 1 (Price)
 -item 2 (Price)
 -item 3 (Price)
Dinner
 -item 1 (Price)
 -item 2 (Price)
 -item 3 (Price)

Daily Totals
- Calories
- Protein
- Carbohydrates
- Fats
- Price

Day 2
-Breakfast
 -item 1 (Price)
 -item 2 (Price)
 -item 3 (Price)
-Lunch
 -item 1 (Price)
 -item 2 (Price)
 -item 3 (Price)
Dinner
 -item 1 (Price)
 -item 2 (Price)
 -item 3 (Price)

Daily Totals
- Calories
- Protein
- Carbohydrates
- Fats
- Price

Day 3
-Breakfast
 -item 1(Price)
 -item 2(Price)
 -item 3(Price)
-Lunch
 -item 1(Price)
 -item 2(Price)
 -item 3(Price)
Dinner
 -item 1(Price)
 -item 2(Price)
 -item 3(Price)

Daily Totals
- Calories
- Protein
- Carbohydrates
- Fats
- Price

Day 4
-Breakfast
 -item 1(Price)
 -item 2(Price)
 -item 3(Price)
-Lunch
 -item 1(Price)
 -item 2(Price)
 -item 3(Price)
Dinner
 -item 1(Price)
 -item 2(Price)
 -item 3(Price)

Daily Totals
- Calories
- Protein
- Carbohydrates
- Fats
- Price

Day 5
-Breakfast
 -item 1(Price)
 -item 2(Price)
 -item 3(Price)
-Lunch
 -item 1(Price)
 -item 2(Price)
 -item 3(Price)
Dinner
 -item 1(Price)
 -item 2(Price)
 -item 3(Price)

Daily Totals
- Calories
- Protein
- Carbohydrates
- Fats
- Price

Day 6
-Breakfast
 -item 1(Price)
 -item 2(Price)
 -item 3(Price)
-Lunch
 -item 1(Price)
 -item 2(Price)
 -item 3(Price)
Dinner
 -item 1(Price)
 -item 2(Price)
 -item 3(Price)

Daily Totals
- Calories
- Protein
- Carbohydrates
- Fats
- Price

Day 7
-Breakfast
 -item 1(Price)
 -item 2(Price)
 -item 3(Price)
-Lunch
 -item 1(Price)
 -item 2(Price)
 -item 3(Price)
Dinner
 -item 1(Price)
 -item 2(Price)
 -item 3(Price)

Daily Totals
- Calories
- Protein
- Carbohydrates
- Fats
- Price

(at the end)

NOte:

Daily Macro and Micro-nutrient lists



Day 1
-Breakfast
 -item 1 (Price)
   - Calories (kcal)
   - Protein (g)
   - Carbs (g)
   - Fats (g)
   - Iron (mg)
   - Calcium (mg)
   - Vitamin C (mg)
   - Cost (₹)
 -item 2 (Price)
   - Calories (kcal)
   - Protein (g)
   - Carbs (g)
   - Fats (g)
   - Iron (mg)
   - Calcium (mg)
   - Vitamin C (mg)
   - Cost (₹)
 -item 3 (Price)
    - Calories (kcal)
   - Protein (g)
   - Carbs (g)
   - Fats (g)
   - Iron (mg)
   - Calcium (mg)
   - Vitamin C (mg)
   - Cost (₹)
-Lunch
 -item 1 (Price)
    - Calories (kcal)
   - Protein (g)
   - Carbs (g)
   - Fats (g)
   - Iron (mg)
   - Calcium (mg)
   - Vitamin C (mg)
   - Cost (₹)
 -item 2 (Price)
    - Calories (kcal)
   - Protein (g)
   - Carbs (g)
   - Fats (g)
   - Iron (mg)
   - Calcium (mg)
   - Vitamin C (mg)
   - Cost (₹)
 -item 3 (Price)
    - Calories (kcal)
   - Protein (g)
   - Carbs (g)
   - Fats (g)
   - Iron (mg)
   - Calcium (mg)
   - Vitamin C (mg)
   - Cost (₹)
Dinner
 -item 1 (Price)
    - Calories (kcal)
   - Protein (g)
   - Carbs (g)
   - Fats (g)
   - Iron (mg)
   - Calcium (mg)
   - Vitamin C (mg)
   - Cost (₹)
 -item 2 (Price)
    - Calories (kcal)
   - Protein (g)
   - Carbs (g)
   - Fats (g)
   - Iron (mg)
   - Calcium (mg)
   - Vitamin C (mg)
   - Cost (₹)
 -item 3 (Price)
    - Calories (kcal)
   - Protein (g)
   - Carbs (g)
   - Fats (g)
   - Iron (mg)
   - Calcium (mg)
   - Vitamin C (mg)
   - Cost (₹)


Day 2
-Breakfast
 -item 1 (Price)
   - Calories (kcal)
   - Protein (g)
   - Carbs (g)
   - Fats (g)
   - Iron (mg)
   - Calcium (mg)
   - Vitamin C (mg)
   - Cost (₹)
 -item 2 (Price)
   - Calories (kcal)
   - Protein (g)
   - Carbs (g)
   - Fats (g)
   - Iron (mg)
   - Calcium (mg)
   - Vitamin C (mg)
   - Cost (₹)
 -item 3 (Price)
    - Calories (kcal)
   - Protein (g)
   - Carbs (g)
   - Fats (g)
   - Iron (mg)
   - Calcium (mg)
   - Vitamin C (mg)
   - Cost (₹)
-Lunch
 -item 1 (Price)
    - Calories (kcal)
   - Protein (g)
   - Carbs (g)
   - Fats (g)
   - Iron (mg)
   - Calcium (mg)
   - Vitamin C (mg)
   - Cost (₹)
 -item 2 (Price)
    - Calories (kcal)
   - Protein (g)
   - Carbs (g)
   - Fats (g)
   - Iron (mg)
   - Calcium (mg)
   - Vitamin C (mg)
   - Cost (₹)
 -item 3 (Price)
    - Calories (kcal)
   - Protein (g)
   - Carbs (g)
   - Fats (g)
   - Iron (mg)
   - Calcium (mg)
   - Vitamin C (mg)
   - Cost (₹)
Dinner
 -item 1 (Price)
    - Calories (kcal)
   - Protein (g)
   - Carbs (g)
   - Fats (g)
   - Iron (mg)
   - Calcium (mg)
   - Vitamin C (mg)
   - Cost (₹)
 -item 2 (Price)
    - Calories (kcal)
   - Protein (g)
   - Carbs (g)
   - Fats (g)
   - Iron (mg)
   - Calcium (mg)
   - Vitamin C (mg)
   - Cost (₹)
 -item 3 (Price)
    - Calories (kcal)
   - Protein (g)
   - Carbs (g)
   - Fats (g)
   - Iron (mg)
   - Calcium (mg)
   - Vitamin C (mg)
   - Cost (₹)

Day 3
-Breakfast
 -item 1 (Price)
   - Calories (kcal)
   - Protein (g)
   - Carbs (g)
   - Fats (g)
   - Iron (mg)
   - Calcium (mg)
   - Vitamin C (mg)
   - Cost (₹)
 -item 2 (Price)
   - Calories (kcal)
   - Protein (g)
   - Carbs (g)
   - Fats (g)
   - Iron (mg)
   - Calcium (mg)
   - Vitamin C (mg)
   - Cost (₹)
 -item 3 (Price)
    - Calories (kcal)
   - Protein (g)
   - Carbs (g)
   - Fats (g)
   - Iron (mg)
   - Calcium (mg)
   - Vitamin C (mg)
   - Cost (₹)
-Lunch
 -item 1 (Price)
    - Calories (kcal)
   - Protein (g)
   - Carbs (g)
   - Fats (g)
   - Iron (mg)
   - Calcium (mg)
   - Vitamin C (mg)
   - Cost (₹)
 -item 2 (Price)
    - Calories (kcal)
   - Protein (g)
   - Carbs (g)
   - Fats (g)
   - Iron (mg)
   - Calcium (mg)
   - Vitamin C (mg)
   - Cost (₹)
 -item 3 (Price)
    - Calories (kcal)
   - Protein (g)
   - Carbs (g)
   - Fats (g)
   - Iron (mg)
   - Calcium (mg)
   - Vitamin C (mg)
   - Cost (₹)
Dinner
 -item 1 (Price)
    - Calories (kcal)
   - Protein (g)
   - Carbs (g)
   - Fats (g)
   - Iron (mg)
   - Calcium (mg)
   - Vitamin C (mg)
   - Cost (₹)
 -item 2 (Price)
    - Calories (kcal)
   - Protein (g)
   - Carbs (g)
   - Fats (g)
   - Iron (mg)
   - Calcium (mg)
   - Vitamin C (mg)
   - Cost (₹)
 -item 3 (Price)
    - Calories (kcal)
   - Protein (g)
   - Carbs (g)
   - Fats (g)
   - Iron (mg)
   - Calcium (mg)
   - Vitamin C (mg)
   - Cost (₹)

Day 4
-Breakfast
 -item 1 (Price)
   - Calories (kcal)
   - Protein (g)
   - Carbs (g)
   - Fats (g)
   - Iron (mg)
   - Calcium (mg)
   - Vitamin C (mg)
   - Cost (₹)
 -item 2 (Price)
   - Calories (kcal)
   - Protein (g)
   - Carbs (g)
   - Fats (g)
   - Iron (mg)
   - Calcium (mg)
   - Vitamin C (mg)
   - Cost (₹)
 -item 3 (Price)
    - Calories (kcal)
   - Protein (g)
   - Carbs (g)
   - Fats (g)
   - Iron (mg)
   - Calcium (mg)
   - Vitamin C (mg)
   - Cost (₹)
-Lunch
 -item 1 (Price)
    - Calories (kcal)
   - Protein (g)
   - Carbs (g)
   - Fats (g)
   - Iron (mg)
   - Calcium (mg)
   - Vitamin C (mg)
   - Cost (₹)
 -item 2 (Price)
    - Calories (kcal)
   - Protein (g)
   - Carbs (g)
   - Fats (g)
   - Iron (mg)
   - Calcium (mg)
   - Vitamin C (mg)
   - Cost (₹)
 -item 3 (Price)
    - Calories (kcal)
   - Protein (g)
   - Carbs (g)
   - Fats (g)
   - Iron (mg)
   - Calcium (mg)
   - Vitamin C (mg)
   - Cost (₹)
Dinner
 -item 1 (Price)
    - Calories (kcal)
   - Protein (g)
   - Carbs (g)
   - Fats (g)
   - Iron (mg)
   - Calcium (mg)
   - Vitamin C (mg)
   - Cost (₹)
 -item 2 (Price)
    - Calories (kcal)
   - Protein (g)
   - Carbs (g)
   - Fats (g)
   - Iron (mg)
   - Calcium (mg)
   - Vitamin C (mg)
   - Cost (₹)
 -item 3 (Price)
    - Calories (kcal)
   - Protein (g)
   - Carbs (g)
   - Fats (g)
   - Iron (mg)
   - Calcium (mg)
   - Vitamin C (mg)
   - Cost (₹)

Day 5
-Breakfast
 -item 1 (Price)
   - Calories (kcal)
   - Protein (g)
   - Carbs (g)
   - Fats (g)
   - Iron (mg)
   - Calcium (mg)
   - Vitamin C (mg)
   - Cost (₹)
 -item 2 (Price)
   - Calories (kcal)
   - Protein (g)
   - Carbs (g)
   - Fats (g)
   - Iron (mg)
   - Calcium (mg)
   - Vitamin C (mg)
   - Cost (₹)
 -item 3 (Price)
    - Calories (kcal)
   - Protein (g)
   - Carbs (g)
   - Fats (g)
   - Iron (mg)
   - Calcium (mg)
   - Vitamin C (mg)
   - Cost (₹)
-Lunch
 -item 1 (Price)
    - Calories (kcal)
   - Protein (g)
   - Carbs (g)
   - Fats (g)
   - Iron (mg)
   - Calcium (mg)
   - Vitamin C (mg)
   - Cost (₹)
 -item 2 (Price)
    - Calories (kcal)
   - Protein (g)
   - Carbs (g)
   - Fats (g)
   - Iron (mg)
   - Calcium (mg)
   - Vitamin C (mg)
   - Cost (₹)
 -item 3 (Price)
    - Calories (kcal)
   - Protein (g)
   - Carbs (g)
   - Fats (g)
   - Iron (mg)
   - Calcium (mg)
   - Vitamin C (mg)
   - Cost (₹)
Dinner
 -item 1 (Price)
    - Calories (kcal)
   - Protein (g)
   - Carbs (g)
   - Fats (g)
   - Iron (mg)
   - Calcium (mg)
   - Vitamin C (mg)
   - Cost (₹)
 -item 2 (Price)
    - Calories (kcal)
   - Protein (g)
   - Carbs (g)
   - Fats (g)
   - Iron (mg)
   - Calcium (mg)
   - Vitamin C (mg)
   - Cost (₹)
 -item 3 (Price)
    - Calories (kcal)
   - Protein (g)
   - Carbs (g)
   - Fats (g)
   - Iron (mg)
   - Calcium (mg)
   - Vitamin C (mg)
   - Cost (₹)

Day 6
-Breakfast
 -item 1 (Price)
   - Calories (kcal)
   - Protein (g)
   - Carbs (g)
   - Fats (g)
   - Iron (mg)
   - Calcium (mg)
   - Vitamin C (mg)
   - Cost (₹)
 -item 2 (Price)
   - Calories (kcal)
   - Protein (g)
   - Carbs (g)
   - Fats (g)
   - Iron (mg)
   - Calcium (mg)
   - Vitamin C (mg)
   - Cost (₹)
 -item 3 (Price)
    - Calories (kcal)
   - Protein (g)
   - Carbs (g)
   - Fats (g)
   - Iron (mg)
   - Calcium (mg)
   - Vitamin C (mg)
   - Cost (₹)
-Lunch
 -item 1 (Price)
    - Calories (kcal)
   - Protein (g)
   - Carbs (g)
   - Fats (g)
   - Iron (mg)
   - Calcium (mg)
   - Vitamin C (mg)
   - Cost (₹)
 -item 2 (Price)
    - Calories (kcal)
   - Protein (g)
   - Carbs (g)
   - Fats (g)
   - Iron (mg)
   - Calcium (mg)
   - Vitamin C (mg)
   - Cost (₹)
 -item 3 (Price)
    - Calories (kcal)
   - Protein (g)
   - Carbs (g)
   - Fats (g)
   - Iron (mg)
   - Calcium (mg)
   - Vitamin C (mg)
   - Cost (₹)
Dinner
 -item 1 (Price)
    - Calories (kcal)
   - Protein (g)
   - Carbs (g)
   - Fats (g)
   - Iron (mg)
   - Calcium (mg)
   - Vitamin C (mg)
   - Cost (₹)
 -item 2 (Price)
    - Calories (kcal)
   - Protein (g)
   - Carbs (g)
   - Fats (g)
   - Iron (mg)
   - Calcium (mg)
   - Vitamin C (mg)
   - Cost (₹)
 -item 3 (Price)
    - Calories (kcal)
   - Protein (g)
   - Carbs (g)
   - Fats (g)
   - Iron (mg)
   - Calcium (mg)
   - Vitamin C (mg)
   - Cost (₹)

Day 7
-Breakfast
 -item 1 (Price)
   - Calories (kcal)
   - Protein (g)
   - Carbs (g)
   - Fats (g)
   - Iron (mg)
   - Calcium (mg)
   - Vitamin C (mg)
   - Cost (₹)
 -item 2 (Price)
   - Calories (kcal)
   - Protein (g)
   - Carbs (g)
   - Fats (g)
   - Iron (mg)
   - Calcium (mg)
   - Vitamin C (mg)
   - Cost (₹)
 -item 3 (Price)
    - Calories (kcal)
   - Protein (g)
   - Carbs (g)
   - Fats (g)
   - Iron (mg)
   - Calcium (mg)
   - Vitamin C (mg)
   - Cost (₹)
-Lunch
 -item 1 (Price)
    - Calories (kcal)
   - Protein (g)
   - Carbs (g)
   - Fats (g)
   - Iron (mg)
   - Calcium (mg)
   - Vitamin C (mg)
   - Cost (₹)
 -item 2 (Price)
    - Calories (kcal)
   - Protein (g)
   - Carbs (g)
   - Fats (g)
   - Iron (mg)
   - Calcium (mg)
   - Vitamin C (mg)
   - Cost (₹)
 -item 3 (Price)
    - Calories (kcal)
   - Protein (g)
   - Carbs (g)
   - Fats (g)
   - Iron (mg)
   - Calcium (mg)
   - Vitamin C (mg)
   - Cost (₹)
Dinner
 -item 1 (Price)
    - Calories (kcal)
   - Protein (g)
   - Carbs (g)
   - Fats (g)
   - Iron (mg)
   - Calcium (mg)
   - Vitamin C (mg)
   - Cost (₹)
 -item 2 (Price)
    - Calories (kcal)
   - Protein (g)
   - Carbs (g)
   - Fats (g)
   - Iron (mg)
   - Calcium (mg)
   - Vitamin C (mg)
   - Cost (₹)
 -item 3 (Price)
    - Calories (kcal)
   - Protein (g)
   - Carbs (g)
   - Fats (g)
   - Iron (mg)
   - Calcium (mg)
   - Vitamin C (mg)
   - Cost (₹)
"""

Example = """
<Student Input>
1. Your age:  18
2. Gender (M/F/O):  M
3. Current weight (kg):  48
4. Height (cm):  166
5. Goal (weight_loss/muscle_gain/maintain):  muscle_gain
6. Allergies (comma separated):  none
7. City (for local food options):  pune
8. Hostel/PG/Home/Office?  PG
9. Cooking? (none/kettle/microwave/full_kitchen):  none
10. Available utensils (comma separated):  none
11. Fridge access? (none/shared/private):  none
12. Daily food budget (₹):  250
13. Where you eat (mess/dhaba/swiggy/home):  mess
14. Mess restrictions (veg_only/no_eggs/etc):  none
15. Preferred cuisines (north/south/street/etc):  none
16. Favorite foods:  none
17. Foods you hate:  none
18. Spice tolerance (low/medium/high):  high
19. Does Your Hostel/PG provide food: NO
20. How many times food does your hostel/PG provide food(Breakfast/Lunch/Dinner): (0/0/0)
</Student Input>

<Output>

In Pune, for an 18-year-old male weighing 48 kg and 166 cm tall, aiming for muscle gain with a daily budget of ₹250 and eating all meals from a mess, here's a 7-day meal plan.

---

Day 1
- Breakfast
    - Poha (₹30)
    - 2 Boiled Eggs (₹20)
- Lunch
    - 3 Roti, Dal, Sabzi (₹70)
    - Small bowl of Curd (₹10)
- Dinner
    - Chicken Curry (150g chicken) with 2 Roti (₹100)

Daily Totals
- Calories: 2200-2400 kcal
- Protein: 90-100g
- Carbohydrates: 280-300g
- Fats: 70-80g
- Price: ₹200

---

Day 2
- Breakfast
    - 2 Dosa with Sambar and Chutney (₹40)
    - 1 Banana (₹5)
- Lunch
    - 3 Roti, Mixed Vegetable Sabzi, Dal Fry (₹70)
    - Green Salad (₹10)
- Dinner
    - Egg Bhurji (2 eggs) with 2 Pav (₹60)
    - Small bowl of Sprouted Moong Dal (₹20)

Daily Totals
- Calories: 2100-2300 kcal
- Protein: 85-95g
- Carbohydrates: 270-290g
- Fats: 65-75g
- Price: ₹205

---

Day 3
- Breakfast
    - Upma with peanuts and vegetables (₹30)
    - Glass of Milk (200ml) (₹20)
- Lunch
    - Rice Plate (Rice, Dal, Veg Curry, Salad) (₹80)
    - Papad (₹5)
- Dinner
    - Paneer Bhurji (100g paneer) with 2 Roti (₹90)

Daily Totals
- Calories: 2300-2500 kcal
- Protein: 95-105g
- Carbohydrates: 290-310g
- Fats: 75-85g
- Price: ₹225

---

Day 4
- Breakfast
    - 2 Aloo Paratha with Curd (₹50)
- Lunch
    - 3 Roti, Chole, Rice (₹70)
    - Onion Salad (₹5)
- Dinner
    - Fish Curry (1 piece fish) with Rice (₹100)

Daily Totals
- Calories: 2250-2450 kcal
- Protein: 90-100g
- Carbohydrates: 280-300g
- Fats: 70-80g
- Price: ₹225

---

Day 5
- Breakfast
    - Idli Vada Sambar (2 Idli, 1 Vada) (₹40)
- Lunch
    - 3 Roti, Anda Curry (2 eggs), Salad (₹80)
- Dinner
    - Veg Pulao with Raita (₹70)
    - 1 Orange (₹10)

Daily Totals
- Calories: 2150-2350 kcal
- Protein: 80-90g
- Carbohydrates: 270-290g
- Fats: 65-75g
- Price: ₹200

---

Day 6
- Breakfast
    - Misal Pav (₹40)
- Lunch
    - 3 Roti, Soyabean Sabzi, Dal (₹70)
    - Buttermilk (₹10)
- Dinner
    - Chicken Thali (Chicken Gravy, 2 Roti, Rice) (₹110)

Daily Totals
- Calories: 2350-2550 kcal
- Protein: 100-110g
- Carbohydrates: 290-310g
- Fats: 80-90g
- Price: ₹230

---

Day 7
- Breakfast
    - Bread Omelette (2 eggs, 2 slices bread) (₹40)
    - Apple (₹15)
- Lunch
    - Thalipeeth with Curd (₹60)
- Dinner
    - Veg Kolhapuri with 3 Roti (₹80)

Daily Totals
- Calories: 2100-2300 kcal
- Protein: 80-90g
- Carbohydrates: 260-280g
- Fats: 65-75g
- Price: ₹195

---
Note: All the micros and macros are approximate and can vary based on the specific ingredients and preparation methods. Prices are approximate and can vary depending on the region and vendor in Pune. Your daily budget is ₹250, and the meal plan provides sufficient nutrition for muscle gain within this budget.

---

### Daily Macro and Micro-nutrient lists

Day 1
- Breakfast
    - Poha (₹30)
        - Calories: 200-250 kcal
        - Protein: 5-7g
        - Carbs: 40-50g
        - Fats: 5-8g
        - Iron: 2-3mg
        - Calcium: 30-40mg
        - Vitamin C: 5-10mg
        - Cost: ₹30
    - 2 Boiled Eggs (₹20)
        - Calories: 150-160 kcal
        - Protein: 12-14g
        - Carbs: 1-2g
        - Fats: 10-11g
        - Iron: 1.5-2mg
        - Calcium: 50-60mg
        - Vitamin C: 0mg
        - Cost: ₹20
- Lunch
    - 3 Roti, Dal, Sabzi (₹70)
        - Calories: 600-700 kcal
        - Protein: 20-25g
        - Carbs: 80-90g
        - Fats: 20-25g
        - Iron: 5-7mg
        - Calcium: 100-120mg
        - Vitamin C: 10-15mg
        - Cost: ₹70
    - Small bowl of Curd (₹10)
        - Calories: 60-70 kcal
        - Protein: 3-4g
        - Carbs: 4-5g
        - Fats: 3-4g
        - Iron: 0.1-0.2mg
        - Calcium: 120-150mg
        - Vitamin C: 0-1mg
        - Cost: ₹10
- Dinner
    - Chicken Curry (150g chicken) with 2 Roti (₹100)
        - Calories: 1000-1200 kcal
        - Protein: 50-60g
        - Carbs: 80-90g
        - Fats: 50-60g
        - Iron: 4-5mg
        - Calcium: 80-100mg
        - Vitamin C: 5-10mg
        - Cost: ₹100

Day 2
- Breakfast
    - 2 Dosa with Sambar and Chutney (₹40)
        - Calories: 250-300 kcal
        - Protein: 8-10g
        - Carbs: 45-55g
        - Fats: 5-8g
        - Iron: 2-3mg
        - Calcium: 40-50mg
        - Vitamin C: 5-10mg
        - Cost: ₹40
    - 1 Banana (₹5)
        - Calories: 100-110 kcal
        - Protein: 1g
        - Carbs: 25-30g
        - Fats: 0.3g
        - Iron: 0.3mg
        - Calcium: 5mg
        - Vitamin C: 10mg
        - Cost: ₹5
- Lunch
    - 3 Roti, Mixed Vegetable Sabzi, Dal Fry (₹70)
        - Calories: 600-700 kcal
        - Protein: 20-25g
        - Carbs: 80-90g
        - Fats: 20-25g
        - Iron: 5-7mg
        - Calcium: 100-120mg
        - Vitamin C: 15-20mg
        - Cost: ₹70
    - Green Salad (₹10)
        - Calories: 30-50 kcal
        - Protein: 1-2g
        - Carbs: 5-8g
        - Fats: 0-1g
        - Iron: 0.5-1mg
        - Calcium: 20-30mg
        - Vitamin C: 10-15mg
        - Cost: ₹10
- Dinner
    - Egg Bhurji (2 eggs) with 2 Pav (₹60)
        - Calories: 500-600 kcal
        - Protein: 20-25g
        - Carbs: 40-50g
        - Fats: 30-35g
        - Iron: 3-4mg
        - Calcium: 80-100mg
        - Vitamin C: 5-10mg
        - Cost: ₹60
    - Small bowl of Sprouted Moong Dal (₹20)
        - Calories: 100-120 kcal
        - Protein: 8-10g
        - Carbs: 20-25g
        - Fats: 1-2g
        - Iron: 2-3mg
        - Calcium: 30-40mg
        - Vitamin C: 5-10mg
        - Cost: ₹20

Day 3
- Breakfast
    - Upma with peanuts and vegetables (₹30)
        - Calories: 220-270 kcal
        - Protein: 6-8g
        - Carbs: 35-45g
        - Fats: 8-10g
        - Iron: 1-2mg
        - Calcium: 20-30mg
        - Vitamin C: 5-10mg
        - Cost: ₹30
    - Glass of Milk (200ml) (₹20)
        - Calories: 120-130 kcal
        - Protein: 6-7g
        - Carbs: 10-12g
        - Fats: 5-7g
        - Iron: 0.1mg
        - Calcium: 240-250mg
        - Vitamin C: 2-3mg
        - Cost: ₹20
- Lunch
    - Rice Plate (Rice, Dal, Veg Curry, Salad) (₹80)
        - Calories: 700-800 kcal
        - Protein: 25-30g
        - Carbs: 100-110g
        - Fats: 20-25g
        - Iron: 6-8mg
        - Calcium: 120-150mg
        - Vitamin C: 20-25mg
        - Cost: ₹80
    - Papad (₹5)
        - Calories: 50-60 kcal
        - Protein: 2-3g
        - Carbs: 10-12g
        - Fats: 0.5-1g
        - Iron: 0.5mg
        - Calcium: 10-15mg
        - Vitamin C: 0mg
        - Cost: ₹5
- Dinner
    - Paneer Bhurji (100g paneer) with 2 Roti (₹90)
        - Calories: 1200-1400 kcal
        - Protein: 60-70g
        - Carbs: 80-90g
        - Fats: 70-80g
        - Iron: 4-5mg
        - Calcium: 300-350mg
        - Vitamin C: 10-15mg
        - Cost: ₹90

Day 4
- Breakfast
    - 2 Aloo Paratha with Curd (₹50)
        - Calories: 400-500 kcal
        - Protein: 10-12g
        - Carbs: 50-60g
        - Fats: 15-20g
        - Iron: 2-3mg
        - Calcium: 80-100mg
        - Vitamin C: 5-10mg
        - Cost: ₹50
- Lunch
    - 3 Roti, Chole, Rice (₹70)
        - Calories: 700-800 kcal
        - Protein: 25-30g
        - Carbs: 100-110g
        - Fats: 20-25g
        - Iron: 6-8mg
        - Calcium: 100-120mg
        - Vitamin C: 10-15mg
        - Cost: ₹70
    - Onion Salad (₹5)
        - Calories: 20-30 kcal
        - Protein: 0.5-1g
        - Carbs: 4-6g
        - Fats: 0g
        - Iron: 0.2mg
        - Calcium: 10-15mg
        - Vitamin C: 5-8mg
        - Cost: ₹5
- Dinner
    - Fish Curry (1 piece fish) with Rice (₹100)
        - Calories: 1100-1300 kcal
        - Protein: 55-65g
        - Carbs: 80-90g
        - Fats: 60-70g
        - Iron: 3-4mg
        - Calcium: 70-90mg
        - Vitamin C: 5-10mg
        - Cost: ₹100

Day 5
- Breakfast
    - Idli Vada Sambar (2 Idli, 1 Vada) (₹40)
        - Calories: 300-350 kcal
        - Protein: 10-12g
        - Carbs: 50-60g
        - Fats: 8-10g
        - Iron: 2-3mg
        - Calcium: 50-60mg
        - Vitamin C: 5-10mg
        - Cost: ₹40
- Lunch
    - 3 Roti, Anda Curry (2 eggs), Salad (₹80)
        - Calories: 800-900 kcal
        - Protein: 30-35g
        - Carbs: 80-90g
        - Fats: 35-40g
        - Iron: 5-6mg
        - Calcium: 150-180mg
        - Vitamin C: 10-15mg
        - Cost: ₹80
- Dinner
    - Veg Pulao with Raita (₹70)
        - Calories: 700-800 kcal
        - Protein: 15-20g
        - Carbs: 100-110g
        - Fats: 25-30g
        - Iron: 4-5mg
        - Calcium: 80-100mg
        - Vitamin C: 10-15mg
        - Cost: ₹70
    - 1 Orange (₹10)
        - Calories: 60-70 kcal
        - Protein: 1g
        - Carbs: 15-18g
        - Fats: 0.2g
        - Iron: 0.1mg
        - Calcium: 40-50mg
        - Vitamin C: 50-60mg
        - Cost: ₹10

Day 6
- Breakfast
    - Misal Pav (₹40)
        - Calories: 350-400 kcal
        - Protein: 10-12g
        - Carbs: 45-55g
        - Fats: 15-20g
        - Iron: 3-4mg
        - Calcium: 60-70mg
        - Vitamin C: 5-10mg
        - Cost: ₹40
- Lunch
    - 3 Roti, Soyabean Sabzi, Dal (₹70)
        - Calories: 700-800 kcal
        - Protein: 30-35g
        - Carbs: 90-100g
        - Fats: 20-25g
        - Iron: 7-9mg
        - Calcium: 150-180mg
        - Vitamin C: 10-15mg
        - Cost: ₹70
    - Buttermilk (₹10)
        - Calories: 40-50 kcal
        - Protein: 2-3g
        - Carbs: 3-4g
        - Fats: 1-2g
        - Iron: 0.1mg
        - Calcium: 100-120mg
        - Vitamin C: 0-1mg
        - Cost: ₹10
- Dinner
    - Chicken Thali (Chicken Gravy, 2 Roti, Rice) (₹110)
        - Calories: 1300-1500 kcal
        - Protein: 60-70g
        - Carbs: 100-120g
        - Fats: 70-80g
        - Iron: 5-6mg
        - Calcium: 100-120mg
        - Vitamin C: 10-15mg
        - Cost: ₹110

Day 7
- Breakfast
    - Bread Omelette (2 eggs, 2 slices bread) (₹40)
        - Calories: 300-350 kcal
        - Protein: 15-18g
        - Carbs: 30-35g
        - Fats: 15-18g
        - Iron: 2-3mg
        - Calcium: 60-70mg
        - Vitamin C: 0-2mg
        - Cost: ₹40
    - Apple (₹15)
        - Calories: 90-100 kcal
        - Protein: 0.5g
        - Carbs: 22-25g
        - Fats: 0.3g
        - Iron: 0.1mg
        - Calcium: 10mg
        - Vitamin C: 8-10mg
        - Cost: ₹15
- Lunch
    - Thalipeeth with Curd (₹60)
        - Calories: 500-600 kcal
        - Protein: 20-25g
        - Carbs: 60-70g
        - Fats: 20-25g
        - Iron: 4-5mg
        - Calcium: 150-180mg
        - Vitamin C: 5-10mg
        - Cost: ₹60
- Dinner
    - Veg Kolhapuri with 3 Roti (₹80)
        - Calories: 700-800 kcal
        - Protein: 20-25g
        - Carbs: 90-100g
        - Fats: 30-35g
        - Iron: 5-6mg
        - Calcium: 120-150mg
        - Vitamin C: 15-20mg
        - Cost: ₹80
"""

app = Flask(__name__)
app.secret_key = b'\xe9\xae\xe4\xa7\x95h1:\xc8q\xe4B'

# Function to create tasks (similar to crewai.py)
def create_tasks(user_data):
    profile_user = Task(
        description=f"Process this Indian user data: {user_data}",
        expected_output="Structured dietary constraints analysis",
        agent=user_profiler
    )

    calculate_needs = Task(
        description=f"""Calculate nutrition needs for Indian context using these guidelines:
        {Result_instructions}
        {Pricing}
        {Hostel_PG_Considerations}""",
        expected_output="Daily macros using Indian foods (dal, roti, etc.) with cost breakdown",
        agent=nutrition_calculator,
        context=[profile_user]
    )

    design_meals = Task(
        description=f"""Create India-specific meal plan following these rules:
        {Diet_Plan}
        {Food_pricing}
        Sample output format: {Sample_output}""",
        expected_output="7-day plan with cost breakdown (₹ per meal) in exact required format",
        agent=meal_designer,
        context=[calculate_needs]
    )

    structured_output = Task(
        description=f"""Structure the output exactly like this example:
        {Example}
        Following all these rules:
        {Result_instructions}
        {Pricing}
        {Hostel_PG_Considerations}
        {nutritional_list}
        {Diet_Plan}""",
        expected_output="Perfectly formatted meal plan matching all requirements",
        agent=output_structurer,
        context=[design_meals]
    )
    
    return [profile_user, calculate_needs, design_meals, structured_output]


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_data = {}
        user_data['age'] = request.form.get('age')
        user_data['gender'] = request.form.get('gender')
        user_data['weight_kg'] = request.form.get('weight_kg')
        user_data['height_cm'] = request.form.get('height_cm')
        user_data['diet_type'] = request.form.get('diet_type')

        goal_val = request.form.get('goal')
        if goal_val == 'others':
            user_data['goal'] = request.form.get('goal_other', '')
        else:
            user_data['goal'] = goal_val
        
        if request.form.get('has_allergies') == 'yes':
            allergies_val = [a.strip() for a in request.form.get('allergies', '').split(',') if a.strip()]
            user_data['allergies'] = allergies_val
        else:
            user_data['allergies'] = ['none']
        
        user_data['location'] = request.form.get('location')

        living_type_val = request.form.get('living_type')
        if living_type_val == 'others':
            user_data['living_type'] = request.form.get('living_type_other', '')
        else:
            user_data['living_type'] = living_type_val
        
        user_data['daily_budget'] = request.form.get('daily_budget')

        food_sources_list = request.form.getlist('food_sources')
        if 'others' in food_sources_list:
            other_food_sources = [f.strip() for f in request.form.get('food_sources_other', '').split(',') if f.strip()]
            food_sources_list = [f for f in food_sources_list if f != 'others'] + other_food_sources
        if not food_sources_list:
            food_sources_list = ['none']
        user_data['food_sources'] = food_sources_list

        # Add default values for fields not asked in the simplified form
        user_data['cooking_access'] = user_data.get('cooking_access', 'none')
        user_data['utensils'] = user_data.get('utensils', ['none'])
        user_data['food_storage'] = user_data.get('food_storage', 'none')
        user_data['mess_rules'] = user_data.get('mess_rules', ['none'])
        user_data['cuisines'] = user_data.get('cuisines', ['none'])
        user_data['favorite_foods'] = user_data.get('favorite_foods', ['none'])
        user_data['hated_foods'] = user_data.get('hated_foods', ['none'])
        user_data['spice_level'] = user_data.get('spice_level', 'medium')
        user_data['hostel_provides_food'] = user_data.get('hostel_provides_food', 'NO')
        user_data['hostel_food_times'] = user_data.get('hostel_food_times', '0/0/0')
        
        print(f"[DEBUG] Final user data for meal plan generation: {user_data}")

        meal_plan_result = generate_meal_plan_backend(user_data)
        session['meal_plan_content'] = str(meal_plan_result)
        return redirect(url_for('meal_plan_display'))
    
    return render_template('index.html')

def generate_meal_plan_backend(user_input):
    # Retrieve all user data directly from the passed argument
    crew = Crew(
        agents=[user_profiler, nutrition_calculator, meal_designer, output_structurer],
        tasks=create_tasks(user_input),
        verbose=True
    )
    
    result = crew.kickoff()
    # Assuming the final structured output is the raw_output of the last task
    # The 'output_structurer' task should have the final formatted string
    if result and hasattr(result, 'tasks_outputs') and result.tasks_outputs:
        # Find the output of the 'output_structurer' task
        for task_output in result.tasks_outputs:
            if task_output.description.startswith('Structure the output exactly like this example'):
                return task_output.raw_output
        # Fallback if the specific task is not found, or take the last task's output
        return result.tasks_outputs[-1].raw_output
    return str(result) if result else 'No meal plan generated.'

@app.route('/meal_plan_display')
def meal_plan_display():
    meal_plan_content = session.pop('meal_plan_content', 'No meal plan generated.')
    session.clear() # Clear all session data after displaying
    return render_template('output.html', meal_plan_content=meal_plan_content)

if __name__ == '__main__':
    app.run(debug=True)
