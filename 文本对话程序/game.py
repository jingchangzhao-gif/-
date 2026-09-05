# -*- coding: utf-8 -*-
"""
林中小屋 · 雪山寒假(命令行文字冒险)
====================================
场景与物品均按《故事大纲》设计,交互方式与 demo.py 相同:
  每到一个场景 → 显示区域描述 + 可交互对象菜单(随状态变化) → 输入数字执行

主线解谜链(按你的设定):
  厨房拿【打火机】
    → 大厅点燃壁炉(暖和起来,火光里有东西反光)
    → 浇灭炉火,在灰烬里拿到【床头抽屉钥匙】
    → (在大厅查看窗户 → 红色信号弹 → 舅舅独自出门)之后才能上二楼
    → 舅舅卧室:用【床头抽屉钥匙】开抽屉,拿到【地下室钥匙】
    → 大厅地下室门:用【地下室钥匙】进入地下室(里面有一圈可交互物品)
    → 地下室最里面的工具台:拿到【二楼储藏室钥匙】
    → 二楼走廊:打开储藏室 → 看舅舅的日记 → 真相 → 结局选择
"""

INTRO = """\
========================================
        林中小屋 · 雪山寒假
========================================
寒假,你应约来到雪山深处的护林员舅舅家中。
屋外大雪封山,屋内的炉火还没生起来。
舅舅反复叮嘱你:二楼的储藏室和地下室,千万别进去。
可越是不让进的地方,你越是想看看……
(玩法:输入菜单里的数字按回车;0 退出)
"""

# ---------------------------------------------------------------- 场景数据
ROOMS = {
    # ============ 一楼 ============
    "hall": {
        "name": "一楼大厅",
        "desc": "宽敞的木屋大厅:三张旧沙发围着还没生火的壁炉,墙上钉着一张巨大的熊皮,角落里搁着滑雪板,一台老式电视蒙着灰。窗外雪下得正紧。",
        "acts": [
            {"kind": "look", "label": "查看墙上的挂钟",
             "reply": "老式挂钟滴答走着,指针刚过午后。"},
            {"kind": "look", "label": "查看墙上的熊头与熊皮",
             "reply": "一张巨大的棕熊皮钉在墙上,头颅空洞地望着你,像在质问什么。"},
            {"kind": "look", "label": "查看三张旧沙发",
             "reply": "围着壁炉摆了一圈,沙发罩积着灰,一坐下去就会扬起一片尘。"},
            {"kind": "look", "label": "查看门边的滑雪板",
             "reply": "一副木制滑雪板,舅舅说这几天雪况正好,改天带你上雪山。"},
            {"kind": "look", "label": "查看潮湿的柴火",
             "reply": "壁炉边的柴火受了潮,恐怕不容易点着。"},
            {"kind": "look", "label": "查看老式电视",
             "reply": "屏幕蒙着一层灰,大概很久没人打开过了。"},

            {"kind": "window", "label": "凑到窗边往外看",
             "reply": "你贴近窗玻璃呵了口气,搓出一个小圆。就在那片白芒之外,一抹红色信号弹拖着尾巴高高升起,划破灰白的天际——那是舅舅平日巡林的暗号。几乎同时,门廊外传来他绑雪鞋的声音:他匆匆出门去了信号弹升起的方向。\n   屋里一下安静下来,只剩下你,和这座藏了许多门道的木屋。"},

            {"kind": "fire", "label": "点燃壁炉",
             "show_when": [("item", "打火机"), ("not_flag", "fire_lit")],
             "reply": "你用打火机点着了引柴,炉火腾起,暖意一寸寸爬上指尖。火光在墙上摇晃——你注意到,火苗深处有什么金属的东西,正在微微反光。"},
            {"kind": "douse", "label": "浇灭炉火,拨开灰烬",
             "show_when": [("flag", "fire_lit")],
             "reply": "你舀了瓢水浇灭炉火。灰烬里,静静躺着一把被熏黑的小钥匙——原来舅舅把备用钥匙藏在了壁炉里。你把它收了起来。",
             "again": "你再次浇灭了炉火,灰烬里已经什么都没有了。"},

            {"kind": "go", "label": "前往一楼厨房", "target": "kitchen"},
            {"kind": "go", "label": "前往一楼厕所", "target": "toilet"},
            {"kind": "go", "label": "走上二楼的楼梯", "target": "stairs_up",
             "need_flag": "uncle_gone",
             "deny_flag": "舅舅还在家。你不想当着他的面,往楼上探头探脑。"},
            {"kind": "go", "label": "走向通向地下室的门", "target": "basement",
             "need_flag": "uncle_gone",
             "deny_flag": "舅舅明令不许进地下室。趁他还在家,还是别打它的主意。",
             "need_item": "地下室钥匙",
             "deny_item": "地下室的门上了锁,你需要一把钥匙才能打开它。"},
        ],
    },

    "kitchen": {
        "name": "一楼厨房",
        "desc": "窄而旧的厨房。料理台上搁着一只老式打火机,角落柜子里塞着些速食食品,水槽锈迹斑斑。",
        "acts": [
            {"kind": "look", "label": "查看锈迹斑斑的菜刀",
             "reply": "刀刃卷了口,锈得看不出本色。水槽边还留着没洗净的肉沫。"},
            {"kind": "look", "label": "查看柜子里的速食食品",
             "reply": "几包泡面、几罐午餐肉,量多得像是为长期封山备的。"},
            {"kind": "take", "label": "拿起料理台上的打火机", "item": "打火机",
             "reply": "一只老式金属打火机,擦一下就能打出火。你把它收进了口袋。"},
            {"kind": "look", "label": "查看零散的厨房用品",
             "reply": "锅碗瓢盆都旧了,唯独这把打火机擦得干干净净,像是被特意放在这里的。"},
            {"kind": "go", "label": "回到一楼大厅", "target": "hall"},
        ],
    },

    "toilet": {
        "name": "一楼厕所",
        "desc": "窄小的卫生间:一个多年没用过的浴缸,一面布满裂痕的镜子。",
        "acts": [
            {"kind": "look", "label": "查看久未使用的浴缸",
             "reply": "积着干燥的水垢与灰尘,显然空置了好多年。"},
            {"kind": "look", "label": "查看布满裂痕的镜子",
             "reply": "裂痕把你分成许多错位的碎片,看不清自己的脸。"},
            {"kind": "look", "label": "查看洗漱用品",
             "reply": "毛巾发硬,牙刷毛都岔开了,像是很长一段时间没人用过这间厕所。"},
            {"kind": "go", "label": "回到一楼大厅", "target": "hall"},
        ],
    },

    # ============ 地下室 ============
    "basement": {
        "name": "地下室",
        "desc": "台阶尽头是一间阴冷的地窖。血腥与铁锈的味道扑面而来:大铁钩、切割器械映着冷光,靠墙排着几台嗡嗡作响的大冰箱。最深处的工具台上,搁着一串钥匙。",
        "acts": [
            {"kind": "look", "label": "查看墙上的切割器械",
             "reply": "铁钩与锯架上锈迹斑斑,尺寸大得吓人,像是常用来处理大型猎物。"},
            {"kind": "look", "label": "查看一排手术刀",
             "reply": "手术刀码放得整整齐齐,刀刃却干净得反常,和周围的血腥味格格不入。"},
            {"kind": "look", "label": "查看上了锁的枪柜",
             "reply": "枪柜上了锁。透过玻璃,隐约能看见几支猎枪的轮廓。"},
            {"kind": "look", "label": "拉开大冰箱的门",
             "reply": "你拉开一条缝,又猛地关上——里面整整齐齐分着类:棕熊、老虎、狼……全是骨架与冻肉,按种类贴着标签。"},
            {"kind": "take", "label": "查看最里面的工具台", "item": "二楼储藏室钥匙",
             "reply": "工具台上搁着一串钥匙。你取下其中一把——它的尺寸,正对着二楼那间储藏室的门锁。"},
            {"kind": "go", "label": "回到一楼大厅", "target": "hall"},
        ],
    },

    # ============ 二楼 ============
    "stairs_up": {
        "name": "二楼走廊",
        "desc": "木楼梯踩上去吱呀作响。走廊里并排着几扇门:舅舅的卧室、阳台,以及那间永远上着铁锁的储藏室。",
        "acts": [
            {"kind": "go", "label": "推开舅舅卧室的门", "target": "uncle_bedroom"},
            {"kind": "go", "label": "走向阳台", "target": "balcony"},
            {"kind": "go", "label": "去开二楼储藏室的门", "target": "storage_up",
             "need_item": "二楼储藏室钥匙",
             "deny_item": "门上挂着结实的铁锁,任你怎么推都纹丝不动。钥匙应该在别处。",
             "ok": "钥匙插进锁眼,咔哒一声,铁锁应声而开。你推门走了进去。"},
            {"kind": "go", "label": "下楼回到一楼大厅", "target": "hall"},
        ],
    },

    "uncle_bedroom": {
        "name": "舅舅卧室",
        "desc": "床铺叠得整齐,衣柜里挂着厚外套,空气里有一点旧木头与烟草的气味。床头柜上放着一只上了锁的小抽屉。",
        "acts": [
            {"kind": "look", "label": "查看床铺",
             "reply": "被子叠得整齐,枕边放着一副望远镜。"},
            {"kind": "look", "label": "查看衣柜",
             "reply": "挂着几件沾着雪屑的厚外套和护林员制服。"},
            {"kind": "look", "label": "查看换洗衣物",
             "reply": "有几件微微发霉,闻起来不太对味。"},
            {"kind": "look", "label": "查看吃剩下的饼干",
             "reply": "包装拆了一半,像是临时出门,没来得及吃完。"},
            {"kind": "look", "label": "查看野生动物书籍",
             "reply": "全是动物图鉴和标本制作的书,书页翻得起了毛边。"},
            {"kind": "look", "label": "查看上锁的床头抽屉",
             "reply": "一只上了锁的小抽屉,锁眼朝外。钥匙……会放在哪儿呢?"},
            {"kind": "open", "label": "用床头抽屉钥匙打开抽屉",
             "show_when": [("item", "床头抽屉钥匙"), ("not_flag", "has_basement_key")],
             "reply": "熏黑的小钥匙插进锁眼,咔哒一声,抽屉开了。你拨开一张干纸,底下静静躺着一把冰凉的地下室钥匙。",
             "give": "地下室钥匙",
             "set_flags": ["has_basement_key"]},
            {"kind": "go", "label": "回到二楼走廊", "target": "stairs_up"},
        ],
    },

    "balcony": {
        "name": "阳台",
        "desc": "露天的木阳台覆着薄雪,摆着一套桌椅板凳,桌上还放着一杯冒着热气的红茶。",
        "acts": [
            {"kind": "look", "label": "查看桌椅板凳",
             "reply": "木桌椅落着薄薄一层雪,像是刚有人坐过。"},
            {"kind": "look", "label": "查看冒着热气的红茶",
             "reply": "茶还冒着热气——舅舅出门应该没有多久。远处雪山绵延,雪线白得刺眼。"},
            {"kind": "go", "label": "回到二楼走廊", "target": "stairs_up"},
        ],
    },

    "storage_up": {
        "name": "二楼储藏室",
        "desc": "这间被舅舅上了锁的储藏室,小小斗室里物证狼藉:象牙雕件、鳄鱼皮、狼皮摊了一地。桌上一本笔记本摊开着。",
        "acts": [
            {"kind": "look", "label": "查看象牙雕件",
             "reply": "雕工精致的象牙制品,本该是被法律禁止交易的东西。"},
            {"kind": "look", "label": "查看鳄鱼皮",
             "reply": "一整张鳄鱼皮晾在架子上,鳞片冰冷。"},
            {"kind": "look", "label": "查看灰白的狼皮",
             "reply": "狼皮摊在地上,眼睛的位置还留着两个空洞。"},
            {"kind": "look", "label": "查看动物牙齿项链",
             "reply": "一串狼牙穿成的项链,齿尖磨得发亮,像是常被人把玩。"},
            {"kind": "read", "label": "翻开桌上摊开的日记本",
             "reply": "你一页页翻下去——舅舅原本确实是名出色的护林员,守着一整片林海。直到一个雪夜里,他救起一个断了腿的盗猎者。盗猎者告诉他:一头成年棕熊,在富商那里价值六十万。\n\n从此他再没把人送去警局,而是默许了一项协议——他供猎物,盗猎者替他销赃。冰箱里那些分好类的骨架与冻肉,就是这几年的账本。\n\n窗外林海雪原静静下着雪,屋内是成山的森森白骨。你合上日记,手指有些发凉。",
             "append_endings": True},
            {"kind": "go", "label": "回到二楼走廊", "target": "stairs_up"},
        ],
    },
}

# 结局文案(读日记后追加为可选操作)
ENDINGS = [
    {"kind": "ending", "label": "等舅舅回来,当面把这一切摊开",
     "reply": "你把日记和满屋的证物一件件摊在舅舅面前。他沉默了很久,炉火在你身后噼啪作响。终于,他低低应了一声——「……是该有个了断了。」\n这个寒假,你没有选择沉默,而是陪他,把那个困在雪与林里的自己交了出去。",
     "epilogue": "结局一 · 直面"},
    {"kind": "ending", "label": "不动声色,离开后交给森林公安",
     "reply": "你假装什么都没发现,照常和舅舅过完了这个寒假。\n离开雪山之后,你把日记和记录一并交给了森林公安。许多年后再回来,林海依旧安静,小屋换了主人,雪山还是那年的雪山。",
     "epilogue": "结局二 · 守护这片山林"},
]

START = "hall"


def main():
    bag = []                                  # 背包(物品名列表)
    flags = {"uncle_gone": False,             # 舅舅是否已出门
             "fire_lit": False,               # 壁炉是否燃着
             "has_basement_key": False}       # 是否已拿地下室钥匙
    room_id = START
    finished = False

    print(INTRO)

    while not finished:
        room = ROOMS[room_id]
        # 当前状态下"可见"的操作(有些操作会随状态出现/消失)
        acts = []
        for a in room["acts"]:
            ok = True
            for req_type, req_val in a.get("show_when", []):
                if req_type == "item" and req_val not in bag:
                    ok = False
                elif req_type == "not_item" and req_val in bag:
                    ok = False
                elif req_type == "flag" and not flags.get(req_val):
                    ok = False
                elif req_type == "not_flag" and flags.get(req_val):
                    ok = False
            if ok:
                acts.append(a)

        # ① 显示:你现在在哪、这个区域里有什么
        print("=" * 34)
        print(f"你在【{room['name']}】")
        print(room["desc"])
        print(f"背包:{bag if bag else '(空空如也)'}")
        # ② 显示可交互对象菜单(会随状态变化)
        print("你可以:")
        for i, a in enumerate(acts, 1):
            print(f"  {i}. {a['label']}")
        print("  0. 退出游戏")
        # ③ 读入选择
        try:
            cmd = input("\n> ").strip()
        except EOFError:
            break
        if cmd in ("0", "q", "quit", "退出"):
            print("再见!")
            break
        if not cmd.isdigit() or not (1 <= int(cmd) <= len(acts)):
            print("输入无效,请重新输入一个数字。\n")
            continue
        act = acts[int(cmd) - 1]
        kind = act["kind"]

        # ④ 按类型执行
        if kind == "look":
            print(act["reply"])

        elif kind == "take":
            bag.append(act["item"])
            print(act["reply"])
            room["acts"].remove(act)          # 拿走后从菜单消失

        elif kind == "go":
            if act.get("need_flag") and not flags.get(act["need_flag"]):
                print(act["deny_flag"])
            elif act.get("need_item") and act["need_item"] not in bag:
                print(act["deny_item"])
            else:
                if act.get("ok"):
                    print(act["ok"])
                room_id = act["target"]       # 切换场景 → 下一轮重新渲染

        elif kind == "fire":                  # 点燃壁炉
            flags["fire_lit"] = True
            print(act["reply"])

        elif kind == "douse":                 # 浇灭炉火,取壁炉里藏的钥匙
            flags["fire_lit"] = False
            if "床头抽屉钥匙" not in bag:
                bag.append("床头抽屉钥匙")
                print(act["reply"])
            else:
                print(act["again"])

        elif kind == "window":                # 看窗户:信号弹 → 舅舅出门
            flags["uncle_gone"] = True
            print(act["reply"])
            room["acts"].remove(act)

        elif kind == "open":                  # 用钥匙开床头抽屉
            bag.append(act["give"])
            for f in act.get("set_flags", []):
                flags[f] = True
            print(act["reply"])
            room["acts"].remove(act)

        elif kind == "read":                  # 读日记 → 真相 + 追加结局选项
            print(act["reply"])
            room["acts"].remove(act)
            for e in ENDINGS:
                room["acts"].append(e)

        elif kind == "ending":                # 结局
            print(act["reply"])
            print(f"\n—— {act['epilogue']} ——")
            finished = True

        print()


if __name__ == "__main__":
    main()
