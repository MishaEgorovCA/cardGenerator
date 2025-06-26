#!/usr/bin/env python3
"""
Template Analyzer - Helper tool to find optimal positions on your card template

This script helps you determine the best coordinates for text and image placement
on your card template by showing a grid overlay and allowing you to click to
get coordinates.
"""

from PIL import Image, ImageDraw, ImageFont
import tkinter as tk
from tkinter import filedialog, messagebox
import json


class TemplateAnalyzer:
    """Interactive tool to analyze card templates and find optimal positioning."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Card Template Analyzer")
        self.template_path = None
        self.canvas = None
        self.image = None
        self.photo = None
        
    def run(self):
        """Run the template analyzer."""
        # Create UI
        self.create_ui()
        
        # Start the application
        self.root.mainloop()
    
    def create_ui(self):
        """Create the user interface."""
        # File selection frame
        file_frame = tk.Frame(self.root)
        file_frame.pack(pady=10)
        
        tk.Button(file_frame, text="Load Template", 
                 command=self.load_template).pack(side=tk.LEFT, padx=5)
        
        tk.Button(file_frame, text="Save Coordinates", 
                 command=self.save_coordinates).pack(side=tk.LEFT, padx=5)
        
        tk.Button(file_frame, text="Show Grid", 
                 command=self.toggle_grid).pack(side=tk.LEFT, padx=5)
        
        # Instructions
        instructions = tk.Label(self.root, 
                              text="Load a template, then click on areas to get coordinates.\n" +
                                   "Click where you want: Title position, Image area corners, Description area corners",
                              justify=tk.LEFT)
        instructions.pack(pady=5)
        
        # Canvas for image display
        self.canvas = tk.Canvas(self.root, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-1>", self.on_click)
        
        # Coordinates display
        self.coord_label = tk.Label(self.root, text="Click on the template to see coordinates")
        self.coord_label.pack(pady=5)
        
        # Collected coordinates
        self.coordinates = {
            "title_position": None,
            "image_area": [],
            "description_area": []
        }
        
        self.show_grid = False
    
    def load_template(self):
        """Load a template image."""
        file_path = filedialog.askopenfilename(
            title="Select Card Template",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        
        if file_path:
            self.template_path = file_path
            self.display_template()
    
    def display_template(self):
        """Display the template on the canvas."""
        if not self.template_path:
            return
        
        # Load and display image
        self.image = Image.open(self.template_path)
        
        # Resize if too large
        max_size = 800
        if max(self.image.size) > max_size:
            self.image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        # Convert to PhotoImage for tkinter
        display_image = self.image.copy()
        if self.show_grid:
            display_image = self.add_grid(display_image)
        
        self.photo = tk.PhotoImage(data=display_image.tobytes(), format='ppm')
        
        # Update canvas
        self.canvas.config(width=self.image.size[0], height=self.image.size[1])
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
    
    def add_grid(self, image):
        """Add a grid overlay to help with positioning."""
        grid_image = image.copy()
        draw = ImageDraw.Draw(grid_image)
        
        width, height = grid_image.size
        grid_size = 50
        
        # Draw vertical lines
        for x in range(0, width, grid_size):
            draw.line([(x, 0), (x, height)], fill=(200, 200, 200), width=1)
        
        # Draw horizontal lines
        for y in range(0, height, grid_size):
            draw.line([(0, y), (width, y)], fill=(200, 200, 200), width=1)
        
        return grid_image
    
    def toggle_grid(self):
        """Toggle grid display."""
        self.show_grid = not self.show_grid
        if self.template_path:
            self.display_template()
    
    def on_click(self, event):
        """Handle canvas clicks to collect coordinates."""
        x, y = event.x, event.y
        
        # Update coordinate display
        self.coord_label.config(text=f"Clicked: ({x}, {y})")
        
        # Ask user what this coordinate represents
        choice = messagebox.askyesnocancel(
            "Coordinate Type",
            f"Coordinates: ({x}, {y})\n\n" +
            "What does this position represent?\n\n" +
            "Yes = Title position\n" +
            "No = Image/Description area corner\n" +
            "Cancel = Just show coordinates"
        )
        
        if choice is True:  # Title position
            self.coordinates["title_position"] = [x, y]
            messagebox.showinfo("Saved", f"Title position saved: ({x}, {y})")
        
        elif choice is False:  # Area corner
            area_choice = messagebox.askyesno(
                "Area Type",
                "Is this for the Image area?\n\n" +
                "Yes = Image area corner\n" +
                "No = Description area corner"
            )
            
            if area_choice:  # Image area
                self.coordinates["image_area"].append([x, y])
                messagebox.showinfo("Saved", 
                                  f"Image area corner {len(self.coordinates['image_area'])} saved: ({x}, {y})")
            else:  # Description area
                self.coordinates["description_area"].append([x, y])
                messagebox.showinfo("Saved", 
                                  f"Description area corner {len(self.coordinates['description_area'])} saved: ({x}, {y})")
    
    def save_coordinates(self):
        """Save collected coordinates to a JSON file."""
        if not any([self.coordinates["title_position"], 
                   self.coordinates["image_area"], 
                   self.coordinates["description_area"]]):
            messagebox.showwarning("No Data", "No coordinates have been collected yet!")
            return
        
        # Format coordinates for config file
        config_data = {
            "card_settings": {},
            "message": "Coordinates collected from template analyzer"
        }
        
        if self.coordinates["title_position"]:
            config_data["card_settings"]["title_position"] = self.coordinates["title_position"]
        
        if len(self.coordinates["image_area"]) >= 2:
            # Convert corner points to area rectangle
            corners = self.coordinates["image_area"]
            x_coords = [p[0] for p in corners]
            y_coords = [p[1] for p in corners]
            config_data["card_settings"]["image_area"] = [
                min(x_coords), min(y_coords), max(x_coords), max(y_coords)
            ]
        
        if len(self.coordinates["description_area"]) >= 2:
            # Convert corner points to area rectangle
            corners = self.coordinates["description_area"]
            x_coords = [p[0] for p in corners]
            y_coords = [p[1] for p in corners]
            config_data["card_settings"]["description_area"] = [
                min(x_coords), min(y_coords), max(x_coords), max(y_coords)
            ]
        
        # Save to file
        save_path = filedialog.asksaveasfilename(
            title="Save Coordinates",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        
        if save_path:
            with open(save_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            messagebox.showinfo("Saved", f"Coordinates saved to {save_path}")
            
            # Show summary
            summary = "Collected Coordinates:\n\n"
            for key, value in config_data["card_settings"].items():
                summary += f"{key}: {value}\n"
            
            messagebox.showinfo("Summary", summary)


def main():
    """Run the template analyzer."""
    app = TemplateAnalyzer()
    app.run()


if __name__ == "__main__":
    main()
