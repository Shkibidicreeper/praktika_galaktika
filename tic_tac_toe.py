import pygame
import sys
import mysql.connector

pygame.init()

# размеры окна
WIDTH, HEIGHT = 500, 500
CELL_SIZE = WIDTH // 3

# Настройки цвета
GREY = (192, 192, 192)
RED = (255, 50, 60)
BLUE = (0, 191, 255)
LINE_COLOR = (0, 0, 0)

# экран
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Крестики-нолики')

# Инициализация игрового поля
board = [["" for _ in range(3)] for _ in range(3)]
current_player = "X"

def draw_board():
    screen.fill(GREY)
    # Рисуем линии
    pygame.draw.line(screen, LINE_COLOR, (CELL_SIZE, 0), (CELL_SIZE, HEIGHT), 5)
    pygame.draw.line(screen, LINE_COLOR, (CELL_SIZE * 2, 0), (CELL_SIZE * 2, HEIGHT), 5)
    pygame.draw.line(screen, LINE_COLOR, (0, CELL_SIZE), (WIDTH, CELL_SIZE), 5)
    pygame.draw.line(screen, LINE_COLOR, (0, CELL_SIZE * 2), (WIDTH, CELL_SIZE * 2), 5)

    # Рисуем Х и О
    for row in range(3):
        for col in range(3):
            if board[row][col] == "X":
                pygame.draw.line(screen, RED, (col * CELL_SIZE + 30, row * CELL_SIZE + 30),
                                 (col * CELL_SIZE + CELL_SIZE - 30, row * CELL_SIZE + CELL_SIZE - 30), 10)
                pygame.draw.line(screen, RED, (col * CELL_SIZE + CELL_SIZE - 30, row * CELL_SIZE + 30),
                                 (col * CELL_SIZE + 30, row * CELL_SIZE + CELL_SIZE - 30), 10)
            elif board[row][col] == "O":
                pygame.draw.circle(screen, BLUE, (col * CELL_SIZE + CELL_SIZE // 2, row * CELL_SIZE + CELL_SIZE // 2), 60, 10)

def create_connection():
    connection = None
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='your_username',
            password='your_password',
            database='tictactoe'
        )
        print("Connection to MySQL DB successful")
    except mysql.connector.Error as e:
        print(f"The error '{e}' occurred")
    return connection

def save_game(connection, player1, player2, winner):
    cursor = connection.cursor()
    query = "INSERT INTO games (playerX, playerO, winner) VALUES (%s, %s, %s)"
    cursor.execute(query, (player1, player2, winner))
    connection.commit()
    print("Game saved successfully")

def get_games(connection):
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM games")
    results = cursor.fetchall()
    return results

def check_winner():
    for row in board:
        if row[0] == row[1] == row[2] != "":
            return row[0]
    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] != "":
            return board[0][col]
    if board[0][0] == board[1][1] == board[2][2] != "":
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != "":
        return board[0][2]
    return None

def check_draw():
    for row in board:
        if "" in row:
            return False
    return True

def reset_game():
    global board, current_player
    board = [["" for _ in range(3)] for _ in range(3)]
    current_player = "X"

def main():
    global current_player
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                row = y // CELL_SIZE
                col = x // CELL_SIZE

                if board[row][col] == "":
                    board[row][col] = current_player
                    winner = check_winner()
                    if winner:
                        print(f'Player {winner} wins!')
                        reset_game()
                    elif check_draw():
                        print("It's a draw!")
                        reset_game()
                    else:
                        current_player = "O" if current_player == "X" else "X"

        draw_board()
        pygame.display.flip()

if __name__ == "__main__":
    main()