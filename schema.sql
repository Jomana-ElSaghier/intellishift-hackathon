CREATE TABLE "customers" (
  "customer_id" varchar PRIMARY KEY,
  "customer_name" varchar,
  "segment" varchar
);

CREATE TABLE "locations" (
  "location_id" serial PRIMARY KEY,
  "country" varchar,
  "region" varchar,
  "state" varchar,
  "city" varchar,
  "postal_code" varchar
);

CREATE TABLE "shipping_modes" (
  "shipping_id" serial PRIMARY KEY,
  "ship_mode" varchar UNIQUE
);

CREATE TABLE "categories" (
  "category_id" serial PRIMARY KEY,
  "category_name" varchar UNIQUE
);

CREATE TABLE "subcategories" (
  "subcategory_id" serial PRIMARY KEY,
  "subcategory_name" varchar,
  "category_id" int
);

CREATE TABLE "products" (
  "product_id" varchar PRIMARY KEY,
  "product_name" varchar,
  "subcategory_id" int
);

CREATE TABLE "orders" (
  "order_id" varchar PRIMARY KEY,
  "customer_id" varchar,
  "location_id" int,
  "shipping_id" int,
  "order_date" date,
  "ship_date" date
);

CREATE TABLE "order_items" (
  "order_item_id" serial PRIMARY KEY,
  "row_id" int UNIQUE,
  "order_id" varchar,
  "product_id" varchar,
  "sales" decimal
);

ALTER TABLE "orders" ADD FOREIGN KEY ("customer_id") REFERENCES "customers" ("customer_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "orders" ADD FOREIGN KEY ("location_id") REFERENCES "locations" ("location_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "orders" ADD FOREIGN KEY ("shipping_id") REFERENCES "shipping_modes" ("shipping_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "products" ADD FOREIGN KEY ("subcategory_id") REFERENCES "subcategories" ("subcategory_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "subcategories" ADD FOREIGN KEY ("category_id") REFERENCES "categories" ("category_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "order_items" ADD FOREIGN KEY ("order_id") REFERENCES "orders" ("order_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "order_items" ADD FOREIGN KEY ("product_id") REFERENCES "products" ("product_id") DEFERRABLE INITIALLY IMMEDIATE;
