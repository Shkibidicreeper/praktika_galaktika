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
TEXT_COLOR = (0, 0, 0)

# экран
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Крестики-нолики')

# Инициализация игрового поля
board = [["" for _ in range(3)] for _ in range(3)]
current_player = "X"
player1 = ""
player2 = ""

font = pygame.font.Font(None, 36)

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

    # Отображаем имена игроков
    player_text = font.render(f'Player 1: {player1} (X)    Player 2: {player2} (O)', True, TEXT_COLOR)
    screen.blit(player_text, (10, HEIGHT - 40))

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

def reset_game(connection, player1, player2, winner=None):
    if winner:
        save_game(connection, player1, player2, winner)
    global board, current_player
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
                        input_active = False  # Оба игрока ввели свои имена
                elif event.key == pygame.K_BACKSPACE:
                    text_input = text_input[:-1]
                else:
                    text_input += event.unicode
                    # Ограничиваем количество вводимых символов
                    if len(text_input) > 20:
                        text_input = text_input[:20]
        
        # Отображение экрана ввода
        screen.fill(GREY)
        input_text = font.render(f'Player {player_turn} name: {text_input}', True, TEXT_COLOR)
        screen.blit(input_text, (10, 10))
        pygame.display.flip()

def draw_score(player1_score, player2_score):
    score_text = font.render(f'Score - Player 1 (X): {player1_score}    Player 2 (O): {player2_score}', True, TEXT_COLOR)
    screen.blit(score_text, (10, HEIGHT - 70))

def main():
    global current_player
    
    display_input_screen()  # Позволить игрокам ввести свои имена
    
    # Получаем текущий счёт из базы данных перед началом игры
    connection = create_connection()
    scores = get_scores(connection)  
    if scores and len(scores) > 0:
        player1_score = scores[0]['playerX_score']  
        player2_score = scores[0]['playerO_score']  
    else:
        player1_score, player2_score = 0, 0  
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                connection.close()  # Закрыть соединение с БД при выходе

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                row = y // CELL_SIZE
                col = x // CELL_SIZE

                if board[row][col] == "":
                    board[row][col] = current_player
                    winner = check_winner()
                    if winner:
                        print(f'Player {winner} wins!')
                        reset_game(connection, player1, player2, winner)
                        if winner == "X":
                            player1_score += 1
                        else:
                            player2_score += 1
                    elif check_draw():
                        print("It's a draw!")
                        reset_game(connection, player1, player2)
                    else:
                        current_player = "O" if current_player == "X" else "X"

        draw_board()
        draw_score(player1_score, player2_score)  # Отображаем счет
        pygame.display.flip()

# Функция для получения счета из базы данных
def get_scores(connection):
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT playerX_score, playerO_score FROM scores")
    return cursor.fetchall()

if __name__ == "__main__":
    main()