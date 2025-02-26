import sys
import random
import string


def read_words_from_file(filename):
    with open(filename, "r") as f:
        content = f.read()
    return content.split()


def generate_grid(size):
    return [[' ' for _ in range(size)] for _ in range(size)]


def can_place_word(grid, word, row, col, direction):
    size = len(grid)
    length = len(word)
    delta_row, delta_col = direction
    end_row = row + delta_row * (length - 1)
    end_col = col + delta_col * (length - 1)

    if not (0 <= end_row < size and 0 <= end_col < size):
        return False

    for i in range(length):
        r, c = row + i * delta_row, col + i * delta_col
        if grid[r][c] not in (' ', word[i]):
            return False
    return True


def place_word(grid, word, row, col, direction):
    delta_row, delta_col = direction
    for i in range(len(word)):
        grid[row + i * delta_row][col + i * delta_col] = word[i]


def fill_empty_spaces(grid):
    size = len(grid)
    for r in range(size):
        for c in range(size):
            if grid[r][c] == ' ':
                grid[r][c] = random.choice(string.ascii_uppercase)


def generate_word_search(words, size=20, max_attempts=100, max_retries=100):
    directions = [(1, 0), (0, 1), (1, 1), (-1, 1),
                  (1, -1), (-1, -1), (0, -1), (-1, 0)]

    for attempt in range(max_retries):
        grid = generate_grid(size)
        word_positions = []
        unplaced_words = []

        for word in words:
            placed = False
            attempts = 0

            while not placed and attempts < max_attempts:
                row, col = random.randint(
                    0, size - 1), random.randint(0, size - 1)
                direction = random.choice(directions)

                if can_place_word(grid, word, row, col, direction):
                    place_word(grid, word, row, col, direction)
                    word_positions.append((word, row, col, direction))
                    placed = True

                attempts += 1

            if not placed:
                unplaced_words.append(word)

        if not unplaced_words:
            fill_empty_spaces(grid)
            return grid, word_positions

    raise ValueError(
        f"Could not place the following words after {max_retries} attempts: {', '.join(unplaced_words)}")


def save_grid_as_svg(grid, filename, word_positions=None, highlight_words=False):
    size = len(grid)
    cell_size = int(20 * 1.3)
    arrowhead_size = 6
    svg_content = ["<svg xmlns='http://www.w3.org/2000/svg' width='{}' height='{}'>".format(
        size * cell_size, size * cell_size)]

    for r in range(size):
        for c in range(size):
            x, y = c * cell_size, r * cell_size
            svg_content.append(
                "<rect x='{}' y='{}' width='{}' height='{}' stroke='black' fill='white' stroke-opacity='0'/>".format(x, y, cell_size, cell_size))
            svg_content.append("<text x='{}' y='{}' font-size='14' text-anchor='middle' fill='black' font-family='Helvetica'>{}</text>".format(
                x + cell_size // 2, y + cell_size // 2 + 5, grid[r][c]))

    if highlight_words and word_positions:
        svg_content.append("""
        <defs>
            <marker id='arrowhead' markerWidth='6' markerHeight='6' refX='5' refY='3' orient='auto' markerUnits='strokeWidth'>
                <path d='M0,0 L6,3 L0,6 L2,3 Z' fill='red'/>
            </marker>
        </defs>
        """)

        for word, row, col, (dr, dc) in word_positions:
            x_start = col * cell_size + cell_size // 2
            y_start = row * cell_size + cell_size // 2
            x_end = (col + (len(word) - 1) * dc) * cell_size + cell_size // 2
            y_end = (row + (len(word) - 1) * dr) * cell_size + cell_size // 2

            svg_content.append(
                "<line x1='{}' y1='{}' x2='{}' y2='{}' stroke='red' stroke-width='1' marker-end='url(#arrowhead)'/>".format(x_start, y_start, x_end, y_end))

    svg_content.append("</svg>")
    with open(filename, "w") as f:
        f.write("\n".join(svg_content))
    print(f"SVG saved as {filename}")


def main():
    if len(sys.argv) != 3:
        print("Usage: python test_svg3.py <grid_size> <filename>")
        sys.exit(1)

    try:
        size = int(sys.argv[1])  # Read grid size from command line
    except ValueError:
        print("Error: Grid size must be an integer.")
        sys.exit(1)

    filename = sys.argv[2]  # Read filename from command line
    words = read_words_from_file(filename)

    try:
        puzzle, word_positions = generate_word_search(words, size)
        save_grid_as_svg(puzzle, "word_search.svg")
        save_grid_as_svg(puzzle, "word_search_answers.svg",
                         word_positions, highlight_words=True)
        print("Puzzle successfully generated and saved as SVG.")
    except ValueError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
