// ─── Altere antes do deploy ────────────────────────────────────────────────
const CONFIG = {
  // URL da API no Vercel (mesma origin em produção: "")
  API: "",   // ex em dev local: "http://localhost:8000/api" | em produção: "" (mesmo domínio)

  // Supabase — Project Settings > API
  SUPABASE_URL: "https://SEU_PROJETO.supabase.co",
  SUPABASE_KEY: "eyJ...",  // anon/public key (segura para expor no frontend)
};
