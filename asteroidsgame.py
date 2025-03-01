import pygame
import sys
import random
import serial
import mysql.connector
import os

conexion = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="asteroidsdb"
)

mycursor = conexion.cursor()
# Inicializar Pygame
pygame.init()

# Inicializar el mezclador de música de Pygame
pygame.mixer.init()

# Definir dimensiones de la pantalla
WIDTH, HEIGHT = 600, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Asteroids")

# Definir colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Obtener el directorio actual
base_path = os.path.dirname(os.path.abspath(__file__))

# Cargar y reproducir el sonido de fondo
pygame.mixer.music.load(os.path.join(base_path, "sound/background_music.mp3"))
pygame.mixer.music.play(-1)  # Reproducir en bucle infinito

# Cargar la imagen de fondo y redimensionarla
background = pygame.transform.scale(pygame.image.load(os.path.join(base_path, "img/background/background.png")), (WIDTH, HEIGHT))

# Cargar sonidos de destrucción y disparo
destroy_sound = pygame.mixer.Sound(os.path.join(base_path, "sound/explosion.wav"))
shoot_sound = pygame.mixer.Sound(os.path.join(base_path, "sound/laser.wav"))
damage_sound = pygame.mixer.Sound(os.path.join(base_path, "sound/damage.wav"))
death_sound = pygame.mixer.Sound(os.path.join(base_path, "sound/death_sound.wav"))

# Cargar imágenes de asteroides y redimensionarlas
asteroid_images = {
    "white": pygame.transform.scale(pygame.image.load(os.path.join(base_path, "img/asteroids/white_asteroid.png")), (30, 30)),
    "green": pygame.transform.scale(pygame.image.load(os.path.join(base_path, "img/asteroids/green_asteroid.png")), (30, 30)),
    "blue": pygame.transform.scale(pygame.image.load(os.path.join(base_path, "img/asteroids/blue_asteroid.png")), (30, 30)),
    "red": pygame.transform.scale(pygame.image.load(os.path.join(base_path, "img/asteroids/red_asteroid.png")), (30, 30))
}

# Cargar y redimensionar la imagen de la nave
ship_image = pygame.transform.scale(pygame.image.load(os.path.join(base_path, "img/player/spaceship.png")), (40, 40))

# Cargar imágenes de explosión y redimensionarlas
explosion_images = [pygame.transform.scale(pygame.image.load(os.path.join(base_path, f"img/explosions/explosion{i}.png")), (50, 50)) for i in range(1, 6)]

destroyed_asteroids = {
    "white": 0,
    "green": 0,
    "blue": 0,
    "red": 0
}

# Inicializar el tiempo de partida
start_time = pygame.time.get_ticks()

ts = 0

tes = 0

# Definir constantes para la nave
TRIANGLE_WIDTH = 30
TRIANGLE_HEIGHT = 30
TRIANGLE_SPEED = 9

# Definir constantes para los rayos
BULLET_WIDTH = 5
BULLET_HEIGHT = 15
BULLET_SPEED = 5

# Definir constantes para los meteoritos
METEOR_WIDTH = 30
METEOR_HEIGHT = 30
METEOR_SPEED = 3
METEOR_ANGLE_CHANGE = 1  # Cambio de ángulo para los meteoritos diagonales

# Definir función para dibujar la nave
def draw_triangle(x, y):
    screen.blit(ship_image, (x, y))

# Definir función para dibujar los rayos
def draw_bullet(x, y):
    pygame.draw.rect(screen, WHITE, (x, y, BULLET_WIDTH, BULLET_HEIGHT))

# Definir función para dibujar los asteroides
def draw_asteroid(x, y, color):
    image = asteroid_images[color]
    screen.blit(image, (x, y))

# Definir función para dibujar las explosiones
def draw_explosion(x, y, frame):
    screen.blit(explosion_images[frame], (x, y))

# Inicializar posición de la nave
triangle_x = WIDTH // 2 - TRIANGLE_WIDTH // 2
triangle_y = HEIGHT - 2 * TRIANGLE_HEIGHT

# Inicializar municiones
ammo = 30

# Inicializar contador de vidas
lives = 3

# Inicializar contador de puntuación
score = 0

# Lista para almacenar los rayos disparados
bullets = []

# Lista para almacenar los meteoritos
asteroids = []

# Lista para almacenar las explosiones
explosions = []

# Fuente para el texto
font = pygame.font.Font(None, 36)

# Bucle principal del juego
clock = pygame.time.Clock()
running = True

# Inicializar conexión serial con Arduino
ser = serial.Serial('COM3', 9600)  # Ajusta el puerto COM según corresponda

while running:
    screen.blit(background, (0, 0))  # Dibujar la imagen de fondo

    # Manejo de eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if ser.in_waiting > 0:
            data = ser.readline().decode().strip()
            if data == "disparar" and ammo > 0:
                bullets.append([triangle_x + TRIANGLE_WIDTH / 2 - BULLET_WIDTH / 2, triangle_y - BULLET_HEIGHT])
                ammo -= 1
                ts += 1
                shoot_sound.play()



    if ser.in_waiting > 0:
        data = ser.readline().decode().strip()
        if data == "disparar" and ammo > 0:
            bullets.append([triangle_x + TRIANGLE_WIDTH / 2 - BULLET_WIDTH / 2, triangle_y - BULLET_HEIGHT])
            ammo -= 1
            ts += 1
            shoot_sound.play() 
        if data == "izquierda" and triangle_x > 0:
            triangle_x -= TRIANGLE_SPEED
        elif data == "derecha" and triangle_x < WIDTH - TRIANGLE_WIDTH:
            triangle_x += TRIANGLE_SPEED
           

    # Dibujar la nave
    draw_triangle(triangle_x, triangle_y)

    # Dibujar y mover los rayos
    for bullet in bullets:
        bullet[1] -= BULLET_SPEED
        draw_bullet(bullet[0], bullet[1])

    # Eliminar los rayos que están fuera de la pantalla
    bullets = [bullet for bullet in bullets if bullet[1] > 0]

    # Generar asteroides
    if random.randint(0, 100) < 2:
        asteroids.append([random.randint(0, WIDTH - METEOR_WIDTH), 0, random.choice(["white", "green", "blue", "red"])])

    # Dibujar y mover los asteroides
    for asteroid in asteroids:
        asteroid[1] += METEOR_SPEED  # Mover hacia abajo
        draw_asteroid(asteroid[0], asteroid[1], asteroid[2])

    # Eliminar los asteroides que están fuera de la pantalla
    asteroids = [asteroid for asteroid in asteroids if asteroid[1] < HEIGHT]

    # Detectar colisiones entre rayos y asteroides
    for bullet in bullets:
        for asteroid in asteroids:
            if bullet[0] + BULLET_WIDTH >= asteroid[0] and bullet[0] <= asteroid[0] + METEOR_WIDTH and bullet[1] <= asteroid[1] + METEOR_HEIGHT:
                bullet_color = asteroid[2]
                bullets.remove(bullet)
                asteroids.remove(asteroid)
                ammo += 3
                score += 1
                destroy_sound.play()
                explosions.append([asteroid[0], asteroid[1], 0])  # Añadir explosión en la posición del asteroide destruido
                destroyed_asteroids[bullet_color] += 1  # Incrementar el contador del color correspondiente
                tes += 1

    # Detectar colisiones entre nave y asteroides
    for asteroid in asteroids:
        if triangle_x + TRIANGLE_WIDTH >= asteroid[0] and triangle_x <= asteroid[0] + METEOR_WIDTH and triangle_y <= asteroid[1] + METEOR_HEIGHT:
            asteroids.remove(asteroid)
            lives -= 1
            if(lives > 0):
                damage_sound.play()
            else:
                death_sound.play()    
            explosions.append([asteroid[0], asteroid[1], 0])  # Añadir explosión en la posición del asteroide destruido

    # Dibujar y actualizar las explosiones
    for explosion in explosions:
        draw_explosion(explosion[0], explosion[1], explosion[2])
        explosion[2] += 1  # Avanzar al siguiente cuadro de la animación
        if explosion[2] >= len(explosion_images):
            explosions.remove(explosion)

    # Mostrar contador de municiones
    ammo_text = font.render("Ammo: " + str(ammo), True, WHITE)
    screen.blit(ammo_text, (10, 10))

    # Mostrar contador de vidas
    lives_text = font.render("Lives: " + str(lives), True, WHITE)
    screen.blit(lives_text, (10, 50))

    # Mostrar contador de puntuación
    score_text = font.render("Score: " + str(score), True, WHITE)
    screen.blit(score_text, (10, 90))

    # Verificar si el jugador se ha quedado sin vidas
    if lives <= 0:
        game_over_text = font.render("Game Over", True, WHITE)
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - game_over_text.get_height() // 2))
        pygame.display.flip()
        pygame.time.wait(3000)  # Esperar 3 segundos antes de salir
        running = False

    # Calcular el tiempo transcurrido
    elapsed_time = (pygame.time.get_ticks() - start_time) // 1000
    time_text = font.render("Time: " + str(elapsed_time) + "s", True, WHITE)
    screen.blit(time_text, (10, 170))

    # Actualizar la pantalla
    pygame.display.flip()

    # Controlar la velocidad del juego
    clock.tick(60)  # 60 fotogramas por segundo

pygame.quit()
nombre = input("Ingrese su nombre: ")
puntuacion = score
balas_usadas = ts
balas_efectivas = tes
tiempo_juego = int(elapsed_time)
asteroides_blancos = destroyed_asteroids["white"]
asteroides_verdes = destroyed_asteroids["green"]
asteroides_azules = destroyed_asteroids["blue"]
asteroides_rojos = destroyed_asteroids["red"]
insert_query = """
INSERT INTO resultados (nombre, puntuacion, balas_usadas, balas_efectivas, tiempo_juego, asteroides_blancos, asteroides_verdes, asteroides_azules, asteroides_rojos)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

data = (nombre, puntuacion, balas_usadas, balas_efectivas, tiempo_juego, asteroides_blancos, asteroides_verdes, asteroides_azules, asteroides_rojos)

mycursor.execute(insert_query, data)
conexion.commit()
mycursor.close()
conexion.close()

sys.exit()