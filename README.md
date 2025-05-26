# MTG Efficiency Variable Database

A FastAPI-powered Magic: The Gathering card database with advanced filtering capabilities.

## Features
- Advanced card search with name, type, and oracle text filters
- Color identity and exact color matching
- Mana value filtering with multiple conditions
- Card type filtering with AND/OR logic
- Real-time autocomplete suggestions
- Mobile-responsive design

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Place your `filtered_cards.json` file in the project root
3. Run: `python fast_gallery.py`
4. Open: `http://localhost:8000`

## Data Processing
Use `filter.py` to process Scryfall JSON data into the required format.