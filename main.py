from fastapi import FastAPI, Path, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal, Optional
import json

app = FastAPI() #Defining Fast api object

#creating pydantic model for for validating and structuring incoming consultant data
class Consultant(BaseModel):
    id: Annotated[str, Field(..., description = 'ID of Consultant', examples= ['C01'])] 
    name: Annotated[str, Field(..., description= 'Name of the Consultant',  examples= ['John'])]
    city: Annotated[str, Field(..., description= 'Current city of the Consultant', examples= ['Dallas'])]
    gender: Annotated[Literal['Male', 'Female', 'Others'], Field(..., description= 'Gender of the Consultant')]
    pay_rate: Annotated[float, Field(..., gt= 0, description= 'Pay rate of consultant in doller per hour')] 
    billing_rate: Annotated[float, Field(..., gt= 0, description= 'Billing rate of the client for the consultant in doller per hour')] 

    @computed_field
    @property
    def margin(self) -> float:
        margin= round(self.billing_rate - self.pay_rate , 2)
        return margin 
    
    @computed_field
    @property
    def expense(self) -> float:
        expense = round(((self.pay_rate) * 10) / 100, 2)
        return expense 
    
    @computed_field
    @property
    def profit(self) -> float:
        profit= round(self.billing_rate - (self.pay_rate + self.expense), 2)
        return profit 

#Creating Pydantic model for update the consultant details in the database
class ConsultatntUpdate(BaseModel):
    name: Annotated[Optional[str], Field(default= None)] 
    city: Annotated[Optional[str], Field(default= None)]
    gender: Annotated[Optional[Literal['Male', 'Female', 'Others']], Field(default= None)] 
    pay_rate: Annotated[Optional[float], Field(default= None, gt= 0)]
    billing_rate: Annotated[Optional[float], Field(default= None, gt= 0)]



# Open and Load json data
def load_data():   
    with open("consultant.json", "r") as f:
        data = json.load(f)
        return data 
    
# saving dict file into json format 
def save_data(data):
    with open('consultant.json', 'w') as f:
        json.dump(data, f) 

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
def sort_consultant(sort_by: str =Query(..., description= "Sort on the basis of pay rate, billing rate, or Margin"), order: str = Query('asc', description='Sort in asc or desc order')):
    valid_fields = ['pay_rate','billing_rate','margin']
    
    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f'Invalid Field, select from {valid_fields}')
    
    if order not in ['asc','desc']:
        raise HTTPException(status_code=400, detail='Invalid Order select b/w asc and desc')
    
    data = load_data()
    sort_order= True if order == 'desc' else False 
    sorted_data = sorted(data.values(), key = lambda x: x.get(sort_by, 0), reverse= sort_order)
    return sorted_data



# Creating an API endpoint to add new consultant data to the database 
@app.post('/create')
def create_consultant(consultant: Consultant):
    #loading data
    data = load_data()
    #check the consultant already exists 
    if consultant.id in data:
        raise HTTPException(status_code= 400, detail= 'Consultant already exists')
    #add new consultant to the data base 
    data[consultant.id] = consultant.model_dump(exclude=['id']) #model_dump-convert json file into dict 
    # Save the updated data to the JSON file
    save_data(data) 
    return JSONResponse(status_code= 201, content= {'message': 'Consultant created successfully'})


# Creating an API endpoint to update existing consultant data to the database 
@app.put('/edit/{consultant_id}')
def update_consultant(consultant_id: str, consultant_update: ConsultatntUpdate):
    data = load_data()
    # Check if the consultant exists; raise an error if not found
    if consultant_id not in data:
        raise HTTPException(status_code= 404, detail= 'Consultant not found')
    
     # Retrieve current consultant information for the given ID
    existing_consultant_info = data[consultant_id]
    # Extract only the fields provided in the update request
    updated_consultant_info = consultant_update.model_dump(exclude_unset= True)
     # Update only the provided fields in the existing consultant record
    for key, value in updated_consultant_info.items():
        existing_consultant_info[key] = value 

    # Add consultant ID back to the data for Pydantic validation and computed fields
    existing_consultant_info['id']=consultant_id
    # Convert updated data into a Pydantic model to re-validate and recalculate
    # computed fields such as margin, expense, and profit
    consultant_pydantic_obj = Consultant(**existing_consultant_info)   

    # Convert the validated Pydantic object back to a dictionary
    # excluding the ID before storing it in the database
    existing_consultant_info = consultant_pydantic_obj.model_dump(exclude='id')

    # Save the updated consultant record back to the database
    data[consultant_id] = existing_consultant_info

    # Save the updated data to the JSON file
    save_data(data)

    return JSONResponse(status_code= 200, content= {'message': 'Consultant Updated'})


# Creating an API endpoint to delete existing consultant data from the database 
@app.delete('/delete/{consultant_id}')
def delete_consultant(consultant_id: str):
    data = load_data()
    if consultant_id not in data:
        raise HTTPException(status_code= 404, detail= 'Consultant Not Found')

    del data[consultant_id]
    save_data(data) # Save the updated data to the JSON file
    return JSONResponse(status_code= 200, content= {'message': 'Consultant Deleted'})
