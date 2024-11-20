import pygame
import sys
import mysql.connector
import logging

pygame.init()

# Размеры окна
WIDTH, HEIGHT = 500, 700
CELL_SIZE = WIDTH // 3

# Настройки цвета
GREY = (192, 192, 192)
RED = (255, 50, 60)
BLUE = (0, 191, 255)
LINE_COLOR = (0, 0, 0)
TEXT_COLOR = (0, 0, 0)

# Экран
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Крестики-нолики')

# Инициализация игрового поля
board = [["" for _ in range(3)] for _ in range(3)]
current_player = "X"
player1 = ""
player2 = ""

font = pygame.font.Font(None, 36)
game_over = False
game_message = ""

def draw_board():
    screen.fill(GREY)
    # Рисуем линии
    for i in range(1, 4):
        pygame.draw.line(screen, LINE_COLOR, (i * CELL_SIZE, 0), (i * CELL_SIZE, HEIGHT), 5)
        pygame.draw.line(screen, LINE_COLOR, (0, i * CELL_SIZE), (WIDTH, i * CELL_SIZE), 5)

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

    # Отображаем имена игроков
    player_text = font.render(f'Player 1: {player1} (X)    Player 2: {player2} (O)', True, TEXT_COLOR)
    screen.blit(player_text, (10, HEIGHT - 40))

    # Отображаем сообщение о завершении игры, если это нужно
    if game_over:
        message_text = font.render(game_message, True, TEXT_COLOR)
        screen.blit(message_text, (WIDTH // 2 - message_text.get_width() // 2, HEIGHT // 2 - 20))

def create_connection():
    try:
        connection = mysql.connector.connect(host="192.168.3.111", user="is61-8", password="cxitmrxu", database="tic_tac_toe") 
        print("Connection to MySQL DB successful")
        return connection
    except mysql.connector.Error as e:
        print(f"The error '{e}' occurred")
        return None

def save_game(connection, player1, player2, winner):
    cursor = connection.cursor()
    query = "INSERT INTO games (playerX, playerO, winner) VALUES (%s, %s, %s)"
    try:
        cursor.execute(query, (player1, player2, winner))
        connection.commit()
        print("Game saved successfully")
        
        # Обновление результатов
        update_scores(connection, winner)
    except mysql.connector.Error as e:
        print(f"Error saving game: {e}")

def update_scores(connection, winner):
    cursor = connection.cursor()
    query = "INSERT INTO scores (playerX_score, playerO_score) VALUES (%s, %s) ON DUPLICATE KEY UPDATE "
    if winner == "X":
        query += "playerX_score = playerX_score + 1"
    elif winner == "O":
        query += "playerO_score = playerO_score + 1"
    
    try:
        cursor.execute(query, (0, 0))  # Просто нужно передать что-то, здесь не важно
        connection.commit()
        print("Scores updated successfully")
    except mysql.connector.Error as e:
        print(f"Error updating scores: {e}")

def get_scores(connection):
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT playerX_score, playerO_score FROM scores")
    return cursor.fetchall()

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

def reset_game(connection, player1, player2, winner=None):
    global board, current_player, game_over, game_message
    if winner:
        game_message = f'Player {winner} wins!'
        save_game(connection, player1, player2, winner)
    elif check_draw():
        game_message = "It's a draw!"
    
    game_over = True
    board = [["" for _ in range(3)] for _ in range(3)]
    current_player = "X"

def display_input_screen():
    global player1, player2
    input_active = True
    text_input = ""
    player_turn = 1

    while input_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if player_turn == 1:
                        player1 = text_input
                        text_input = ""
                        player_turn = 2
                    else:
                        player2 = text_input
                        input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    text_input = text_input[:-1]
                elif len(text_input) < 20:
                    text_input += event.unicode

        # Отображение экрана ввода
        screen.fill(GREY)
        input_text = font.render(f'Player {player_turn} name: {text_input}', True, TEXT_COLOR)
        screen.blit(input_text, (10, 10))
        pygame.display.flip()

def draw_score(player1_score, player2_score):
    score_text = font.render(f'Score - Player 1 (X): {player1_score}    Player 2 (O): {player2_score}', True, TEXT_COLOR)
    screen.blit(score_text, (10, HEIGHT - 70))

def main():
    global current_player, game_over

    display_input_screen()

    # Получаем текущий счёт из базы данных перед началом игры
    connection = create_connection()
    if connection:
        scores = get_scores(connection)  
        player1_score, player2_score = (scores[0]['playerX_score'], scores[0]['playerO_score']) if scores else (0, 0)  
    else:
        player1_score, player2_score = 0, 0  
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if connection:
                    connection.close()
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                x, y = event.pos
                row, col = y // CELL_SIZE, x // CELL_SIZE

                if board[row][col] == "":
                    board[row][col] = current_player
                    winner = check_winner()
                    
                    if winner or check_draw():
                        reset_game(connection, player1, player2, winner)
                        if winner == "X":
                            player1_score += 1
                        elif winner == "O":
                            player2_score += 1
                    else:
                        current_player = "O" if current_player == "X" else "X"

        draw_board()
        draw_score(player1_score, player2_score)  # Отображаем счёт
        pygame.display.flip()

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    main()