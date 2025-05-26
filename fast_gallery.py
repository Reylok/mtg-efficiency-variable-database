from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

app = FastAPI(title="MTG Efficiency Variable Database")

# Static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Global cards data
cards_data = []

@app.on_event("startup")
async def load_cards():
    """Load cards once at startup"""
    global cards_data
    try:
        with open("filtered_cards.json", 'r') as f:
            data = json.load(f)
        cards_data = data.get('cards', [])
        print(f"Loaded {len(cards_data)} cards")
    except Exception as e:
        print(f"Error loading cards: {e}")
        cards_data = []

def get_card_color_identity(card: Dict[str, Any]) -> set:
    """Extract color identity from card (same logic as Streamlit version)"""
    card_colors = set()
    
    # Check mana cost
    mana_cost = card.get('mana_cost', '') or ''
    for color in ['W', 'U', 'B', 'R', 'G']:
        if color in mana_cost:
            card_colors.add(color)
    
    # Check oracle text
    oracle_text = card.get('oracle_text', '') or ''
    for color in ['W', 'U', 'B', 'R', 'G']:
        if f'{{{color}}}' in oracle_text or f'{{{color}/' in oracle_text:
            card_colors.add(color)
    
    # Check faces for multi-faced cards
    faces = card.get('faces', [])
    for face in faces:
        face_mana_cost = face.get('mana_cost', '') or ''
        face_oracle_text = face.get('oracle_text', '') or ''
        
        for color in ['W', 'U', 'B', 'R', 'G']:
            if color in face_mana_cost:
                card_colors.add(color)
            if f'{{{color}}}' in face_oracle_text or f'{{{color}/' in face_oracle_text:
                card_colors.add(color)
    
    return card_colors

def get_exact_card_colors(card: Dict[str, Any]) -> set:
    """Extract exact colors from card's mana cost only (for exact color matching)"""
    card_colors = set()
    
    # Check main mana cost
    mana_cost = card.get('mana_cost', '') or ''
    for color in ['W', 'U', 'B', 'R', 'G']:
        if color in mana_cost:
            card_colors.add(color)
    
    # Check faces for multi-faced cards
    faces = card.get('faces', [])
    for face in faces:
        face_mana_cost = face.get('mana_cost', '') or ''
        for color in ['W', 'U', 'B', 'R', 'G']:
            if color in face_mana_cost:
                card_colors.add(color)
    
    return card_colors

def filter_cards(
    cards: List[Dict], 
    name_search: str = "",
    type_search: str = "",
    oracle_search: str = "",
    regex_mode: bool = False,
    word_order: bool = True,
    colors: List[str] = [],
    colorless: bool = False,
    exact_colors: bool = False,  # New parameter for exact color matching
    exact_types: bool = True,
    cmc_filters: List[Dict] = [],
    type_filters: List[Dict] = [],
    sort_by: str = "EDHREC Rank"
) -> List[Dict]:
    """Apply all filters and sorting (updated with exact color matching)"""
    
    filtered_cards = cards.copy()
    
    # Name search
    if name_search:
        filtered_cards = [
            card for card in filtered_cards 
            if name_search.lower() in (card.get('name') or '').lower()
        ]
    
    # Type search
    if type_search:
        filtered_cards = [
            card for card in filtered_cards 
            if type_search.lower() in (card.get('type_line') or '').lower()
        ]
    
    # Oracle text search
    if oracle_search:
        def matches_oracle_search(card):
            oracle_text = (card.get('oracle_text') or '').lower()
            search_term = oracle_search.lower()
            
            try:
                if regex_mode:
                    return bool(re.search(search_term, oracle_text))
                elif not word_order:
                    search_words = search_term.split()
                    return all(word in oracle_text for word in search_words)
                else:
                    return search_term in oracle_text
            except re.error:
                return search_term in oracle_text
        
        filtered_cards = [card for card in filtered_cards if matches_oracle_search(card)]
    
    # Color filtering (updated with exact color matching)
    if colors or colorless:
        def matches_color_criteria(card):
            if exact_colors:
                # Exact color matching - card must have exactly the selected colors
                card_colors = get_exact_card_colors(card)
            else:
                # Color identity matching - card's identity must be subset of selected colors
                card_colors = get_card_color_identity(card)
            
            selected_colors = set(colors) if colors else set()
            
            if colorless and not colors:
                # Only colorless cards
                return len(card_colors) == 0
            elif colorless and colors:
                # Colorless OR exactly the selected colors
                if exact_colors:
                    return len(card_colors) == 0 or card_colors == selected_colors
                else:
                    return len(card_colors) == 0 or card_colors.issubset(selected_colors)
            elif colors:
                # Cards with the specified colors
                if exact_colors:
                    return card_colors == selected_colors
                else:
                    return card_colors.issubset(selected_colors)
            
            return True
        
        filtered_cards = [card for card in filtered_cards if matches_color_criteria(card)]
    
    # CMC filters
    active_cmc_filters = [f for f in cmc_filters if f.get("operator") != "any"]
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
    
    # Type filters (updated with AND/OR logic)
    active_type_filters = [f for f in type_filters if f.get("operator") != "any"]
    if active_type_filters:
        def matches_type_filter(card):
            type_line = (card.get('type_line') or '').lower()
            
            if exact_types:
                # AND logic - card must match ALL type filters
                for type_filter in active_type_filters:
                    operator = type_filter["operator"]
                    type_name = type_filter["type"]
                    
                    if type_name == 'Other':
                        main_types = ['land', 'creature', 'artifact', 'enchantment', 'instant', 'sorcery', 'planeswalker']
                        type_matches = not any(main_type in type_line for main_type in main_types)
                    else:
                        type_matches = type_name.lower() in type_line
                    
                    if operator == "is" and not type_matches:
                        return False
                    elif operator == "is not" and type_matches:
                        return False
                return True
            else:
                # OR logic - card must match AT LEAST ONE type filter
                for type_filter in active_type_filters:
                    operator = type_filter["operator"]
                    type_name = type_filter["type"]
                    
                    if type_name == 'Other':
                        main_types = ['land', 'creature', 'artifact', 'enchantment', 'instant', 'sorcery', 'planeswalker']
                        type_matches = not any(main_type in type_line for main_type in main_types)
                    else:
                        type_matches = type_name.lower() in type_line
                    
                    if operator == "is" and type_matches:
                        return True
                    elif operator == "is not" and not type_matches:
                        return True
                return False
        
        filtered_cards = [card for card in filtered_cards if matches_type_filter(card)]
    
    # Sorting
    if 'Name' in sort_by:
        filtered_cards.sort(key=lambda x: (x.get('name') or '').lower(), reverse=('Z-A' in sort_by))
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
    
    return filtered_cards

@app.get("/", response_class=HTMLResponse)
async def gallery_view(request: Request):
    """Main gallery page"""
    return templates.TemplateResponse("gallery.html", {
        "request": request,
        "title": "MTG Efficiency Variable Database"
    })

@app.get("/api/search")
async def search_cards(
    name: str = "",
    type_search: str = "",
    oracle: str = "",
    regex_mode: bool = False,
    word_order: bool = True,
    colors: str = "",  # Comma-separated color codes
    colorless: bool = False,
    exact_colors: bool = False,  # New parameter for exact color matching
    exact_types: bool = True,
    cmc_filters: str = "",  # JSON string
    type_filters: str = "",  # JSON string
    sort_by: str = "EDHREC Rank",
    page: int = 1,
    per_page: int = 50
):
    """API endpoint for card search - returns JSON"""
    
    # Parse color filters
    color_list = [c.strip() for c in colors.split(",") if c.strip()] if colors else []
    
    # Parse JSON filters
    try:
        cmc_filter_list = json.loads(cmc_filters) if cmc_filters else []
        type_filter_list = json.loads(type_filters) if type_filters else []
    except json.JSONDecodeError:
        cmc_filter_list = []
        type_filter_list = []
    
    # Apply filters
    filtered_cards = filter_cards(
        cards_data,
        name_search=name,
        type_search=type_search,
        oracle_search=oracle,
        regex_mode=regex_mode,
        word_order=word_order,
        colors=color_list,
        colorless=colorless,
        exact_colors=exact_colors,  # Pass the new parameter
        exact_types=exact_types, 
        cmc_filters=cmc_filter_list,
        type_filters=type_filter_list,
        sort_by=sort_by
    )
    
    # Pagination
    total_cards = len(filtered_cards)
    total_pages = (total_cards - 1) // per_page + 1 if total_cards > 0 else 1
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    page_cards = filtered_cards[start_idx:end_idx]
    
    return {
        "cards": page_cards,
        "total_cards": total_cards,
        "total_pages": total_pages,
        "current_page": page,
        "per_page": per_page
    }

@app.get("/api/suggest")
async def suggest_cards(q: str = "", limit: int = 10):
    """API endpoint for card name suggestions"""
    if not q or len(q) < 2:
        return {"suggestions": []}
    
    query = q.lower()
    suggestions = []
    
    # Find matching card names
    for card in cards_data:
        card_name = card.get('name', '')
        if query in card_name.lower():
            suggestions.append(card_name)
            
            if len(suggestions) >= limit:
                break
    
    # Sort by relevance (exact matches first, then starts-with, then contains)
    def sort_key(name):
        name_lower = name.lower()
        if name_lower == query:
            return (0, name)  # Exact match first
        elif name_lower.startswith(query):
            return (1, name)  # Starts with second
        else:
            return (2, name)  # Contains third
    
    suggestions.sort(key=sort_key)
    
    return {"suggestions": suggestions[:limit]}

@app.get("/api/suggest-types")
async def suggest_types(q: str = "", limit: int = 10):
    """API endpoint for card type suggestions"""
    if not q:
        return {"suggestions": []}
    
    query = q.lower()
    type_words = set()
    
    # Extract all unique type words from all cards
    for card in cards_data:
        type_line = card.get('type_line', '')
        if type_line:
            # Split by common separators and clean
            words = re.split(r'[\s—\-]+', type_line)
            for word in words:
                # Clean word of special characters but keep valid type words
                cleaned_word = word.strip().replace('\'s', '')
                if cleaned_word and len(cleaned_word) > 1:
                    type_words.add(cleaned_word)
    
    # Find matching type words
    suggestions = []
    for type_word in type_words:
        if query in type_word.lower():
            suggestions.append(type_word)
    
    # Sort by relevance and commonality
    # Count occurrences for better sorting
    type_counts = {}
    for card in cards_data:
        type_line = card.get('type_line', '')
        for suggestion in suggestions:
            if suggestion in type_line:
                type_counts[suggestion] = type_counts.get(suggestion, 0) + 1
    
    def sort_key(type_text):
        type_lower = type_text.lower()
        count = type_counts.get(type_text, 0)
        if type_lower == query:
            return (0, -count, type_text)  # Exact match first
        elif type_lower.startswith(query):
            return (1, -count, type_text)  # Starts with second
        else:
            return (2, -count, type_text)  # Contains third
    
    suggestions.sort(key=sort_key)
    
    # Also add some common type combinations if they match
    common_combinations = [
        "Legendary Creature", "Artifact Creature", "Enchantment Creature",
        "Legendary Planeswalker", "Snow Creature", "Tribal Instant",
        "Tribal Sorcery", "Legendary Artifact", "Legendary Enchantment",
        "Equipment", "Aura", "Vehicle", "Saga", "Class", "Adventure"
    ]
    
    for combo in common_combinations:
        if query in combo.lower() and combo not in suggestions:
            suggestions.append(combo)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_suggestions = []
    for s in suggestions:
        if s not in seen:
            seen.add(s)
            unique_suggestions.append(s)
    
    return {"suggestions": unique_suggestions[:limit]}

@app.get("/card/{card_id}")
async def card_detail(request: Request, card_id: str):
    """Card detail page"""
    # Find card by some identifier (you'd need to add an ID field)
    card = next((c for c in cards_data if c.get('name') == card_id), None)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    
    return templates.TemplateResponse("card_detail.html", {
        "request": request,
        "card": card
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)