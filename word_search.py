import sys
import random
import string
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF


def read_phrases_from_file(filename):
    with open(filename, "r") as f:
        content = f.read().splitlines()
    return [phrase.replace(" ", "") for phrase in content if phrase.strip()]


def generate_grid(rows, cols):
    return [[' ' for _ in range(cols)] for _ in range(rows)]


def can_place_word(grid, word, row, col, direction):
    rows, cols = len(grid), len(grid[0])
    length = len(word)
    delta_row, delta_col = direction
    end_row = row + delta_row * (length - 1)
    end_col = col + delta_col * (length - 1)

    if not (0 <= end_row < rows and 0 <= end_col < cols):
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
    rows, cols = len(grid), len(grid[0])
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == ' ':
                grid[r][c] = random.choice(string.ascii_uppercase)


def generate_word_search(words, rows=20, cols=20, max_attempts=100, max_retries=100):
    directions = [(1, 0), (0, 1), (1, 1), (-1, 1),
                  (1, -1), (-1, -1), (0, -1), (-1, 0)]

    for attempt in range(max_retries):
        grid = generate_grid(rows, cols)
        word_positions = []
        unplaced_words = []

        for word in words:
            placed = False
            attempts = 0

            while not placed and attempts < max_attempts:
                row, col = random.randint(
                    0, rows - 1), random.randint(0, cols - 1)
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
    rows = len(grid)
    cols = len(grid[0])
    cell_size = int(17 * 1.3)
    arrowhead_size = 6
    svg_content = ["<svg xmlns='http://www.w3.org/2000/svg' width='{}' height='{}'>".format(
        cols * cell_size, rows * cell_size)]

    for r in range(rows):
        for c in range(cols):
            x, y = c * cell_size, r * cell_size
            svg_content.append(
                "<rect x='{}' y='{}' width='{}' height='{}' stroke='black' fill='white' stroke-opacity='0'/>".format(x, y, cell_size, cell_size))
            svg_content.append("<text x='{}' y='{}' font-size='15' text-anchor='middle' fill='black' font-family='Arial'>{}</text>".format(
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


def save_svgs_to_pdf(svg_file1, svg_file2, output_pdf="word_search.pdf", scale_factor=1/1):
    """
    Creates a PDF with two SVG images centered and scaled.

    :param svg_file1: First SVG file to include in the PDF
    :param svg_file2: Second SVG file to include in the PDF
    :param output_pdf: Output PDF filename
    :param scale_factor: Scale factor for the SVG images
    """
    c = canvas.Canvas(output_pdf, pagesize=letter)
    page_width, page_height = letter  # Get page dimensions

    # Add title and description to the first page
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(page_width / 2, page_height - 50, "Word Search Puzzle")
    c.setFont("Helvetica", 12)
    c.drawCentredString(page_width / 2, page_height - 70,
                        "Solve the following puzzle by finding all the hidden words!")

    def draw_svg(svg_file):
        drawing = svg2rlg(svg_file)  # Load SVG

        # Scale the drawing
        drawing.width *= scale_factor
        drawing.height *= scale_factor
        drawing.scale(scale_factor, scale_factor)

        # Calculate the centered position
        x = (page_width - drawing.width) / 2
        y = (page_height - drawing.height) / 1.5

        # Draw the SVG centered and scaled
        renderPDF.draw(drawing, c, x, y)

    draw_svg(svg_file1)

    # Add title for word list
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(page_width / 2, 120, "Words List")

    c.setFont("Helvetica", 11)
    # Read words from words.txt and print them with wrapping
    try:
        with open("words.txt", "r") as f:
            words = f.readlines()
            words = [word.strip() for word in words]
            max_width = page_width * 0.8
            y_position = 100  # Adjusted to print after the puzzle
            line = ""
            for word in words:
                if c.stringWidth(line + word, "Helvetica", 11) < max_width:
                    line += (", " if line else "") + word
                else:
                    c.drawCentredString(page_width / 2, y_position, line)
                    y_position -= 15
                    line = word
            if line:
                c.drawCentredString(page_width / 2, y_position, line)
    except FileNotFoundError:
        c.drawCentredString(page_width / 2, 100, "(Word list not found)")

    c.showPage()  # Move to the next page

    # Add title and description to the second page
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(page_width / 2, page_height - 50, "Solution")
    c.setFont("Helvetica", 12)
    c.drawCentredString(page_width / 2, page_height - 70,
                        "Solve the following puzzle by finding all the hidden words!")

    draw_svg(svg_file2)

    # Save the PDF
    c.save()


def main():
    if len(sys.argv) != 4:
        print("Usage: python script.py <rows> <cols> <filename>")
        sys.exit(1)

    try:
        rows = int(sys.argv[1])  # Read row size
        cols = int(sys.argv[2])  # Read column size
    except ValueError:
        print("Error: Rows and columns must be integers.")
        sys.exit(1)

    filename = sys.argv[3]  # Read filename from command line
    words = read_phrases_from_file(filename)

    try:
        puzzle, word_positions = generate_word_search(words, rows, cols)
        save_grid_as_svg(puzzle, "word_search.svg")
        save_grid_as_svg(puzzle, "word_search_answers.svg",
                         word_positions, highlight_words=True)
        print("Puzzle successfully generated and saved as SVG.")

        save_svgs_to_pdf("word_search.svg", "word_search_answers.svg")

    except ValueError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
