import pygame
import sys
from random import randint, choice
from math import radians, sin, cos

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
FPS = 60


class Game:
    """ игра """
    def __init__(self):
        pygame.init()
        screen_info = pygame.display.Info()
        self.W = screen_info.current_w
        self.H = screen_info.current_h
        self.screen = pygame.display.set_mode(
            (self.W, self.H),
            pygame.FULLSCREEN
        )
        self.screen_rect = self.screen.get_rect()
        self.player_1 = Paddle(
            self.screen_rect,
            (self.screen_rect.width * 0.1, self.screen_rect.centery),
            keys=(pygame.K_w, pygame.K_s),
        )
        self.player_2 = Paddle(
            self.screen_rect,
            (self.screen_rect.width * 0.9, self.screen_rect.centery),
            is_automatic=True
        )
        self.ball = Ball(self.screen_rect)
        self.ball.throw_in()
        score_1 = Score(
            center=(
                self.screen_rect.width * 0.25,
                self.screen_rect.height * 0.1
            ),
            text=self.player_1.score,
            player=self.player_1
        )
        score_2 = Score(
            center=(
                self.screen_rect.width * 0.75,
                self.screen_rect.height * 0.1
            ),
            text=self.player_2.score,
            player=self.player_2
        )
        self.paddles = pygame.sprite.Group()
        self.balls = pygame.sprite.Group()
        self.scores = pygame.sprite.Group()
        self.scores.add(score_1)
        self.scores.add(score_2)
        self.paddles.add(self.player_1)
        self.paddles.add(self.player_2)
        self.balls.add(self.ball)
        self.clock = pygame.time.Clock()
        self.main_loop()

    def main_loop(self):
        game = True
        while game:
            dt = self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game = False

            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                game = False

            self.paddles.update(self.ball.rect, dt)
            self.ball.update(self.paddles)
            self.check_gool()
            self.scores.update()
            self.screen.fill(BLACK)
            self.paddles.draw(self.screen)
            self.balls.draw(self.screen)
            pygame.draw.line(
                self.screen,
                WHITE,
                self.screen_rect.midtop,
                self.screen_rect.midbottom
            )
            self.scores.draw(self.screen)
            pygame.display.flip()
        pygame.quit()

    def check_gool(self):
        if self.ball.rect.right >= self.screen_rect.right:
            self.player_1.score += 1
            self.ball.throw_in()
        if self.ball.rect.left <= self.screen_rect.left:
            self.player_2.score += 1
            self.ball.throw_in()


class Paddle(pygame.sprite.Sprite):
    """
    ракетка

    TODO:
    поведение автоматической ракетки - она движется относительно Y мяча
    """
    def __init__(
            self,
            screen_rect=None,
            center=(0, 0),
            color=WHITE,
            size=None,
            speed=5,
            keys=(pygame.K_UP, pygame.K_DOWN),
            is_automatic=False,
    ):
        self.score = 0
        super().__init__()
        self.screen_rect = screen_rect
        if not size:
            size = (
                self.screen_rect.width * 0.01,
                self.screen_rect.height * 0.10
            )
        self.image = pygame.Surface(size)
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speed = speed
        self.keys = keys
        self.is_automatic = is_automatic
        self.elapsed_time = 0

    def update(self, ball_rect, dt):
        if self.is_automatic:
            self.elapsed_time += dt
            if self.elapsed_time >= 30:
                if self.rect.centery < ball_rect.centery:
                    if self.rect.bottom < self.screen_rect.bottom:
                        self.rect.y += self.speed
                if self.rect.centery > ball_rect.centery:
                    if self.rect.top > self.screen_rect.top:
                        self.rect.y -= self.speed
                self.elapsed_time = 0
        else:
            keys = pygame.key.get_pressed()
            if keys[self.keys[0]]:
                if self.rect.top > self.screen_rect.top:
                    self.rect.y -= self.speed
            if keys[self.keys[1]]:
                if self.rect.bottom < self.screen_rect.bottom:
                    self.rect.y += self.speed


class Ball(pygame.sprite.Sprite):
    def __init__(
            self,
            screen_rect=None,
            center=None,
            color=WHITE,
            size=None,
            speed=5,
            direction=90,
            vel_x=0,
            vel_y=0,
    ):
        super().__init__()
        self.screen_rect = screen_rect
        if not size:
            size = (
                self.screen_rect.width * 0.01,
                self.screen_rect.width * 0.01
            )
        self.image = pygame.Surface(size)
        self.image.fill(color)
        self.rect = self.image.get_rect()
        if not center:
            self.rect.center = screen_rect.center
        self.speed = speed
        self.direction = direction
        self.vel_x = vel_x
        self.vel_y = vel_y

    def update(self, paddles_group):
        self.move()
        self.wall_bounce()
        self.paddles_bounse(paddles_group)

    def move(self):
        self.vel_x = sin(radians(self.direction)) * self.speed
        self.vel_y = cos(radians(self.direction)) * self.speed * -1
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

    def throw_in(self):
        self.rect.center = self.screen_rect.center
        self.direction = choice((randint(45, 135), randint(225, 315)))

    def wall_bounce(self):
        if self.rect.top <= self.screen_rect.top:
            self.direction *= -1
            self.direction += 180
        elif self.rect.bottom >= self.screen_rect.bottom:
            self.direction *= -1
            self.direction += 180

    def paddles_bounse(self, paddles_group):
        for paddle in paddles_group:
            if paddle.rect.colliderect(self.rect):
                self.direction *= -1


class Score(pygame.sprite.Sprite):
    def __init__(
        self,
        size=50,
        center=(1, 1),
        color=WHITE,
        text="0",
        player=None
    ):
        super().__init__()
        self.player = player
        self.text = text
        self.color = color
        self.font = pygame.font.Font(None, size)
        self.image = self.font.render(str(self.text), True, self.color,)
        self.rect = self.image.get_rect()
        self.rect.center = center

    def update(self):
        self.image = self.font.render(str(self.player.score), True, self.color)
        self.rect = self.image.get_rect(center=self.rect.center)


game = Game()
sys.exit()
