import pygame
import random

WIDTH, HEIGHT = 700, 800
BUFFER = 100
BG_COLOR = "peru"
ROWS, COLS = 20, 20
MINES = 5

COLORS = {
    -1: "bisque",  # Hidden Square
    0: "beige",  # Shown Square
    1: "blue",
    2: "green",
    3: "red",
    4: "purple",
    5: "maroon",
    6: "turquoise",
    7: "black",
    8: "gray",
}

win: pygame.Surface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("MineSweeper")

pygame.font.init()
FONT = pygame.font.SysFont("comicsans", 20)
TITLEFONT = pygame.font.SysFont("comicsans", 80)

FLAG = pygame.transform.scale(
    pygame.image.load("flag.png"), (WIDTH // ROWS - 10, WIDTH // ROWS - 10)
)
MINE = pygame.transform.scale(
    pygame.image.load("mine.png"), (WIDTH // ROWS - 10, WIDTH // ROWS - 10)
)


def get_neighbors(grid, x, y, offset=1):
    neighbors = []
    for i in range(x - offset, x + offset + 1):  # All rows
        for j in range(y - offset, y + offset + 1):  # All columns
            if i < 0 or j < 0 or i >= len(grid) or j >= len(grid[0]):
                continue
            if i == x and j == y:
                continue
            neighbors.append((i, j))
    return neighbors


def create_grid(rows, cols, num_mines, click_pos):
    # Define grid
    grid = [[0 for _ in range(cols)] for _ in range(rows)]

    # Randomize mines
    mines = set()
    friendlies = get_neighbors(grid, *click_pos, offset=2)
    friendlies.append(click_pos)
    while len(mines) < num_mines:
        x = random.randint(0, rows - 1)
        y = random.randint(0, cols - 1)
        if (x, y) in friendlies:
            continue
        mines.add((x, y))

    # Set mines
    for pos in mines:
        grid[pos[0]][pos[1]] = -1
        for neighbor in get_neighbors(grid, pos[0], pos[1]):
            if grid[neighbor[0]][neighbor[1]] != -1:
                grid[neighbor[0]][neighbor[1]] += 1

    return grid, mines


def create_mask(mask, field, click_pos):
    mask[click_pos[0]][click_pos[1]] = True
    for neighbor in get_neighbors(field, click_pos[0], click_pos[1]):
        if not mask[neighbor[0]][neighbor[1]] and field[neighbor[0]][neighbor[1]] == 0:
            mask = create_mask(mask, field, neighbor)
        if field[neighbor[0]][neighbor[1]] != -1:
            mask[neighbor[0]][neighbor[1]] = True
    return mask


def draw_grid(win, grid, mask, flags):
    step = WIDTH // ROWS
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            x = j * step
            y = i * step + BUFFER
            if mask[i][j]:
                pygame.draw.rect(
                    win, COLORS[0], pygame.Rect(x + 2, y + 2, step - 4, step - 4), border_radius=2
                )
                if grid[i][j] > 0:
                    text = FONT.render(str(grid[i][j]), True, COLORS[grid[i][j]])
                    win.blit(
                        text,
                        (
                            x + step // 2 - text.get_width() // 2,
                            y + step // 2 - text.get_height() // 2,
                        ),
                    )
                if grid[i][j] == -1:
                    pygame.draw.rect(
                        win, BG_COLOR, pygame.Rect(x + 2, y + 2, step - 4, step - 4),
                        border_radius=2
                    )
                    win.blit(
                        MINE,
                        (
                            x + step // 2 - MINE.get_width() // 2,
                            y + step // 2 - MINE.get_height() // 2,
                        ),
                    )
            else:
                pygame.draw.rect(
                    win, COLORS[-1], pygame.Rect(x + 2, y + 2, step - 4, step - 4), border_radius=2
                )
                if (i, j) in flags:
                    win.blit(
                        FLAG,
                        (
                            x + step // 2 - FLAG.get_width() // 2,
                            y + step // 2 - FLAG.get_height() // 2,
                        ),
                    )


def pos_from_mouse(x, y):
    gy = (y - BUFFER) // ((HEIGHT - BUFFER) // ROWS)
    gx = x // (WIDTH // COLS)
    if gy < 0:
        return None
    return gy, gx


def redraw(win, field, mask, flags=(), message="MINESWEEPER!"):
    win.fill(BG_COLOR)
    draw_grid(win, field, mask, flags)
    text = TITLEFONT.render(message, True, COLORS[0])
    win.blit(
        text,
        (
            WIDTH // 2 - text.get_width() // 2,
            BUFFER // 2 - text.get_height() // 2,
        ),
    )
    pygame.display.update()


def pregame(win, grid, mask):
    clicked = False
    while not clicked:
        pygame.time.delay(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    pos = pos_from_mouse(*pygame.mouse.get_pos())
                    if not pos:
                        continue
                    return pos

        redraw(win, grid, mask)


def game_win(win, grid, mask, mines, flags=()):
    run = True
    while run:
        pygame.time.delay(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

        if len(mines) <= 0:
            break
        if random.random() < 0.25:
            mine = random.choice(list(mines))
            mask[mine[0]][mine[1]] = True
            mines.remove(mine)

        redraw(win, grid, mask, flags, message="YOU WIN!")
    pygame.time.delay(2000)
    mask = [[True for _ in range(COLS)] for _ in range(ROWS)]
    redraw(win, grid, mask, flags, message="YOU WIN!")
    pygame.time.delay(5000)
    with open("last_game.txt", "w", encoding="utf-8") as f:
        for row in grid:
            for x in row:
                f.write(("+" if x == -1 else (" " if x == 0 else str(x))) + " ")
            f.write("\n")
    pygame.quit()


def game_loss(win, grid, mask, mines, flags=()):
    run = True
    while run:
        pygame.time.delay(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

        if len(mines) <= 0:
            break
        if random.random() < 0.25:
            mine = random.choice(list(mines))
            mask[mine[0]][mine[1]] = True
            mines.remove(mine)

        redraw(win, grid, mask, flags)
    redraw(win, grid, mask, flags, message="Game Over :(")
    pygame.time.delay(2000)
    mask = [[True for _ in range(COLS)] for _ in range(ROWS)]
    redraw(win, grid, mask, flags, message="Game Over :(")
    pygame.time.delay(5000)
    with open("last_game.txt", "w", encoding="utf-8") as f:
        for row in grid:
            for x in row:
                f.write(("+" if x == -1 else (" " if x == 0 else str(x))) + " ")
            f.write("\n")
    pygame.quit()


def main(win):
    pre_field = [[0 for _ in range(COLS)] for _ in range(ROWS)]
    pre_mask = [[False for _ in range(COLS)] for _ in range(ROWS)]

    click_pos = pregame(win, pre_field, pre_mask)
    field, mines = create_grid(ROWS, COLS, MINES, click_pos)
    mask = create_mask(pre_mask, field, click_pos)
    flags = set()

    run = True
    while run:
        pygame.time.delay(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            if event.type == pygame.MOUSEBUTTONDOWN:
                pressed = pygame.mouse.get_pressed()
                if pressed[0]:
                    pos = pos_from_mouse(*pygame.mouse.get_pos())
                    value = field[pos[0]][pos[1]]
                    if value == -1:
                        pygame.time.delay(1000)
                        game_loss(win, field, mask, mines, flags)
                        quit()
                    if value == 0:
                        mask = create_mask(mask, field, pos)
                    elif value > 0:
                        mask[pos[0]][pos[1]] = True
                elif pressed[2]:
                    pos = pos_from_mouse(*pygame.mouse.get_pos())
                    if pos in flags:
                        flags.remove(pos)
                    else:
                        flags.add(pos)

        redraw(win, field, mask, flags)

        if flags == mines:
            pygame.time.delay(1000)
            game_win(win, field, mask, mines, flags)
            quit()
    pygame.quit()


if __name__ == "__main__":
    main(win)
