from fastapi import FastAPI, Path, HTTPException, Query
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

#creating dynamic path to view any particular consultant data
@app.get("/consultant/{consultant_id}")
def view_consultant(consultant_id: str = Path(...,description="ID of the consultant in the database", example="C01")):
    data = load_data()
    if consultant_id in data:
        return data[consultant_id]
    raise HTTPException(status_code=404, detail="Consultant not found")

#creating endpoint to view consultant data in sorted way 
@app.get("/sort")
def sort_consultant(sort_by: str =Query(..., description= "Sort on the basis of pay rate, bill rate, or Margin"), order: str = Query('asc', description='Sort in asc or desc order')):
    
    valid_fields = ['pay_rate','billing_rate','margin']
    
    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f'Invalid Field, select from {valid_fields}')
    
    if order not in ['asc','desc']:
        raise HTTPException(status_code=400, detail='Invalid Order select b/w asc and desc')
    
    data = load_data()

    sort_order= True if order == 'desc' else False 

    sorted_data = sorted(data.values(), key = lambda x: x.get(sort_by, 0), reverse= sort_order)

    return sorted_data