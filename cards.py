CHANCE_CARDS = {
    1: {"desc": "Gain $3M", "cap_mod": 3},
    2: {"desc": "-$1M per ship", "cost_mod": -1, "min_price": 1},
    3: {"desc": "-1 demand", "dem_mod": -1, "min_dem": 1},
    4: {"desc": "Gain 2pts", "pts_mod": 2},
    5: {"desc": "No penalty if unsupplied", "special": "no_penalty"},
    6: {"desc": "Pay $2M", "cap_mod": -2, "fail_penalty": -1},
    7: {"desc": "+$1M per ship", "cost_mod": 1},
    8: {"desc": "+1 demand", "dem_mod": 1},
    9: {"desc": "Deduct 2 pts", "pts_mod": -2},
    10: {"desc": "Pay $1M", "cap_mod": -1, "fail_penalty": -1}
}

SITUATION_CARDS = {
    # Format: [Demand, Price, Type]
    1: {"A": [2, 1, "normal"], "B": [1, 1, "normal"]},
    2: {"A": [3, 2, "normal"], "B": [2, 2, "normal"]},
    3: {"A": [5, 2, "normal"], "B": [4, 2, "normal"]},
    4: {"A": [3, 2, "delay"],  "B": [2, 2, "delay"]},
    5: {"A": [3, 3, "normal"], "B": [2, 3, "normal"]},
    6: {"A": [3, 2, "must"],   "B": [2, 2, "must"]}
}