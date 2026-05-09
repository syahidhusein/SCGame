import pandas as pd
from cards import CHANCE_CARDS, SITUATION_CARDS

class Player:
    def __init__(self, name):
        self.name = name
        self.capital = 40
        self.points = 0
        self.demands_met = 0
        self.inventory = 0
        self.pending_shipments = 0
        self.pending_points = 0 
        self.pending_demands_met = 0 
        self.history = []

class SupplyChainLab:
    def __init__(self, player_names):
        self.players = [Player(n) for n in player_names]
        
    def resolve_turn(self, player, chance_id, sit_id, sit_type, action, extra_qty=0, partial_qty=0):
        # 1. APPLY PREVIOUS DELAYS
        player.points += player.pending_points
        player.demands_met += player.pending_demands_met
        
        extra_from_delay = player.pending_shipments - player.pending_demands_met
        player.inventory += max(0, extra_from_delay)
        
        # 2. RESET PENDINGS
        player.pending_shipments = 0
        player.pending_points = 0
        player.pending_demands_met = 0

        c = CHANCE_CARDS[chance_id]
        s = SITUATION_CARDS[sit_id][sit_type]
        
        adj_demand = max(s[0] + c.get("dem_mod", 0), c.get("min_dem", 1))
        adj_cost = max(s[1] + c.get("cost_mod", 0), c.get("min_price", 1))
        
        player.capital += c.get("cap_mod", 0)
        player.points += c.get("pts_mod", 0)
        
        if player.capital < 0:
            player.points += c.get("fail_penalty", 0)
            player.capital = 0

        # 3. PURCHASE LOGIC
        is_must = s[2] == "must"
        
        # CHANCE 5 OVERRIDE: If the shield is active, it completely nullifies the "MUST" constraint
        if c.get("special") == "no_penalty":
            is_must = False 

        if is_must:
            max_buyable = player.capital // adj_cost
            total_to_buy = min(adj_demand, max_buyable)
        else:
            total_needed = adj_demand if action in ["full", "stock"] else 0
            if action == "partial":
                total_needed = partial_qty 
            total_to_buy = total_needed + extra_qty

        # 4. TRANSACTION & DELAY STORAGE
        total_bill = total_to_buy * adj_cost
        if player.capital >= total_bill:
            player.capital -= total_bill
            
            if s[2] == "delay": 
                will_fulfill = min(adj_demand, total_to_buy)
                player.pending_shipments = total_to_buy
                player.pending_points = (will_fulfill * 2)
                player.pending_demands_met = will_fulfill
            else:
                player.inventory += total_to_buy
        
        # 5. SCORING CURRENT ROUND
        fulfilled = min(adj_demand, player.inventory)
        player.inventory -= fulfilled
        player.demands_met += fulfilled
        player.points += (fulfilled * 2)
        
        # 6. PENALTY CURRENT ROUND
        unmet = adj_demand - fulfilled
        if unmet > 0:
            if c.get("special") == "no_penalty":
                pass # Handled silently in UI
            else:
                player.points -= unmet

    def leaderboard(self):
        stats = [{"Name": p.name, "Pts": p.points, "Met": p.demands_met, "Cap": p.capital, "Inv": p.inventory} for p in self.players]
        return pd.DataFrame(stats).sort_values(by=["Pts", "Met", "Cap"], ascending=False)