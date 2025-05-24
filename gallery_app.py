import streamlit as st
import json
from pathlib import Path
import re

def show_card_detail(card):
    """Display detailed view of a single card"""
    # Back button at top left
    if st.button("← Back to Gallery", key="back_button"):
        st.session_state.selected_card = None
        st.rerun()
    
    card_name = card.get('name', 'Unknown Card')
    
    # Check if card has multiple faces
    faces = card.get('faces', [])
    if faces:
        # Multi-faced card - split the name by " // "
        face_names = card_name.split(' // ')
        
        for i, face in enumerate(faces):
            # Use the split name if available, otherwise fall back to face name or generic
            if i < len(face_names):
                face_name = face_names[i]
            else:
                face_name = face.get('name', f'Face {i+1}')
            
            st.markdown(f"""
            <div style='text-align: center; margin-bottom: 35px;'>
                <h1 style='font-size: 32px; text-shadow: 0 0 25px rgba(120, 119, 198, 0.8); 
                        margin: 0; color: #f0f0f8; font-weight: bold;'>
                {face_name}
                </h1>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 3])  # More space for details
            
            with col1:
                if face.get('image_url'):
                    st.image(face['image_url'], use_container_width=True)
                else:
                    st.write("No image available")
            
            with col2:
                
                # Organize face details in columns
                face_col1, face_col2 = st.columns(2)
                
                with face_col1:
                    if face.get('mana_cost'):
                        st.markdown(f"""
                        <div style='background: rgba(45, 45, 68, 0.4); border: 1px solid rgba(120, 119, 198, 0.3); 
                                    border-radius: 6px; padding: 12px; margin: 6px 0; text-align: center;'>
                        <strong style='font-size: 18px;'>Mana Cost:</strong><br>{face['mana_cost']}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    if face.get('cmc'):
                        st.markdown(f"""
                        <div style='background: rgba(45, 45, 68, 0.4); border: 1px solid rgba(120, 119, 198, 0.3); 
                                    border-radius: 6px; padding: 12px; margin: 6px 0; text-align: center;'>
                        <strong style='font-size: 18px;'>Converted Mana Cost:</strong><br>{face['cmc']}
                        </div>
                        """, unsafe_allow_html=True)
                        
                    if face.get('type_line'):
                        st.markdown(f"""
                        <div style='background: rgba(45, 45, 68, 0.4); border: 1px solid rgba(120, 119, 198, 0.3); 
                                    border-radius: 6px; padding: 12px; margin: 6px 0; text-align: center;'>
                        <strong style='font-size: 18px;'>Type:</strong><br>{face['type_line']}
                        </div>
                        """, unsafe_allow_html=True)
                        
                    # Stats for this face
                    if face.get('power') and face.get('toughness'):
                        st.markdown(f"""
                        <div style='background: rgba(45, 45, 68, 0.4); border: 1px solid rgba(120, 119, 198, 0.3); 
                                    border-radius: 6px; padding: 12px; margin: 6px 0; text-align: center;'>
                        <strong style='font-size: 18px;'>Power/Toughness:</strong><br>{face['power']}/{face['toughness']}
                        </div>
                        """, unsafe_allow_html=True)
                
                with face_col2:
                    # Right column for face details - placeholder for now
                    st.write("")
                
                # Rules text gets full width below
                if face.get('oracle_text'):
                    st.markdown(f"""
                    <div style="
                        background: rgba(45, 45, 68, 0.3);
                        border: 1px solid rgba(120, 119, 198, 0.2);
                        border-radius: 8px;
                        padding: 20px;
                        margin-top: 12px;
                        font-size: 18px;
                        line-height: 1.8;
                        text-align: center;
                    ">
                    {face['oracle_text']}
                    </div>
                    """, unsafe_allow_html=True)
            
            if i < len(faces) - 1:  # Add separator between faces
                st.divider()
    else:
        # Single-faced card - better space utilization
        col1, col2 = st.columns([1, 3])  # Give more space to details
        
        with col1:
            if card.get('image_url'):
                st.image(card['image_url'], use_container_width=True)  # Scale to container
            else:
                st.write("No image available")
        
        with col2:
            
            # Card name with enhanced styling
            st.markdown(f"""
            <div style='text-align: center; margin-bottom: 35px;'>
                <h1 style='font-size: 32px; text-shadow: 0 0 25px rgba(120, 119, 198, 0.8); 
                        margin: 0; color: #f0f0f8; font-weight: bold;'>
                {card_name}
                </h1>
            </div>
            """, unsafe_allow_html=True)
            
            # Organize info in columns for better space usage
            detail_col1, detail_col2 = st.columns(2)
            # Organize info in columns for better space usage
            detail_col1, detail_col2 = st.columns(2)
            
            with detail_col1:
                if card.get('mana_cost'):
                    st.markdown(f"""
                    <div style='background: rgba(45, 45, 68, 0.4); border: 1px solid rgba(120, 119, 198, 0.3); 
                                border-radius: 6px; padding: 12px; margin: 6px 0; text-align: center;'>
                    <strong style='font-size: 18px;'>Mana Cost:</strong><br>{card['mana_cost']}
                    </div>
                    """, unsafe_allow_html=True)
                
                if card.get('cmc'):
                    st.markdown(f"""
                    <div style='background: rgba(45, 45, 68, 0.4); border: 1px solid rgba(120, 119, 198, 0.3); 
                                border-radius: 6px; padding: 12px; margin: 6px 0; text-align: center;'>
                    <strong style='font-size: 18px;'>Converted Mana Cost:</strong><br>{card['cmc']}
                    </div>
                    """, unsafe_allow_html=True)
                    
                if card.get('type_line'):
                    st.markdown(f"""
                    <div style='background: rgba(45, 45, 68, 0.4); border: 1px solid rgba(120, 119, 198, 0.3); 
                                border-radius: 6px; padding: 12px; margin: 6px 0; text-align: center;'>
                    <strong style='font-size: 18px;'>Type:</strong><br>{card['type_line']}
                    </div>
                    """, unsafe_allow_html=True)
                    
                # Stats
                if card.get('power') and card.get('toughness'):
                    st.markdown(f"""
                    <div style='background: rgba(45, 45, 68, 0.4); border: 1px solid rgba(120, 119, 198, 0.3); 
                                border-radius: 6px; padding: 12px; margin: 6px 0; text-align: center;'>
                    <strong style='font-size: 18px;'>Power/Toughness:</strong><br>{card['power']}/{card['toughness']}
                    </div>
                    """, unsafe_allow_html=True)
            
            with detail_col2:
                # Market info
                if card.get('edhrec_rank'):
                    st.markdown(f"""
                    <div style='background: rgba(45, 45, 68, 0.4); border: 1px solid rgba(120, 119, 198, 0.3); 
                                border-radius: 6px; padding: 12px; margin: 6px 0; text-align: center;'>
                    <strong style='font-size: 18px;'>EDHREC Rank:</strong><br>{card['edhrec_rank']}
                    </div>
                    """, unsafe_allow_html=True)
                    
                if card.get('usd_price'):
                    st.markdown(f"""
                    <div style='background: rgba(45, 45, 68, 0.4); border: 1px solid rgba(120, 119, 198, 0.3); 
                                border-radius: 6px; padding: 12px; margin: 6px 0; text-align: center;'>
                    <strong style='font-size: 18px;'>Price:</strong><br>${card['usd_price']}
                    </div>
                    """, unsafe_allow_html=True)
                
                # Set info
                if card.get('set_name'):
                    st.markdown(f"""
                    <div style='background: rgba(45, 45, 68, 0.4); border: 1px solid rgba(120, 119, 198, 0.3); 
                                border-radius: 6px; padding: 12px; margin: 6px 0; text-align: center;'>
                    <strong style='font-size: 18px;'>Set:</strong><br>{card['set_name']}
                    </div>
                    """, unsafe_allow_html=True)
                    
                if card.get('rarity'):
                    st.markdown(f"""
                    <div style='background: rgba(45, 45, 68, 0.4); border: 1px solid rgba(120, 119, 198, 0.3); 
                                border-radius: 6px; padding: 12px; margin: 6px 0; text-align: center;'>
                    <strong style='font-size: 18px;'>Rarity:</strong><br>{card['rarity']}
                    </div>
                    """, unsafe_allow_html=True)
            
            # Rules text gets full width below
            if card.get('oracle_text'):
                # Use a container with more readable styling
                st.markdown(f"""
                <div style="
                    background: rgba(45, 45, 68, 0.3);
                    border: 1px solid rgba(120, 119, 198, 0.2);
                    border-radius: 8px;
                    padding: 20px;
                    margin-top: 12px;
                    font-size: 18px;
                    line-height: 1.8;
                    text-align: center;
                ">
                {card['oracle_text']}
                </div>
                """, unsafe_allow_html=True)

def main():
    st.set_page_config(
        page_title="MTG Card Gallery",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Mystical background styling
    st.markdown("""
    <style>
    /* Main background with subtle mystical gradient */
    .stApp {
        background: linear-gradient(135deg, 
            #1a1a2e 0%, 
            #16213e 25%, 
            #0f3460 50%, 
            #16213e 75%, 
            #1a1a2e 100%);
        background-attachment: fixed;
    }
    
    /* Subtle arcane pattern overlay */
    .stApp::before {
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            radial-gradient(circle at 25% 25%, rgba(120, 119, 198, 0.03) 0%, transparent 50%),
            radial-gradient(circle at 75% 75%, rgba(120, 119, 198, 0.03) 0%, transparent 50%),
            radial-gradient(circle at 50% 50%, rgba(255, 215, 0, 0.01) 0%, transparent 50%);
        pointer-events: none;
        z-index: -1;
    }
    
    /* Sidebar with parchment-like styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #2d2d44 0%, #232339 100%);
        border-right: 1px solid rgba(120, 119, 198, 0.2);
    }
    
    /* Text styling for mystical feel */
    .stMarkdown, .stText {
        color: #e8e8f0;
    }
    
    /* Headers with subtle glow */
    h1, h2, h3 {
        color: #f0f0f8;
        text-shadow: 0 0 10px rgba(120, 119, 198, 0.3);
    }
    
    /* Card containers with subtle mystical border */
    .element-container img {
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4), 
                    0 0 20px rgba(120, 119, 198, 0.1);
        transition: all 0.3s ease;
    }
    
    .element-container img:hover {
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.6), 
                    0 0 30px rgba(120, 119, 198, 0.2);
        transform: translateY(-2px);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #3d3d5c, #2d2d44);
        color: #e8e8f0;
        border: 1px solid rgba(120, 119, 198, 0.3);
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #4d4d6c, #3d3d54);
        border-color: rgba(120, 119, 198, 0.5);
        box-shadow: 0 0 15px rgba(120, 119, 198, 0.2);
    }
    
    /* Selectbox and input styling */
    .stSelectbox > div > div, .stTextInput > div > div > input {
        background: linear-gradient(135deg, #2d2d44, #232339);
        color: #e8e8f0;
        border: 1px solid rgba(120, 119, 198, 0.3);
        border-radius: 6px;
    }
    
    /* Make selectboxes look more clickable */
    .stSelectbox > div > div {
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .stSelectbox > div > div:hover {
        border-color: rgba(120, 119, 198, 0.6);
        box-shadow: 0 0 10px rgba(120, 119, 198, 0.2);
        background: linear-gradient(135deg, #3d3d54, #2d2d44);
    }
    
    /* Add loading cursor during interactions */
    .stApp.stLoading {
        cursor: wait !important;
    }
    
    .stApp.stLoading * {
        cursor: wait !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'selected_card' not in st.session_state:
        st.session_state.selected_card = None

    if 'current_page' not in st.session_state:
        st.session_state.current_page = 1
    
    # Load filtered data
    try:
        with open(Path("filtered_cards.json"), 'r') as f:
            data = json.load(f)
        cards = data.get('cards', [])
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return

    # Show card detail if one is selected
    if st.session_state.selected_card is not None:
        show_card_detail(st.session_state.selected_card)
        return

    # Gallery view
    st.markdown("""
    <div style='text-align: center; margin-bottom: 35px;'>
        <h1 style='font-size: 2.5rem; text-shadow: 0 0 25px rgba(120, 119, 198, 0.8); 
                margin: 0; color: #f0f0f8; font-weight: bold;'>
        MTG Efficiency Variable Database
        </h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Filtering and Sorting controls
    with st.sidebar:
        # Name search
        name_search = st.text_input("Search Card Name", placeholder="e.g. Lightning Bolt")
        
        # Card type/subtype search
        type_search = st.text_input("Search Card Types", placeholder="e.g. Goblin, Equipment, Legendary")
        
        # Oracle text search with regex support
        oracle_search = st.text_input("Search Oracle Text", placeholder="e.g. flying, draw.*card, tap.*untap")
        
        # Search options
        col1, col2 = st.columns(2)
        with col1:
            regex_mode = st.checkbox("Regex mode", help="Enable regular expressions")
        with col2:
            word_order = st.checkbox("Word order matters", help="Uncheck for flexible word matching")
        
        # Color identity filter
        st.subheader("Color Identity")
        col1, col2, col3 = st.columns(3)
        with col1:
            white_checked = st.checkbox("⚪", key="white")
            black_checked = st.checkbox("⚫", key="black")
        with col2:
            blue_checked = st.checkbox("🔵", key="blue")
            red_checked = st.checkbox("🔴", key="red")
        with col3:
            green_checked = st.checkbox("🟢", key="green")
            colorless_checked = st.checkbox("◯", key="colorless")
        
        # CMC filter with dynamic dropdowns
        st.subheader("Mana Value")
        
        # Initialize CMC filters in session state
        if 'cmc_filters' not in st.session_state:
            st.session_state.cmc_filters = [{"operator": "any", "value": 2}]
        
        cmc_operators = ["any", "equals", "less than", "less than or equal", "greater than", "greater than or equal"]
        
        # Display existing CMC filters
        for i, filter_data in enumerate(st.session_state.cmc_filters):
            col1, col2 = st.columns(2)
            with col1:
                operator = st.selectbox(
                    "CMC Operator", 
                    cmc_operators,
                    index=cmc_operators.index(filter_data["operator"]) if filter_data["operator"] in cmc_operators else 0,
                    key=f"cmc_op_{i}",
                    label_visibility="collapsed"
                )
            with col2:
                if operator != "any":
                    value = st.number_input(
                        "CMC Value", 
                        min_value=0, 
                        max_value=20, 
                        value=filter_data["value"],
                        key=f"cmc_val_{i}",
                        label_visibility="collapsed"
                    )
                else:
                    # Hide the right dropdown by showing empty space
                    st.empty()
                    value = 2  # Default value when "any" is selected
            
            # Update the filter data
            st.session_state.cmc_filters[i] = {"operator": operator, "value": value}
        
        # Add new filter if the last one is being used
        if len(st.session_state.cmc_filters) == 0 or st.session_state.cmc_filters[-1]["operator"] != "any":
            if st.button("+ Add CMC Filter"):
                st.session_state.cmc_filters.append({"operator": "any", "value": 2})
                st.rerun()
        
        # Clear all CMC filters button
        if len(st.session_state.cmc_filters) > 1:
            if st.button("Clear CMC Filters"):
                st.session_state.cmc_filters = [{"operator": "any", "value": 2}]
                st.rerun()
        
        # Card type filters with dynamic dropdowns
        st.subheader("Card Types")
        
        # Initialize type filters in session state
        if 'type_filters' not in st.session_state:
            st.session_state.type_filters = [{"operator": "any", "type": "Land"}]
        
        type_options = ["Land", "Creature", "Artifact", "Enchantment", "Instant", "Sorcery", "Planeswalker", "Other"]
        type_operators = ["any", "is", "is not"]
        
        # Display existing type filters
        for i, filter_data in enumerate(st.session_state.type_filters):
            col1, col2 = st.columns(2)
            with col1:
                operator = st.selectbox(
                    "Type Operator", 
                    type_operators,
                    index=type_operators.index(filter_data["operator"]) if filter_data["operator"] in type_operators else 0,
                    key=f"type_op_{i}",
                    label_visibility="collapsed"
                )
            with col2:
                if operator != "any":
                    type_val = st.selectbox(
                        "Card Type",
                        type_options,
                        index=type_options.index(filter_data["type"]) if filter_data["type"] in type_options else 0,
                        key=f"type_val_{i}",
                        label_visibility="collapsed"
                    )
                else:
                    # Hide the right dropdown by showing empty space
                    st.empty()
                    type_val = "Land"  # Default value when "any" is selected
            
            # Update the filter data
            st.session_state.type_filters[i] = {"operator": operator, "type": type_val}
        
        # Add new filter if the last one is being used
        if len(st.session_state.type_filters) == 0 or st.session_state.type_filters[-1]["operator"] != "any":
            if st.button("+ Add Type Filter"):
                st.session_state.type_filters.append({"operator": "any", "type": "Land"})
                st.rerun()
        
        # Clear all filters button
        if len(st.session_state.type_filters) > 1:
            if st.button("Clear Type Filters"):
                st.session_state.type_filters = [{"operator": "any", "type": "Land"}]
                st.rerun()
        
        sort_by = st.selectbox("Sort by", [
            'EDHREC Rank',
            'Name (A-Z)',
            'Mana Value (Low-High)',
            'Mana Value (High-Low)',
            'Price (Low-High)'
        ])

    # Apply filters
    filtered_cards = cards
    
    # Name search (simple substring search)
    if name_search:
        filtered_cards = [
            card for card in filtered_cards 
            if name_search.lower() in (card.get('name') or '').lower()
        ]
    
    # Card type/subtype search
    if type_search:
        filtered_cards = [
            card for card in filtered_cards 
            if type_search.lower() in (card.get('type_line') or '').lower()
        ]
    
    # Color identity filter
    selected_colors = []
    if white_checked:
        selected_colors.append('W')
    if blue_checked:
        selected_colors.append('U')
    if black_checked:
        selected_colors.append('B')
    if red_checked:
        selected_colors.append('R')
    if green_checked:
        selected_colors.append('G')
    
    if selected_colors or colorless_checked:
        def matches_color_identity(card):
            # Get card's color identity from mana cost and oracle text
            card_colors = set()
            
            # Check mana cost
            mana_cost = card.get('mana_cost', '') or ''
            if 'W' in mana_cost:
                card_colors.add('W')
            if 'U' in mana_cost:
                card_colors.add('U')
            if 'B' in mana_cost:
                card_colors.add('B')
            if 'R' in mana_cost:
                card_colors.add('R')
            if 'G' in mana_cost:
                card_colors.add('G')
            
            # Check oracle text for mana symbols
            oracle_text = card.get('oracle_text', '') or ''
            if '{W}' in oracle_text or '{W/' in oracle_text:
                card_colors.add('W')
            if '{U}' in oracle_text or '{U/' in oracle_text:
                card_colors.add('U')
            if '{B}' in oracle_text or '{B/' in oracle_text:
                card_colors.add('B')
            if '{R}' in oracle_text or '{R/' in oracle_text:
                card_colors.add('R')
            if '{G}' in oracle_text or '{G/' in oracle_text:
                card_colors.add('G')
            
            # Check faces for multi-faced cards
            faces = card.get('faces', [])
            for face in faces:
                face_mana_cost = face.get('mana_cost', '') or ''
                face_oracle_text = face.get('oracle_text', '') or ''
                
                # Check face mana cost
                if 'W' in face_mana_cost:
                    card_colors.add('W')
                if 'U' in face_mana_cost:
                    card_colors.add('U')
                if 'B' in face_mana_cost:
                    card_colors.add('B')
                if 'R' in face_mana_cost:
                    card_colors.add('R')
                if 'G' in face_mana_cost:
                    card_colors.add('G')
                
                # Check face oracle text
                if '{W}' in face_oracle_text or '{W/' in face_oracle_text:
                    card_colors.add('W')
                if '{U}' in face_oracle_text or '{U/' in face_oracle_text:
                    card_colors.add('U')
                if '{B}' in face_oracle_text or '{B/' in face_oracle_text:
                    card_colors.add('B')
                if '{R}' in face_oracle_text or '{R/' in face_oracle_text:
                    card_colors.add('R')
                if '{G}' in face_oracle_text or '{G/' in face_oracle_text:
                    card_colors.add('G')
            
            # If colorless is checked and no other colors selected, show only colorless
            if colorless_checked and not selected_colors:
                return len(card_colors) == 0
            
            # If only colorless is checked with other colors, include colorless cards
            # If colors are selected, card must have only the selected colors (subset)
            if selected_colors:
                return card_colors.issubset(set(selected_colors))
            
            return True
        
        filtered_cards = [card for card in filtered_cards if matches_color_identity(card)]
    
    # Oracle text search with regex and flexible word matching
    if oracle_search:
        def matches_oracle_search(card):
            oracle_text = (card.get('oracle_text') or '').lower()
            search_term = oracle_search.lower()
            
            try:
                if regex_mode:
                    # Direct regex search
                    return bool(re.search(search_term, oracle_text))
                elif not word_order:
                    # Split search into words and check if all words exist (any order)
                    search_words = search_term.split()
                    return all(word in oracle_text for word in search_words)
                else:
                    # Simple substring search (original behavior)
                    return search_term in oracle_text
            except re.error:
                # If regex is invalid, fall back to simple search
                return search_term in oracle_text
        
        filtered_cards = [card for card in filtered_cards if matches_oracle_search(card)]
    
    # CMC filter with multiple conditions
    if 'cmc_filters' in st.session_state and st.session_state.cmc_filters:
        # Only apply filters that aren't "any"
        active_cmc_filters = [f for f in st.session_state.cmc_filters if f["operator"] != "any"]
        
        if active_cmc_filters:
            def meets_cmc_criteria(card):
                cmc = card.get('cmc')
                if cmc == "" or cmc is None:
                    card_cmc = 0
                else:
                    try:
                        card_cmc = int(cmc)
                    except (ValueError, TypeError):
                        card_cmc = 0
                
                # All CMC filters must pass (AND logic)
                for cmc_filter in active_cmc_filters:
                    operator = cmc_filter["operator"]
                    value = cmc_filter["value"]
                    
                    if operator == "equals" and card_cmc != value:
                        return False
                    elif operator == "less than" and card_cmc >= value:
                        return False
                    elif operator == "less than or equal" and card_cmc > value:
                        return False
                    elif operator == "greater than" and card_cmc <= value:
                        return False
                    elif operator == "greater than or equal" and card_cmc < value:
                        return False
                
                return True
            
            filtered_cards = [card for card in filtered_cards if meets_cmc_criteria(card)]
    
    # Card type filters with dynamic dropdowns
    if 'type_filters' in st.session_state and st.session_state.type_filters:
        # Only apply filters that aren't "any"
        active_filters = [f for f in st.session_state.type_filters if f["operator"] != "any"]
        
        if active_filters:
            def matches_type_filter(card):
                type_line = (card.get('type_line') or '').lower()
                
                # All type filters must pass (AND logic)
                for type_filter in active_filters:
                    operator = type_filter["operator"]
                    type_name = type_filter["type"]
                    
                    if type_name == 'Other':
                        # Check if it's NOT any of the main types
                        main_types = ['land', 'creature', 'artifact', 'enchantment', 'instant', 'sorcery', 'planeswalker']
                        type_matches = not any(main_type in type_line for main_type in main_types)
                    elif type_name == 'any':
                        type_matches = True
                    else:
                        type_matches = type_name.lower() in type_line
                    
                    if operator == "is" and not type_matches:
                        return False
                    elif operator == "is not" and type_matches:
                        return False
                
                return True
            
            filtered_cards = [card for card in filtered_cards if matches_type_filter(card)]

    # Apply sorting to filtered cards
    if 'Name' in sort_by:
        filtered_cards.sort(
            key=lambda x: (x.get('name') or '').lower(), 
            reverse=('Z-A' in sort_by)
        )
    elif 'Mana Value' in sort_by:
        def safe_cmc(card):
            cmc = card.get('cmc')
            if cmc == "" or cmc is None:
                return 0
            try:
                return int(cmc)
            except (ValueError, TypeError):
                return 0
        filtered_cards.sort(key=safe_cmc, reverse=('High-Low' in sort_by))
    elif 'EDHREC' in sort_by:
        filtered_cards.sort(key=lambda x: x.get('edhrec_rank') or 99999)
    elif 'Price' in sort_by:
        def safe_price(card):
            price = card.get('usd_price')
            if price == "" or price is None:
                return 0.0
            try:
                return float(price)
            except (ValueError, TypeError):
                return 0.0
        filtered_cards.sort(key=safe_price, reverse=('High-Low' in sort_by))

    # Show filter results - centered
    st.markdown(f"<p style='text-align: center;'>Showing {len(filtered_cards)} cards</p>", unsafe_allow_html=True)

    # Pagination controls
    cards_per_page = 50
    total_pages = (len(filtered_cards) - 1) // cards_per_page + 1 if filtered_cards else 1
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button("← Previous", disabled=(st.session_state.current_page <= 1), use_container_width=True):
            st.session_state.current_page -= 1
            st.rerun()
    with col2:
        st.write("")  # Empty space
    with col3:
        st.markdown(f"<p style='text-align: center; margin: 0; padding-top: 8px;'>Page {st.session_state.current_page} of {total_pages}</p>", unsafe_allow_html=True)
    with col4:
        st.write("")  # Empty space
    with col5:
        if st.button("Next →", disabled=(st.session_state.current_page >= total_pages), use_container_width=True):
            st.session_state.current_page += 1
            st.rerun()
    
    # Calculate cards for current page
    start_idx = (st.session_state.current_page - 1) * cards_per_page
    end_idx = start_idx + cards_per_page
    page_cards = filtered_cards[start_idx:end_idx]
    
    # Display grid - only current page cards  
    cols = st.columns(5)
    for idx, card in enumerate(page_cards):
        with cols[idx % 5]:
            # Create unique key for this card
            card_key = f"card_{start_idx + idx}"
            
            # Just the image and a small link
            if card.get('image_url'):
                st.image(card['image_url'], use_container_width=True)
                
                if st.button("🔍", key=card_key, help="View details", use_container_width=True):
                    st.session_state.selected_card = card
                    st.rerun()
            else:
                # No image fallback
                name = card.get('name', 'Unknown Card')
                if st.button(f"{name}\n(No Image)", key=card_key, use_container_width=True):
                    st.session_state.selected_card = card
                    st.rerun()

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button("← Previous", disabled=(st.session_state.current_page <= 1), key="prev_bottom", use_container_width=True):
            st.session_state.current_page -= 1
            st.rerun()
    with col2:
        st.write("")  # Empty space
    with col3:
        st.markdown(f"<p style='text-align: center; margin: 0; padding-top: 8px;'>Page {st.session_state.current_page} of {total_pages}</p>", unsafe_allow_html=True)
    with col4:
        st.write("")  # Empty space
    with col5:
        if st.button("Next →", disabled=(st.session_state.current_page >= total_pages), key="next_bottom", use_container_width=True):
            st.session_state.current_page += 1
            st.rerun()

if __name__ == "__main__":
    main()