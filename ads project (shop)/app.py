# app.py
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import json
from collections import deque, defaultdict

app = Flask(__name__)

# Predefined items with their values, weights, and prices
ITEMS = [
    {"id": 1, "name": "Milk", "value": 8, "weight": 2, "price": 3.50},
    {"id": 2, "name": "Bread", "value": 7, "weight": 1, "price": 2.50},
    {"id": 3, "name": "Eggs", "value": 9, "weight": 1, "price": 3.00},
    {"id": 4, "name": "Cheese", "value": 10, "weight": 3, "price": 5.00},
    {"id": 5, "name": "Apples", "value": 6, "weight": 2, "price": 4.00},
    {"id": 6, "name": "Chicken", "value": 10, "weight": 4, "price": 7.50},
    {"id": 7, "name": "Rice", "value": 7, "weight": 3, "price": 2.00},
    {"id": 8, "name": "Pasta", "value": 6, "weight": 2, "price": 1.50},
    {"id": 9, "name": "Tomatoes", "value": 7, "weight": 1, "price": 3.00},
    {"id": 10, "name": "Cereal", "value": 5, "weight": 2, "price": 4.50},
    {"id": 11, "name": "Coffee", "value": 9, "weight": 1, "price": 6.00},
    {"id": 12, "name": "Sugar", "value": 4, "weight": 2, "price": 2.00},
    {"id": 13, "name": "Flour", "value": 3, "weight": 3, "price": 1.50},
    {"id": 14, "name": "Butter", "value": 8, "weight": 1, "price": 4.00},
    {"id": 15, "name": "Yogurt", "value": 6, "weight": 2, "price": 3.50},
]

# Item hashmap for O(1) lookup
item_map = {item["id"]: item for item in ITEMS}

@app.route('/')
def index():
    return render_template('index.html', items=ITEMS)

# BFS algorithm to find all combinations that meet criteria
def bfs_find_items(max_weight, max_price):
    results = []
    visited = set()
    queue = deque([([], 0, 0, 0, 0)])  # (items, total_weight, total_price, total_value, current_idx)
    
    while queue:
        current_items, weight, price, value, idx = queue.popleft()
        
        # Skip if we've seen this state before
        state = (tuple(sorted(current_items)), idx)
        if state in visited:
            continue
        visited.add(state)
        
        # If valid combination, add to results
        if current_items:
            results.append({
                "items": [item_map[item_id] for item_id in current_items],
                "total_weight": weight,
                "total_price": price,
                "total_value": value
            })
        
        # Try adding each remaining item
        for i in range(idx, len(ITEMS)):
            item = ITEMS[i]
            new_weight = weight + item["weight"]
            new_price = price + item["price"]
            
            # Only add if it doesn't exceed constraints
            if new_weight <= max_weight and new_price <= max_price:
                new_items = current_items + [item["id"]]
                queue.append((new_items, new_weight, new_price, value + item["value"], i + 1))
    
    # Sort by value (descending)
    results.sort(key=lambda x: x["total_value"], reverse=True)
    return results

# DFS algorithm to find all combinations that meet criteria
def dfs_find_items(max_weight, max_price):
    results = []
    visited = set()
    
    def dfs(current_items, weight, price, value, idx):
        # Skip if we've seen this state before
        state = (tuple(sorted(current_items)), idx)
        if state in visited:
            return
        visited.add(state)
        
        # If valid combination, add to results
        if current_items:
            results.append({
                "items": [item_map[item_id] for item_id in current_items],
                "total_weight": weight,
                "total_price": price,
                "total_value": value
            })
        
        # Try adding each remaining item
        for i in range(idx, len(ITEMS)):
            item = ITEMS[i]
            new_weight = weight + item["weight"]
            new_price = price + item["price"]
            
            # Only add if it doesn't exceed constraints
            if new_weight <= max_weight and new_price <= max_price:
                new_items = current_items + [item["id"]]
                dfs(new_items, new_weight, new_price, value + item["value"], i + 1)
    
    dfs([], 0, 0, 0, 0)
    
    # Sort by value (descending)
    results.sort(key=lambda x: x["total_value"], reverse=True)
    return results

# Knapsack algorithm to find the optimal combination
def knapsack_find_items(max_weight, max_price):
    # We'll use a 3D DP table: [price][weight][item_index]
    # Each cell contains the maximum value achievable
    
    # Convert price to an integer (multiply by 100 to handle cents)
    max_price_int = int(max_price * 100)
    
    # Initialize DP table
    dp = [[[-1 for _ in range(len(ITEMS) + 1)] for _ in range(max_weight + 1)] for _ in range(max_price_int + 1)]
    chosen = [[[[] for _ in range(len(ITEMS) + 1)] for _ in range(max_weight + 1)] for _ in range(max_price_int + 1)]
    
    def solve(p, w, i):
        # Base cases
        if i == 0:
            return 0
        
        # If we've already computed this state
        if dp[p][w][i] != -1:
            return dp[p][w][i]
        
        # If this item is too heavy or expensive, skip it
        item = ITEMS[i-1]
        item_price_int = int(item["price"] * 100)
        if item["weight"] > w or item_price_int > p:
            dp[p][w][i] = solve(p, w, i-1)
            chosen[p][w][i] = chosen[p][w][i-1].copy()
            return dp[p][w][i]
        
        # Otherwise, we have two choices: take it or leave it
        leave_value = solve(p, w, i-1)
        take_value = item["value"] + solve(p - item_price_int, w - item["weight"], i-1)
        
        if take_value > leave_value:
            dp[p][w][i] = take_value
            chosen[p][w][i] = chosen[p - item_price_int][w - item["weight"]][i-1] + [item["id"]]
        else:
            dp[p][w][i] = leave_value
            chosen[p][w][i] = chosen[p][w][i-1].copy()
        
        return dp[p][w][i]
    
    # Solve the knapsack problem
    max_value = solve(max_price_int, max_weight, len(ITEMS))
    
    # Retrieve the chosen items
    chosen_ids = chosen[max_price_int][max_weight][len(ITEMS)]
    chosen_items = [item_map[item_id] for item_id in chosen_ids]
    
    # Calculate the totals
    total_weight = sum(item["weight"] for item in chosen_items)
    total_price = sum(item["price"] for item in chosen_items)
    total_value = sum(item["value"] for item in chosen_items)
    
    return [{
        "items": chosen_items,
        "total_weight": total_weight,
        "total_price": total_price,
        "total_value": total_value
    }]

@app.route('/optimize', methods=['POST'])
def optimize():
    data = request.json
    max_weight = int(data.get('max_weight', 10))
    max_price = float(data.get('max_price', 20.0))
    algorithm = data.get('algorithm', 'knapsack')
    
    if algorithm == 'bfs':
        results = bfs_find_items(max_weight, max_price)
    elif algorithm == 'dfs':
        results = dfs_find_items(max_weight, max_price)
    else:  # default to knapsack
        results = knapsack_find_items(max_weight, max_price)
    
    return jsonify(results[:10])  # Return top 10 results




@app.route('/item/<int:item_id>')
def get_item(item_id):
    if item_id in item_map:
        return jsonify(item_map[item_id])
    return jsonify({"error": "Item not found"}), 404



if __name__ == '__main__':
    app.run(debug=True)
