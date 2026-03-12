#!/usr/bin/env python3
"""
Project Launcher - Gerencie e abra todos os arquivos/programas de um projeto de uma vez.
Execute: python project_launcher.py
Acesse: http://localhost:5000
"""

import json
import os
import platform
import subprocess
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "projects_data.json")

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"projects": []}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def open_item(item):
    """Abre um arquivo, programa ou URL."""
    path = item.get("path", "").strip()
    if not path:
        return False, "Caminho vazio"
    
    system = platform.system()
    try:
        # URLs (http/https/www)
        if path.startswith(("http://", "https://", "www.")):
            url = path if path.startswith("http") else "https://" + path
            webbrowser.open(url)
            return True, "URL aberta"
        
        # Arquivos e programas
        if system == "Windows":
            os.startfile(path)
        elif system == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
        return True, "Item aberto"
    except Exception as e:
        return False, str(e)

HTML = r"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Project Launcher</title>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #0a0a0f;
    --surface: #111118;
    --surface2: #1a1a25;
    --border: #2a2a3a;
    --accent: #6ee7b7;
    --accent2: #818cf8;
    --accent3: #f472b6;
    --text: #e8e8f0;
    --muted: #6b6b80;
    --danger: #f87171;
    --radius: 12px;
  }

  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: 'Syne', sans-serif;
    min-height: 100vh;
    overflow-x: hidden;
  }

  /* Background grid */
  body::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
      linear-gradient(rgba(110,231,183,0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(110,231,183,0.03) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
    z-index: 0;
  }

  /* Glow blob */
  body::after {
    content: '';
    position: fixed;
    top: -200px;
    left: -200px;
    width: 600px;
    height: 600px;
    background: radial-gradient(circle, rgba(110,231,183,0.06) 0%, transparent 70%);
    pointer-events: none;
    z-index: 0;
  }

  .app { position: relative; z-index: 1; max-width: 900px; margin: 0 auto; padding: 40px 20px 80px; }

  /* Header */
  .header { margin-bottom: 48px; }
  .header-top { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 16px; }
  .logo { display: flex; align-items: center; gap: 12px; }
  .logo-icon {
    width: 42px; height: 42px;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 20px;
    box-shadow: 0 0 20px rgba(110,231,183,0.3);
  }
  .logo-text { font-size: 22px; font-weight: 800; letter-spacing: -0.5px; }
  .logo-sub { font-family: 'DM Mono', monospace; font-size: 11px; color: var(--muted); letter-spacing: 2px; text-transform: uppercase; }

  .btn-new {
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    color: #0a0a0f;
    border: none;
    padding: 10px 20px;
    border-radius: 8px;
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 13px;
    cursor: pointer;
    letter-spacing: 0.5px;
    transition: all 0.2s;
    display: flex; align-items: center; gap: 6px;
  }
  .btn-new:hover { transform: translateY(-1px); box-shadow: 0 8px 20px rgba(110,231,183,0.3); }

  /* Stats bar */
  .stats { display: flex; gap: 24px; margin-top: 24px; padding: 16px 20px; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); }
  .stat { display: flex; flex-direction: column; gap: 2px; }
  .stat-val { font-size: 22px; font-weight: 800; color: var(--accent); }
  .stat-label { font-family: 'DM Mono', monospace; font-size: 10px; color: var(--muted); text-transform: uppercase; letter-spacing: 1.5px; }

  /* Search */
  .search-wrap { position: relative; margin-bottom: 28px; }
  .search-wrap svg { position: absolute; left: 14px; top: 50%; transform: translateY(-50%); color: var(--muted); pointer-events: none; }
  #search {
    width: 100%;
    background: var(--surface);
    border: 1px solid var(--border);
    color: var(--text);
    padding: 12px 14px 12px 42px;
    border-radius: var(--radius);
    font-family: 'DM Mono', monospace;
    font-size: 13px;
    transition: border-color 0.2s;
    outline: none;
  }
  #search:focus { border-color: var(--accent); }
  #search::placeholder { color: var(--muted); }

  /* Projects grid */
  .projects { display: flex; flex-direction: column; gap: 16px; }

  .empty-state { text-align: center; padding: 80px 20px; color: var(--muted); }
  .empty-icon { font-size: 48px; margin-bottom: 16px; }
  .empty-state h3 { font-size: 18px; font-weight: 700; margin-bottom: 8px; color: var(--text); }
  .empty-state p { font-size: 14px; }

  /* Project card */
  .project-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    overflow: hidden;
    transition: border-color 0.2s, transform 0.2s;
    animation: fadeIn 0.3s ease;
  }
  .project-card:hover { border-color: var(--accent2); transform: translateY(-1px); }

  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
  }

  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 20px;
    cursor: pointer;
    gap: 12px;
  }
  .card-header:hover { background: rgba(255,255,255,0.02); }

  .card-title-group { display: flex; align-items: center; gap: 12px; min-width: 0; }
  .card-color {
    width: 10px; height: 10px;
    border-radius: 50%;
    flex-shrink: 0;
    box-shadow: 0 0 8px currentColor;
  }
  .card-name { font-size: 15px; font-weight: 700; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .card-desc { font-size: 12px; color: var(--muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-top: 1px; }

  .card-meta { display: flex; align-items: center; gap: 10px; flex-shrink: 0; }
  .badge {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    padding: 3px 8px;
    border-radius: 20px;
    background: var(--surface2);
    border: 1px solid var(--border);
    color: var(--muted);
    white-space: nowrap;
  }

  .btn-launch {
    background: var(--accent);
    color: #0a0a0f;
    border: none;
    padding: 7px 14px;
    border-radius: 6px;
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 11px;
    cursor: pointer;
    letter-spacing: 0.5px;
    transition: all 0.2s;
    white-space: nowrap;
  }
  .btn-launch:hover { background: #a7f3d0; box-shadow: 0 4px 12px rgba(110,231,183,0.3); }

  .card-actions { display: flex; gap: 6px; }
  .btn-icon {
    background: transparent;
    border: 1px solid var(--border);
    color: var(--muted);
    width: 30px; height: 30px;
    border-radius: 6px;
    cursor: pointer;
    display: flex; align-items: center; justify-content: center;
    transition: all 0.2s;
    font-size: 13px;
  }
  .btn-icon:hover { background: var(--surface2); color: var(--text); border-color: var(--accent2); }
  .btn-icon.danger:hover { color: var(--danger); border-color: var(--danger); }

  .chevron { transition: transform 0.2s; font-size: 12px; color: var(--muted); }
  .project-card.open .chevron { transform: rotate(180deg); }

  /* Items list */
  .items-panel {
    border-top: 1px solid var(--border);
    padding: 0 20px;
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.3s ease, padding 0.3s ease;
  }
  .project-card.open .items-panel { max-height: 600px; padding: 16px 20px; }

  .item-row {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 10px;
    border-radius: 8px;
    transition: background 0.15s;
    margin-bottom: 4px;
  }
  .item-row:hover { background: var(--surface2); }

  .item-type-icon {
    width: 28px; height: 28px;
    border-radius: 6px;
    display: flex; align-items: center; justify-content: center;
    font-size: 13px;
    flex-shrink: 0;
  }
  .type-url { background: rgba(129,140,248,0.15); }
  .type-file { background: rgba(110,231,183,0.15); }
  .type-app { background: rgba(244,114,182,0.15); }

  .item-path { font-family: 'DM Mono', monospace; font-size: 11px; color: var(--muted); flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .item-name { font-size: 13px; font-weight: 600; min-width: 0; }

  .item-actions { display: flex; gap: 4px; flex-shrink: 0; }
  .btn-item-del {
    background: transparent; border: none; color: var(--muted);
    cursor: pointer; padding: 4px; border-radius: 4px;
    font-size: 12px; transition: color 0.2s;
    line-height: 1;
  }
  .btn-item-del:hover { color: var(--danger); }

  .add-item-row {
    display: flex; gap: 8px; align-items: center;
    margin-top: 10px; padding-top: 12px;
    border-top: 1px dashed var(--border);
    flex-wrap: wrap;
  }
  .add-item-row input, .add-item-row select {
    background: var(--surface2);
    border: 1px solid var(--border);
    color: var(--text);
    padding: 7px 10px;
    border-radius: 7px;
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    outline: none;
    transition: border-color 0.2s;
  }
  .add-item-row input:focus, .add-item-row select:focus { border-color: var(--accent); }
  .add-item-row input { flex: 1; min-width: 140px; }
  .add-item-row select { min-width: 80px; }
  .btn-add-item {
    background: var(--surface2);
    border: 1px solid var(--accent);
    color: var(--accent);
    padding: 7px 12px;
    border-radius: 7px;
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 11px;
    cursor: pointer;
    transition: all 0.2s;
    white-space: nowrap;
  }
  .btn-add-item:hover { background: var(--accent); color: #0a0a0f; }

  /* Modal */
  .modal-overlay {
    display: none;
    position: fixed; inset: 0;
    background: rgba(0,0,0,0.75);
    z-index: 100;
    align-items: center; justify-content: center;
    backdrop-filter: blur(4px);
  }
  .modal-overlay.show { display: flex; }

  .modal {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 32px;
    width: 100%; max-width: 480px;
    margin: 20px;
    animation: modalIn 0.2s ease;
  }
  @keyframes modalIn {
    from { opacity: 0; transform: scale(0.95); }
    to { opacity: 1; transform: scale(1); }
  }

  .modal h2 { font-size: 20px; font-weight: 800; margin-bottom: 24px; }

  .form-group { margin-bottom: 16px; }
  .form-label { display: block; font-family: 'DM Mono', monospace; font-size: 10px; color: var(--muted); text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 6px; }
  .form-input {
    width: 100%;
    background: var(--surface2);
    border: 1px solid var(--border);
    color: var(--text);
    padding: 10px 12px;
    border-radius: 8px;
    font-family: 'Syne', sans-serif;
    font-size: 14px;
    outline: none;
    transition: border-color 0.2s;
  }
  .form-input:focus { border-color: var(--accent); }

  .color-options { display: flex; gap: 8px; flex-wrap: wrap; }
  .color-opt {
    width: 28px; height: 28px; border-radius: 50%;
    cursor: pointer; border: 2px solid transparent;
    transition: transform 0.15s, border-color 0.15s;
  }
  .color-opt:hover { transform: scale(1.15); }
  .color-opt.selected { border-color: white; transform: scale(1.1); }

  .modal-actions { display: flex; gap: 10px; justify-content: flex-end; margin-top: 24px; }
  .btn-cancel {
    background: transparent; border: 1px solid var(--border); color: var(--muted);
    padding: 9px 18px; border-radius: 8px;
    font-family: 'Syne', sans-serif; font-weight: 600; font-size: 13px;
    cursor: pointer; transition: all 0.2s;
  }
  .btn-cancel:hover { border-color: var(--text); color: var(--text); }
  .btn-save {
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    color: #0a0a0f; border: none;
    padding: 9px 20px; border-radius: 8px;
    font-family: 'Syne', sans-serif; font-weight: 700; font-size: 13px;
    cursor: pointer; transition: all 0.2s;
  }
  .btn-save:hover { opacity: 0.9; box-shadow: 0 4px 14px rgba(110,231,183,0.3); }

  /* Toast */
  .toast {
    position: fixed; bottom: 24px; right: 24px;
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 12px 18px;
    font-size: 13px;
    display: flex; align-items: center; gap: 8px;
    z-index: 200;
    transform: translateY(80px);
    opacity: 0;
    transition: all 0.3s;
    max-width: 320px;
  }
  .toast.show { transform: translateY(0); opacity: 1; }
  .toast.success { border-color: var(--accent); }
  .toast.error { border-color: var(--danger); }

  @media (max-width: 600px) {
    .stats { flex-wrap: wrap; gap: 16px; }
    .card-header { flex-wrap: wrap; }
  }
</style>
</head>
<body>
<div class="app">

  <header class="header">
    <div class="header-top">
      <div class="logo">
        <div class="logo-icon">🚀</div>
        <div>
          <div class="logo-text">Project Launcher</div>
          <div class="logo-sub">Gerenciador de Projetos</div>
        </div>
      </div>
      <button class="btn-new" onclick="openModal()">
        <span>＋</span> Novo Projeto
      </button>
    </div>
    <div class="stats" id="stats"></div>
  </header>

  <div class="search-wrap">
    <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
      <circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/>
    </svg>
    <input id="search" type="text" placeholder="Buscar projetos..." oninput="renderProjects()">
  </div>

  <div id="projects" class="projects"></div>
</div>

<!-- Modal -->
<div class="modal-overlay" id="modal" onclick="closeModalOutside(event)">
  <div class="modal">
    <h2 id="modal-title">Novo Projeto</h2>
    <div class="form-group">
      <label class="form-label">Nome do Projeto</label>
      <input class="form-input" id="proj-name" placeholder="Ex: Relatório Q4, Demo Cliente X..." maxlength="60">
    </div>
    <div class="form-group">
      <label class="form-label">Descrição (opcional)</label>
      <input class="form-input" id="proj-desc" placeholder="Breve descrição..." maxlength="120">
    </div>
    <div class="form-group">
      <label class="form-label">Cor</label>
      <div class="color-options" id="color-options"></div>
    </div>
    <input type="hidden" id="proj-id" value="">
    <div class="modal-actions">
      <button class="btn-cancel" onclick="closeModal()">Cancelar</button>
      <button class="btn-save" onclick="saveProject()">Salvar</button>
    </div>
  </div>
</div>

<!-- Toast -->
<div class="toast" id="toast"></div>

<script>
const COLORS = ['#6ee7b7','#818cf8','#f472b6','#fb923c','#facc15','#38bdf8','#a78bfa','#34d399','#f87171','#e879f9'];
let projects = [];
let openCards = new Set();
let selectedColor = COLORS[0];
let editingId = null;

// Init color pickers
const co = document.getElementById('color-options');
COLORS.forEach(c => {
  const d = document.createElement('div');
  d.className = 'color-opt' + (c === COLORS[0] ? ' selected' : '');
  d.style.background = c;
  d.onclick = () => {
    document.querySelectorAll('.color-opt').forEach(x => x.classList.remove('selected'));
    d.classList.add('selected');
    selectedColor = c;
  };
  co.appendChild(d);
});

async function api(method, path, body) {
  const r = await fetch(path, {
    method,
    headers: {'Content-Type': 'application/json'},
    body: body ? JSON.stringify(body) : undefined
  });
  return r.json();
}

async function load() {
  const d = await api('GET', '/api/projects');
  projects = d.projects || [];
  renderProjects();
  renderStats();
}

function renderStats() {
  const total = projects.length;
  const items = projects.reduce((s, p) => s + (p.items||[]).length, 0);
  document.getElementById('stats').innerHTML = `
    <div class="stat"><span class="stat-val">${total}</span><span class="stat-label">Projetos</span></div>
    <div class="stat"><span class="stat-val">${items}</span><span class="stat-label">Itens total</span></div>
  `;
}

function renderProjects() {
  const q = document.getElementById('search').value.toLowerCase();
  const filtered = q ? projects.filter(p => p.name.toLowerCase().includes(q) || (p.desc||'').toLowerCase().includes(q)) : projects;
  const el = document.getElementById('projects');

  if (!filtered.length) {
    el.innerHTML = `<div class="empty-state"><div class="empty-icon">📂</div><h3>${q ? 'Nenhum projeto encontrado' : 'Nenhum projeto ainda'}</h3><p>${q ? 'Tente outro termo de busca.' : 'Clique em "+ Novo Projeto" para começar.'}</p></div>`;
    return;
  }

  el.innerHTML = filtered.map(p => renderCard(p)).join('');
}

function renderCard(p) {
  const isOpen = openCards.has(p.id);
  const items = p.items || [];
  const typeIcon = t => t === 'url' ? '🌐' : t === 'app' ? '⚙️' : '📄';
  const typeClass = t => t === 'url' ? 'type-url' : t === 'app' ? 'type-app' : 'type-file';

  const itemsHtml = items.map((item, i) => `
    <div class="item-row">
      <div class="item-type-icon ${typeClass(item.type)}">${typeIcon(item.type)}</div>
      <div style="flex:1;min-width:0;">
        <div class="item-name">${esc(item.name || item.path)}</div>
        <div class="item-path">${esc(item.path)}</div>
      </div>
      <div class="item-actions">
        <button class="btn-item-del" onclick="deleteItem('${p.id}',${i})" title="Remover">✕</button>
      </div>
    </div>
  `).join('');

  return `
    <div class="project-card ${isOpen ? 'open' : ''}" id="card-${p.id}">
      <div class="card-header" onclick="toggleCard('${p.id}')">
        <div class="card-title-group">
          <div class="card-color" style="background:${p.color||'#6ee7b7'};color:${p.color||'#6ee7b7'}"></div>
          <div>
            <div class="card-name">${esc(p.name)}</div>
            ${p.desc ? `<div class="card-desc">${esc(p.desc)}</div>` : ''}
          </div>
        </div>
        <div class="card-meta">
          <span class="badge">${items.length} ${items.length === 1 ? 'item' : 'itens'}</span>
          <button class="btn-launch" onclick="launchProject(event,'${p.id}')">▶ Abrir Tudo</button>
          <div class="card-actions">
            <button class="btn-icon" onclick="editProject(event,'${p.id}')" title="Editar">✏️</button>
            <button class="btn-icon danger" onclick="deleteProject(event,'${p.id}')" title="Excluir">🗑</button>
          </div>
          <span class="chevron">▾</span>
        </div>
      </div>
      <div class="items-panel">
        ${items.length ? itemsHtml : '<p style="color:var(--muted);font-size:13px;padding:4px 0 8px;">Nenhum item ainda. Adicione abaixo.</p>'}
        <div class="add-item-row">
          <input id="new-name-${p.id}" placeholder="Nome (opcional)">
          <input id="new-path-${p.id}" placeholder="Caminho ou URL...">
          <select id="new-type-${p.id}">
            <option value="file">📄 Arquivo</option>
            <option value="url">🌐 URL</option>
            <option value="app">⚙️ Programa</option>
          </select>
          <button class="btn-add-item" onclick="addItem('${p.id}')">+ Adicionar</button>
        </div>
      </div>
    </div>
  `;
}

function esc(s) {
  if (!s) return '';
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function toggleCard(id) {
  if (openCards.has(id)) openCards.delete(id);
  else openCards.add(id);
  renderProjects();
}

function openModal(id) {
  editingId = id || null;
  const p = id ? projects.find(x => x.id === id) : null;
  document.getElementById('modal-title').textContent = p ? 'Editar Projeto' : 'Novo Projeto';
  document.getElementById('proj-name').value = p ? p.name : '';
  document.getElementById('proj-desc').value = p ? (p.desc||'') : '';
  selectedColor = p ? (p.color||COLORS[0]) : COLORS[0];
  document.querySelectorAll('.color-opt').forEach((el, i) => {
    el.classList.toggle('selected', COLORS[i] === selectedColor);
  });
  document.getElementById('modal').classList.add('show');
  setTimeout(() => document.getElementById('proj-name').focus(), 100);
}

function closeModal() { document.getElementById('modal').classList.remove('show'); }
function closeModalOutside(e) { if (e.target === document.getElementById('modal')) closeModal(); }

async function saveProject() {
  const name = document.getElementById('proj-name').value.trim();
  if (!name) { toast('Digite um nome para o projeto', 'error'); return; }
  const desc = document.getElementById('proj-desc').value.trim();

  if (editingId) {
    const p = projects.find(x => x.id === editingId);
    p.name = name; p.desc = desc; p.color = selectedColor;
    await api('PUT', `/api/projects/${editingId}`, {name, desc, color: selectedColor});
    toast('Projeto atualizado!', 'success');
  } else {
    const d = await api('POST', '/api/projects', {name, desc, color: selectedColor});
    projects.push(d.project);
    openCards.add(d.project.id);
    toast('Projeto criado!', 'success');
  }
  closeModal();
  renderProjects();
  renderStats();
}

function editProject(e, id) { e.stopPropagation(); openModal(id); }

async function deleteProject(e, id) {
  e.stopPropagation();
  if (!confirm('Excluir este projeto?')) return;
  await api('DELETE', `/api/projects/${id}`);
  projects = projects.filter(p => p.id !== id);
  openCards.delete(id);
  renderProjects();
  renderStats();
  toast('Projeto excluído', 'success');
}

async function addItem(pid) {
  const pathEl = document.getElementById(`new-path-${pid}`);
  const nameEl = document.getElementById(`new-name-${pid}`);
  const typeEl = document.getElementById(`new-type-${pid}`);
  const path = pathEl.value.trim();
  if (!path) { toast('Informe o caminho ou URL', 'error'); return; }
  const name = nameEl.value.trim() || path.split(/[\\/]/).pop() || path;
  const type = typeEl.value;
  const d = await api('POST', `/api/projects/${pid}/items`, {name, path, type});
  const p = projects.find(x => x.id === pid);
  p.items = d.items;
  pathEl.value = ''; nameEl.value = '';
  renderProjects();
  renderStats();
  openCards.add(pid);
  toast('Item adicionado!', 'success');
}

async function deleteItem(pid, idx) {
  const d = await api('DELETE', `/api/projects/${pid}/items/${idx}`);
  const p = projects.find(x => x.id === pid);
  p.items = d.items;
  openCards.add(pid);
  renderProjects();
  renderStats();
  toast('Item removido', 'success');
}

async function launchProject(e, pid) {
  e.stopPropagation();
  const p = projects.find(x => x.id === pid);
  if (!p.items || !p.items.length) { toast('Nenhum item cadastrado!', 'error'); return; }
  const d = await api('POST', `/api/projects/${pid}/launch`);
  const ok = d.results.filter(r => r.ok).length;
  const fail = d.results.filter(r => !r.ok).length;
  if (fail === 0) toast(`✅ ${ok} item(ns) aberto(s)!`, 'success');
  else toast(`⚠️ ${ok} aberto(s), ${fail} falhou`, 'error');
}

let toastTimer;
function toast(msg, type='success') {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.className = `toast ${type} show`;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => t.classList.remove('show'), 3000);
}

// Enter key in modal
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') closeModal();
  if (e.key === 'Enter' && document.getElementById('modal').classList.contains('show')) saveProject();
});

load();
</script>
</body>
</html>
"""

import uuid

class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Silencia logs

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def send_html(self, html):
        body = html.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length:
            return json.loads(self.rfile.read(length))
        return {}

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/" or path == "/index.html":
            self.send_html(HTML)
        elif path == "/api/projects":
            self.send_json(load_data())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        path = urlparse(self.path).path
        body = self.read_body()
        data = load_data()
        parts = path.strip("/").split("/")
        # POST /api/projects
        if path == "/api/projects":
            proj = {
                "id": str(uuid.uuid4())[:8],
                "name": body.get("name", "Sem nome"),
                "desc": body.get("desc", ""),
                "color": body.get("color", "#6ee7b7"),
                "items": []
            }
            data["projects"].append(proj)
            save_data(data)
            self.send_json({"project": proj})
        # POST /api/projects/{id}/items
        elif len(parts) == 4 and parts[0] == "api" and parts[1] == "projects" and parts[3] == "items":
            pid = parts[2]
            for p in data["projects"]:
                if p["id"] == pid:
                    p.setdefault("items", []).append({
                        "name": body.get("name", ""),
                        "path": body.get("path", ""),
                        "type": body.get("type", "file")
                    })
                    save_data(data)
                    self.send_json({"items": p["items"]})
                    return
            self.send_json({"error": "not found"}, 404)
        # POST /api/projects/{id}/launch
        elif len(parts) == 4 and parts[3] == "launch":
            pid = parts[2]
            for p in data["projects"]:
                if p["id"] == pid:
                    results = []
                    for item in p.get("items", []):
                        ok, msg = open_item(item)
                        results.append({"ok": ok, "msg": msg, "item": item.get("name", "")})
                    self.send_json({"results": results})
                    return
            self.send_json({"error": "not found"}, 404)
        else:
            self.send_response(404)
            self.end_headers()

    def do_PUT(self):
        path = urlparse(self.path).path
        body = self.read_body()
        data = load_data()
        parts = path.strip("/").split("/")
        # PUT /api/projects/{id}
        if len(parts) == 3 and parts[0] == "api" and parts[1] == "projects":
            pid = parts[2]
            for p in data["projects"]:
                if p["id"] == pid:
                    p["name"] = body.get("name", p["name"])
                    p["desc"] = body.get("desc", p.get("desc", ""))
                    p["color"] = body.get("color", p.get("color", "#6ee7b7"))
                    save_data(data)
                    self.send_json({"project": p})
                    return
            self.send_json({"error": "not found"}, 404)
        else:
            self.send_response(404)
            self.end_headers()

    def do_DELETE(self):
        path = urlparse(self.path).path
        data = load_data()
        parts = path.strip("/").split("/")
        # DELETE /api/projects/{id}
        if len(parts) == 3 and parts[0] == "api" and parts[1] == "projects":
            pid = parts[2]
            data["projects"] = [p for p in data["projects"] if p["id"] != pid]
            save_data(data)
            self.send_json({"ok": True})
        # DELETE /api/projects/{id}/items/{idx}
        elif len(parts) == 5 and parts[3] == "items":
            pid, idx = parts[2], int(parts[4])
            for p in data["projects"]:
                if p["id"] == pid:
                    p.setdefault("items", []).pop(idx)
                    save_data(data)
                    self.send_json({"items": p["items"]})
                    return
            self.send_json({"error": "not found"}, 404)
        else:
            self.send_response(404)
            self.end_headers()


if __name__ == "__main__":
    PORT = 5000
    server = HTTPServer(("localhost", PORT), Handler)
    url = f"http://localhost:{PORT}"
    print(f"\n🚀 Project Launcher rodando em {url}")
    print("   Pressione Ctrl+C para parar.\n")
    webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Servidor encerrado.")