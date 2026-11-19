import { useState } from "react";
import { api, setTokens } from "../api";

export default function Auth({ onLogin }) {
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ username: "", password: "", first_name: "", email: "", phone: "" });
  const [error, setError] = useState("");
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  async function submit(e) {
    e.preventDefault();
    setError("");
    try {
      if (mode === "register") await api("/auth/register/", { method: "POST", body: form });
      const tokens = await api("/auth/login/", {
        method: "POST", body: { username: form.username, password: form.password },
      });
      setTokens(tokens);
      onLogin(await api("/auth/me/"));
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <form className="auth card" onSubmit={submit}>
      <h1>{mode === "login" ? "Log in to book your visit" : "Create your account"}</h1>
      {mode === "register" && (
        <>
          <input placeholder="Your name" value={form.first_name} onChange={set("first_name")} required />
          <input type="email" placeholder="Email" value={form.email} onChange={set("email")} required />
          <input placeholder="Phone" value={form.phone} onChange={set("phone")} />
        </>
      )}
      <input placeholder="Username" value={form.username} onChange={set("username")} required />
      <input type="password" placeholder="Password (min 8 characters)" value={form.password}
        onChange={set("password")} required />
      {error && <p className="error">{error}</p>}
      <button>{mode === "login" ? "Log in" : "Sign up"}</button>
      <button type="button" className="link"
        onClick={() => { setMode(mode === "login" ? "register" : "login"); setError(""); }}>
        {mode === "login" ? "New here? Create an account" : "Have an account? Log in"}
      </button>
    </form>
  );
}
