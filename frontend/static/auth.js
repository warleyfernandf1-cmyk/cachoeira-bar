// ─── Auth helpers ──────────────────────────────────────────────────────────
const AUTH = {
  getToken() { return localStorage.getItem("cb_token"); },
  getUser()  { return JSON.parse(localStorage.getItem("cb_user") || "null"); },

  save(token, perfil, nome) {
    localStorage.setItem("cb_token", token);
    localStorage.setItem("cb_user", JSON.stringify({ perfil, nome }));
  },

  logout() {
    localStorage.removeItem("cb_token");
    localStorage.removeItem("cb_user");
    window.location.href = "/";
  },

  require(...perfisPermitidos) {
    if (!this.getToken()) { window.location.href = "/"; return false; }
    const user = this.getUser();
    if (perfisPermitidos.length && !perfisPermitidos.includes(user.perfil)) {
      alert("Acesso negado para seu perfil.");
      window.location.href = "/";
      return false;
    }
    return true;
  },

  headers() {
    return {
      "Authorization": `Bearer ${this.getToken()}`,
      "Content-Type":  "application/json",
    };
  },

  // ── Supabase Realtime ────────────────────────────────────────────────────
  // Subscreve mudanças nas tabelas pedidos e pedidos_setores.
  // onMudanca(payload) é chamado a cada alteração.
  // Retorna o channel para poder cancelar a subscrição se necessário.
  conectarRealtime(onMudanca) {
    const sb = _sbClient();

    const channel = sb.channel("operacional")
      .on("postgres_changes", { event: "*", schema: "public", table: "pedidos" },         onMudanca)
      .on("postgres_changes", { event: "*", schema: "public", table: "pedidos_setores" }, onMudanca)
      .subscribe((status) => {
        // Atualiza indicador visual em todas as páginas que usam data-rt-status
        const cor   = status === "SUBSCRIBED" ? "var(--success)" : "var(--warning)";
        const texto = status === "SUBSCRIBED" ? "● Online" : "● Conectando…";
        document.querySelectorAll("[data-rt-status]").forEach(el => {
          el.textContent  = texto;
          el.style.color  = cor;
        });
      });

    return channel;
  },
};

// ── Supabase client singleton ────────────────────────────────────────────────
function _sbClient() {
  if (!window.__sb) {
    window.__sb = supabase.createClient(CONFIG.SUPABASE_URL, CONFIG.SUPABASE_KEY);
  }
  return window.__sb;
}

// ── apiFetch com tratamento de 401 ─────────────────────────────────────────
async function apiFetch(path, options = {}) {
  const base = CONFIG.API || "";
  const res  = await fetch(`${base}/api${path}`, {
    ...options,
    headers: { ...AUTH.headers(), ...(options.headers || {}) },
  });
  if (res.status === 401) { AUTH.logout(); return; }
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Erro na requisição");
  }
  return res.json();
}
