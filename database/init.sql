CREATE Table "users"(
  user_id text PRIMARY KEY,
  user_location text
);

CREATE Table "orders" (
  order_id SERIAL PRIMARY KEY ,
  restaurant_id int,
  order_cutoff text,
  user_id text
);

CREATE Table "restaurants" (
  restaurant_id SERIAL PRIMARY KEY,
  restaurant_name text 
);

CREATE Table "restaurantTags" (
  id SERIAL PRIMARY KEY,
  restaurant_id int,
  user_id text
);

ALTER TABLE "orders" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("user_id");
ALTER TABLE "orders" ADD FOREIGN KEY ("restaurant_id") REFERENCES "restaurants"("restaurant_id");
ALTER TABLE "restaurantTags" ADD FOREIGN KEY ("restaurant_id") REFERENCES 
"restaurants"("restaurant_id");
ALTER TABLE "restaurantTags" ADD FOREIGN KEY ("user_id") REFERENCES 
"users"("user_id");



INSERT INTO users ("user_id","user_location")
VALUES
('ivanleomk','Yale-NUS'),
('ZHAOOOOOO','Yale-NUS'),
('Lemistletoe','Yale-NUS'),
('Aadi','Yale-NUS'),
('Leonard','Yale-NUS'),
('ABCDE','Tembusu');

INSERT INTO restaurants ("restaurant_name")
VALUES
('Al Amaan Restaurant'),
('MacDonalds'),
('Burger King'),
('Super Snacks'),
('Bee Fong Wanton Mee');