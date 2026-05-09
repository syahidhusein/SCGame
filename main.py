from engine import SupplyChainLab

names = input("Enter player names separated by commas: ").split(",")
game = SupplyChainLab([n.strip() for n in names])

for r in range(1, 7):
    print(f"\n--- ROUND {r} ---")
    for player in game.players:
        print(f"\nTurn: {player.name} (Cap: ${player.capital}M, Pts: {player.points}), Inv: {player.inventory}, Demands Met : {player.demands_met}")
        c_id = int(input("Chance Card # (1-10): "))
        s_id = int(input("Situation Card # (1-6): "))
        s_type = input("Situation A or B? ").upper()
        act = input("Action (full/partial/none/stock): ").lower()
        extra = 0
        if act == "stock":
            extra = int(input("How many extra units to buy? "))
        
        game.resolve_turn(player, c_id, s_id, s_type, act, extra)
        print(f"End of turn: Cap: ${player.capital}M, Pts: {player.points}, Inventory: {player.inventory}, Demands Met: {player.demands_met}")
    
    print("\nEnd of Round Leaderboard:")
    print(game.leaderboard())