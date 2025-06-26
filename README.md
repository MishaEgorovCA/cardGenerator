# Auto Card Designer

An automated card generation tool that creates game cards from spreadsheet data using a template image.

## Features

- **Spreadsheet Support**: Read card data from CSV or Excel files
- **Template-Based Design**: Use your own card template as the base
- **Automated Text Placement**: Automatically positions titles and descriptions
- **Image Integration**: Adds card artwork to designated areas
- **Type-Based Borders**: Different colored borders for card types (D=Red, V=Green, P=Blue, ?=Yellow)
- **Batch Processing**: Generate hundreds of cards automatically
- **Configurable Settings**: Customize fonts, positions, and colors

## Quick Start

### 1. Setup
```bash
# Install dependencies
pip install -r requirements.txt
```

### 2. Prepare Your Files

**Template Image**: Place your card template in the `templates/` directory
- Should have a clear area for the card image
- Space at the top for the title
- Area below the image for description text

**Card Images**: Place individual card artwork in the `images/` directory

**Spreadsheet**: Create a CSV or Excel file with these columns:
- `title`: Card name
- `description`: What the card does
- `type`: Card type (D, V, P, or ?)
- `image`: Path to the card's image file

### 3. Generate Cards
```bash
# Basic usage
python card_generator.py data/your_cards.csv

# Custom template and output directory
python card_generator.py data/your_cards.csv -t templates/my_template.png -o my_output
```

## Project Structure
```
Auto Card Designer/
├── card_generator.py       # Main script
├── config.json            # Configuration settings
├── requirements.txt        # Python dependencies
├── data/                   # Input spreadsheets
│   └── sample_cards.csv    # Example data
├── templates/              # Card template images
├── images/                 # Card artwork
└── output/                 # Generated cards
```

## Configuration

Edit `config.json` to customize:
- Font sizes and positions
- Border colors for card types
- Image and text area coordinates
- Output format settings

## Card Types

| Type | Name    | Border Color | Description |
|------|---------|--------------|-------------|
| D    | Defense | Red          | Defensive cards |
| V    | Victory | Green        | Victory condition cards |
| P    | Power   | Blue         | Power/attack cards |
| ?    | Mystery | Yellow       | Special/mystery cards |

## Spreadsheet Format

Your spreadsheet should have these columns:

| title | description | type | image |
|-------|-------------|------|-------|
| Fire Blast | Deal 3 damage to any target | P | images/fire_blast.png |
| Shield Wall | All creatures gain +0/+2 | D | images/shield_wall.png |

## Template Requirements

Your card template should be a PNG image with:
- **Title Area**: Space at the top (default: 50px from left, 20px from top)
- **Image Area**: Square/rectangular area for card artwork (default: 75,80 to 295,280)
- **Description Area**: Text area below image (default: 20,300 to 350,450)

## Tips

1. **Image Size**: Card images will be automatically resized to fit the designated area
2. **Text Wrapping**: Long descriptions automatically wrap within the text area
3. **Missing Images**: Cards will still generate if image files are missing
4. **Batch Processing**: Process hundreds of cards at once
5. **Error Handling**: Script continues if individual cards fail to generate

## Troubleshooting

**"Template file not found"**: Place your template image in the `templates/` directory

**"Font issues"**: The script will fallback to system default fonts if custom fonts aren't available

**"Image not loading"**: Check that image paths in your spreadsheet are correct and files exist

## Example Usage

```bash
# Generate cards from sample data
python card_generator.py data/sample_cards.csv

# Use custom template
python card_generator.py data/my_cards.xlsx -t templates/fantasy_template.png

# Custom output directory
python card_generator.py data/cards.csv -o final_cards
```

## License

MIT License - Feel free to use and modify for your projects!
