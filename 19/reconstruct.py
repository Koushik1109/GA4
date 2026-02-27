from PIL import Image
import numpy as np

def reconstruct_and_desaturate():
    # Load the scrambled image
    img = Image.open('jigsaw.webp').convert('RGB')
    
    width, height = img.size
    rows, cols = 5, 5
    tile_w = width // cols
    tile_h = height // rows
    
    # Mapping table (verified 1-to-1)
    mapping = [
        (0, 0, 2, 1), (0, 1, 1, 1), (0, 2, 4, 1), (0, 3, 0, 3), (0, 4, 0, 1),
        (1, 0, 1, 4), (1, 1, 2, 0), (1, 2, 2, 4), (1, 3, 4, 2), (1, 4, 2, 2),
        (2, 0, 0, 0), (2, 1, 3, 2), (2, 2, 4, 3), (2, 3, 3, 0), (2, 4, 3, 4),
        (3, 0, 1, 0), (3, 1, 2, 3), (3, 2, 3, 3), (3, 3, 4, 4), (3, 4, 0, 2),
        (4, 0, 3, 1), (4, 1, 1, 2), (4, 2, 1, 3), (4, 3, 0, 4), (4, 4, 4, 0)
    ]
    
    img_arr = np.array(img).astype(np.float64)
    recon_arr = np.zeros_like(img_arr)
    
    for s_row, s_col, o_row, o_col in mapping:
        s_top, s_left = s_row * tile_h, s_col * tile_w
        o_top, o_left = o_row * tile_h, o_col * tile_w
        recon_arr[o_top:o_top+tile_h, o_left:o_left+tile_w] = img_arr[s_top:s_top+tile_h, s_left:s_left+tile_w]
    
    # Grayscale conversion using luminance coefficients and np.round (round to even)
    r, g, b = recon_arr[:,:,0], recon_arr[:,:,1], recon_arr[:,:,2]
    gray_f = 0.2126 * r + 0.7152 * g + 0.0722 * b
    
    # Using np.round (round half to even) as a standard for scientific data
    gray = np.round(gray_f).astype(np.uint8)
    
    # Save as PNG
    grayscale_img = Image.fromarray(gray, mode='L')
    grayscale_img.save('output.png')
    print("Reconstructed grayscale image saved as output.png (Numpy Round-to-Even)")

if __name__ == "__main__":
    reconstruct_and_desaturate()
