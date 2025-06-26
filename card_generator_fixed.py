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
        self.title_max_font_size = card_settings.get("title_max_font_size", 64)
        self.description_font_size = card_settings.get("description_font_size", 16)
        self.description_max_font_size = card_settings.get("description_max_font_size", 48)
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
        Add a colored border with square outer edge and rounded inner edge.
        
        Args:
            image: The card image
            card_type: Card type (D, V, P, or ?)
            
        Returns:
            Image with colored border
        """
        # Create a copy to avoid modifying the original
        bordered_image = image.copy()
        
        # Get color for this card type
        color = self.type_colors.get(card_type.upper(), (128, 128, 128))  # Gray default
        
        width, height = bordered_image.size
        
        # Get corner radius from config (with fallback)
        card_settings = self.config.get("card_settings", {})
        corner_radius = card_settings.get("border_corner_radius", 15)
        corner_radius = min(corner_radius, self.border_width - 2)  # Ensure it fits within border
        
        # Create a mask for the border with square outer edge and rounded inner edge
        mask = Image.new('L', (width, height), 0)
        mask_draw = ImageDraw.Draw(mask)
        
        # Draw the outer square rectangle (full border area)
        mask_draw.rectangle([0, 0, width-1, height-1], fill=255)
        
        # Draw the inner rounded rectangle (content area) to "cut out" the center
        inner_x1 = self.border_width
        inner_y1 = self.border_width
        inner_x2 = width - 1 - self.border_width
        inner_y2 = height - 1 - self.border_width
        
        if inner_x2 > inner_x1 and inner_y2 > inner_y1:
            self._draw_filled_rounded_rectangle(mask_draw, inner_x1, inner_y1, 
                                              inner_x2, inner_y2, corner_radius, 0)
        
        # Create a colored border image
        border_img = Image.new('RGBA', (width, height), color + (255,))
        
        # Apply the mask to create the border shape
        border_img.putalpha(mask)
        
        # Composite the border onto the original image
        bordered_image = Image.alpha_composite(bordered_image.convert('RGBA'), border_img)
        
        return bordered_image.convert('RGB')
    
    def _draw_filled_rounded_rectangle(self, draw: ImageDraw.Draw, x1: int, y1: int, 
                                     x2: int, y2: int, radius: int, fill_value: int):
        """Draw a filled rounded rectangle on a mask."""
        if radius <= 0 or x2 <= x1 or y2 <= y1:
            # No rounding or invalid dimensions, just draw a regular rectangle
            if x2 > x1 and y2 > y1:
                draw.rectangle([x1, y1, x2, y2], fill=fill_value)
            return
        
        # Ensure radius doesn't exceed half the width or height
        max_radius = min((x2 - x1) // 2, (y2 - y1) // 2)
        radius = min(radius, max_radius)
        
        if radius <= 0:
            draw.rectangle([x1, y1, x2, y2], fill=fill_value)
            return
        
        # Draw the main rectangle (without corners)
        draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill_value)  # Middle
        draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill_value)  # Center
        
        # Draw the four corner circles
        draw.ellipse([x1, y1, x1 + radius * 2, y1 + radius * 2], fill=fill_value)  # Top-left
        draw.ellipse([x2 - radius * 2, y1, x2, y1 + radius * 2], fill=fill_value)  # Top-right
        draw.ellipse([x1, y2 - radius * 2, x1 + radius * 2, y2], fill=fill_value)  # Bottom-left
        draw.ellipse([x2 - radius * 2, y2 - radius * 2, x2, y2], fill=fill_value)  # Bottom-right
    
    def add_text_to_card(self, image: Image.Image, title: str, description: str, 
                        title_area: Tuple[int, int, int, int], 
                        description_area: Tuple[int, int, int, int]) -> Image.Image:
        """
        Add title and description text to the card.
        
        Args:
            image: The card image
            title: Card title text
            description: Card description text
            title_area: (x1, y1, x2, y2) area for title
            description_area: (x1, y1, x2, y2) area for description
            
        Returns:
            Image with text added
        """
        text_image = image.copy()
        draw = ImageDraw.Draw(text_image)
        
        # Add title with scaling to fit area
        self._draw_scaled_title(draw, title, title_area)
        
        # Add description with text color and word wrapping
        self._draw_wrapped_text(draw, description, description_area, self.description_font)
        
        return text_image

    def _draw_scaled_title(self, draw: ImageDraw.Draw, title: str, 
                          title_area: Tuple[int, int, int, int]):
        """Draw title text with automatic scaling to fit the area."""
        x1, y1, x2, y2 = title_area
        max_width = x2 - x1
        max_height = y2 - y1
        
        # Get maximum font size from config
        max_font_size = self.title_max_font_size
        min_font_size = 12
        
        # Try to find the largest font size that fits
        best_font = None
        best_font_size = max_font_size
        
        # Try different font sizes starting from max and working down
        for font_size in range(max_font_size, min_font_size - 1, -2):
            try:
                test_font = self._load_font(font_size, bold=True)
                
                # Get text bounding box
                bbox = draw.textbbox((0, 0), title, font=test_font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                # Check if text fits within the area
                if text_width <= max_width and text_height <= max_height:
                    best_font = test_font
                    best_font_size = font_size
                    break
            except:
                continue
        
        # Fallback if no font size worked
        if best_font is None:
            best_font = self._load_font(min_font_size, bold=True)
        
        # Get final text dimensions for centering
        bbox = draw.textbbox((0, 0), title, font=best_font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Center the text in the area
        text_x = x1 + (max_width - text_width) // 2
        text_y = y1 + (max_height - text_height) // 2
        
        # Draw the title
        draw.text((text_x, text_y), title, fill=self.title_color, font=best_font)
    
    def _draw_wrapped_text(self, draw: ImageDraw.Draw, text: str, 
                          area: Tuple[int, int, int, int], font: ImageFont.FreeTypeFont):
        """Draw text with automatic word wrapping and intelligent scaling to fit the area."""
        x1, y1, x2, y2 = area
        max_width = x2 - x1
        max_height = y2 - y1
        
        # Get maximum font size from config
        max_font_size = self.description_max_font_size
        min_font_size = 8
        
        # Try to find the largest font size that fits
        best_font = font
        best_font_size = self.description_font_size
        
        # Try different font sizes starting from max and working down
        for font_size in range(max_font_size, min_font_size - 1, -2):
            try:
                test_font = self._load_font(font_size)
                lines = self._wrap_text_to_fit(text, max_width, test_font, draw)
                
                # Calculate total height needed
                line_height = test_font.size + 4
                total_height = len(lines) * line_height
                
                if total_height <= max_height:
                    best_font = test_font
                    best_font_size = font_size
                    break
            except:
                continue
        
        # Final word wrap with the best font
        lines = self._wrap_text_to_fit(text, max_width, best_font, draw)
        
        # Draw lines starting from the top of the area (no vertical centering)
        line_height = best_font.size + 4
        y_offset = y1
        
        for line in lines:
            if y_offset + line_height > y2:
                break  # Don't draw beyond the area
            draw.text((x1, y_offset), line, fill=self.text_color, font=best_font)
            y_offset += line_height
    
    def _wrap_text_to_fit(self, text: str, max_width: int, font: ImageFont.FreeTypeFont, 
                         draw: ImageDraw.Draw) -> List[str]:
        """Helper method to wrap text to fit within max_width."""
        words = text.split()
        lines = []
        current_line = ""
        
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
        
        return lines
    
    def add_image_to_card(self, template: Image.Image, card_image_path: str,
                         image_area: Tuple[int, int, int, int], card_type: str = '?') -> Image.Image:
        """
        Add a card image to the template, scaling to fill the entire area.
        
        Args:
            template: The template image
            card_image_path: Path to the card's image
            image_area: (x1, y1, x2, y2) area where image should be placed
            card_type: Card type for fallback color and letter
            
        Returns:
            Template with card image added
        """
        result = template.copy()
        
        if not card_image_path or not Path(card_image_path).exists():
            # If no image, fill with card type color and draw type letter
            if card_image_path:  # Only show warning if a path was provided
                print(f"Warning: Image not found: {card_image_path}")
            return self._create_fallback_image(result, image_area, card_type)
        
        try:
            # Load the card image
            card_img = Image.open(card_image_path)
            x1, y1, x2, y2 = image_area
            target_width = x2 - x1
            target_height = y2 - y1
            
            # Calculate scaling to fill the entire area (may crop edges)
            img_width, img_height = card_img.size
            scale_x = target_width / img_width
            scale_y = target_height / img_height
            
            # Use the larger scale to ensure the image fills the entire area
            scale = max(scale_x, scale_y)
            
            # Calculate new dimensions
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            
            # Resize the image
            card_img = card_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Calculate crop box to center the image
            crop_x = (new_width - target_width) // 2
            crop_y = (new_height - target_height) // 2
            
            # Crop to exact target size
            if new_width > target_width or new_height > target_height:
                card_img = card_img.crop((
                    crop_x, crop_y, 
                    crop_x + target_width, crop_y + target_height
                ))
            
            # Paste the image at the exact position
            result.paste(card_img, (x1, y1))
            
        except Exception as e:
            print(f"Error loading image {card_image_path}: {e}")
        
        return result

    def _create_fallback_image(self, template: Image.Image, image_area: Tuple[int, int, int, int], 
                              card_type: str) -> Image.Image:
        """
        Create a fallback image when the card image is missing.
        Fills the image area with the card type color and draws the type letter.
        
        Args:
            template: The template image
            image_area: (x1, y1, x2, y2) area where image should be placed
            card_type: Card type (D, V, P, ?)
            
        Returns:
            Template with fallback image area filled
        """
        result = template.copy()
        draw = ImageDraw.Draw(result)
        
        x1, y1, x2, y2 = image_area
        target_width = x2 - x1
        target_height = y2 - y1
        
        # Get the color for this card type
        type_color = self.type_colors.get(card_type, self.type_colors.get('?', (128, 128, 128)))
        
        # Fill the image area with the type color
        draw.rectangle([x1, y1, x2-1, y2-1], fill=type_color)
        
        # Calculate font size for the type letter (make it large but not too large)
        letter_font_size = min(target_width, target_height) // 3
        letter_font = self._load_font(letter_font_size, bold=True)
        
        # Calculate center position for the letter
        letter = card_type
        
        # Get text bounding box to center it properly
        bbox = draw.textbbox((0, 0), letter, font=letter_font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        letter_x = x1 + (target_width - text_width) // 2
        letter_y = y1 + (target_height - text_height) // 2
        
        # Draw the type letter in white
        draw.text((letter_x, letter_y), letter, fill=(255, 255, 255), font=letter_font)
        
        return result
    
    def generate_card(self, card_data: Dict, title_area: Tuple[int, int, int, int],
                     description_area: Tuple[int, int, int, int],
                     image_area: Tuple[int, int, int, int]) -> Image.Image:
        """
        Generate a single card from the template and data.
        
        Args:
            card_data: Dictionary with card information
            title_area: Area for title text
            description_area: Area for description text
            image_area: Area for card image
            
        Returns:
            Generated card image
        """
        # Load template
        template = Image.open(self.template_path)
        
        # Get card type for image handling
        card_type = str(card_data.get('type', '?'))
        
        # Add card image (will show fallback if image missing or not provided)
        image_path = card_data.get('image', '') if 'image' in card_data else ''
        template = self.add_image_to_card(template, image_path, image_area, card_type)
        
        # Add text
        title = str(card_data.get('title', ''))
        description = str(card_data.get('description', ''))
        template = self.add_text_to_card(template, title, description, title_area, description_area)
        
        # Add colored border based on type
        template = self.add_colored_border(template, card_type)
        
        return template
    
    def generate_cards_from_spreadsheet(self, spreadsheet_path: str,
                                      title_area: Tuple[int, int, int, int] = None,
                                      description_area: Tuple[int, int, int, int] = None,
                                      image_area: Tuple[int, int, int, int] = None):
        """
        Generate all cards from a spreadsheet.
        
        Args:
            spreadsheet_path: Path to the spreadsheet file
            title_area: Area for card titles (uses config if None)
            description_area: Area for card descriptions (uses config if None)
            image_area: Area for card images (uses config if None)
        """
        # Use config settings if parameters not provided
        card_settings = self.config.get("card_settings", {})
        if title_area is None:
            title_area = tuple(card_settings.get("title_area", [50, 20, 350, 80]))
        if description_area is None:
            description_area = tuple(card_settings.get("description_area", [20, 300, 350, 450]))
        if image_area is None:
            image_area = tuple(card_settings.get("image_area", [75, 80, 295, 280]))
        
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
                card_image = self.generate_card(card_data, title_area, description_area, image_area)
                
                # Save the card with sanitized filename
                safe_title = card_data['title'].replace('?', '_').replace(':', '_').replace('/', '_').replace('\\', '_').replace('*', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
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
