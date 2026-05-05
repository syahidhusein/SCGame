import pandas as pd
from cards import CHANCE_CARDS, SITUATION_CARDS


# 4a not carrying forward, points next round, inventory next round, if last round then minus points but no inventory and no demand met.


class Player:
    def __init__(self, name):
        self.name = name
        self.capital = 40
        self.points = 0
        self.demands_met = 0
        self.inventory = 0
        self.pending_shipments = [] 
        self.history = []

    def save_state(self):
        state = (self.capital, self.points, self.demands_met, self.inventory, list(self.pending_shipments))
        self.history.append(state)

    def undo(self):
        if self.history:
            self.capital, self.points, self.demands_met, self.inventory, self.pending_shipments = self.history.pop()

class SupplyChainLab:
    def __init__(self, player_names):
        self.players = [Player(n) for n in player_names]
        
    def resolve_turn(self, player, chance_id, sit_id, sit_type, action, extra_qty=0):
        player.save_state()
        c = CHANCE_CARDS[chance_id]
        s = SITUATION_CARDS[sit_id][sit_type]
        
        # MODIFIERS FROM TABLES (image_49cbc1.png & image_497a02.png)
        adj_demand = max(s[0] + c.get("dem_mod", 0), c.get("min_dem", 1))
        adj_cost = max(s[1] + c.get("cost_mod", 0), c.get("min_price", 1))
        
        # CHANCE CARD IMMEDIATE EFFECTS
        player.capital += c.get("cap_mod", 0)
        player.points += c.get("pts_mod", 0)
        
        # Handle "Unable to pay" capital penalty (-1pt)
        if player.capital < 0:
            player.points += c.get("fail_penalty", 0)
            player.capital = 0

        # SITUATION 6 OVERRIDE ("MUST" logic)
        if s[2] == "must":
            # Force purchase based on available capital
            max_buyable = player.capital // adj_cost
            total_to_buy = min(adj_demand, max_buyable)
        else:
            # Standard Decision Logic
            total_needed = adj_demand if action in ["full", "stock"] else 0
            if action == "partial":
                total_needed = int(input(f"Units fulfilled for {player.name}: "))
            total_to_buy = total_needed + extra_qty

        # FINANCIAL TRANSACTION
        total_bill = total_to_buy * adj_cost
        if player.capital >= total_bill:
            player.capital -= total_bill
            if s[2] == "delay": # SITUATION 4
                player.pending_shipments.append([total_to_buy, 1])
            else:
                player.inventory += total_to_buy
        
        # SCORING & CHANCE 5 OVERRIDE
        fulfilled = min(adj_demand, player.inventory)
        player.inventory -= fulfilled
        player.demands_met += fulfilled
        player.points += (fulfilled * 2)
        
        unmet = adj_demand - fulfilled
        if unmet > 0:
            # Increment the player's total unmet demands tally
            # player.unmet_demands += unmet 
            
            # Check if Chance Card 5 was drawn this turn
            if c.get("special") == "no_penalty":
                print(f"Chance Card 5 Active: {player.name} avoids -{unmet} penalty.")
            else:
                player.points -= unmet

    def leaderboard(self):
        stats = [{"Name": p.name, "Pts": p.points, "Met": p.demands_met, "Cap": p.capital} for p in self.players]
        return pd.DataFrame(stats).sort_values(by=["Pts", "Met", "Cap"], ascending=False)