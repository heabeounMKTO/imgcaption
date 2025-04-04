import os
import json
import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk
from PIL import Image, ImageTk
import glob

class ImageCaptioningApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Captioning Tool")
        self.root.geometry("1200x700")
        
        # Data structures
        self.current_image_path = None
        self.image_paths = []
        self.current_index = -1
        self.captions = {}
        self.captions_file = "captions.json"
        
        # Set up the main frames
        self.setup_ui()
        
        # Load existing captions if file exists
        self.load_captions()
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left frame for image viewer
        left_frame = ttk.Frame(main_frame, relief=tk.RIDGE, borderwidth=2)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Right frame for caption editor
        right_frame = ttk.Frame(main_frame, relief=tk.RIDGE, borderwidth=2)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=5, pady=5, ipadx=5, ipady=5)
        right_frame.config(width=400)
        
        # Set up image viewer
        self.setup_image_viewer(left_frame)
        
        # Set up caption editor
        self.setup_caption_editor(right_frame)
        
        # Set up control buttons
        self.setup_control_buttons(right_frame)
    
    def setup_image_viewer(self, parent):
        # Canvas for image display with scrollbars
        self.canvas_frame = ttk.Frame(parent)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        h_scrollbar = ttk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        v_scrollbar = ttk.Scrollbar(self.canvas_frame)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Canvas for image
        self.canvas = tk.Canvas(
            self.canvas_frame,
            xscrollcommand=h_scrollbar.set,
            yscrollcommand=v_scrollbar.set,
            bg='black'
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Configure scrollbars
        h_scrollbar.config(command=self.canvas.xview)
        v_scrollbar.config(command=self.canvas.yview)
        
        # Bind mouse events for zooming
        self.canvas.bind("<MouseWheel>", self.zoom)  # Windows
        self.canvas.bind("<Button-4>", self.zoom)  # Linux scroll up
        self.canvas.bind("<Button-5>", self.zoom)  # Linux scroll down
        
        # Image info label
        self.image_info = ttk.Label(parent, text="No image loaded", anchor=tk.CENTER)
        self.image_info.pack(fill=tk.X, pady=5)
        
        # Image display
        self.image_on_canvas = None
        self.zoom_scale = 4.0 
    
    def setup_caption_editor(self, parent):
        # Caption label
        caption_label = ttk.Label(parent, text="Image Caption:", font=('Arial', 12, 'bold'))
        caption_label.pack(anchor=tk.W, pady=(10, 5))
        
        # Caption text editor
        self.caption_text = scrolledtext.ScrolledText(parent, wrap=tk.WORD, height=10, font=('Arial', 14))
        self.caption_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Save caption button
        save_caption_btn = ttk.Button(parent, text="Save Caption", command=self.save_current_caption)
        save_caption_btn.pack(fill=tk.X, pady=5)
        
        # Status label for caption loading/saving
        self.status_label = ttk.Label(parent, text="", foreground="green")
        self.status_label.pack(fill=tk.X, pady=5)
    
    def setup_control_buttons(self, parent):
        # Controls frame
        controls_frame = ttk.LabelFrame(parent, text="Controls")
        controls_frame.pack(fill=tk.BOTH, pady=10)
        
        # File loading buttons
        file_frame = ttk.Frame(controls_frame)
        file_frame.pack(fill=tk.X, pady=5)
        
        load_image_btn = ttk.Button(file_frame, text="Load Image", command=self.load_single_image)
        load_image_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        
        load_dir_btn = ttk.Button(file_frame, text="Load Directory", command=self.load_directory)
        load_dir_btn.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=5)
        
        # Navigation buttons
        nav_frame = ttk.Frame(controls_frame)
        nav_frame.pack(fill=tk.X, pady=5)
        
        prev_btn = ttk.Button(nav_frame, text="Previous Image", command=self.prev_image)
        prev_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        
        next_btn = ttk.Button(nav_frame, text="Next Image", command=self.next_image)
        next_btn.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=5)
        
        # Reset zoom button
        reset_zoom_btn = ttk.Button(controls_frame, text="Reset Zoom", command=self.reset_zoom)
        reset_zoom_btn.pack(fill=tk.X, pady=5, padx=5)
    
    def show_status(self, message, is_error=False):
        """Display a status message"""
        self.status_label.config(text=message, foreground="red" if is_error else "green")
    
    def load_captions(self):
        """Load captions from JSON file if it exists"""
        if os.path.exists(self.captions_file):
            try:
                with open(self.captions_file, 'r') as f:
                    self.captions = json.load(f)
                self.show_status(f"Loaded {len(self.captions)} captions from {self.captions_file}")
                print(f"Loaded captions: {self.captions}")  # Debug print
            except json.JSONDecodeError:
                self.captions = {}
                self.show_status(f"Error loading captions: Invalid JSON format", True)
            except Exception as e:
                self.captions = {}
                self.show_status(f"Error loading captions: {str(e)}", True)
        else:
            self.captions = {}
    
    def save_captions(self):
        """Save all captions to JSON file"""
        try:
            with open(self.captions_file, 'w') as f:
                json.dump(self.captions, f, indent=4)
            return True
        except Exception as e:
            self.show_status(f"Error saving captions: {str(e)}", True)
            return False
    
    def save_current_caption(self):
        """Save the current caption"""
        if self.current_image_path:
            caption = self.caption_text.get(1.0, tk.END).strip()
            self.captions[self.current_image_path] = caption
            if self.save_captions():
                self.show_status(f"Caption saved for {os.path.basename(self.current_image_path)}")
    
    def load_single_image(self):
        """Load a single image from file dialog"""
        file_path = filedialog.askopenfilename(
            title="Select Image File",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif *.bmp")]
        )
        if file_path:
            # Convert to absolute path for consistency
            file_path = os.path.abspath(file_path)
            self.image_paths = [file_path]
            self.current_index = 0
            self.display_current_image()
    
    def load_directory(self):
        """Load all images from a directory"""
        directory = filedialog.askdirectory(title="Select Directory with Images")
        if directory:
            # Set captions file to be in this directory
            self.captions_file = os.path.join(directory, "captions.json")
            
            # Load captions from this directory if available
            self.load_captions()
            
            # Get all image files in the directory
            image_extensions = ["*.jpg", "*.jpeg", "*.png", "*.gif", "*.bmp"]
            self.image_paths = []
            for ext in image_extensions:
                self.image_paths.extend(glob.glob(os.path.join(directory, ext)))
            
            # Convert all paths to absolute for consistency
            self.image_paths = [os.path.abspath(path) for path in self.image_paths]
            
            if self.image_paths:
                self.current_index = 0
                self.display_current_image()
                self.show_status(f"Loaded {len(self.image_paths)} images from {directory}")
            else:
                self.show_status("No images found in selected directory", True)
    
    def find_caption_for_image(self, image_path):
        """Find caption for an image trying different path formats"""
        # Try absolute path
        abs_path = os.path.abspath(image_path)
        if abs_path in self.captions:
            return self.captions[abs_path]
        
        # Try relative path
        rel_path = os.path.relpath(image_path)
        if rel_path in self.captions:
            # Update to use absolute path for consistency
            self.captions[abs_path] = self.captions[rel_path]
            return self.captions[rel_path]
        
        # Try just the filename
        filename = os.path.basename(image_path)
        if filename in self.captions:
            # Update to use absolute path for consistency
            self.captions[abs_path] = self.captions[filename]
            return self.captions[filename]
        
        # Try without extension
        basename = os.path.splitext(filename)[0]
        if basename in self.captions:
            # Update to use absolute path for consistency
            self.captions[abs_path] = self.captions[basename]
            return self.captions[basename]
        
        # Try looking for path fragments in keys
        for key in self.captions:
            if filename in key or basename in key:
                # Update to use absolute path for consistency
                self.captions[abs_path] = self.captions[key]
                return self.captions[key]
        
        return None
    
    def display_current_image(self):
        """Display the current image and its caption"""
        if 0 <= self.current_index < len(self.image_paths):
            self.current_image_path = self.image_paths[self.current_index]
            
            # Reset zoom
            self.zoom_scale = 4.0
            
            try:
                # Open and prepare the image
                self.original_image = Image.open(self.current_image_path)
                self.display_image()
                
                # Update image info
                image_name = os.path.basename(self.current_image_path)
                self.image_info.config(text=f"Image {self.current_index + 1}/{len(self.image_paths)}: {image_name}")
                
                # Load caption if exists
                self.caption_text.delete(1.0, tk.END)
                
                # Try to find caption for this image
                caption = self.find_caption_for_image(self.current_image_path)
                
                if caption:
                    self.caption_text.insert(tk.END, caption)
                    self.show_status(f"Loaded existing caption for {image_name}")
                else:
                    self.show_status(f"No existing caption for {image_name}")
            
            except Exception as e:
                self.show_status(f"Error loading image: {str(e)}", True)
    
    def display_image(self):
        """Display the image with current zoom level"""
        if hasattr(self, 'original_image'):
            # Calculate new dimensions
            width = int(self.original_image.width * self.zoom_scale)
            height = int(self.original_image.height * self.zoom_scale)
            
            # Resize image
            if self.zoom_scale != 1.0:
                resized_img = self.original_image.resize((width, height), Image.LANCZOS)
            else:
                resized_img = self.original_image
                
            # Convert to PhotoImage
            self.tk_image = ImageTk.PhotoImage(resized_img)
            
            # Update canvas
            self.canvas.delete("all")
            self.image_on_canvas = self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)
            
            # Set scrollable area
            self.canvas.config(scrollregion=(0, 0, width, height))
    
    def zoom(self, event):
        """Handle zoom events"""
        # Determine zoom direction based on event
        if event.num == 4 or event.delta > 0:  # Zoom in
            self.zoom_scale *= 1.1
        elif event.num == 5 or event.delta < 0:  # Zoom out
            self.zoom_scale = max(0.1, self.zoom_scale / 1.1)
        
        # Update display
        self.display_image()
    
    def reset_zoom(self):
        """Reset zoom to original size"""
        if hasattr(self, 'original_image'):
            self.zoom_scale = 1.0
            self.display_image()
    
    def next_image(self):
        """Show next image"""
        # Save current caption before moving
        self.save_current_caption()
        
        if self.image_paths and self.current_index < len(self.image_paths) - 1:
            self.current_index += 1
            self.display_current_image()
    
    def prev_image(self):
        """Show previous image"""
        # Save current caption before moving
        self.save_current_caption()
        
        if self.image_paths and self.current_index > 0:
            self.current_index -= 1
            self.display_current_image()

def main():
    root = tk.Tk()
    app = ImageCaptioningApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
