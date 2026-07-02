from sqlalchemy import create_engine
import pandas as pd
import numpy as np 
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
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

features = customer_features[
    [
        "Orders_Frequency",
        "Total_Spending",
        "Average_Order_Value",
        
        "Recency",
        "Shipping_Delay"
    ]
]



StandardScaler = StandardScaler()

X = StandardScaler.fit_transform(features)


inertia = []

for k in range(2, 11):
    model = KMeans(n_clusters=k, random_state=42 , n_init=10)
    model.fit(X)
    inertia.append(model.inertia_)

plt.plot(range(2,11), inertia, marker='o')
plt.xlabel("Number of Clusters")
plt.ylabel("Inertia")
plt.show()


k_means = KMeans(
    n_clusters=4,
    random_state=42,
    n_init=10
)

customer_features["Cluster"] = k_means.fit_predict(X)


cluster_summary = (
    customer_features
    .groupby("Cluster")[
        [
            "Total_Spending",
            "Orders_Frequency",
            "Average_Order_Value",
            "Recency"
        ]
    ]
    .mean()
)


print("#Clusters_summary#")
print(cluster_summary)



cluster_names = {
    0: "VIP",
    1: "At-Risk",
    2: "Regular",
    3: "New"
}

cluster_score = cluster_summary.copy()
# avoid dominator 
# 1. Initialize the scaler
scaler = MinMaxScaler()
# 2. Define the columns to scale
numerical_cols =cluster_summary.columns.tolist()
# 3. Scale the data and create new columns
scaled_features = scaler.fit_transform(cluster_score[numerical_cols])

# 4. Assign back to your DataFrame

cluster_score["Score"] = (
    cluster_summary["Total_Spending"]+
    cluster_summary["Orders_Frequency"]  
)
best_cluster = cluster_score["Score"].idxmax()

print("Best cluster:", cluster_names[best_cluster])
print(cluster_score.loc[best_cluster])


customer_features["Customer_level"] = (
    customer_features["Cluster"].map(cluster_names)
)
print(customer_features.head(10))


best_customers = customer_features[
    customer_features["Customer_level"] == cluster_names[best_cluster]
]
print(best_customers.head(10))


def predict_random_row_cluster():
    
    random_sample = customer_features.sample(n=1, random_state=None) 
    row_index = random_sample.index[0]
    
    # 2. Extract only the exact features used during training
    feature_cols = ["Orders_Frequency", "Total_Spending", "Average_Order_Value", "Recency", "Shipping_Delay"]
    sample_features = random_sample[feature_cols]
    
    # 3. Scale the single row using your already fitted StandardScaler
    scaled_sample = StandardScaler.transform(sample_features)
    
    # 4. Predict the cluster ID and get its text name
    predicted_cluster_id = k_means .predict(scaled_sample)[0]
    customer_level = cluster_names[predicted_cluster_id]
    
    # 5. Calculate soft-clustering percentages using distance metrics
    # kmeans.transform returns the Euclidean distance to all 4 cluster centers
    distances = k_means .transform(scaled_sample)[0]
    
    # Invert the distances (closer distance = higher percentage match)
    inverted_distances = 1.0 / (distances + 1e-6)
    match_percentages = (inverted_distances / inverted_distances.sum()) * 100
    
    # --- Print Beautiful Results Summary ---
    print(f"==================================================")
    print(f"RANDOM ROW PERFORMANCE TEST (Row Index: {row_index})")
    print(f"==================================================")
    print(f"Assigned cluster Level: **{cluster_names[predicted_cluster_id]}** (Cluster ID: {predicted_cluster_id})")
    print(random_sample.T)
    
    

predict_random_row_cluster()

#__________________________________________________________________
#higest region revenue
region_revenue = (customer_features.groupby("Region")["Total_Spending"].sum())

print ("region_revenue",region_revenue.to_dict())

highest_revenue = region_revenue.max()
highest_region_revenue = region_revenue[region_revenue == highest_revenue].index[0]

print("Highest region revenue:",highest_region_revenue ,highest_revenue)

#average delay by region 
region_delay = customer_features.groupby("Region")["Shipping_Delay"].mean()
print ("region_delay",region_delay.to_dict())

highest_delay = region_delay.max()
highest_region_delay = region_delay[region_delay == highest_delay].index[0]

print("Highest region delay:",highest_region_delay ,math.ceil(highest_delay))

