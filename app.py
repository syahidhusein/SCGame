import streamlit as st
import pandas as pd
from engine import SupplyChainLab

st.markdown(
    """
    <style>
        /* Change sidebar width */
        [data-testid="stSidebar"] {
            min-width: 350px;
            max-width: 350px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# --- SESSION STATE INITIALIZATION ---
if "game" not in st.session_state:
    st.session_state.game = None
    st.session_state.current_round = 1
    st.session_state.current_player_idx = 0

st.set_page_config(page_title="Supply Chain Lab", layout="wide")
st.title("📦 Supply Chain Lab")

# --- GAME SETUP ---
if st.session_state.game is None:
    st.header("Game Setup")
    player_input = st.text_input("Enter player names (comma separated):", "Ben, Bob, Brian")
    if st.button("Start Game"):
        names = [n.strip() for n in player_input.split(",") if n.strip()]
        st.session_state.game = SupplyChainLab(names)
        st.rerun()

# --- MAIN GAME LOOP ---
else:
    game = st.session_state.game
    r = st.session_state.current_round
    p_idx = st.session_state.current_player_idx
    
    # End of Game Check
    if r > 6:
        st.success("🎉 Game Over! Final Leaderboard:")
        st.dataframe(game.leaderboard(), use_container_width=True)
        if st.button("Start New Game"):
            st.session_state.game = None
            st.session_state.current_round = 1
            st.session_state.current_player_idx = 0
            st.rerun()
        st.stop()

    player = game.players[p_idx]
    
    # --- UNIQUE TURN KEY ---
    # This guarantees that when the player or round changes, Streamlit creates brand new, empty widgets!
    turn_key = f"R{r}_P{p_idx}"

    # --- SIDEBAR: LEADERBOARD & RULES ---
    with st.sidebar:
        st.header(f"Round {r} Leaderboard")
        st.dataframe(game.leaderboard(), use_container_width=True)
        
        st.markdown("---")
        st.header("📝 Scorekeeper Takeaways")
        st.info(
            "**1.** If unable to buy full demand but has inventory, do **'partial'** action.\n\n"
            "**2.** If want to use stock instead of buy and stock is enough to meet full demand, do **'none'** action.\n\n"
            "**3.** Situation 6 (**MUST**) overrides choices and auto-spends capital.\n\n"
            "**4.** Chance Card 5 overrides all situations, including situation 6. Current logic allows carry forward to next rounds. Scorekeeper decides if allowed or must use in same round."
        )

    # --- MAIN AREA: TURN RESOLUTION ---
    st.subheader(f"🔄 Round {r} | Turn: **{player.name}**")
    
    # Display Current Player Stats
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Capital", f"${player.capital}M")
    col2.metric("Points", player.points)
    col3.metric("Inventory", player.inventory)
    col4.metric("Demands Met", player.demands_met)
    
    st.markdown("---")
    
    # --- REACTIVE INPUTS (No Form Used) ---
    st.write("### Play Cards")
    c1, c2, c3 = st.columns(3)
    c_id = c1.number_input("Chance Card # (1-10)", min_value=1, max_value=10, step=1, key=f"chance_{turn_key}")
    s_id = c2.number_input("Situation Card # (1-6)", min_value=1, max_value=6, step=1, key=f"sit_{turn_key}")
    s_type = c3.radio("Situation Type", ["A", "B"], horizontal=True, key=f"type_{turn_key}")

    st.write("### Action")
    # Because there is no form, selecting "partial" immediately reruns the UI to show the next field
    act = st.selectbox("Player Action:", ["full", "partial", "none", "stock"], key=f"act_{turn_key}")
    
    partial_qty = 0
    extra_qty = 0
    
    # Conditional fields will pop up instantly now
    pc1, pc2 = st.columns(2)
    with pc1:
        if act == "partial":
            partial_qty = st.number_input("Units partially fulfilled:", min_value=1, step=1, key=f"part_{turn_key}")
        elif act == "stock":
            extra_qty = st.number_input("Extra units to stock up:", min_value=1, step=1, key=f"stock_{turn_key}")

    # Main Action Button
    if st.button("Resolve Turn", type="primary", key=f"submit_{turn_key}"):
        
        # Execute turn logic
        game.resolve_turn(player, c_id, s_id, s_type, act, extra_qty, partial_qty)
        
        # Move to next player / round
        if st.session_state.current_player_idx < len(game.players) - 1:
            st.session_state.current_player_idx += 1
        else:
            st.session_state.current_player_idx = 0
            st.session_state.current_round += 1
            
        st.rerun()