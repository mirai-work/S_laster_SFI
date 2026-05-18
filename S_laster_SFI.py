import pyxel
import math
import random

# --- 定数定義 ---
W, H = 240, 160
FOCAL_LENGTH = 140
STAR_COUNT = 300

# --- ユーティリティ ---
def rotate(x, y, angle):
    c, s = math.cos(angle), math.sin(angle)
    return x * c - y * s, x * s + y * c

class App:
    def __init__(self):
        pyxel.init(W, H, title="STAR LUSTER: SOLID FORCE INFINITY", fps=30)

        try:
            pyxel.images[0].load(0, 0, "taitoruGE01.png")
            pyxel.images[1].load(0, 0, "ending.png")
        except:
            pass

        self.AREA_THEMES = {
            1: [0, 11, 3, 5, 12],  # 宇宙 (黒・紺)
            2: [1, 10, 9, 2, 8],   # 火山 (暗赤・橙)
            3: [1, 12, 6, 7, 13],  # 氷河 (青・白)
            4: [5, 7, 6, 13, 7],   # 惑星 (緑・茶)
            5: [0, 14, 8, 1, 13]   # 要塞 (黒・紫・灰)
        }

            # --- サウンド・音楽定義 ---
        try:
            # --- 音楽の設定用の関数を修正 ---
            # 引数を可変（*s_ids）にすることで、音を1つでも2つでも設定可能にします
            def set_bgm_ch(m_id, *s_ids):
                # 基本はch1, 2, 3に音を割り当てる
                ch1 = s_ids[0]
                ch2 = s_ids[1] if len(s_ids) > 1 else s_ids[0]
                ch3 = s_ids[2] if len(s_ids) > 2 else s_ids[0]
                pyxel.musics[m_id].set([], [ch1], [ch2], [ch3])

            # --- 効果音 ---
            pyxel.sounds[0].set("a3a2c3", "p", "6", "vff", 5) # Shot
            pyxel.sounds[1].set("c2c1g1g1", "n", "7", "ffffffff", 20) # Exp
            pyxel.sounds[2].set("g2g1", "n", "7", "f", 10) # Damage
            pyxel.sounds[3].set("c3e3g3c4", "p", "6", "vvvv", 15) # Item/PowerUp
            pyxel.sounds[4].set("b4g4", "s", "7", "n", 35)

            # --- 音楽 ---
            # Sound 10 (大河)
            pyxel.sounds[10].set(
                "g1g2d3g4 g1g2d3g4 a#1a#2f3a#4 c2c3g3c4 d2d3a3d4 d2d3a3d4 " +
                "d2d3a3d4 d2d3a3d4 f1f2c3f4 f1f2c3f4 g1g2d3g4 g1g2d3g4 a1a2e3a4 r", 
                "s", "45676543", "v", 30
            )
            set_bgm_ch(0, 10)
            
            # 各ステージBGM
            pyxel.sounds[11].set("a2c3e3a3 g3e3c3g2", "p", "5", "v", 15); set_bgm_ch(1, 11)
            pyxel.sounds[12].set("f2a2c3f3 e3c3a2e2", "t", "6", "v", 25); set_bgm_ch(2, 12)
            pyxel.sounds[13].set("c4g3e4c4 b3g3d4b3", "s", "4", "v", 30); set_bgm_ch(3, 13)
            pyxel.sounds[14].set("d3f3a3d4 c4a3f3c3", "p", "6", "v", 20); set_bgm_ch(4, 14)
            pyxel.sounds[15].set("g2g2g3g3 f2f2f3f3", "t", "7", "v", 10); set_bgm_ch(5, 15)
            
            # エンディング
            pyxel.sounds[16].set("a2 c3 e3 g3 f3 e3 d3 f3", "s", "5", "v v v v v v v v", 50)
            set_bgm_ch(6, 16)
            
            # 最終ボス (17と27の2つの音を重ねる)
            pyxel.sounds[17].set(
                "c1 c1 c1 c1 c#1 c#1 c#1 c#1", # 8音
                "s", "6", "v", 15
            )
            pyxel.sounds[27].set(
                "c2 g2 a#2 g2 c#2 g#2 b2 g#2", # 8音
                "s", "5", "v", 15
            )
            set_bgm_ch(7, 17, 27) # これでエラーにならなくなります
            
            # その他
            pyxel.sounds[18].set("c3g3c4e4 d4b3g3d3", "s", "5", "v", 40); set_bgm_ch(8, 18)
            pyxel.sounds[19].set("c3g2e2c2", "s", "6", "vvvv", 60); set_bgm_ch(9, 19)
        except:
            pass
        self.cmd_input = []
        self.invincible = False
        self.bg_objects = []
        self.current_music = -1
        self.reset()
        pyxel.run(self.update, self.draw)

    def play_bgm(self, m_id):
        if self.current_music != m_id:
            pyxel.stop()
            pyxel.playm(m_id, loop=True)
            self.current_music = m_id

    def reset(self):
        self.px = self.py = self.pz = 0
        self.vx = self.vy = 0
        self.roll = 0
        self.pitch = 0
        self.speed = 15.0
        self.target_speed = 15.0
        self.hp = 100
        self.max_hp = 100
        self.energy = 100
        self.score = 0
        self.area = 1
        self.invincible = False
        self.show_area_select = False # メニューを非表示にする
        self.cmd_input = []           # 入力履歴もクリア
        self.area_kills = 0
        self.target_kills = 15
        self.state = "TITLE"
        self.timer = 0
        self.shake = 0
        self.flash = 0
        self.flash_green = 0
        self.stars = [[random.uniform(-1500, 1500), random.uniform(-1500, 1500), random.uniform(0, 2000)] for _ in range(STAR_COUNT)]
        self.enemies = []
        self.bullets = []
        self.ebullets = []
        self.particles = []
        self.explosions = []
        self.items = []
        self.boss = None
        self.memorial_data = []
        self.result_timer = 0
        self.last_stage_score = 0
        self.bg_objects = []
        self.last_boss_bonus = 0
        self.current_music = -1        

    def project(self, x, y, z):
        tz = z - self.pz
        if tz <= 5: return None
        dx, dy = x - self.px, y - self.py
        rx, ry = rotate(dx, dy, self.roll)
        f = FOCAL_LENGTH
        sx = W / 2 + rx * f / tz
        sy = H / 2 + ry * f / tz
        return sx, sy, tz
    
    def update(self):
        self.timer += 1
        btn_start = pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_START)

        if self.state == "TITLE":
            self.play_bgm(0)
        elif self.state == "GAMEOVER":
            self.play_bgm(7)
        elif self.state == "ENDING":
            self.play_bgm(6)
        elif self.state == "PLAY" or self.state == "RESULT":
            if self.boss:
                self.play_bgm(7 if self.boss['is_final'] else 6)
            else:
                self.play_bgm(self.area)
        # --- シールド警告音（新しい音色 Sound 4） ---
        if self.state == "PLAY" and self.hp <= 20:
            if self.timer % 12 == 0: # 鳴る間隔
                try:
                    pyxel.play(2, 4) # チャンネル2でSound 4を再生
                except:
                    pass

        if self.state == "PLAY" and not self.boss:
            if len(self.enemies) < 3 + self.area and self.timer % 30 == 0:
                etype = random.randint(0, 2)
                on_ground = False
                if self.area in [2, 4]: 
                    on_ground = True
                elif self.area == 5:
                    on_ground = random.choice([True, False])

                if on_ground:
                    ey = self.py + 200
                else:
                    ey = self.py + random.uniform(-300, 300)
                
                self.enemies.append({
                    "x": self.px + random.uniform(-400, 400),
                    "y": ey,
                    "z": self.pz + 2000,
                    "base_z": self.pz + 2000,
                    "hp": 1 + (self.area // 2),
                    "type": etype,
                    "t": 0,
                    "on_ground": on_ground
                })

        if self.state == "TITLE":
            self.pz += 40 
            # --- メニュー表示中の操作 ---
            if getattr(self, 'show_area_select', False):
                # 左右でエリア選択
                if pyxel.btnp(pyxel.KEY_LEFT) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT):
                    self.area = self.area - 1 if self.area > 1 else 5
                    try: pyxel.play(3, 3) # カチッという音
                    except: pass
                if pyxel.btnp(pyxel.KEY_RIGHT) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT):
                    self.area = self.area + 1 if self.area < 5 else 1
                    try: pyxel.play(3, 3)
                    except: pass
                
                # 上下で無敵のON/OFF
                if pyxel.btnp(pyxel.KEY_UP) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_UP):
                    if not self.invincible:
                        self.invincible = True
                        try: pyxel.play(3, 3)
                        except: pass
                if pyxel.btnp(pyxel.KEY_DOWN) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN):
                    if self.invincible:
                        self.invincible = False
                        try: pyxel.play(3, 3)
                        except: pass
            
            # --- コマンド待機中（上上下下） ---
            else:
                new_key = None
                if pyxel.btnp(pyxel.KEY_UP) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_UP): new_key = "U"
                elif pyxel.btnp(pyxel.KEY_DOWN) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN): new_key = "D"
                
                if new_key:
                    self.cmd_input.append(new_key)
                    if len(self.cmd_input) > 4: self.cmd_input.pop(0)
                    if "".join(self.cmd_input) == "UUDD":
                        self.show_area_select = True # ここでメニュー発動！
                        self.invincible = True      # 最初は無敵をONにしてあげる
                        self.cmd_input = []
                        try: pyxel.play(3, 3)
                        except: pass

            # スタート判定
            if btn_start:
                self.cmd_input = []
                self.state = "PLAY"
                self.flash = 30
                self.timer = 0
                self.target_kills = 15 + (self.area - 1) * 5
                self.target_speed = 35.0             
                return

        if self.state == "ENDING": self.update_ending(); return

        # --- ゲームオーバー時の挙動修正 ---
        if self.state == "GAMEOVER":
            if self.timer > 150: # 30fps * 5秒 = 150フレーム
                self.reset()
                self.state = "TITLE"
            return

        if self.state == "RESULT":
            self.result_timer -= 1
            self.pz += self.speed
            self.update_entities()
            if self.result_timer <= 0:
                if self.area < 5:
                    self.area += 1
                    self.target_kills = 15 + (self.area - 1) * 5 
                    self.target_speed = 60.0
                    self.state = "PLAY"
                    self.timer = 0
                    self.bg_objects = [] 
                else:
                    self.state = "ENDING"
                    self.timer = 0
                    self.target_speed = 0.5
            return

        accel = 1.2
        if pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT): self.vx += accel
        elif pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT): self.vx -= accel
        else: self.vx *= 0.85
        if pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN): self.vy += accel
        elif pyxel.btn(pyxel.KEY_UP) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_UP): self.vy -= accel
        else: self.vy *= 0.85

        self.vx = max(-12, min(12, self.vx)); self.vy = max(-10, min(10, self.vy))
        self.px += self.vx; self.py += self.vy; self.pz += self.speed
        if self.speed > 25 and self.area_kills == 0 and not self.boss: self.target_speed = 15.0
        self.speed += (self.target_speed - self.speed) * 0.08
        self.roll += ((-self.vx * 0.1) - self.roll) * 0.15
        self.energy = min(100, self.energy + 0.5)
        
        is_shoot = pyxel.btn(pyxel.KEY_SPACE) or pyxel.btn(pyxel.KEY_Z) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_A) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_B)
        if is_shoot and self.timer % 4 == 0:
            if self.energy > 5:
                self.bullets.append([self.px - 10, self.py + 5, self.pz + 20, 0, 0, 60])
                self.bullets.append([self.px + 10, self.py + 5, self.pz + 20, 0, 0, 60])
                self.energy -= 4
                try: pyxel.play(0, 0)
                except: pass

        if self.state == "PLAY" and not self.boss:
            if random.random() < 0.01: 
                self.bg_objects.append({"type": "PLANET", "x": self.px + random.uniform(-2000, 2000), "y": self.py + random.uniform(-1500, 1500), "z": self.pz + 4000, "size": random.randint(30, 80), "col": random.choice([self.AREA_THEMES[self.area][3], self.AREA_THEMES[self.area][4]]), "seed": random.random()})
            if random.random() < 0.03: 
                self.bg_objects.append({"type": "STAR", "x": self.px + random.uniform(-1000, 1000), "y": self.py + random.uniform(-1000, 1000), "z": self.pz + 2000, "vx": random.uniform(-15, 15), "vy": random.uniform(-15, 15)})

        self.update_entities()
        if self.shake > 0: self.shake -= 1
        if self.flash > 0: self.flash -= 1
        if self.flash_green > 0: self.flash_green -= 1
        if self.hp <= 0: self.state = "GAMEOVER"; self.timer = 0

    def spawn_boss(self):
        is_final = (self.area == 5)
        hp_val = int(self.area * 40) if not is_final else 200
        self.boss = {"x": self.px, "y": self.py, "z": self.pz + 1500, "base_z": self.pz + 1500, "hp": hp_val, 
                     "max_hp": hp_val, "t": 0, "is_final": is_final}
        self.enemies = [] 
        self.flash = 40; self.target_speed = 8.0 if is_final else 12.0

    def spawn_item(self, x, y, z):
        if random.random() < 0.4:
            itype = "H" if random.random() < 0.5 else "E"
            self.items.append({"x": x, "y": y, "z": z, "base_z": z, "type": itype, "t": 0})

    def update_entities(self):
        for obj in self.bg_objects[:]:
            if obj["type"] == "STAR":
                obj["x"] += obj["vx"]; obj["y"] += obj["vy"]
            if obj["z"] < self.pz: self.bg_objects.remove(obj)

        for b in self.bullets[:]:
            b[2] += b[5]
            hit = False
            for e in self.enemies[:]:
                if abs(b[0]-e['x']) < 80 and abs(b[1]-e['y']) < 80 and abs(b[2]-e['z']) < 120:
                    e['hp'] -= 1; hit = True
                    if e['hp'] <= 0:
                        self.score += 300 * self.area
                        if not self.boss:
                            self.area_kills += 1
                            if self.area_kills >= self.target_kills: self.spawn_boss()
                        self.spawn_particles(e['x'], e['y'], e['z'], 20, 8); self.spawn_explosion(e['x'], e['y'], e['z'])
                        self.spawn_item(e['x'], e['y'], e['z'])
                        if e in self.enemies: self.enemies.remove(e)
                    break
            if not hit and self.boss:
                limit_w = 60 if self.boss['is_final'] else 40 
                limit_h = 50 if self.boss['is_final'] else 35
                if abs(b[0]-self.boss['x']) < limit_w and abs(b[1]-self.boss['y']) < limit_h and abs(b[2]-self.boss['z']) < 650:
                    self.boss['hp'] -= 1
                    hit = True
                    self.flash = 2
                    try: pyxel.play(0, 0) # --- ボスへのヒット音を追加 ---
                    except: pass
                    if self.boss['hp'] <= 0:
                        boss_score = 10000 + (self.area - 1) * 5000
                        if self.boss['is_final']: boss_score += 100000
                        self.score += boss_score
                        self.last_boss_bonus = boss_score 
                        self.memorial_data.append({"area": self.area, "score": self.score})
                        self.spawn_particles(self.boss['x'], self.boss['y'], self.boss['z'], 100, 8)
                        self.spawn_explosion(self.boss['x'], self.boss['y'], self.boss['z'], 3)
                        self.boss = None; self.area_kills = 0
                        self.last_stage_score = self.score
                        self.state = "RESULT"
                        self.result_timer = 150 
            if hit or b[2] > self.pz + 1800:
                if b in self.bullets: self.bullets.remove(b)

        for it in self.items[:]:
            it['base_z'] -= 4; it['t'] += 1
            it['z'] = it['base_z'] + math.sin(it['t'] * 0.1) * 40
            if abs(it['x']-self.px) < 50 and abs(it['y']-self.py) < 50 and abs(it['z']-self.pz) < 60:
                if it['type'] == "H": self.hp = min(100, self.hp + 20)
                else: self.energy = min(100, self.energy + 50)
                self.flash_green = 10
                try: pyxel.play(0, 3)
                except: pass
                self.items.remove(it)
            elif it['z'] < self.pz: self.items.remove(it)

        for e in self.enemies[:]:
            e['t'] += 1; e['base_z'] -= (10 + self.area) 
            if e.get('on_ground', False):
                e['z'] = e['base_z']
            else:
                e['z'] = e['base_z'] + math.sin(e['t'] * 0.08) * 100
            
            if e['z'] < self.pz: self.enemies.remove(e); continue
            shot_interval = max(10, 45 - self.area * 7)
            if e['t'] % shot_interval == 0 and e['z'] > self.pz + 300:
                self.shoot_enemy_bullet(e, 0, 0)

        if self.boss:
            b = self.boss; b['t'] += 1
            move_scale = 0.03 if b['is_final'] else 0.06
            b['x'] = self.px + math.sin(b['t'] * move_scale) * (250 if b['is_final'] else 140)
            b['y'] = self.py + math.cos(b['t'] * (move_scale*0.7)) * (150 if b['is_final'] else 90)
            z_offset = 0
            if self.area == 1: z_offset = math.sin(b['t'] * 0.03) * 300
            elif self.area == 2: z_offset = math.cos(b['t'] * 0.08) * 400
            elif self.area == 3: z_offset = 300 + math.sin(b['t'] * 0.04) * 150
            elif self.area == 4: z_offset = math.sin(b['t'] * 0.1) * 500
            elif self.area == 5: z_offset = (math.sin(b['t'] * 0.03) * 200 + math.cos(b['t'] * 0.08) * 200 + math.sin(b['t'] * 0.12) * 200)
            z_base = self.pz + (800 if b['is_final'] else 900)
            target_z = z_base + z_offset
            b['z'] += (target_z - b['z']) * 0.1
            # --- ここから追加 ---
            is_hurry = (b['hp'] / b['max_hp']) < 0.3
            boss_shot_rate = max(15, 60 - self.area * 10)
            if is_hurry:
                boss_shot_rate = max(8, boss_shot_rate // 2) # 弾の間隔を半分に
            # --- 弾の発射処理（ここから重要！） ---
            if b['t'] % boss_shot_rate == 0:
                self.shoot_enemy_bullet(b, 0, 0)
                # インデントを揃えました：弾を撃つタイミングと同じ時だけ音を鳴らす
                if is_hurry:
                    try: pyxel.play(2, 4)
                    except: pass

        for eb in self.ebullets[:]:
            eb[0]+=eb[3]; eb[1]+=eb[4]; eb[2]+=eb[5]
            eb[2] += math.sin(pyxel.frame_count * 0.2) * 2
            if abs(eb[0]-self.px)<25 and abs(eb[1]-self.py)<25 and abs(eb[2]-self.pz)<30:
                if not self.invincible: self.hp -= 15
                self.shake = 12; self.flash = 3; self.ebullets.remove(eb)
                try: pyxel.play(2, 2)
                except: pass
            elif eb[2] < self.pz - 100: self.ebullets.remove(eb)

        for p in self.particles[:]:
            p['x']+=p['vx']; p['y']+=p['vy']; p['z']+=p['vz']; p['life']-=1
            p['z'] += math.sin(p['life'] * 0.5) * 5
            if p['life']<=0: self.particles.remove(p)
        for ex in self.explosions[:]:
            ex['life'] -= 1
            ex['z'] += math.sin(ex['life']) * 10
            if ex['life'] <= 0: self.explosions.remove(ex)

    def update_ending(self):
        if self.timer < 300: self.speed = 60.0 * (1.0 - (self.timer / 300))
        else: self.speed = 1.0
        self.pz += self.speed
        if self.timer > 1100:
            if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_START):
                self.reset(); self.state = "TITLE"

    def shoot_enemy_bullet(self, e, ox, oy):
        dist = e['z'] - self.pz
        if dist <= 0: return
        vx = (self.px - e['x']) / dist * 11 + ox
        vy = (self.py - e['y']) / dist * 11 + oy
        self.ebullets.append([e['x'], e['y'], e['z'], vx, vy, -15])

    def spawn_particles(self, x, y, z, count, col):
        for _ in range(count):
            self.particles.append({'x':x,'y':y,'z':z,'vx':random.uniform(-6,6),'vy':random.uniform(-6,6),
                                   'vz':random.uniform(-4,4),'life':15,'col':col})

    def spawn_explosion(self, x, y, z, size_mult=1):
        self.explosions.append({'x': x, 'y': y, 'z': z, 'life': 10, 'size': 15 * size_mult})
        try: pyxel.play(0, 1)
        except: pass

    def draw(self):
        if self.state == "ENDING": self.draw_ending(); return
        theme = self.AREA_THEMES.get(self.area, self.AREA_THEMES[1])
        pyxel.cls(theme[0])
        # --- ここから追加 ---
        if self.boss and (self.boss['hp'] / self.boss['max_hp']) < 0.3:
            if pyxel.frame_count % 10 < 5:
                pyxel.rect(0, 0, W, 7, 8)       # 上の赤い帯
                pyxel.rect(0, H-7, W, 7, 8)     # 下の赤い帯
                pyxel.text(W//2-45, 1, "WARNING:OVERDRIVE!!", 7)
        # --------------------
        ox, oy = (random.randint(-self.shake, self.shake), random.randint(-self.shake, self.shake)) if self.shake > 0 else (0,0)

        # 背景の地上描画
        if self.area == 2:
            for i in range(5):
                z_line = ((self.pz + i * 400) // 400) * 400
                p1 = self.project(self.px - 1000, self.py + 200, z_line)
                p2 = self.project(self.px + 1000, self.py + 200, z_line)
                if p1 and p2: pyxel.line(int(p1[0]), int(p1[1]), int(p2[0]), int(p2[1]), 2)
        elif self.area in [4, 5]:
            grid_col = 4 if self.area == 4 else 13
            for i in range(6):
                z_line = ((self.pz + i * 300) // 300) * 300
                p1 = self.project(self.px - 1000, self.py + 200, z_line)
                p2 = self.project(self.px + 1000, self.py + 200, z_line)
                if p1 and p2: pyxel.line(int(p1[0]), int(p1[1]), int(p2[0]), int(p2[1]), grid_col)
            for i in range(-3, 4):
                lx = self.px + i * 250
                p1 = self.project(lx, self.py + 200, self.pz)
                p2 = self.project(lx, self.py + 200, self.pz + 1800)
                if p1 and p2: pyxel.line(int(p1[0]), int(p1[1]), int(p2[0]), int(p2[1]), grid_col)

        if self.area == 5:
            for i in range(4):
                z_pos = ((self.pz + i * 500) // 500) * 500
                for side in [-1, 1]:
                    p1 = self.project(self.px + 400 * side, self.py - 300, z_pos)
                    p2 = self.project(self.px + 400 * side, self.py + 300, z_pos)
                    if p1 and p2: pyxel.line(int(p1[0]), int(p1[1]), int(p2[0]), int(p2[1]), theme[4])
                    p3 = self.project(self.px - 400, self.py + 300 * side, z_pos)
                    p4 = self.project(self.px + 400, self.py + 300 * side, z_pos)
                    if p3 and p4: pyxel.line(int(p3[0]), int(p3[1]), int(p4[0]), int(p4[1]), theme[4])

        for s in self.stars:
            s[2] -= self.speed
            if s[2] < self.pz:
                s[2] = self.pz + 2000; s[0] = self.px + random.uniform(-1500, 1500); s[1] = self.py + random.uniform(-1500, 1500)
            p = self.project(s[0], s[1], s[2])
            if p:
                sx, sy, sz = p
                col = 7 if sz < 800 else (theme[4] if self.area != 3 else 6)
                if self.speed > 20:
                    p2 = self.project(s[0], s[1], s[2] + self.speed * 2.5)
                    if p2: pyxel.line(int(sx), int(sy), int(p2[0]), int(p2[1]), col)
                else: pyxel.pset(int(sx+ox), int(sy+oy), col)

        for obj in self.bg_objects:
            p = self.project(obj["x"], obj["y"], obj["z"])
            if p:
                sx, sy, sz = p
                if obj["type"] == "PLANET":
                    rad = obj["size"] * 100 / sz
                    if rad > 0:
                        pyxel.circ(int(sx), int(sy), int(rad), obj["col"])
                        if rad > 4:
                            seed = obj["seed"]
                            for i in range(3):
                                cx = sx + math.cos(seed + i) * (rad * 0.4)
                                cy = sy + math.sin(seed + i) * (rad * 0.4)
                                pyxel.circ(int(cx), int(cy), int(rad * 0.15), theme[4])
                            pyxel.circb(int(sx), int(sy), int(rad), theme[4])
                            if seed > 0.5 and self.area == 4: pyxel.ellib(int(sx - rad*1.5), int(sy - rad*0.4), int(rad*3), int(rad*0.8), theme[4])
                elif obj["type"] == "STAR":
                    p2 = self.project(obj["x"] - obj["vx"]*5, obj["y"] - obj["vy"]*5, obj["z"] + 150)
                    if p2: pyxel.line(int(sx), int(sy), int(p2[0]), int(p2[1]), theme[4]); pyxel.pset(int(sx), int(sy), theme[3])

        for it in self.items:
            p = self.project(it['x'], it['y'], it['z'])
            if p:
                sx, sy, sz = p; s_val = 3000 / sz; c = 8 if it['type'] == "H" else 10
                ang = it['t'] * 0.2
                pts = []
                for dz in [-1, 1]:
                    for dy in [-1, 1]:
                        for dx in [-1, 1]:
                            rx, ry = rotate(dx * s_val, dy * s_val, ang)
                            ry, rz = rotate(ry, dz * s_val, ang * 0.5)
                            pts.append((sx + rx, sy + ry))
                if len(pts) == 8:
                    pyxel.tri(int(pts[0][0]), int(pts[0][1]), int(pts[1][0]), int(pts[1][1]), int(pts[3][0]), int(pts[3][1]), c)
                    pyxel.tri(int(pts[4][0]), int(pts[4][1]), int(pts[5][0]), int(pts[5][1]), int(pts[7][0]), int(pts[7][1]), c)
                for i in range(4):
                    pyxel.line(int(pts[i*2][0]), int(pts[i*2][1]), int(pts[i*2+1][0]), int(pts[i*2+1][1]), 7)
                    pyxel.line(int(pts[i][0]), int(pts[i][1]), int(pts[(i+2)%4 + (4 if i>=2 else 0)][0]), int(pts[(i+2)%4 + (4 if i>=2 else 0)][1]), 7)
                    pyxel.line(int(pts[i][0]), int(pts[i][1]), int(pts[i+4][0]), int(pts[i+4][1]), 7)
                pyxel.circ(int(sx), int(sy), int(s_val*0.4), 7); pyxel.text(int(sx-2), int(sy-2), it['type'], 0); pyxel.circb(int(sx), int(sy), int(s_val + (pyxel.frame_count % 15)), c)
        for e in self.enemies:
            ez = e['z']
            if ez - self.pz <= 5: continue
            t = e['t']
            c1, c2 = theme[1], theme[2]
            scale = 25
            if e.get('on_ground', False):
                if e['type'] == 0:
                    model = [(0,-1.5,0), (-1,-0.8,1), (1,-0.8,1), (1,-0.8,-1), (-1,-0.8,-1), (0,0.5,0)]
                    edges = [(0,1),(0,2),(0,3),(0,4),(1,2),(2,3),(3,4),(4,1), (1,5),(2,5),(3,5),(4,5)]
                elif e['type'] == 1:
                    model = [(0,-1,0), (-1.5,-2,1), (1.5,-2,1), (0,-2,-1.5), (0,0.5,0)]
                    edges = [(0,1),(0,2),(0,3),(1,2),(2,3),(3,1),(0,4)]
                else:
                    model = [(0,-2.5,0), (-1,0.5,1), (1,0.5,1), (1,0.5,-1), (-1,0.5,-1)]
                    edges = [(0,1),(0,2),(0,3),(0,4),(1,2),(2,3),(3,4),(4,1)]
            else:
                if e['type'] == 0:
                    model = [(0,-1,2), (-1.5,0.5,-1), (1.5,0.5,-1), (0,1.5,0)]
                    edges = [(0,1), (0,2), (0,3), (1,2), (2,3), (3,1)]
                elif e['type'] == 1:
                    model = [(-1,-1,-1), (1,-1,-1), (1,1,-1), (-1,1,-1), (-1,-1,1), (1,-1,1), (1,1,1), (-1,1,1)]
                    edges = [(0,1),(1,2),(2,3),(3,0), (4,5),(5,6),(6,7),(7,4), (0,4),(1,5),(2,6),(3,7)]
                else:
                    model = [(0,-1,2), (-2,0,-1), (2,0,-1), (0,2,-1), (-1,-1,-2), (1,-1,-2)]
                    edges = [(0,1),(0,2),(0,3),(1,2),(2,3),(3,1), (1,4),(2,5),(4,5)]

            proj_pts = []
            for mx, my, mz in model:
                if e.get('on_ground', False):
                    rx, rz = mx * scale, mz * scale
                else:
                    rx, rz = rotate(mx * scale, mz * scale, t * 0.1 if e['type'] != 0 else 0)
                ry = my * scale
                if not e.get('on_ground', False):
                    rx, ry = rotate(rx, ry, math.sin(t*0.05)*0.5)
                p = self.project(e['x'] + rx, e['y'] + ry, ez + rz)
                proj_pts.append(p)
            if all(proj_pts):
                pyxel.tri(int(proj_pts[0][0]), int(proj_pts[0][1]), int(proj_pts[1][0]), int(proj_pts[1][1]), int(proj_pts[2][0]), int(proj_pts[2][1]), c1)
                for e1, e2 in edges: pyxel.line(int(proj_pts[e1][0]), int(proj_pts[e1][1]), int(proj_pts[e2][0]), int(proj_pts[e2][1]), 7)

        if self.boss:
            t = self.boss['t']
            rot_y = t * 0.1
            rot_x = math.sin(t * 0.05) * 0.5
            weak_col = 8 if pyxel.frame_count % 4 < 2 else 7
            is_low_hp = (self.boss['hp'] / self.boss['max_hp']) < 0.3
            base_col = theme[1]
            if is_low_hp and pyxel.frame_count % 4 < 2: base_col = 9

            def draw_wire_box(x, y, z, w, h, d, col, rx_off=0, ry_off=0, rz_off=0):
                points = []
                for dz_b in [-d, d]:
                    for dy_b in [-h, h]:
                        for dx_b in [-w, w]:
                            tx, ty = rotate(dx_b, dy_b, rz_off)
                            tx, tz = rotate(tx, dz_b, ry_off)
                            ty, tz = rotate(ty, tz, rx_off)
                            rx_b, rz_b = rotate(tx, tz, rot_y)
                            ry_b, rz_b = rotate(ty, rz_b, rot_x)
                            p_b = self.project(x + rx_b, y + ry_b, z + rz_b)
                            points.append(p_b)
                if all(points):
                    pyxel.tri(int(points[0][0]), int(points[0][1]), int(points[1][0]), int(points[1][1]), int(points[3][0]), int(points[3][1]), col)
                    pyxel.tri(int(points[4][0]), int(points[4][1]), int(points[5][0]), int(points[5][1]), int(points[6][0]), int(points[6][1]), col)
                    for i_b in range(4):
                        pyxel.line(int(points[i_b*2][0]), int(points[i_b*2][1]), int(points[i_b*2+1][0]), int(points[i_b*2+1][1]), 7)
                        pyxel.line(int(points[i_b][0]), int(points[i_b][1]), int(points[(i_b+2)%4 + (4 if i_b>=2 else 0)][0]), int(points[(i_b+2)%4 + (4 if i_b>=2 else 0)][1]), 7)
                        pyxel.line(int(points[i_b][0]), int(points[i_b][1]), int(points[i_b+4][0]), int(points[i_b+4][1]), 7)

            bx, by, bz = self.boss['x'], self.boss['y'], self.boss['z']
            if self.area == 1:
                draw_wire_box(bx-40, by, bz, 20, 20, 40, base_col)
                draw_wire_box(bx+40, by, bz, 20, 20, 40, base_col)
                draw_wire_box(bx, by, bz, 30, 5, 10, weak_col)
            elif self.area == 2:
                for i in range(3): draw_wire_box(bx, by, bz, 60, 5, 60, base_col, ry_off=i*1.0)
                draw_wire_box(bx, by, bz, 20, 30, 20, weak_col)
            elif self.area == 3:
                draw_wire_box(bx, by, bz, 50, 50, 50, base_col, rx_off=t*0.05, ry_off=t*0.05)
                draw_wire_box(bx, by, bz, 20, 20, 20, weak_col)
            elif self.area == 4:
                for s_side in [-1, 1]:
                    draw_wire_box(bx+30*s_side, by+30, bz, 10, 40, 10, base_col, rz_off=0.5*s_side)
                    draw_wire_box(bx+30*s_side, by-30, bz, 10, 40, 10, base_col, rz_off=-0.5*s_side)
                draw_wire_box(bx, by, bz, 15, 15, 80, weak_col)
            elif self.area == 5:
                draw_wire_box(bx, by, bz, 120, 150, 80, 15)
                draw_wire_box(bx-50, by-30, bz+40, 20, 20, 10, weak_col)
                draw_wire_box(bx+50, by-30, bz+40, 20, 20, 10, weak_col)
                draw_wire_box(bx, by+60, bz+40, 40, 10, 5, 8 if pyxel.frame_count % 8 < 4 else 10)

            p_center = self.project(bx, by, bz)
            if p_center:
                sx, sy, sz = p_center
                target_size = (30000 if self.boss['is_final'] else 15000) / sz
                if pyxel.frame_count % 2 == 0:
                    pyxel.rectb(int(sx-target_size), int(sy-target_size), int(target_size*2), int(target_size*2), 10)
                    pyxel.text(int(sx-15), int(sy-target_size-10), "BOSS TARGET", 10)

        for b in self.bullets:
            p = self.project(b[0], b[1], b[2])
            if p: pyxel.rect(int(p[0]+ox), int(p[1]-4+oy), 2, 8, 10)
        for eb in self.ebullets:
            p = self.project(eb[0], eb[1], eb[2])
            if p: pyxel.circ(int(p[0]+ox), int(p[1]+oy), 2, 8 if pyxel.frame_count % 2 == 0 else 7)
        for pr in self.particles:
            p = self.project(pr['x'], pr['y'], pr['z'])
            if p: pyxel.pset(int(p[0]+ox), int(p[1]+oy), pr['col'])
        for ex in self.explosions:
            p = self.project(ex['x'], ex['y'], ex['z'])
            if p:
                sx, sy, sz = p; radius = ex['size'] * 100 / sz
                if radius > 1: pyxel.circ(int(sx + ox), int(sy + oy), int(radius), 8 if pyxel.frame_count % 2 == 0 else 10)

        if self.flash > 0:
            if self.hp <= 0: pyxel.cls(8)
            elif self.state == "PLAY" and self.timer < 31: 
                pyxel.cls(7); pyxel.text(int(W/2-15), int(H/2), "START!", pyxel.frame_count % 16)
            else: pyxel.cls(7)

        self.draw_cockpit(ox, oy)
        self.draw_hud(theme)

        if self.state == "RESULT":
            pyxel.rect(int(W/2-60), int(H/2-30), 120, 60, 0); pyxel.rectb(int(W/2-60), int(H/2-30), 120, 60, 7)
            pyxel.text(int(W/2-35), int(H/2-20), f"STAGE {self.area} CLEAR!", 10)
            pyxel.text(int(W/2-50), int(H/2-5), f"BOSS BONUS: +{self.last_boss_bonus}", 14)
            pyxel.text(int(W/2-50), int(H/2+5), f"TOTAL SCORE: {self.score:07}", 7)
            pyxel.text(int(W/2-35), int(H/2+18), "GREAT MISSION!", pyxel.frame_count % 16)

    def draw_cockpit(self, ox, oy):
        c1, c2 = 1, 13
        if self.hp < 30 and pyxel.frame_count % 10 < 5: 
            c1, c2 = 2, 8 
        elif self.flash_green > 0: 
            c1, c2 = 3, 11
        elif self.flash > 0 and self.hp > 0 and (self.state == "PLAY" or self.state == "RESULT") and self.timer > 31:
            if pyxel.frame_count % 2 == 0: c1, c2 = 8, 7
            
        pyxel.tri(0, H, 40, H, 0, H-80, c1)
        pyxel.line(0, H-80, 40, H, c2)
        pyxel.tri(W, H, W-40, H, W, H-80, c1)
        pyxel.line(W, H-80, W-40, H, c2)
        pyxel.rect(0, H-25, W, 25, c1)
        pyxel.rect(20, H-35, W-40, 10, c1)
        
        l_col = c2 if self.shake == 0 else (7 if pyxel.frame_count % 2 == 0 else c1)
        pyxel.line(0, H-25, 20, H-35, l_col)
        pyxel.line(20, H-35, W-20, H-35, l_col)
        pyxel.line(W-20, H-35, W, H-25, l_col)
        
        for i in range(4):
            by_p = H-23+i*4
            pyxel.line(30, by_p, 40, by_p, c2)
            if pyxel.frame_count % 10 > i*2: 
                pyxel.line(32, by_p+1, 38, by_p+1, 7)
        for i in range(5):
            pyxel.pset(200+i*3, int(H-20+math.sin(pyxel.frame_count*0.3+i)*5), c2)
        pyxel.circb(215, H-15, 4, c2)
        pyxel.line(215, H-15, int(215+math.cos(pyxel.frame_count*0.2)*4), int(H-15+math.sin(pyxel.frame_count*0.2)*4), 7)

    def draw_hud(self, theme):
        cx, cy = W/2, H/2
        pyxel.rectb(int(cx-18), int(cy-18), 37, 37, theme[1])
        pyxel.line(int(cx-5), int(cy), int(cx+5), int(cy), 7); pyxel.line(int(cx), int(cy-5), int(cx), int(cy+5), 7)
        pyxel.text(10, 10, f"AREA: {self.area}", 7); pyxel.text(10, 20, f"KILLS: {self.area_kills}/{self.target_kills}", theme[1])
        pyxel.text(W-70, 10, f"SCORE: {self.score:07}", 7)
        if self.state == "PLAY" and self.invincible: pyxel.text(10, 30, "INVINCIBLE", 10)
        pyxel.text(45, H-23, "SHIELD", 7)
        pyxel.rect(45, H-15, 60, 4, 1); pyxel.rect(45, H-15, int((self.hp/self.max_hp)*60), 4, 8 if self.hp < 30 else 11)
        pyxel.text(135, H-23, "ENERGY", 7)
        pyxel.rect(135, H-15, 60, 4, 1); pyxel.rect(135, H-15, int((self.energy/100)*60), 4, 10)

        if self.boss:
            t_str = "!! GIGANT HUMAN HEAD !!" if self.boss['is_final'] else "GUARDIAN"
            pyxel.text(int(W/2 - len(t_str)*2), 20, t_str, pyxel.frame_count % 16 if self.boss['is_final'] else 7)
            hp_ratio = self.boss['hp']/self.boss['max_hp']
            bar_col = 8 if hp_ratio > 0.3 or pyxel.frame_count % 2 == 0 else 9
            pyxel.rect(int(W/2-40), 28, int(hp_ratio*80), 3, bar_col)

        if self.state == "TITLE":
            pyxel.blt(0, 0, 0, 0, 0, 240, 160)
            if getattr(self, 'show_area_select', False):
                pyxel.rect(60, 105, 120, 32, 0); pyxel.rectb(60, 105, 120, 32, 7)
                sel_col = 10 if pyxel.frame_count % 10 < 5 else 7
                pyxel.text(70, 110, "AREA SELECT    :", 7); pyxel.text(140, 110, f"< {self.area} >", sel_col)
                inv_status = "ON " if self.invincible else "OFF"
                pyxel.text(70, 120, "INVINCIBLE(U/D):", 7); pyxel.text(140, 120, f"[{inv_status}]", 11 if self.invincible else 13)
                pyxel.text(65, 128, "DEBUG MODE ACTIVE", 3)
            if pyxel.frame_count % 30 < 15:
               pyxel.text(83, 95, "PRESS SPACE OR START ", 6)
            pyxel.text(72, 140, "(C)MIRAI WORK / M.T 2026", 7)

        elif self.state == "GAMEOVER":
            pyxel.text(int(W/2-28), int(H/2-5), "MISSION FAILED", 11)
            pyxel.text(int(W/2-18), int(H/2+5), "GAME OVER", 13)

    def draw_ending(self):
        pyxel.cls(0)
        
        t = self.timer

        # 1. 画像のフェードイン処理（t=150〜250の間で徐々に表示）
        if t > 150:
            pyxel.blt(0, 0, 1, 0, 0, 240, 160)
            if t < 250:
                # 黒い隙間を徐々に減らして画像が現れる「ブラインド効果」
                fade_step = t - 150
                thickness = 4 - (fade_step // 25)
                if thickness > 0:
                    for y in range(0, 160, 4):
                        pyxel.rect(0, y, 240, thickness, 0)

        # 2. 星の描画（t=120以降は新しく発生せず消えていく）
        for s in self.stars:
            # ★修正箇所：元の「手前に向かってくる動き（-= 10）」に戻しました
            # （これにより最初から星が正常に画面内に表示されます）
            if s[2] < 5000:
                s[2] -= 10
            
            # 手前(z=1)を通り過ぎた星の処理
            if s[2] < 1: 
                if t < 120:
                    s[2] = 2000 # 序盤は通常通り奥から再発生させる
                else:
                    s[2] = 9999 # t >= 120 の場合は再発生させず、描画されない数値にして消す

            p = self.project(s[0], s[1], s[2])
            if p:
                sx, sy, sz = p
                # sz < 1500 の条件で奥すぎる星を描画しない
                if 0 <= sx < W and 0 <= sy < H and sz < 1500:
                    col = 7 if sz < 500 else 5
                    pyxel.pset(int(sx), int(sy), col)
                    
                    # ★【星の量を多くする工夫】他のコードを一切変えないという条件のため、
                    # 描画時に点対称の位置にもう一つ星を描いて擬似的に量を2倍にしています
                    if 0 <= W - sx < W and 0 <= H - sy < H:
                        pyxel.pset(int(W - sx), int(H - sy), col)

        # 3. エンドロール（画像が完全に表示された後の t=300 から開始）
        msgs = [
            (300, "MISSION ACCOMPLISHED", 11),
            (400, "THE DARK NEBULA HAS BEEN PURIFIED...", 7),
            (550, "--- STAFF ---", 10),
            (620, "GAME DESIGN & PROGRAM: M.T", 7),
            (690, "SPECIAL THANKS: TEAM T.D", 7),
            (760, "THANK YOU FOR PLAYING!", 13),
            (850, "PRESENTS BY 2026 MIRAI WORK", 14),
        ]

        for start_t, txt, col in msgs:
            if t > start_t:
                y_pos = 160 - (t - start_t) * 0.5
                if -10 < y_pos < 170:
                    pyxel.text(int(W/2 - len(txt)*2 + 1), int(y_pos + 1), txt, 0)
                    pyxel.text(int(W/2 - len(txt)*2), int(y_pos), txt, col)

        # 4. 最終スコア表示（全体のタイミングに合わせて遅らせています）
        if t > 1000:
            pyxel.rect(int(W/2-55), 130, 110, 25, 0)
            pyxel.rectb(int(W/2-55), 130, 110, 25, 7)
            pyxel.text(int(W/2-50), 135, f"FINAL SCORE: {self.score:07}", pyxel.frame_count % 16)
            if t > 1100:
                pyxel.text(int(W/2-45), 145, "PRESS SPACE OR START", 7)

# アプリの起動（クラスの外、一番左端に書く！）
App()

