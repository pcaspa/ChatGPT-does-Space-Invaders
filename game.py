import pygame
import sys
import random
import time

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
PLAYER_SIZE = 50
INVADER_SIZE = 30
PLAYER_SPEED = 1
MAX_PLAYER_SPEED = 1
INVADER_SPEED = 3
PLAYER_BULLET_SPEED = 2  # Speed of player's bullets
INVADER_BULLET_SPEED = 50  # Speed of invader's bullets (bombs)
BOMBSCOUNT = 5  # Number of bombs at one time
MAX_BULLET_SPEED = 10
INVADER_ROWS = 4  # Increased to 3 rows
INVADER_PER_ROW = 7
BOMB_DROP_FREQ = 0.002

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Create the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")

# Player
player_image = pygame.image.load("spaceship.png")
player = pygame.transform.scale(player_image, (PLAYER_SIZE, PLAYER_SIZE))
player_rect = player.get_rect()
player_rect.centerx = WIDTH // 2
player_rect.y = HEIGHT - 2 * PLAYER_SIZE

# Invaders
invader_images = [
    pygame.image.load("invader1.png"),  # Image for the 1st row of invaders
    pygame.image.load("invader2.png"),  # Image for the 2nd row of invaders
    pygame.image.load("invader3.png"),  # Image for the 3rd row of invaders
    pygame.image.load("invader4.png"),  # Image for the 4rd row of invaders
]

invaders = []
for row in range(INVADER_ROWS):
    for col in range(INVADER_PER_ROW):
        invader_rect = invader_images[row].get_rect()
        invader_rect.x = col * (INVADER_SIZE + 20)
        invader_rect.y = row * (INVADER_SIZE + 20) + 50
        invaders.append((invader_rect, row))  # Store both the rect and the row index

# Bullets
bullets = []
bullets_hit_invader = []  # List to track bullets that have hit invaders

# Bombs
bombs = []
bombs_hit_player = []  # List to track bombs that have hit the player
BombWait = 0  # add delay for bombs

# Game over flag and timer
game_over = False
game_over_timer = None

# Constants for invader movement delay
invader_move_delay = 30
current_delay = 0

# Score
score = 0

# Player lives
player_lives = 3
font = pygame.font.Font(None, 36)

# Variables for player hit by bomb
player_hit_time = 0
player_hit_duration = 1  # 1 second

# High Score
high_score = 0  # Initialize the high score to 0
try:
    with open("highscore.txt", "r") as file:
        high_score = int(file.read())
except FileNotFoundError:
    pass

level = 1
new_wave_delay = 2000  # Time delay (in milliseconds) between waves
new_wave_timer = pygame.time.get_ticks() + new_wave_delay

# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()


        if not invaders:
            # Increment the level
            level += 1
            # Spawn a new wave of invaders
            new_wave_timer = pygame.time.get_ticks() + new_wave_delay
            for row in range(INVADER_ROWS):
                for col in range(INVADER_PER_ROW):
                    invader_rect = invader_images[row].get_rect()
                    invader_rect.x = col * (INVADER_SIZE + 20)
                    invader_rect.y = row * (INVADER_SIZE + 20) + 50
                    invaders.append((invader_rect, row))


        # Check for key press to restart the game after game over
        if game_over and event.type == pygame.KEYDOWN:
            # Reset game variables
            player_rect.centerx = WIDTH // 2
            player_rect.y = HEIGHT - 2 * PLAYER_SIZE
            player_lives = 3
            bullets.clear()
            bullets_hit_invader.clear()
            bombs.clear()
            bombs_hit_player.clear()
            invaders.clear()
            for row in range(INVADER_ROWS):
                for col in range(INVADER_PER_ROW):
                    invader_rect = invader_images[row].get_rect()
                    invader_rect.x = col * (INVADER_SIZE + 20)
                    invader_rect.y = row * (INVADER_SIZE + 20) + 50
                    invaders.append((invader_rect, row))  # Store both the rect and the row index
            score = 0
            game_over = False
            game_over_timer = None  # Reset the game over timer

    keys = pygame.key.get_pressed()

    if not game_over:
        if keys[pygame.K_LEFT] and player_rect.left > 0:
            player_rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] and player_rect.right < WIDTH:
            player_rect.x += PLAYER_SPEED

        PLAYER_SPEED = min(PLAYER_SPEED + 0.1, MAX_PLAYER_SPEED)

        current_delay += 1
        if current_delay >= invader_move_delay:
            current_delay = 0
            for invader, row in invaders:
                invader.x += INVADER_SPEED

                if invader.colliderect(player_rect):
                    if time.time() - player_hit_time > player_hit_duration:
                        player_lives -= 1
                        player_rect.x = 0  # Reappear on the far left
                        player_hit_time = time.time()
                        if player_lives <= 0:
                            game_over = True
                            game_over_timer = time.time()  # Start the game over timer
                    break

                if invader.left < 0 or invader.right > WIDTH:
                    INVADER_SPEED = -INVADER_SPEED
                    for i, (inv, row_index) in enumerate(invaders):
                        if row_index == row:
                            inv.y += 20

        # Update player bullets
        new_bullets = []

        for i, bullet in enumerate(bullets):
            bullet.y -= PLAYER_BULLET_SPEED  # Move the bullet upwards

            if bullet.y > 0:  # Check if the bullet is still on screen
                new_bullets.append(bullet)

        bullets = new_bullets  # Update the list of bullets

        for i, (invader, row) in enumerate(invaders):
            for j, bullet in enumerate(bullets):
                if invader.colliderect(bullet) and row >= 0:
                    #if not bullets_hit_invader[j]:
                        #bullets_hit_invader[j] = True  # Mark the bullet as hit
                    bullets.remove(bullet)
                    score += 10
                    invaders.remove((invader, row))
                    break  # Exit the inner loop after removing an invader

            if row >= 0:
                if random.random() < BOMB_DROP_FREQ and len(bombs) < BOMBSCOUNT:
                    bomb = pygame.Rect(invader.centerx - 2, invader.y, 4, 10)
                    bombs.append(bomb)
                    bombs_hit_player.append(False)  # Initialize bomb-hit status

        BombWait += 1
        if BombWait > INVADER_BULLET_SPEED:
            BombWait = 0
            for i, (invader, row) in enumerate(invaders):
                for j, bomb in enumerate(bombs):
                    if bomb.colliderect(player_rect):
                        if time.time() - player_hit_time > player_hit_duration:
                            player_lives -= 1
                            player_rect.x = 0  # Reappear on the far left
                            player_hit_time = time.time()
                            time.sleep(1)
                            break

                    if not bombs_hit_player[j] and player_rect.colliderect(bomb):
                        bombs_hit_player[j] = True  # Mark the bomb as hit
                        if time.time() - player_hit_time > player_hit_duration:
                            player_lives -= 1
                            player_rect.x = 0  # Reappear on the far left
                            player_hit_time = time.time()

                    bomb.y += 1  # Use the correct speed for invader bombs

                    if bomb.y > HEIGHT:
                        bombs.remove(bomb)

        # Check for game over condition
        if player_lives <= 0:
            game_over = True
            if game_over_timer is None:
                game_over_timer = time.time()  # Start the game over timer

        # Handle bullet firing
        if keys[pygame.K_SPACE]:
            if len(bullets) < 1:  # Limit the number of bullets on the screen
                bullet = pygame.Rect(player_rect.centerx - 2, player_rect.top, 4, 10)
                bullets.append(bullet)
                bullets_hit_invader.append(False)  # Initialize bullet-hit status

        # Remove bullets that are no longer visible
        bullets = [bullet for bullet in bullets if bullet.y > 0]

    # Clear the screen
    screen.fill(BLACK)

    if not game_over:
        # Create text surfaces
        score_text = font.render("Score: " + str(score), True, GREEN)
        lives_text = font.render("Lives: " + str(player_lives), True, GREEN)
        high_score_text = font.render("High Score: " + str(high_score), True, GREEN)

        # Calculate the positions for the score, lives, and high score text
        text_margin = 10
        text_height = score_text.get_height()

        score_rect = score_text.get_rect(centerx=WIDTH // 2, top=text_margin)  # Center score text
        lives_rect = lives_text.get_rect(topright=(WIDTH - text_margin, text_margin))
        high_score_rect = high_score_text.get_rect(topleft=(text_margin, text_margin))

        screen.blit(score_text, score_rect)
        screen.blit(lives_text, lives_rect)
        screen.blit(high_score_text, high_score_rect)

        screen.blit(player, player_rect)

        for invader, row in invaders:
            if row >= 0:
                screen.blit(invader_images[row], invader)

        for bullet in bullets:
            pygame.draw.rect(screen, GREEN, bullet)

        for bomb in bombs:
            pygame.draw.rect(screen, RED, bomb)
    else:
        if game_over_timer is not None and time.time() - game_over_timer >= 3:
            # Display game over message without clearing the screen
            text = font.render("Game Over - Press any key to play again", True, RED)
            text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(text, text_rect)

            # Update the high score if needed
            if score > high_score:
                high_score = score
                with open("highscore.txt", "w") as file:
                    file.write(str(high_score))

        elif game_over_timer is None:
            game_over_timer = time.time()  # Start the game over timer

    pygame.display.update()
