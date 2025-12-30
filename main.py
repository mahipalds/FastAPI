from fastapi import FastAPI
import json

app = FastAPI() #Defining Fast api object

# Open and Load jason data
def load_data():   
    with open("consultant.json", "r") as f:
        data = json.load(f)
        return data 

#homepage
@app.get("/")
def home():
    return {
        "message": "Welcome to the Consultant Management API! This system helps HR and staffing teams manage consultant information, including pay rates, billing rates, skills, and profit analysis for effective recruitment and project planning."
    }

# About endpoint
@app.get("/about")
def about():
    return {
        "api_name": "Staffing & HR Management API",
        "version": "1.0",
        "description": "This API is designed for HR and staffing professionals to manage consultant data efficiently. It includes detailed information on consultants such as name, location, gender, pay rate, billing rate, margin, expenses, profit, and skills. Use this system to streamline recruitment, optimize staffing decisions, and track consultant profitability.",
        "author": "Mahipal Singh"
    }

#endpoint for view complete consultant data
@app.get("/view")
def view():
    consultant_data = load_data()
    return consultant_data 
