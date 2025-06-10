from PIL import Image, ImageDraw, ImageFont
import os
import argparse
from datetime import datetime

class TradingRecordGenerator:
    def __init__(self, direction="long", token="btc"):
        # Define colors based on the original images
        self.bg_color = (11, 11, 11)  # #0b0b0b Dark background
        self.text_color = (255, 255, 255)  # White text
        self.profit_color = (27, 154, 185)  # #1b9ab9 for positive values
        self.loss_color = (214, 68, 88)  # #d64458 for negative values
        
        # Template image paths
        self.template_path = "./asset/row_title_element.png"
        self.direction = direction.lower()
        self.token = token.lower()
        
        # Cross margin element paths
        if self.direction == "long":
            self.cross_margin_path = "./asset/long_cross_margin_element.png"
        else:
            self.cross_margin_path = "./asset/short_cross_margin_element.png"
        
        # Banner paths based on token
        banner_files = {
            "btc": "./asset/btc_banner.png",
            "eth": "./asset/eth_banner.png", 
            "hype": "./asset/hype_banner.png"
        }
        self.banner_path = banner_files.get(self.token, "./asset/btc_banner.png")
        
        # Layout parameters
        self.line_height = 44
        self.start_y = 40
        self.right_margin = 20  # Margin from right edge
        
    def load_template(self):
        """Load the row title template image"""
        try:
            if os.path.exists(self.template_path):
                return Image.open(self.template_path)
            else:
                print(f"Template not found at {self.template_path}")
                # Create a fallback template
                return Image.new('RGB', (600, 400), self.bg_color)
        except Exception as e:
            print(f"Error loading template: {e}")
            return Image.new('RGB', (600, 400), self.bg_color)
    
    def load_cross_margin_element(self):
        """Load the cross margin element image"""
        try:
            if os.path.exists(self.cross_margin_path):
                return Image.open(self.cross_margin_path)
            else:
                print(f"Cross margin element not found at {self.cross_margin_path}")
                # Create a fallback element
                return Image.new('RGB', (200, 50), self.bg_color)
        except Exception as e:
            print(f"Error loading cross margin element: {e}")
            return Image.new('RGB', (200, 50), self.bg_color)
    
    def load_banner(self):
        """Load the banner image based on token type"""
        try:
            if os.path.exists(self.banner_path):
                return Image.open(self.banner_path)
            else:
                print(f"Banner not found at {self.banner_path}")
                # Create a fallback banner
                return Image.new('RGB', (400, 60), self.bg_color)
        except Exception as e:
            print(f"Error loading banner: {e}")
            return Image.new('RGB', (400, 60), self.bg_color)
    
    def load_font(self, size=24):
        """Load a suitable font, fallback to default if not available"""
        try:
            # Try to load the specific Aileron-SemiBold font first
            font_paths = [
                "./font/Aileron-SemiBold.otf",
                "./font/Aileron-Bold.otf", 
                "./font/Aileron-Regular.otf",
                "arial.ttf",
                "C:/Windows/Fonts/arial.ttf",
                "C:/Windows/Fonts/calibri.ttf",
                "/System/Library/Fonts/Arial.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
            ]
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    return ImageFont.truetype(font_path, size)
            
            # Fallback to default font
            return ImageFont.load_default()
        except:
            return ImageFont.load_default()
    
    def format_number(self, value, decimals=3):
        """Format number with appropriate decimal places"""
        if isinstance(value, (int, float)):
            # If it's a whole number, show no decimals
            if value == int(value):
                return str(int(value))
            
            # Format with specified decimals and remove trailing zeros
            formatted = f"{value:.{decimals}f}"
            # Remove trailing zeros and decimal point if not needed
            formatted = formatted.rstrip('0').rstrip('.')
            return formatted
        return str(value)
    
    def format_datetime(self, dt_string):
        """Format datetime string"""
        return dt_string
    
    def generate_record_numbers(self, position_pnl, quantity, open_price, close_price, 
                              close_value, open_time, close_time, symbol="USDT"):
        """
        Generate a complete trading record by combining cross margin element, template, and numbers
        
        Args:
            position_pnl: Position profit/loss (float)
            quantity: Trading quantity (float) 
            open_price: Opening average price (float)
            close_price: Closing average price (float)
            close_value: Close value in USDT (float)
            open_time: Opening time (string)
            close_time: Full closing time (string)
            symbol: Trading symbol (string, default "USDT")
        """
        
        # Load all image components
        template = self.load_template()
        cross_margin = self.load_cross_margin_element()
        banner = self.load_banner()
        
        template_width, template_height = template.size
        cross_margin_width, cross_margin_height = cross_margin.size
        banner_width, banner_height = banner.size
        
        # Define the numbers area width and spacing
        numbers_width = 450  # Width for the numbers section
        spacing_height = 30  # Black space between cross margin and template
        
        # Calculate combined dimensions
        combined_width = max(template_width + numbers_width, banner_width)
        combined_height = template_height + cross_margin_height + banner_height + spacing_height
        
        # Create the combined image with dark background
        combined_img = Image.new('RGB', (combined_width, combined_height), self.bg_color)
        
        # Paste the banner at the very top
        banner_x_position = (combined_width - banner_width) // 2  # Center the banner
        combined_img.paste(banner, (banner_x_position, 0))
        
        # Paste the cross margin element below the banner
        cross_margin_y_position = banner_height
        combined_img.paste(cross_margin, (0, cross_margin_y_position))
        
        # Fill the remaining area next to cross margin with background color
        if cross_margin_width < combined_width:
            draw_temp = ImageDraw.Draw(combined_img)
            draw_temp.rectangle([
                (cross_margin_width, cross_margin_y_position), 
                (combined_width, cross_margin_y_position + cross_margin_height)
            ], fill=self.bg_color)
        
        # Add black spacing area between cross margin and template
        # (This area is automatically filled with bg_color when we created the image)
        
        # Paste the template (row titles) below the cross margin element + spacing
        template_y_position = banner_height + cross_margin_height + spacing_height
        combined_img.paste(template, (0, template_y_position))
        
        # Create drawing context for the combined image
        draw = ImageDraw.Draw(combined_img)
        
        # Load fonts - adjust sizes based on image size
        large_font = self.load_font(32)  # For PnL
        medium_font = self.load_font(28)  # For main values
        small_font = self.load_font(28)   # For timestamps
        
        # Determine PnL color
        pnl_color = self.profit_color if position_pnl >= 0 else self.loss_color
        pnl_sign = "+" if position_pnl >= 0 else ""
        
        # Calculate positions for the numbers (right side, below cross margin + spacing)
        numbers_start_x = template_width + 20  # 20px margin from template
        numbers_end_x = combined_width - self.right_margin  # Right margin
        
        # Calculate vertical positions based on template height (offset by cross margin height + spacing)
        start_y = template_y_position + (template_height * 0.01)  # Start below cross margin + spacing
        line_spacing = template_height * 0.151  # Line spacing based on template
        
        # Position for right-aligned text in the numbers area
        y_positions = [
            start_y + 0 * line_spacing,   # Position PnL
            start_y + 1 * line_spacing,   # Quantity
            start_y + 2 * line_spacing,   # Open price
            start_y + 3 * line_spacing,   # Close price  
            start_y + 4 * line_spacing,   # Close value
            start_y + 5 * line_spacing,   # Open time
            start_y + 6 * line_spacing,   # Close time
        ]
        
        # Prepare text values
        texts = [
            (f"{pnl_sign}{self.format_number(position_pnl)} {symbol}", large_font, pnl_color),
            (f"{self.format_number(quantity)} {self.token.upper()}", medium_font, self.text_color),
            (self.format_number(open_price), medium_font, self.text_color),
            (self.format_number(close_price), medium_font, self.text_color),
            (f"{self.format_number(close_value)} {symbol}", medium_font, self.text_color),
            (self.format_datetime(open_time), small_font, self.text_color),
            (self.format_datetime(close_time), small_font, self.text_color),
        ]
        
        # Draw text (right-aligned within the numbers area)
        for i, (text, font, color) in enumerate(texts):
            # Get text dimensions for right alignment
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            
            # Calculate x position for right alignment within numbers area
            x = numbers_end_x - text_width
            y = int(y_positions[i])
            
            draw.text((x, y), text, font=font, fill=color)
        
        # Add moderate black padding around the entire image for a more natural look
        padding = 40  # 40px padding on all sides
        
        # Create final image with padding
        final_width = combined_width + (padding * 2)
        final_height = combined_height + (padding * 2)
        final_img = Image.new('RGB', (final_width, final_height), self.bg_color)
        
        # Paste the combined image in the center of the padded image
        final_img.paste(combined_img, (padding, padding))
        
        return final_img
    
    def save_record(self, img, filename="trading_record_numbers.png"):
        """Save the generated image"""
        # Ensure output directory exists
        output_dir = "./output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Create full path with output directory
        full_path = os.path.join(output_dir, filename)
        img.save(full_path)
        print(f"Generated trading record numbers saved as: {full_path}")
        return full_path

# Example usage and test cases
def main():
    parser = argparse.ArgumentParser(description="Generate trading record images")
    parser.add_argument("-d", "--direction", choices=["long", "short"], required=True, 
                       help="Trading direction (long or short)")
    parser.add_argument("-t", "--token", choices=["btc", "eth", "hype"], required=True, 
                       help="Trading token (btc, eth, or hype)")
    parser.add_argument("-p", "--pnl", type=float, required=True,
                       help="Position PnL (can be negative)")
    parser.add_argument("-o", "--open_price", type=float, required=True,
                       help="Opening average price (开仓均价)")
    parser.add_argument("-c", "--close_price", type=float, required=True,
                       help="Closing average price (平仓均价)")
    parser.add_argument("-ot", "--open_time", required=True,
                       help="Opening time in format YYYYMMDDHHMMSS (e.g., 20250608222135)")
    parser.add_argument("-ct", "--close_time", required=True,
                       help="Closing time in format YYYYMMDDHHMMSS (e.g., 20250609012745)")
    args = parser.parse_args()
    
    # Validate that price difference is not zero
    price_diff = args.close_price - args.open_price
    if price_diff == 0:
        print("Error: Close price cannot equal open price (division by zero)")
        return
    
    # Calculate quantity: 平仓数量 = 仓位盈亏 / (平仓均价 - 开仓均价)
    quantity = abs(args.pnl / price_diff)
    
    # Calculate close value: 平仓价值 = 平仓数量 * 平仓均价
    close_value = quantity * args.close_price
    
    # Format timestamps from YYYYMMDDHHMMSS to YYYY-MM-DD HH:MM:SS
    def format_timestamp(timestamp_str):
        if len(timestamp_str) != 14:
            print(f"Warning: Invalid timestamp format '{timestamp_str}', expected YYYYMMDDHHMMSS")
            return timestamp_str
        try:
            year = timestamp_str[:4]
            month = timestamp_str[4:6]
            day = timestamp_str[6:8]
            hour = timestamp_str[8:10]
            minute = timestamp_str[10:12]
            second = timestamp_str[12:14]
            return f"{year}-{month}-{day} {hour}:{minute}:{second}"
        except:
            print(f"Warning: Could not parse timestamp '{timestamp_str}'")
            return timestamp_str
    
    open_time_formatted = format_timestamp(args.open_time)
    close_time_formatted = format_timestamp(args.close_time)
    
    # Create generator and generate the record
    generator = TradingRecordGenerator(args.direction, args.token)
    
    # Generate the trading record with calculated values
    record = generator.generate_record_numbers(
        position_pnl=args.pnl,
        quantity=quantity,
        open_price=args.open_price,
        close_price=args.close_price,
        close_value=close_value,
        open_time=open_time_formatted,
        close_time=close_time_formatted
    )
    
    # Generate filename with timestamp for uniqueness
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"trading_record_{args.direction}_{args.token}_{timestamp}.png"
    
    generator.save_record(record, filename)
    
    print(f"Generated {args.direction} {args.token.upper()} trading record:")
    print(f"  PnL: {args.pnl:+.3f} USDT")
    print(f"  Quantity: {quantity:.3f} {args.token.upper()}")
    print(f"  Open Price: {args.open_price:.3f}")
    print(f"  Close Price: {args.close_price:.3f}")
    print(f"  Close Value: {close_value:.3f} USDT")
    print(f"  Open Time: {open_time_formatted}")
    print(f"  Close Time: {close_time_formatted}")
    print(f"  Saved as: ./output/{filename}")

if __name__ == "__main__":
    main() 