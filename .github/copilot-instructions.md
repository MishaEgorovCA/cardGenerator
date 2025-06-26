# Copilot Instructions for Auto Card Designer

<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

## Project Overview
This is an automated card game design generator that:
- Reads spreadsheet data containing card information (title, description, type, image)
- Uses PIL/Pillow for image manipulation and text overlay
- Generates cards using a template image
- Supports 4 card types (D, V, P, ?) with different border colors
- Batch processes multiple cards from spreadsheet data

## Key Libraries
- **Pillow (PIL)**: For image manipulation, text rendering, and compositing
- **pandas**: For reading and processing spreadsheet data (CSV, Excel)
- **openpyxl**: For Excel file support

## Project Structure
- `card_generator.py`: Main script for card generation
- `data/`: Directory for input spreadsheets
- `templates/`: Directory for card template images
- `images/`: Directory for card artwork/images
- `output/`: Directory for generated cards

## Coding Guidelines
- Use clear variable names for card properties (title, description, type, image_path)
- Handle different image formats and sizes gracefully
- Implement proper error handling for missing files or invalid data
- Use configuration files for customizable settings (fonts, colors, positions)
- Support batch processing with progress indicators
