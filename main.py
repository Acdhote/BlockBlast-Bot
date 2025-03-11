import os
import cv2
from game_logic import detect_board, detect_next_capture, detect_pieces, placements, capture_screen
from ai import score_calculations, costs

def log_image(image_path, message):
    if os.path.exists(image_path):
        print(f"{message} Image saved at {image_path}")
        img = cv2.imread(image_path)
        if img is not None:
            print(f"Image dimensions: {img.shape}")
        else:
            print(f"Warning: Image at {image_path} could not be read!")
    else:
        print(f"Error: {message} Image not found at {image_path}")

def display_placement_with_pieces(original_state, best_placement, piece_positions, pieces):
    piece_chars = ['C', 'A', 'B']  # Changed order to C, A, B
    display_state = [row[:] for row in original_state]
    
    for i, (piece, (row, col)) in enumerate(zip(pieces, piece_positions)):
        for r in range(len(piece)):
            for c in range(len(piece[0])):
                if piece[r][c] == 1:
                    display_state[row+r][col+c] = piece_chars[i]
    
    print("\nBest Placement:")
    for row in display_state:
        print(' '.join(['□' if cell == 0 else ('■' if cell == 1 else cell) for cell in row]))
    
    print("\nInstructions:")
    for i, (piece, (row, col)) in enumerate(zip(pieces, piece_positions)):
        print(f"Place Piece {piece_chars[i]} at position (row={row}, column={col})")

def run_game_logic():
    # Step 1: Capture the screen
    screenshot_path = "images/screenshot.png"
    capture_screen.capture_screen(screenshot_path)
    log_image(screenshot_path, "Screenshot")

    # Step 2: Detect the board
    grid = detect_board.create_grid(screenshot_path)
    print("Detected grid:", grid)
    if not grid:
        print("Warning: Empty grid detected. Check detect_board.py")
        return

    # Step 3: Convert grid to game state matrix
    game_state = detect_board.convert_to_game_state(grid, grid_size=(8, 8))
    print("Game state matrix:")
    for row in game_state:
        print(' '.join(['□' if cell == 0 else '■' for cell in row]))

    # Step 4: Capture the block pool region
    block_pool_region = {"top": 1000, "left": 3100, "width": 800, "height": 200}
    block_pool_image_path = "images/block_pool.png"
    detect_next_capture.capture_block_pool_region(block_pool_region, block_pool_image_path)
    log_image(block_pool_image_path, "Block pool")

    # Step 5: Detect pieces dynamically based on their actual shapes
    detected_pieces = detect_pieces.detect_pieces_dynamic(block_pool_image_path)
    print(f"\nDetected {len(detected_pieces)} pieces:")
    piece_chars = ['C', 'A', 'B']
    for i, piece in enumerate(detected_pieces):
        print(f"\nPiece {piece_chars[i]}:")
        for row in piece:
            print(''.join('■' if cell else '□' for cell in row))

    if not detected_pieces:
        print("Warning: No pieces detected. Check detect_pieces.py")
        return

    # Debugging: Verify individual piece placements
    print("\n=== Debugging Individual Piece Placements ===")
    for i, piece in enumerate(detected_pieces):
        valid_placements = placements.generate_all_placements(game_state, piece)
        print(f"Piece {piece_chars[i]} has {len(valid_placements)} valid placements individually.")

    # Step 6: Generate possible placements for each detected piece
    print("\n=== Calculating Best Placement ===")

    combined_placements = placements.simulate_combined_placements(game_state, detected_pieces)
    print(f"Total valid combined placements: {len(combined_placements)}")

    if combined_placements:
        best_score = float('-inf')
        best_placement = None
        best_piece_positions = None

        for placement_info in combined_placements:
            placement = placement_info[0]
            piece_positions = placement_info[1]
            
            total_lines_cleared, _, _ = costs.calculate_total_lines_cleared(placement)
            combo_streak = 1  # Example value; track combo streak dynamically in your game logic
            score = costs.evaluate_board_state(placement,
                                                            lines_cleared=total_lines_cleared,
                                                            combo_streak=combo_streak)

            if score > best_score:
                best_score = score
                best_placement = placement
                best_piece_positions = piece_positions

        display_placement_with_pieces(game_state, best_placement, best_piece_positions, detected_pieces)
        print(f"\nBest Score: {best_score}")
    else:
        print("No valid combined placements found.")

# Main interactive loop
if __name__ == "__main__":
    while True:
        user_input = input("\nPress [R] to rerun the program or [Q] to quit: ").strip().lower()
        
        if user_input == 'r':
            run_game_logic()  # Run the main game logic
        elif user_input == 'q':
            print("Exiting program. Goodbye!")
            break
        else:
            print("Invalid input. Please press [R] to rerun or [Q] to quit.")
