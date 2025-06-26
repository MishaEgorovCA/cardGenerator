#!/usr/bin/env python3
"""
Auto Card Designer - Automated Card Generation Tool

This script reads card data from a spreadsheet and generates cards using a template.
Supports different card types with colored borders and automatic text placement.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import argparse


class CardGenerator:
    """Main class for generating cards from template and data."""
    
    def __init__(self, template_path: str, output_dir: str = "output", config_path: str = "config.json"):
        """
        Initialize the card generator.
        
        Args:
            template_path: Path to the card template image
            output_dir: Directory to save generated cards
            config_path: Path to configuration file
        """
        self.template_path = Path(template_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Get settings from config
        card_settings = self.config.get("card_settings", {})
        self.title_font_size = card_settings.get("title_font_size", 24)
        self.description_font_size = card_settings.get("description_font_size", 16)
        self.border_width = card_settings.get("border_width", 8)
        self.text_color = tuple(card_settings.get("text_color", [0, 0, 0]))
        self.title_color = tuple(card_settings.get("title_color", [0, 0, 0]))
        
        # Card type colors from config
        self.type_colors = {}
        for card_type, settings in self.config.get("card_types", {}).items():
            self.type_colors[card_type] = tuple(settings.get("color", [128, 128, 128]))
        
        # Fallback colors if not in config
        if not self.type_colors:
            self.type_colors = {
                'D': (255, 0, 0),    # Red for D type
                'V': (0, 255, 0),    # Green for V type  
                'P': (0, 0, 255),    # Blue for P type
                '?': (255, 255, 0)   # Yellow for ? type
            }
        
        # Load fonts (will try to use system fonts)
        self.title_font = self._load_font(self.title_font_size, bold=True)
        self.description_font = self._load_font(self.description_font_size)
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Config file {config_path} not found. Using defaults.")
            return {}
        except json.JSONDecodeError as e:
            print(f"Warning: Error reading config file: {e}. Using defaults.")
            return {}
    
    def _load_font(self, size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
        """Load a font with fallback to default if not available."""
        try:
            # Try to load common fonts
            font_names = [
                "arial.ttf", "Arial.ttf", "calibri.ttf", "Calibri.ttf",
                "DejaVuSans.ttf", "LiberationSans-Regular.ttf"
            ]
            
            if bold:
                bold_fonts = [
                    "arialbd.ttf", "Arial-Bold.ttf", "calibrib.ttf", "Calibri-Bold.ttf",
                    "DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf"
                ]
                font_names = bold_fonts + font_names
            
            for font_name in font_names:
                try:
                    return ImageFont.truetype(font_name, size)
                except OSError:
                    continue
                    
            # Fallback to default font
            return ImageFont.load_default()
            
        except Exception:
            return ImageFont.load_default()
    
    def load_spreadsheet_data(self, file_path: str) -> pd.DataFrame:
        """
        Load card data from spreadsheet file.
        
        Args:
            file_path: Path to CSV or Excel file
            
        Returns:
            DataFrame with card data
        """
        file_path = Path(file_path)
        
        if file_path.suffix.lower() == '.csv':
            return pd.read_csv(file_path)
        elif file_path.suffix.lower() in ['.xlsx', '.xls']:
            return pd.read_excel(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
    
    def add_colored_border(self, image: Image.Image, card_type: str) -> Image.Image:
        """
        Add a colored border to the card based on its type.
        
        Args:
            image: The card image
            card_type: Card type (D, V, P, or ?)
            
        Returns:
            Image with colored border
        """
        # Create a copy to avoid modifying the original
        bordered_image = image.copy()
        draw = ImageDraw.Draw(bordered_image)
        
        # Get color for this card type
        color = self.type_colors.get(card_type.upper(), (128, 128, 128))  # Gray default
        
        # Draw border
        width, height = bordered_image.size
        for i in range(self.border_width):
            draw.rectangle([i, i, width-1-i, height-1-i], outline=color, width=1)
        
        return bordered_image
    
    def add_text_to_card(self, image: Image.Image, title: str, description: str, 
                        title_position: Tuple[int, int], 
                        description_area: Tuple[int, int, int, int]) -> Image.Image:
        """
        Add title and description text to the card.
        
        Args:
            image: The card image
            title: Card title text
            description: Card description text
            title_position: (x, y) position for title
            description_area: (x1, y1, x2, y2) area for description
            
        Returns:
            Image with text added
        """
        text_image = image.copy()
        draw = ImageDraw.Draw(text_image)
        
        # Add title
        draw.text(title_position, title, fill=self.title_color, font=self.title_font)
        
        # Add description with text wrapping
        self._draw_wrapped_text(draw, description, description_area, self.description_font)
        
        return text_image
    
    def _draw_wrapped_text(self, draw: ImageDraw.Draw, text: str, 
                          area: Tuple[int, int, int, int], font: ImageFont.FreeTypeFont):
        """Draw text with automatic word wrapping within the specified area."""
        x1, y1, x2, y2 = area
        max_width = x2 - x1
        max_height = y2 - y1
        
        words = text.split()
        lines = []
        current_line = ""
        
        # Word wrap
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            bbox = draw.textbbox((0, 0), test_line, font=font)
            text_width = bbox[2] - bbox[0]
            
            if text_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        # Draw lines
        y_offset = y1
        line_height = font.size + 4  # Add some line spacing
        
        for line in lines:
            if y_offset + line_height > y2:
                break  # Don't draw beyond the area
            draw.text((x1, y_offset), line, fill=self.text_color, font=font)
            y_offset += line_height
    
    def add_image_to_card(self, template: Image.Image, card_image_path: str,
                         image_area: Tuple[int, int, int, int], card_type: str = '?') -> Image.Image:
        """
        Add a card image to the template, or fill with type color if no image.
        
        Args:
            template: The template image
            card_image_path: Path to the card's image
            image_area: (x1, y1, x2, y2) area where image should be placed
            card_type: Card type for color fill when no image
            
        Returns:
            Template with card image added or color fill
        """
        result = template.copy()
        draw = ImageDraw.Draw(result)
        x1, y1, x2, y2 = image_area
        
        # Check if image exists and is valid
        has_valid_image = (card_image_path and 
                          str(card_image_path).strip() and 
                          card_image_path != 'nan' and
                          Path(card_image_path).exists())
        
        if has_valid_image:
            try:
                # Load and resize the card image
                card_img = Image.open(card_image_path)
                target_size = (x2 - x1, y2 - y1)
                
                # Resize while maintaining aspect ratio
                card_img.thumbnail(target_size, Image.Resampling.LANCZOS)
                
                # Center the image in the area
                img_width, img_height = card_img.size
                center_x = x1 + (target_size[0] - img_width) // 2
                center_y = y1 + (target_size[1] - img_height) // 2
                
                result.paste(card_img, (center_x, center_y))
                
            except Exception as e:
                print(f"Error loading image {card_image_path}: {e}")
                # Fall back to color fill
                has_valid_image = False
        
        if not has_valid_image:
            # Fill image area with card type color (lighter version)
            type_color = self.type_colors.get(card_type.upper(), (128, 128, 128))
            # Make color lighter (add 128 to each RGB component, max 255)
            light_color = tuple(min(255, c + 128) for c in type_color)
            draw.rectangle([x1, y1, x2, y2], fill=light_color, outline=type_color, width=2)
            
            # Add a subtle pattern or text to indicate missing image
            center_x = x1 + (x2 - x1) // 2
            center_y = y1 + (y2 - y1) // 2
            
            # Draw type letter in center
            try:
                # Use larger font for the type letter
                type_font = self._load_font(min(48, (y2 - y1) // 3), bold=True)
                bbox = draw.textbbox((0, 0), card_type.upper(), font=type_font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                text_x = center_x - text_width // 2
                text_y = center_y - text_height // 2
                draw.text((text_x, text_y), card_type.upper(), fill=type_color, font=type_font)
            except:
                # Fallback to simple text
                draw.text((center_x - 10, center_y - 10), card_type.upper(), fill=type_color)
        
        return result
    
    def generate_card(self, card_data: Dict, title_pos: Tuple[int, int],
                     description_area: Tuple[int, int, int, int],
                     image_area: Tuple[int, int, int, int]) -> Image.Image:
        """
        Generate a single card from the template and data.
        
        Args:
            card_data: Dictionary with card information
            title_pos: Position for title text
            description_area: Area for description text
            image_area: Area for card image
            
        Returns:
            Generated card image
        """
        # Load template
        template = Image.open(self.template_path)
        
        # Get card type for color coordination
        card_type = str(card_data.get('type', '?'))
        
        # Add card image if provided, otherwise use type color
        image_path = card_data.get('image', '')
        template = self.add_image_to_card(template, image_path, image_area, card_type)
        
        # Add text
        title = str(card_data.get('title', ''))
        description = str(card_data.get('description', ''))
        template = self.add_text_to_card(template, title, description, title_pos, description_area)
        
        # Add colored border based on type
        template = self.add_colored_border(template, card_type)
        
        return template
    
    def generate_cards_from_spreadsheet(self, spreadsheet_path: str,
                                      title_pos: Tuple[int, int] = None,
                                      description_area: Tuple[int, int, int, int] = None,
                                      image_area: Tuple[int, int, int, int] = None):
        """
        Generate all cards from a spreadsheet.
        
        Args:
            spreadsheet_path: Path to the spreadsheet file
            title_pos: Position for card titles (uses config if None)
            description_area: Area for card descriptions (uses config if None)
            image_area: Area for card images (uses config if None)
        """
        # Use config settings if parameters not provided
        card_settings = self.config.get("card_settings", {})
        if title_pos is None:
            title_pos = tuple(card_settings.get("title_position", [50, 20]))
        if description_area is None:
            description_area = tuple(card_settings.get("description_area", [20, 300, 350, 450]))
        if image_area is None:
            image_area = tuple(card_settings.get("image_area", [75, 80, 295, 280]))
        """
        # Load data
        df = self.load_spreadsheet_data(spreadsheet_path)
        
        print(f"Loaded {len(df)} cards from {spreadsheet_path}")
        print("Required columns: title, description, type, image")
        print("Available columns:", list(df.columns))
        
        # Generate cards
        for index, row in df.iterrows():
            try:
                # Handle missing image values (NaN, empty strings, etc.)
                image_value = row.get('image', '')
                if pd.isna(image_value):
                    image_value = ''
                
                card_data = {
                    'title': str(row.get('title', f'Card {index + 1}')),
                    'description': str(row.get('description', '')),
                    'type': str(row.get('type', '?')),
                    'image': str(image_value) if image_value else ''
                }
                
                # Generate the card
                card_image = self.generate_card(card_data, title_pos, description_area, image_area)
                
                # Save the card with sanitized filename
                safe_title = card_data['title'].replace('?', '_Q_').replace(':', '_').replace('/', '_').replace('\\', '_').replace('*', '_').replace('<', '_').replace('>', '_').replace('|', '_').replace('"', '_')
                output_filename = f"card_{index + 1}_{safe_title.replace(' ', '_')}.png"
                output_path = self.output_dir / output_filename
                card_image.save(output_path, 'PNG')
                
                print(f"Generated: {output_filename}")
                
            except Exception as e:
                print(f"Error generating card {index + 1}: {e}")
        
        print(f"\nCard generation complete! Cards saved to: {self.output_dir}")


def main():
    """Main function to run the card generator."""
    parser = argparse.ArgumentParser(description='Generate cards from spreadsheet data')
    parser.add_argument('spreadsheet', help='Path to spreadsheet file (CSV or Excel)')
    parser.add_argument('-t', '--template', default='templates/card_template.png',
                       help='Path to card template image')
    parser.add_argument('-o', '--output', default='output',
                       help='Output directory for generated cards')
    
    args = parser.parse_args()
    
    # Check if template exists
    if not Path(args.template).exists():
        print(f"Error: Template file not found: {args.template}")
        print("Please place your card template image in the templates/ directory")
        sys.exit(1)
    
    # Check if spreadsheet exists
    if not Path(args.spreadsheet).exists():
        print(f"Error: Spreadsheet file not found: {args.spreadsheet}")
        sys.exit(1)
    
    try:
        # Create generator and process cards
        generator = CardGenerator(args.template, args.output)
        generator.generate_cards_from_spreadsheet(args.spreadsheet)
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
