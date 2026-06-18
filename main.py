"""
osu! PP 推荐谱面工具 — GUI 版 (PyWebView)
使用系统浏览器引擎渲染，支持封面图片、现代化 UI

打包: pyinstaller --onefile --windowed --icon=alphaosu.ico --name "osuPP推荐谱面" osu_pp_gui.py
"""

import json
import os
import re
import threading
import urllib.request
import urllib.error

import webview

# ============================================================
#  API 配置
# ============================================================
API_BASE = "https://alphaosu.keytoix.vip/api/v1"
SAYOBOT_DL = "https://dl.sayobot.cn/beatmaps/download"


def api_get(path, params=None):
    url = f"{API_BASE}{path}"
    if params:
        qs = "&".join(f"{k}={v}" for k, v in params.items() if v is not None)
        url += f"?{qs}"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def api_post(path, data):
    url = f"{API_BASE}{path}"
    body = json.dumps(data).encode()
    req = urllib.request.Request(
        url, data=body,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


# ============================================================
#  Python API —— JS 通过 window.pywebview.api.xxx() 调用
# ============================================================
class Api:
    """暴露给前端 JS 调用的 Python 接口"""

    def __init__(self):
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        self.download_dir = os.path.join(desktop, "osu_pp_maps")

    def login(self, username):
        """登录，返回 uid"""
        try:
            result = api_post("/login", {"username": username})
            if not result.get("success"):
                return {"ok": False, "msg": result.get("message", "登录失败")}
            return {"ok": True, "uid": result["data"]["uid"]}
        except Exception as e:
            return {"ok": False, "msg": str(e)}

    def get_page(self, uid, page):
        """获取一页推荐"""
        try:
            data = api_get("/self/maps/recommend", {
                "uid": uid, "gameMode": 0,
                "current": page, "pageSize": 20, "rule": 4
            })
            if not data.get("success"):
                return {"ok": False, "msg": data.get("message")}
            d = data["data"]
            return {"ok": True, "list": d["list"], "total": d["total"], "next": d["next"]}
        except Exception as e:
            return {"ok": False, "msg": str(e)}

    def choose_dir(self):
        """打开文件夹选择对话框"""
        try:
            result = webview.windows[0].create_file_dialog(
                webview.FOLDER_DIALOG, directory=self.download_dir
            )
            if result and len(result) > 0:
                self.download_dir = result[0]
                return {"ok": True, "path": result[0]}
            return {"ok": False, "msg": "未选择"}
        except Exception as e:
            return {"ok": False, "msg": str(e)}

    def get_download_dir(self):
        """获取当前下载目录"""
        return self.download_dir

    def download(self, set_id, name):
        """下载单个谱面"""
        safe = re.sub(r'[<>:"/\\|?*]', '_', name)
        os.makedirs(self.download_dir, exist_ok=True)

        filename = f"{set_id} {safe}.osz"
        filepath = os.path.join(self.download_dir, filename)

        if os.path.exists(filepath):
            return {"ok": True, "status": "exists", "path": filepath}

        try:
            url = f"{SAYOBOT_DL}/{set_id}"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=120) as resp:
                with open(filepath, "wb") as f:
                    f.write(resp.read())
            return {"ok": True, "status": "ok", "path": filepath}
        except Exception as e:
            return {"ok": False, "msg": str(e)}


# ============================================================
#  HTML 界面
# ============================================================
HTML = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>AlphaOsu! Download Tool</title>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#0d0d18;--s1:#14142a;--s2:#1c1c36;--bd:#2e2e50;
  --t1:#e8e8f0;--t2:#8888a8;--ac:#6c8cff;--ac2:#5470dd;
  --pink:#ff6c8c;--grn:#4cdb8a;--org:#ffb86c;--red:#ff4c6c;
  --r:10px;
}
html,body{width:100%;min-height:100vh;background:var(--bg);color:var(--t1);
  font-family:'Segoe UI',-apple-system,sans-serif;line-height:1.6;overflow-x:hidden}

/* 滚动条 */
::-webkit-scrollbar{width:6px}
::-webkit-scrollbar-track{background:var(--s1)}
::-webkit-scrollbar-thumb{background:var(--bd);border-radius:3px}
::-webkit-scrollbar-thumb:hover{background:var(--ac)}

.wrap{max-width:1040px;margin:0 auto;padding:32px 20px 60px}

/* 标题 */
.logo{display:flex;align-items:center;gap:12px;margin-bottom:4px}
.logo img{width:36px;height:36px;border-radius:8px}
.logo h1{font-size:24px;font-weight:700;
  background:linear-gradient(135deg,var(--ac),var(--pink));
  -webkit-background-clip:text;-webkit-text-fill-color:transparent}
.sub{color:var(--t2);font-size:13px;margin-bottom:28px}

/* 登录 */
.login{display:flex;gap:10px;margin-bottom:24px}
.login input{flex:1;padding:10px 16px;background:var(--s1);border:1px solid var(--bd);
  border-radius:var(--r);color:var(--t1);font-size:14px;outline:none;transition:.2s}
.login input:focus{border-color:var(--ac)}
.login input::placeholder{color:var(--t2)}
.btn{padding:10px 22px;border:none;border-radius:var(--r);font-size:13px;
  font-weight:600;cursor:pointer;transition:.2s;white-space:nowrap}
.btn-p{background:var(--ac);color:#fff}
.btn-p:hover{background:var(--ac2);transform:translateY(-1px)}
.btn-p:disabled{opacity:.4;cursor:wait;transform:none}
.btn-dl{background:var(--grn);color:#000;font-size:12px;padding:4px 10px;border-radius:6px}
.btn-dl:hover{filter:brightness(1.1)}

/* 筛选 */
.flts{background:var(--s1);border:1px solid var(--bd);border-radius:12px;padding:20px 24px;margin-bottom:20px}
.flts h3{font-size:12px;color:var(--t2);text-transform:uppercase;letter-spacing:1px;margin-bottom:16px}
.fg{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px 28px}
@media(max-width:700px){.fg{grid-template-columns:1fr}}
.fg label.lbl{display:block;font-size:12px;color:var(--t2);margin-bottom:6px}
.fg .rd{font-size:12px;color:var(--ac);float:right;margin-top:-18px}
input[type=range]{-webkit-appearance:none;width:100%;height:5px;
  background:var(--s2);border-radius:3px;outline:none;margin:6px 0}
input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;
  width:16px;height:16px;background:var(--ac);border-radius:50%;cursor:pointer;
  box-shadow:0 0 8px rgba(108,140,255,.4)}
.rr{display:flex;gap:8px;align-items:center}
.rr input{flex:1}
.rr span{font-size:11px;color:var(--t2);min-width:32px;text-align:center}
.tw{display:flex;align-items:center;justify-content:space-between;padding:2px 0}
.tw span{font-size:13px}
.sw{position:relative;width:40px;height:22px;cursor:pointer;display:inline-block}
.sw input{display:none}
.sw .tr{position:absolute;inset:0;background:var(--s2);border-radius:11px;
  border:1px solid var(--bd);transition:.3s}
.sw input:checked+.tr{background:var(--ac);border-color:var(--ac)}
.sw .kn{position:absolute;top:2px;left:2px;width:18px;height:18px;
  background:#fff;border-radius:50%;transition:.3s}
.sw input:checked~.kn{transform:translateX(18px)}
.mg{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px}
.mb{display:flex;align-items:center;gap:5px;padding:5px 10px;
  background:var(--s2);border:1px solid var(--bd);border-radius:6px;
  cursor:pointer;font-size:12px;transition:.2s;user-select:none}
.mb:hover{border-color:var(--ac)}
.mb.on{background:rgba(108,140,255,.15);border-color:var(--ac);color:var(--ac)}
.mb .bx{width:14px;height:14px;border:2px solid var(--bd);border-radius:3px;
  display:flex;align-items:center;justify-content:center;font-size:10px;transition:.2s}
.mb.on .bx{background:var(--ac);border-color:var(--ac);color:#fff}

/* 状态 */
.st{padding:10px 16px;background:var(--s1);border:1px solid var(--bd);
  border-radius:var(--r);margin-bottom:16px;font-size:12px;color:var(--t2);
  display:flex;align-items:center;gap:10px}
.st .dt{width:7px;height:7px;border-radius:50%;flex-shrink:0}
.st .dt.ok{background:var(--grn)}.st .dt.ld{background:var(--org);animation:pulse 1s infinite}
.st .dt.er{background:var(--red)}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.3}}
.st .ct{margin-left:auto;color:var(--ac);font-weight:600}

/* 表格 */
.tw2{overflow-x:auto;border-radius:12px;border:1px solid var(--bd);background:var(--s1)}
table{width:100%;border-collapse:collapse;font-size:12px}
thead th{padding:10px 12px;background:var(--s2);color:var(--t2);font-weight:600;
  text-align:left;font-size:11px;text-transform:uppercase;letter-spacing:.5px;
  border-bottom:1px solid var(--bd);white-space:nowrap;position:sticky;top:0;z-index:1}
tbody tr{border-bottom:1px solid rgba(46,46,80,.4);transition:.15s}
tbody tr:hover{background:rgba(108,140,255,.06)}
tbody tr.sel{background:rgba(108,140,255,.12)}
td{padding:8px 12px;vertical-align:middle}
td.n{text-align:right;font-variant-numeric:tabular-nums}
.cover{width:48px;height:36px;border-radius:4px;object-fit:cover;flex-shrink:0}
.map-cell{display:flex;align-items:center;gap:10px}
.map-info a{font-weight:500;color:var(--t1);text-decoration:none;font-size:13px;transition:.2s}
.map-info a:hover{color:var(--ac)}
.map-info .meta{font-size:10px;color:var(--t2);margin-top:1px}
.star{display:inline-flex;align-items:center;gap:2px;padding:2px 7px;
  background:rgba(108,140,255,.12);border-radius:4px;font-size:11px;color:var(--ac)}
.pp{color:var(--grn);font-weight:600}
.inc{color:var(--org)}
.pb{display:flex;align-items:center;gap:5px}
.pb .bar{width:44px;height:3px;background:var(--s2);border-radius:2px;overflow:hidden}
.pb .bar .fl{height:100%;border-radius:2px;transition:.3s}
.mt{display:inline-block;padding:2px 5px;background:rgba(255,108,140,.12);
  color:var(--pink);border-radius:3px;font-size:10px;font-weight:600}
.empty{text-align:center;padding:50px 20px;color:var(--t2)}
.empty .ic{font-size:42px;margin-bottom:12px}
.foot{margin-top:32px;padding:16px;background:var(--s1);border:1px solid var(--bd);
  border-radius:var(--r);font-size:11px;color:var(--t2);line-height:1.8}
.foot a{color:var(--ac);text-decoration:none}.foot a:hover{text-decoration:underline}
</style>
</head>
<body>
<div class="wrap">
  <div class="logo">
    <img src="https://alphaosu.keytoix.vip/assets/favicon.0d142200.ico" alt="AlphaOsu">
    <h1>AlphaOsu! Download Tool</h1>
  </div>
  <p class="sub">基于 AlphaOsu 机器学习推荐，筛选并下载最适合你的 PP 谱面</p>

  <div class="login">
    <input type="text" id="u" placeholder="输入 osu! 用户名..." value="">
    <button class="btn btn-p" id="btnGo" onclick="go()">获取推荐</button>
  </div>

  <div class="flts">
    <h3>🎛️ 筛选条件</h3>
    <div class="fg">
      <div>
        <label class="lbl">⭐ 难度星级</label>
        <div class="rd" id="sD">5.0 - 7.3</div>
        <div class="rr">
          <span id="sL">5.0</span>
          <input type=range id="s0" min=0 max=15 step=0.1 value=5 oninput="uR('s',0,15,1)">
          <input type=range id="s1" min=0 max=15 step=0.1 value=7.3 oninput="uR('s',0,15,1)">
          <span id="sH">7.3</span>
        </div>
      </div>
      <div>
        <label class="lbl">📊 上榜概率</label>
        <div class="rd" id="rD">20% - 100%</div>
        <div class="rr">
          <span id="rL">20%</span>
          <input type=range id="r0" min=0 max=100 step=5 value=20 oninput="uR('r',0,100,0)">
          <input type=range id="r1" min=0 max=100 step=5 value=100 oninput="uR('r',0,100,0)">
          <span id="rH">100%</span>
        </div>
      </div>
      <div>
        <label class="lbl">🏆 破纪录概率</label>
        <div class="rd" id="cD">20% - 100%</div>
        <div class="rr">
          <span id="cL">20%</span>
          <input type=range id="c0" min=0 max=100 step=5 value=20 oninput="uR('c',0,100,0)">
          <input type=range id="c1" min=0 max=100 step=5 value=100 oninput="uR('c',0,100,0)">
          <span id="cH">100%</span>
        </div>
      </div>
      <div>
        <label class="lbl">🎮 其他</label>
        <div class="tw"><span>隐藏已玩过的谱面</span>
          <label class="sw"><input type="checkbox" id="hp" checked onchange="flt()"><div class="tr"></div><div class="kn"></div></label>
        </div>
      </div>
      <div style="grid-column:1/-1">
        <label class="lbl">🎯 Mod 筛选</label>
        <div class="mg" id="mg">
          <div class="mb on" data-m="NM" onclick="tM(this)"><span class="bx">✓</span>NM</div>
          <div class="mb" data-m="HD" onclick="tM(this)"><span class="bx"></span>HD</div>
          <div class="mb" data-m="HR" onclick="tM(this)"><span class="bx"></span>HR</div>
          <div class="mb" data-m="DT" onclick="tM(this)"><span class="bx"></span>DT</div>
          <div class="mb" data-m="HDHR" onclick="tM(this)"><span class="bx"></span>HD+HR</div>
          <div class="mb" data-m="HDDT" onclick="tM(this)"><span class="bx"></span>HD+DT</div>
          <div class="mb" data-m="HRDT" onclick="tM(this)"><span class="bx"></span>HR+DT</div>
          <div class="mb" data-m="HDHRDT" onclick="tM(this)"><span class="bx"></span>HD+HR+DT</div>
        </div>
      </div>
    </div>
  </div>

  <div class="st"><span class="dt" id="dt"></span><span id="stx">输入用户名并点击「获取推荐」</span><span class="ct" id="ct"></span></div>

  <div id="dlBar" style="display:none;margin-bottom:12px;display:flex;gap:8px;align-items:center;flex-wrap:wrap">
    <button class="btn btn-p" onclick="dlAll()" style="font-size:12px;padding:8px 18px">⬇ 全部下载</button>
    <button class="btn" onclick="dlSel()" style="font-size:12px;padding:8px 18px;background:var(--org);color:#000">⬇ 下载选中</button>
    <span style="font-size:12px;color:var(--t2);margin-left:8px">
      <label style="cursor:pointer"><input type="checkbox" id="ckAll" onchange="selAll(this.checked)" style="margin-right:4px">全选</label>
    </span>
    <span style="margin-left:auto;display:flex;align-items:center;gap:6px">
      <span style="font-size:11px;color:var(--t2)">保存到:</span>
      <span id="dlPath" style="font-size:11px;color:var(--ac);max-width:260px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap"></span>
      <button class="btn" onclick="chooseDir()" style="font-size:11px;padding:4px 10px;background:var(--s2);color:var(--t2);border:1px solid var(--bd)">选择...</button>
    </span>
  </div>

  <div class="tw2" id="tw" style="display:none">
    <table><thead><tr>
      <th><input type="checkbox" id="ckAll2" onchange="selAll(this.checked)"></th>
      <th>#</th><th>谱面</th><th>Mod</th><th>难度</th>
      <th>预测PP</th><th>+PP</th><th>上榜%</th><th>破纪录%</th><th></th>
    </tr></thead><tbody id="tb"></tbody></table>
  </div>

  <div class="empty" id="emp"><div class="ic">🎯</div><p>输入你的 osu! 用户名，获取 AI 推荐的 PP 谱面</p></div>

  <div class="foot">
    <p>数据来源：<a href="https://alphaosu.keytoix.vip/" target="_blank">AlphaOsu!</a> — 机器学习推荐 PP 谱面</p>
    <p>下载源：<a href="https://sayobot.cn/" target="_blank">Sayobot</a> 镜像 · .osz 双击导入 osu! · 保存到桌面/osu_pp_maps/</p>
  </div>
</div>

<script>
// 所有数据
let ALL=[], DISP=[];
const SAYOBOT='https://dl.sayobot.cn/beatmaps/download';
let DL_COUNT={ok:0,skip:0,fail:0,total:0};

// ---- 滑块 ----
function uR(t,lo,hi,d){
  let a=Math.min(+$(`#${t}0`).value,+$(`#${t}1`).value),
      b=Math.max(+$(`#${t}0`).value,+$(`#${t}1`).value);
  a=Math.max(lo,Math.min(hi,a)); b=Math.max(lo,Math.min(hi,b));
  $(`#${t}0`).value=a; $(`#${t}1`).value=b;
  const s=d?'':'%';
  $(`#${t}L`).textContent=a.toFixed(d)+s;
  $(`#${t}H`).textContent=b.toFixed(d)+s;
  $(`#${t}D`).textContent=a.toFixed(d)+s+' - '+b.toFixed(d)+s;
  flt();
}

// ---- Mod ----
function tM(el){
  if(el.classList.contains('on')&&document.querySelectorAll('.mb.on').length<=1)return;
  el.classList.toggle('on');
  el.querySelector('.bx').textContent=el.classList.contains('on')?'✓':'';
  flt();
}
function gMods(){return[...document.querySelectorAll('.mb.on')].map(e=>e.dataset.m)}

// ---- 状态 ----
function sSt(t,x,c){$('#dt').className='dt '+(t==='ok'?'ok':t==='ld'?'ld':'er');$('#stx').textContent=x;$('#ct').textContent=c||''}

// ---- 全选/反选 ----
function selAll(v){document.querySelectorAll('.row-cb').forEach(cb=>{cb.checked=v;cb.closest('tr').classList.toggle('sel',v)})}
function onCb(cb){cb.closest('tr').classList.toggle('sel',cb.checked)}
function getSel(){
  const sels=[];document.querySelectorAll('.row-cb:checked').forEach(cb=>sels.push(+cb.dataset.i));
  return sels
}

// ---- 批量下载 ----
async function dlBatch(indices){
  if(!indices.length)return;
  const btns=document.querySelectorAll('.btn-dl'); // disable all
  DL_COUNT={ok:0,skip:0,fail:0,total:indices.length};
  for(const i of indices){
    const m=DISP[i];
    sSt('ld',`⬇ [${DL_COUNT.ok+DL_COUNT.skip+DL_COUNT.fail+1}/${DL_COUNT.total}] ${m.mapName.slice(0,35)}...`);
    const r=await window.pywebview.api.download(m._sid,m.mapName);
    if(r.ok){DL_COUNT[r.status==='exists'?'skip':'ok']++}else{DL_COUNT.fail++}
  }
  sSt('ok',`下载完成: ${DL_COUNT.ok} 新, ${DL_COUNT.skip} 跳过, ${DL_COUNT.fail} 失败`);
}
function dlAll(){dlBatch(DISP.map((_,i)=>i))}
function dlSel(){const s=getSel();if(!s.length){sSt('er','请先勾选要下载的谱面');return}dlBatch(s)}

// ---- 登录 + 获取 ----
async function go(){
  const u=$('#u').value.trim(); if(!u)return;
  const btn=$('#btnGo'); btn.disabled=true;
  try{
    sSt('ld','正在登录...');
    const lr=await window.pywebview.api.login(u);
    if(!lr.ok){sSt('er','登录失败: '+lr.msg);return}
    sSt('ld','正在获取推荐...');
    ALL=[];
    let pg=1;
    while(true){
      const r=await window.pywebview.api.get_page(lr.uid,pg);
      if(!r.ok){sSt('er','获取失败: '+r.msg);return}
      ALL.push(...r.list);
      sSt('ld',`获取中... ${ALL.length}/${r.total}`);
      if(r.next===-1||ALL.length>=r.total)break;
      pg=r.next;
    }
    sSt('ok',`${u} 的推荐已加载`,'');
    flt();
  }catch(e){sSt('er','错误: '+e)}
  finally{btn.disabled=false}
}

// ---- 筛选 ----
function flt(){
  if(!ALL.length)return;
  const sm=Math.min(+$('#s0').value,+$('#s1').value),sx=Math.max(+$('#s0').value,+$('#s1').value);
  const rm=Math.min(+$('#r0').value,+$('#r1').value),rx=Math.max(+$('#r0').value,+$('#r1').value);
  const cm=Math.min(+$('#c0').value,+$('#c1').value),cx=Math.max(+$('#c0').value,+$('#c1').value);
  const hp=$('#hp').checked, mods=gMods();

  const f=ALL.filter(m=>{
    if(m.difficulty<sm||m.difficulty>sx)return false;
    if(hp&&m.currentPP!=null)return false;
    if(mods.length&&!mods.some(md=>(m.mod||[]).includes(md)))return false;
    if(m.passPercent!=null){const p=m.passPercent*100;if(p<rm||p>rx)return false}
    if(m.newRecordPercent!=null){const p=m.newRecordPercent*100;if(p<cm||p>cx)return false}
    return true;
  });

  // 去重
  const seen=new Set(),u=[];
  for(const m of f){
    const sid=setId(m.mapCoverUrl);
    if(sid&&!seen.has(sid)){seen.add(sid);u.push({...m,_sid:sid})}
  }
  DISP=u;
  render(u);
  sSt('ok','筛选完成',`${u.length} / ${ALL.length} 个谱面`);
}

function render(ms){
  const tb=$('#tb'),tw=$('#tw'),emp=$('#emp');
  if(!ms.length){tw.style.display='none';emp.style.display='block';$('#dlBar').style.display='none';emp.querySelector('.ic').textContent='😢';emp.querySelector('p').textContent='没有符合筛选条件的谱面';return}
  emp.style.display='none';tw.style.display='block';$('#dlBar').style.display='flex';
  tb.innerHTML=ms.map((m,i)=>{
    const pp=m.predictPP?m.predictPP.toFixed(0):'-';
    const inc=m.ppIncrementExpect?m.ppIncrementExpect.toFixed(1):'-';
    const rp=m.passPercent!=null?(m.passPercent*100):null;
    const np=m.newRecordPercent!=null?(m.newRecordPercent*100):null;
    const mod=(m.mod||['NM']).join('/');
    const mn=Math.floor(m.length/60),sc=String(Math.floor(m.length%60)).padStart(2,'0');
    const bpm=m.bpm?Math.round(m.bpm):'?';
    const cover=m.mapCoverUrl||'';
    return`<tr>
      <td><input type="checkbox" class="row-cb" data-i="${i}" onchange="onCb(this)"></td>
      <td style="color:var(--t2)">${i+1}</td>
      <td><div class="map-cell">
        <img class="cover" src="${cover}" loading="lazy" onerror="this.style.display='none'">
        <div class="map-info">
          <a href="${m.mapLink}" target="_blank">${esc(m.mapName)}</a>
          <div class="meta">BPM ${bpm} · ${mn}:${sc} · ${(m.sliderRatio*100).toFixed(0)}% slider</div>
        </div>
      </div></td>
      <td><span class="mt">${mod}</span></td>
      <td><span class="star">★ ${m.difficulty.toFixed(2)}</span></td>
      <td class="n"><span class="pp">${pp}</span></td>
      <td class="n"><span class="inc">+${inc}pp</span></td>
      <td class="n">${pct(rp)}</td>
      <td class="n">${pct(np)}</td>
      <td><a class="btn btn-dl" href="${SAYOBOT}/${m._sid}" target="_blank" title="下载 .osz">⬇</a></td>
    </tr>`;
  }).join('');
}

function pct(p){
  if(p==null)return'<span style="color:var(--t2)">-</span>';
  const c=p>=70?'var(--grn)':p>=40?'var(--org)':'var(--red)';
  return`<div class="pb"><div class="bar"><div class="fl" style="width:${p}%;background:${c}"></div></div><span style="color:${c}">${p.toFixed(0)}%</span></div>`;
}

function $(s){return document.querySelector(s)}
function esc(s){const d=document.createElement('div');d.textContent=s;return d.innerHTML}
function setId(u){const m=u&&u.match(/\/beatmaps\/(\d+)\//);return m?m[1]:null}

// 初始化
uR('s',0,15,1);uR('r',0,100,0);uR('c',0,100,0);
$('#u').addEventListener('keydown',e=>{if(e.key==='Enter')go()});

// 下载目录选择
async function chooseDir(){const r=await window.pywebview.api.choose_dir();if(r.ok)$('#dlPath').textContent=r.path}
async function initPath(){$('#dlPath').textContent=await window.pywebview.api.get_download_dir()}

// PyWebView 就绪回调
window.addEventListener('pywebviewready',()=>{initPath()});
</script>
</body>
</html>'''


def main():
    api = Api()
    window = webview.create_window(
        "AlphaOsu! Download Tool",
        html=HTML,
        js_api=api,
        width=1100,
        height=750,
        min_size=(900, 600),
    )
    webview.start(debug=False)


if __name__ == "__main__":
    main()
