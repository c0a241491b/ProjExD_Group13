import pygame
import sys
import random
import os

# --- 設定 ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
TILE_SIZE = 64 # タイルサイズ

# 色定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (34, 139, 34)
GRAY = (169, 169, 169)
RED = (255, 0, 0)       # こうかとん
BLUE = (0, 0, 255)      # 雑魚敵
YELLOW = (255, 215, 0)  # ボス
CYAN = (0, 255, 255)    # MP
FLASH_COLOR = (255, 255, 255) # ダメージ時の閃光
GOLD = (255, 223, 0)    # レベルアップ用

COLORS = {
    0: (50, 180, 50), # 草
    1: (160, 130, 80), # 土
    2: (100, 100, 100), # 岩
    3: (200, 50, 50), # 火
    4: (0, 0, 255) # 水
}

# 状態定数
STATE_MAP = "MAP"
STATE_BATTLE = "BATTLE"
STATE_ENDING = "ENDING"
STATE_GAME_OVER = "GAME_OVER"

# マップID
MAP_VILLAGE = 0
MAP_FIELD_ID = 1
MAP_CAMPUS = 2

MAP_FIELD = [
    [0,0,0,0,0,0,0,0,0,0,0,0,4,4,4,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,4,4,4,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,4,4,4,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,4,4,4,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,4,4,4,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,2,4,4,4,0,0,0,0,0,0,0,0,0,0,0],
    [1,1,1,1,1,1,1,1,0,0,0,4,4,4,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,2,0,0,0,0,0,0,4,4,4,1,1,1,1,1,1,1,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,4,4,4,0,0,0,0,0,0,1,1,1,1,1,1],
    [0,0,0,0,0,0,0,0,0,4,4,4,0,0,0,0,3,3,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,4,4,4,0,0,0,0,3,3,3,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,4,4,4,0,0,0,3,3,3,3,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,4,4,4,0,0,0,0,0,3,3,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,4,4,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,4,4,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,4,4,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,4,4,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,4,4,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
]

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # 現在のディレクトリ

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("RPG こうく - Level Up System")
        self.clock = pygame.time.Clock()
        
        self.font = self.get_japanese_font(32)
        self.small_font = self.get_japanese_font(24)

        # プレイヤー初期状態
        self.player_pos = [50, 300]
        self.player_size = 40
        self.speed = 5
        
        # ステータス・レベル関連（変更点）
        self.player_level = 1
        self.player_exp = 0
        self.player_next_exp = 100 # 次のレベルまで必要な経験値
        
        self.player_max_hp = 100
        self.player_hp = 100
        self.player_max_mp = 100
        self.player_mp = 100
        
        # ゲーム進行管理
        self.state = STATE_MAP
        self.current_map = MAP_VILLAGE
        self.is_boss_battle = False
        
        # 戦闘用変数
        self.enemies = []
        self.battle_logs = []

        self.map_field = MapField(self.screen)

    def get_japanese_font(self, size):
        font_names = ["meiryo", "msgothic", "yugothic", "hiraginosans", "notosanscjkjp"]
        available_fonts = pygame.font.get_fonts()
        for name in font_names:
            if name in available_fonts:
                return pygame.font.SysFont(name, size)
        return pygame.font.Font(None, size)

    def run(self):
        while True:
            self.handle_events()
            result = self.map_field.update()
            self.update()
            self.draw()
            self.clock.tick(FPS)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if self.state == STATE_BATTLE:
                    if event.key == pygame.K_a:
                        self.execute_turn("ATTACK")
                    elif event.key == pygame.K_m:
                        self.execute_turn("MAGIC")
                    elif event.key == pygame.K_h:
                        self.execute_turn("HOIMI")
                
                elif self.state == STATE_ENDING or self.state == STATE_GAME_OVER:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

    def update(self):
        # --- 敵のアニメーション処理 ---
        if self.state == STATE_BATTLE:
            enemies_to_remove = []
            
            for enemy in self.enemies:
                # 1. ダメージ演出
                if enemy.get("flash_timer", 0) > 0:
                    enemy["flash_timer"] -= 1

                # 2. 死亡演出
                if enemy["hp"] <= 0:
                    if "death_timer" not in enemy:
                        enemy["death_timer"] = 60 
                        self.battle_logs.append(f"{enemy['name']}をやっつけた！")

                    enemy["death_timer"] -= 1
                    
                    # タイマー0で消滅（経験値獲得）
                    if enemy["death_timer"] <= 0:
                        self.gain_exp(enemy["xp"]) # 経験値処理へ
                        enemies_to_remove.append(enemy)

            # 消滅実行
            for enemy in enemies_to_remove:
                if enemy in self.enemies:
                    self.enemies.remove(enemy)
            
            if len(self.enemies) == 0:
                self.end_battle(win=True)


        # --- 移動画面処理 ---
        if self.state == STATE_MAP:
            keys = pygame.key.get_pressed()
            moved = False
            
            if keys[pygame.K_LEFT]:
                self.player_pos[0] -= self.speed
                moved = True
            if keys[pygame.K_RIGHT]:
                self.player_pos[0] += self.speed
                moved = True
            if keys[pygame.K_UP]:
                self.player_pos[1] -= self.speed
                moved = True
            if keys[pygame.K_DOWN]:
                self.player_pos[1] += self.speed
                moved = True

            self.check_map_transition()
            if moved and self.current_map == MAP_FIELD_ID:
                self.check_random_encounter()

            
            if self.current_map == MAP_CAMPUS and self.player_pos[0] > 700:
                self.start_battle(is_boss=True)

    # --- 重要：経験値とレベルアップ処理 ---
    def gain_exp(self, amount):
        self.player_exp += amount
        self.battle_logs.append(f"{amount} Expを獲得！")
        
        # レベルアップ判定
        while self.player_exp >= self.player_next_exp:
            self.player_level += 1
            self.player_exp -= self.player_next_exp # 現在のExpを消費して次のレベルへ
            self.player_next_exp = int(self.player_next_exp * 1.5) # 必要経験値増加
            
            # ステータス上昇
            self.player_max_hp += 20
            self.player_max_mp += 10
            
            # 全回復（ボーナス）
            self.player_hp = self.player_max_hp
            self.player_mp = self.player_max_mp
            
            self.battle_logs.append(f"レベルアップ！ Lv{self.player_level} になった！")
            self.battle_logs.append("最大HPとMPが増え、全回復した！")

    def check_map_transition(self):
        if self.player_pos[0] > SCREEN_WIDTH:
            if self.current_map < MAP_CAMPUS:
                self.current_map += 1
                self.player_pos[0] = 10
            else:
                self.player_pos[0] = SCREEN_WIDTH - self.player_size
        elif self.player_pos[0] < 0:
            if self.current_map > MAP_VILLAGE:
                self.current_map -= 1
                self.player_pos[0] = SCREEN_WIDTH - 10
            else:
                self.player_pos[0] = 0

    def check_random_encounter(self):
        if random.randint(0, 100) < 1:
            self.start_battle(is_boss=False)

    def start_battle(self, is_boss):
        self.state = STATE_BATTLE
        self.is_boss_battle = is_boss
        self.enemies = []
        self.battle_logs = ["敵が現れた！"]

        if is_boss:
            self.enemies.append({
                "name": "悪の組織",
                "hp": 1000, "max_hp": 1000, "atk": 40, "xp": 5000, # ボスは高経験値
                "color": YELLOW, "rect": pygame.Rect(300, 50, 200, 200),
                "flash_timer": 0
            })
        else:
            num_enemies = random.randint(1, 3)
            for i in range(num_enemies):
                x_pos = 150 + i * 180
                self.enemies.append({
                    "name": f"課題{i+1}",
                    "hp": 50, "max_hp": 50, "atk": 10, "xp": 40, # 雑魚は40Exp
                    "color": BLUE, "rect": pygame.Rect(x_pos, 100, 100, 100),
                    "flash_timer": 0
                })

    def execute_turn(self, action_type):
        self.battle_logs = [] 
        valid_targets = [e for e in self.enemies if e["hp"] > 0]

        if not valid_targets and len(self.enemies) == 0:
            return

        # --- プレイヤー行動 ---
        # レベルに応じた威力補正
        level_bonus = (self.player_level - 1) * 2

        if action_type == "HOIMI":
            if self.player_mp >= 10:
                self.player_mp -= 10
                base_heal = random.randint(30, 50)
                heal_amount = base_heal + level_bonus # レベルで回復量も増える
                
                old_hp = self.player_hp
                self.player_hp = min(self.player_max_hp, self.player_hp + heal_amount)
                recovered = self.player_hp - old_hp
                self.battle_logs.append(f"ホイミ！ HPが{recovered}回復！")
            else:
                self.battle_logs.append("MPが足りない！")

        elif action_type == "MAGIC":
            if self.player_mp >= 30:
                if valid_targets:
                    target = valid_targets[0]
                    self.player_mp -= 30
                    
                    base_dmg = random.randint(50, 80)
                    damage = base_dmg + (level_bonus * 2) # 魔法はレベル恩恵大
                    
                    if random.randint(0, 100) < 10:
                        damage = int(damage * 1.5)
                        self.battle_logs.append("会心の一撃！！")
                    
                    target["hp"] -= damage
                    target["flash_timer"] = 10 
                    self.battle_logs.append(f"魔法攻撃！{target['name']}に{damage}ダメ！")
            else:
                self.battle_logs.append("MPが足りない！")

        elif action_type == "ATTACK":
            if valid_targets:
                target = valid_targets[0]
                base_dmg = random.randint(20, 30)
                damage = base_dmg + level_bonus

                if random.randint(0, 100) < 15:
                    damage = damage * 2
                    self.battle_logs.append("会心の一撃！！")

                target["hp"] -= damage
                target["flash_timer"] = 10 
                self.battle_logs.append(f"攻撃！ {target['name']}に{damage}ダメ！")

        # --- 敵の反撃 ---
        surviving_enemies = [e for e in self.enemies if e["hp"] > 0]
        total_dmg = 0
        for enemy in surviving_enemies:
            hit_chance = random.randint(0, 100)
            if hit_chance < 20: 
                self.battle_logs.append(f"{enemy['name']}の攻撃ミス！")
            else:
                dmg = random.randint(enemy["atk"] - 3, enemy["atk"] + 3)
                total_dmg += dmg
        
        if total_dmg > 0:
            self.player_hp -= total_dmg
            self.battle_logs.append(f"敵の攻撃！ 計{total_dmg}のダメージ！")

        if self.player_hp <= 0:
            self.player_hp = 0
            self.end_battle(win=False)

    def end_battle(self, win):
        if win:
            if self.is_boss_battle:
                self.state = STATE_ENDING
            else:
                self.state = STATE_MAP
        else:
            self.state = STATE_GAME_OVER

    def draw(self):
        self.screen.fill(BLACK)

        if self.current_map == MAP_FIELD_ID:
            self.map_field.draw(self.player_pos)

        if self.state == STATE_MAP:
            color = GREEN
            if self.current_map == MAP_VILLAGE: color = (100, 200, 100)
            elif self.current_map == MAP_CAMPUS: color = GRAY
            pygame.draw.rect(self.screen, color, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.draw.rect(self.screen, RED, (*self.player_pos, self.player_size, self.player_size))
            
            # マップ画面のステータス表示（Lv追加）
            status_str = f"Lv:{self.player_level}  HP:{self.player_hp}/{self.player_max_hp}"
            status = self.font.render(status_str, True, BLACK)
            self.screen.blit(status, (550, 20))

        elif self.state == STATE_BATTLE:
            for enemy in self.enemies:
                if "death_timer" in enemy:
                    if (enemy["death_timer"] // 5) % 2 == 0:
                        pygame.draw.rect(self.screen, (100, 0, 0), enemy["rect"])
                else:
                    draw_color = enemy["color"]
                    if enemy.get("flash_timer", 0) > 0:
                        draw_color = FLASH_COLOR
                    pygame.draw.rect(self.screen, draw_color, enemy["rect"])
                    
                    if enemy["hp"] > 0:
                        hp_rate = max(0, enemy["hp"] / enemy["max_hp"])
                        pygame.draw.rect(self.screen, RED, (enemy["rect"].x, enemy["rect"].y - 10, enemy["rect"].width, 5))
                        pygame.draw.rect(self.screen, GREEN, (enemy["rect"].x, enemy["rect"].y - 10, enemy["rect"].width * hp_rate, 5))

            # UI描画
            ui_y_start = 350
            ui_height = SCREEN_HEIGHT - ui_y_start
            pygame.draw.rect(self.screen, BLACK, (0, ui_y_start, SCREEN_WIDTH, ui_height))
            pygame.draw.rect(self.screen, WHITE, (0, ui_y_start, SCREEN_WIDTH, ui_height), 2)

            # ステータス表示（Lv, Exp追加）
            hp_color = WHITE if self.player_hp > 30 else RED
            
            # LvとExp
            lv_text = f"Lv: {self.player_level}"
            exp_text = f"Exp: {self.player_exp}/{self.player_next_exp}"
            self.screen.blit(self.font.render(lv_text, True, GOLD), (30, ui_y_start + 15))
            self.screen.blit(self.small_font.render(exp_text, True, WHITE), (120, ui_y_start + 20))

            # HPとMP
            hp_text = f"HP: {self.player_hp}/{self.player_max_hp}"
            mp_text = f"MP: {self.player_mp}/{self.player_max_mp}"
            self.screen.blit(self.font.render(hp_text, True, hp_color), (300, ui_y_start + 15))
            self.screen.blit(self.font.render(mp_text, True, CYAN), (550, ui_y_start + 15))

            # コマンド
            cmd_text = "[A]たたかう  [M]まほう(30)  [H]ホイミ(10)"
            self.screen.blit(self.font.render(cmd_text, True, YELLOW), (30, ui_y_start + 60))

            # 区切り線
            line_y = ui_y_start + 100
            pygame.draw.line(self.screen, WHITE, (0, line_y), (SCREEN_WIDTH, line_y), 1)

            # ログ
            display_logs = self.battle_logs[-5:] 
            for i, log in enumerate(display_logs):
                log_color = WHITE
                if "会心" in log: log_color = YELLOW
                if "やっつけた" in log: log_color = (255, 100, 100)
                if "レベルアップ" in log: log_color = GOLD # レベルアップは金色
                
                txt = self.small_font.render(log, True, log_color)
                self.screen.blit(txt, (30, line_y + 10 + i * 28))

        elif self.state == STATE_ENDING:
            self.screen.fill(WHITE)
            msg = self.font.render("MISSION COMPLETE!", True, BLACK)
            self.screen.blit(msg, (200, 300))

        elif self.state == STATE_GAME_OVER:
            self.screen.fill(BLACK)
            msg = self.font.render("GAME OVER...", True, RED)
            self.screen.blit(msg, (300, 300))

        pygame.display.flip()



def check_move(player_x, player_y):
    """
    もしプレイヤーがx=24,y=9にいるなら次のワールドに移動する指示を返す
    引数:
        player_x: プレイヤーのX座標
        player_y: プレイヤーのY座標
    戻り値:
        True または None
    """
    if player_x == 24 and player_y == 9:
        return True
    return None

def load_image(path): # 画像読み込み
    """
    指定されたパスから画像を読み込む関数
    引数:
        path: 画像ファイルのパス
    戻り値:
        読み込んだ画像オブジェクト または None
    """
    full = os.path.join(BASE_DIR, path) # フルパス取得
    if os.path.exists(full): # ファイル存在確認
        return pygame.image.load(full).convert_alpha() # 画像読み込み
    return None # 画像なし


class MapField: # フィールド画面クラス
    def __init__(self, screen): # 初期化
        self.screen = screen # 画面情報
        self.map_data = MAP_FIELD # マップデータ

        self.player_x = 1 # プレイヤー座標
        self.player_y = 1 # プレイヤー座標

        self.move_cool = 0 # 移動クールタイム

        self.tile_images = self.load_tiles() # タイル画像読み込み
        self.player_img_flont = load_image("fig/map_mahou_1.png") # プレイヤー画像読み込み
        self.player_img_back = load_image("fig/map_mahou_b_1.png") # プレイヤー画像読み込み
        self.player_img_right = load_image("fig/map_mahou_r_1.png") # プレイヤー画像読み込み
        self.player_img_left = load_image("fig/map_mahou_l_1.png") # プレイヤー画像読み込み
        self.player_img = self.player_img_flont # 初期プレイヤー画像

    def load_tiles(self): # タイル画像読み込み
        tiles = {} # タイル画像辞書
        tiles[0] = load_image("fig/grass.png") # 草タイル
        tiles[1] = load_image("fig/load_1.png") # 土タイル
        tiles[2] = load_image("fig/stone.png") # 岩タイル
        tiles[3] = load_image("fig/flower.png") # 花タイル
        tiles[4] = load_image("fig/river_1.png") # 水タイル
        tiles[5] = load_image("fig/tree.png") # 木タイル
        return tiles # タイル画像辞書返却

    def update(self): # 更新処理
        if self.move_cool > 0: # 移動クールタイム中
            self.move_cool -= 1 # クールタイム減少
            return

        keys = pygame.key.get_pressed() # キー取得
        dx, dy = 0, 0 # 移動量初期化
        # dx : x方向移動量
        # dy : y方向移動量

        if keys[pygame.K_LEFT]: 
            dx = -1 # 左移動
            self.player_img = self.player_img_left
        elif keys[pygame.K_RIGHT]: 
            dx = 1 # 右移動
            self.player_img = self.player_img_right
        elif keys[pygame.K_UP]: 
            dy = -1 # 上移動
            self.player_img = self.player_img_back
        elif keys[pygame.K_DOWN]: 
            dy = 1 # 下移動
            self.player_img = self.player_img_flont

        if dx or dy: # 移動がある場合
            nx = self.player_x + dx # 新しいX座標
            ny = self.player_y + dy # 新しいY座標
            #self.map_data : マップデータ参照(MAP_FIELD)
            if 0 <= ny < len(self.map_data) and 0 <= nx < len(self.map_data[0]): # 範囲内確認
                if self.map_data[ny][nx] in [0, 1]: # 移動可能タイル確認
                    self.player_x = nx # プレイヤーX座標更新
                    self.player_y = ny # プレイヤーY座標更新
                    self.move_cool = 8 # 移動クールタイム設定

    def draw(self): # 描画処理
        # カメラ位置計算
        map_width = len(self.map_data[0]) * TILE_SIZE # マップ幅
        map_height = len(self.map_data) * TILE_SIZE # マップ高さ

        camera_x = self.player_x * TILE_SIZE - SCREEN_WIDTH // 2 # カメラX座標
        camera_y = self.player_y * TILE_SIZE - SCREEN_HEIGHT // 2 # カメラY座標
        print(camera_x, camera_y)

        #camera_x = max(0, min(camera_x, map_width - SCREEN_WIDTH)) # カメラX座標調整
        #camera_y = max(0, min(camera_y, map_height - SCREEN_HEIGHT)) # カメラY座標調整

        # マップ描画
        for y, row in enumerate(self.map_data): # マップデータ走査
            for x, tile in enumerate(row): # 各タイル走査
                px = x * TILE_SIZE - camera_x # 画面X座標
                py = y * TILE_SIZE - camera_y # 画面Y座標
                if -TILE_SIZE < px < SCREEN_WIDTH and -TILE_SIZE < py < SCREEN_HEIGHT: # 画面内確認
                    img = self.tile_images.get(tile) # タイル画像取得
                    if img: # 画像がある場合
                        img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE)) # 画像サイズ変更
                        self.screen.blit(img, (px, py)) # 画像描画
                    else: # 画像がない場合
                        pygame.draw.rect( # 四角形描画
                            self.screen, # 画面
                            COLORS[tile],  # 色
                            (px, py, TILE_SIZE, TILE_SIZE) # 位置とサイズ
                        )

        px = self.player_x * TILE_SIZE - camera_x # プレイヤー画面X座標
        py = self.player_y * TILE_SIZE - camera_y # プレイヤー画面Y座標
        if self.player_img: # プレイヤー画像がある場合
            img = pygame.transform.scale(self.player_img, (TILE_SIZE, TILE_SIZE)) # 画像サイズ変更
            self.screen.blit(img, (px, py)) # プレイヤー描画
        else: # プレイヤー画像がない場合
            pygame.draw.rect(self.screen, (255, 0, 0), (px, py, TILE_SIZE, TILE_SIZE)) # 赤四角描画


if __name__ == "__main__":
    game = Game()
    game.run()