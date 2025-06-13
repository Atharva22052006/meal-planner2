# Meal Planner API

A Flask-based API for meal planning using CrewAI.

## Deployment on Render

1. Fork this repository
2. Create a new Web Service on Render
3. Connect your GitHub repository
4. Add the following environment variables in Render:
   - `GOOGLE_API_KEY`: Your Google API key
   - Any other environment variables your app needs

## Local Development

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up environment variables
4. Run the application:
   ```
   python app.py
   ```

## API Endpoints

- `/generate_meal_plan`: Generate a meal plan based on user preferences
- `/get_recipe`: Get detailed recipe information 