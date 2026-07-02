from sqlalchemy import create_engine
import pandas as pd
import numpy as np 
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression 
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score , mean_absolute_error,mean_squared_error,root_mean_squared_error
from sklearn.preprocessing import PolynomialFeatures
import matplotlib.pyplot as plt
import random 
import math
conn = create_engine(
    "postgresql://postgres:postgres 26@localhost:5432/intellishift"
)

customers = pd.read_sql_table("customers", conn)
orders = pd.read_sql_table("orders", conn)
locations = pd.read_sql_table("locations", conn)
shipping_modes = pd.read_sql_table("shipping_modes", conn)
order_items = pd.read_sql_table("order_items", conn)
products = pd.read_sql_table("products", conn)
subcategories = pd.read_sql_table("subcategories", conn)
categories = pd.read_sql_table("categories", conn)

print(customers.columns.tolist())


#merge tables
df = (
    orders
    .merge(customers, on="customer_id", how="left")
    .merge(locations, on="location_id", how="left")
    .merge(shipping_modes, on="shipping_id", how="left")
    .merge(order_items, on="order_id", how="left")
    .merge(products, on="product_id", how="left")
    .merge(subcategories, on="subcategory_id", how="left")
    .merge(categories, on="category_id", how="left")
)


#calculate delays
df["order_date"] = pd.to_datetime(df["order_date"])
df["ship_date"] = pd.to_datetime(df["ship_date"])

df["shipping_delay"]= (df["ship_date"] - df["order_date"]).dt.days


reference_date= df["order_date"].max() + pd.Timedelta(days=1)

customer_features = (
    df.groupby("customer_id")
      .agg(
          Customer_Name=("customer_name", "first"),

          Segment=("segment", "first"),

          Region=("region", "first"),

          Country=("country", "first"),

          Orders_Frequency=("order_id", "nunique"),

          Total_Spending=("sales", "sum"),
          

          Last_Purchase_Date=("order_date", "max"),

          Shipping_Delay=("shipping_delay", "mean"),

          Preferred_Product_Category=(
              "category_name",
              lambda x: x.mode().iloc[0]
          ),

         
          Recency=(
              "order_date",
              lambda x: (reference_date - x.max()).days
          )
      )
      .reset_index()
)

customer_features["Average_Order_Value"] = (
    customer_features["Total_Spending"] /
    customer_features["Orders_Frequency"].replace(0, 1)
)


#_______________________________________________
#encoding
cat_columns =["Segment", "Region", "Country" ,"Preferred_Product_Category"] 
customer_features_encoded={}
for col in cat_columns:
    print(f"--- Unique values in '{col}' ---")
    unique_values=customer_features[col].unique()
    print(unique_values)
    print("\n")

Cat_customer_features = pd.get_dummies(
    customer_features, 
    columns=cat_columns, 
    drop_first=True, 
    dtype=int
)

#CLV 
print("#CLV#")


X = customer_features[
    [
         
        "Shipping_Delay",
        "Average_Order_Value",
        "Orders_Frequency",
        "Recency"
        
    ]
]

scaler = StandardScaler()

X = scaler.fit_transform(X)

y = customer_features["Total_Spending"]

X=pd.concat([customer_features, Cat_customer_features], axis=1)

X = X.select_dtypes(include=['number'])
X.columns = X.columns.astype(str)

print("X shape:", X.shape)
print("y shape:", y.shape)
x_train, x_test , y_train ,y_test =train_test_split(X, y, test_size=0.2, random_state=42)


regressor= RandomForestRegressor(n_estimators=100, random_state=42)
regressor.fit(x_train,y_train)

y_pred = regressor.predict(x_test)

# Model evaluation using R-squared metric

r2 = r2_score(y_test, y_pred)

print("R-squared: ", r2)

mae = mean_absolute_error(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
rmse = root_mean_squared_error(y_test, y_pred)

print("MAE:", mae)
print("MSE:", mse)
print("RMSE:", rmse)

comparison = pd.DataFrame({
    "Actual": y_test.values,
    "Predicted": y_pred ,
    "percentage_error": (np.abs((y_test.values - y_pred)) / y_test.values )* 100
})

print(comparison.head(15))


residuals = y_test - y_pred
plt.figure(figsize=(6,4))
plt.scatter(y_pred, residuals)
plt.axhline(0, color='red')
plt.xlabel("Predicted")
plt.ylabel("Residual")
plt.show()




#test 
def test_single_customer_spending(model=regressor ):
    row_index = random.randint(0,len(x_test)-1)
    
    single_x = x_test.iloc[[row_index]]
    actual_Spending = y_test.iloc[row_index]
    
    predicted_spending = model.predict(single_x)[0]
    if predicted_spending < 0: predicted_spending = 0 # Ground lower bound to 0
    
    #  Calculate Risk Percentage based on the maximum known delay
    percentage_error= percentage_error = (
        abs(actual_Spending - predicted_spending)/ actual_Spending ) * 100
    
    
    print("\n=== Calculated customer_Spending ===")
    print(f"Test Row Index Reference: {row_index}")
    print(f"Actual Observed Spending  : {actual_Spending:.2f} units")
    print(f"Model Predicted Spending  : {predicted_spending:.2f} units")
    print(f"Calculated customer_Spending  Error  : {percentage_error:.2f}%")
    
    return predicted_spending, percentage_error

test_single_customer_spending()


###PolynomialFeatures
print("###Polynomial")
poly = PolynomialFeatures(degree=3)
x_poly = poly.fit_transform(x_train)
x_test_poly = poly.transform(x_test)
# Fit the linear regression model to the polynomial features
model = LinearRegression()
model.fit(x_poly, y_train)

# Evaluate the model on the original data
y_pred = model.predict(x_test_poly)

r2 = r2_score(y_test, y_pred)
print("R-squared: ", r2)

mae = mean_absolute_error(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
rmse = root_mean_squared_error(y_test, y_pred)

print("MAE:", mae)
print("MSE:", mse)
print("RMSE:", rmse)

comparison = pd.DataFrame({
    "Actual": y_test.values,
    "Predicted": y_pred ,
    "percentage_error": (np.abs((y_test.values - y_pred)) / y_test.values )* 100
})

print(comparison.head(15))


residuals = y_test - y_pred
plt.figure(figsize=(6,4))
plt.scatter(y_pred, residuals)
plt.axhline(0, color='red')
plt.xlabel("Predicted")
plt.ylabel("Residual")
plt.show()


### Delay prediction
print ("### Delay prediction")
X = customer_features[
    [
         
        "Total_Spending",
        "Average_Order_Value",
        "Orders_Frequency",
        "Recency",
       
    ]
]

scaler = StandardScaler()

X = scaler.fit_transform(X)

y = customer_features["Shipping_Delay"]

X=pd.concat([customer_features, Cat_customer_features], axis=1)

X = X.select_dtypes(include=['number'])
X.columns = X.columns.astype(str)

print("X shape:", X.shape)
print("y shape:", y.shape)



x_train, x_test , y_train ,y_test =train_test_split(X, y, test_size=0.2, random_state=42)
regressor = RandomForestRegressor(random_state=42)

regressor.fit(x_train, y_train)

# Keep predictions as an array for evaluation
y_pred = regressor.predict(x_test)

r2 = r2_score(y_test, y_pred)

mae = mean_absolute_error(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
rmse = root_mean_squared_error(y_test, y_pred)

# Round only for display
display_pred = np.round(y_pred).astype(int)

max_possible_delay = customer_features["Shipping_Delay"].max()

delay_risk_percentage = (display_pred / max_possible_delay) * 100
delay_risk_percentage = np.clip(delay_risk_percentage, 0, 100)

results = pd.DataFrame({
    "Actual_Delay": np.round(y_test).astype(int),
    "Predicted_Delay": display_pred,
    "Risk_Percentage": delay_risk_percentage
})

print(results.head(10))

print("R-squared: ", r2)
print("MAE:", mae)
print("MSE:", mse)
print("RMSE:", rmse)

residuals = y_test - y_pred
plt.figure(figsize=(6,4))
plt.scatter(y_pred, residuals)
plt.axhline(0, color='red')
plt.xlabel("Predicted")
plt.ylabel("Residual")
plt.show()


def test_single_delivery_delay():
    row_index = random.randint(0,len(x_test)-1)
    max_delay_value= customer_features["Shipping_Delay"].max()

    single_x = x_test.iloc[[row_index]]
    actual_delay = y_test.iloc[row_index]
    
    predicted_delay  = regressor.predict(single_x)[0]
    if predicted_delay < 0: predicted_delay = 0 # Ground lower bound to 0
    
    #  Calculate Risk Percentage based on the maximum known delay
    risk_percentage = (predicted_delay / max_delay_value) * 100
    if risk_percentage > 100: risk_percentage = 100.0
    
    print("\n=== Single Row Delay Regression Test ===")
    print(f"Test Row Index Reference: {row_index}")
    print(f"Actual Observed Delay  : {actual_delay:.2f} units")
    print(f"Model Predicted Delay  : {predicted_delay:.2f} units")
    print(f"Calculated Delay Risk  : {risk_percentage:.2f}%")
    
    return predicted_delay, risk_percentage



# Test 

test_single_delivery_delay()
