# Getting Started with Auto Card Designer

## Step 1: Prepare Your Template
1. Create a card template image (PNG format recommended)
2. The template should have:
   - A clear rectangular area for the card image
   - Space at the top for the card title
   - Area below the image for description text
3. Place your template in the `templates/` directory

## Step 2: Prepare Your Card Images
1. Collect all the artwork for your cards
2. Save them as PNG, JPG, or other common image formats
3. Place them in the `images/` directory
4. Note the filenames - you'll need these for your spreadsheet

## Step 3: Create Your Spreadsheet
Create a CSV or Excel file with these columns:
- **title**: The card's name
- **description**: What the card does (can be long text)
- **type**: Card type - use D, V, P, or ? (determines border color)
- **image**: Path to the card's image file (e.g., "images/fire_blast.png")

## Step 4: Generate Your Cards
Open a terminal in VS Code and run:
```bash
python card_generator.py data/your_spreadsheet.csv
```

Or use VS Code tasks:
- Press `Ctrl+Shift+P`
- Type "Tasks: Run Task"
- Select "Generate Sample Cards" or "Run Card Generator (Custom File)"

## Example Spreadsheet Row
```
title: Fire Blast
description: Deal 3 damage to any target. This spell cannot be countered by opponent spells.
type: P
image: images/fire_blast.png
```

## Card Types and Border Colors
- **D** (Defense) = Red border
- **V** (Victory) = Green border  
- **P** (Power) = Blue border
- **?** (Mystery) = Yellow border

## Customization
Edit `config.json` to adjust:
- Text positions and sizes
- Border colors
- Image placement areas
- Font settings

Your generated cards will appear in the `output/` directory!
