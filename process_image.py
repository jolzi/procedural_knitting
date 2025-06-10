from PIL import Image
import numpy as np

def process_image_to_height_map(image_path, target_width, target_height):
    """Process BMP image to a height map suitable for budgetV."""
    # Load the image
    img = Image.open(image_path).convert('L')  # Convert to grayscale

    # Resize the image to match target dimensions
    img_resized = img.resize((target_width, target_height), Image.Resampling.LANCZOS)

    # Convert image to numpy array
    height_map = np.array(img_resized)

    # Convert to integer values for budgetV (range -2 to 2)
    height_map = np.round((height_map / 255.0) * 4 - 2).astype(int)

    # Save to txt file (optional)
    np.savetxt("height_map.txt", height_map, fmt='%d')

    return height_map

# Example usage
if __name__ == "__main__":
    height_map = process_image_to_height_map(
        "test_textures/AlligatorNoise.1.bmp", target_width=50, target_height=50)
    print(height_map)
