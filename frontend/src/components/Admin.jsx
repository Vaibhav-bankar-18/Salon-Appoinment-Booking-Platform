import { useEffect, useState } from "react";
import { api } from "../api";
import Tabs from "./Tabs.jsx";
import Bookings from "./Bookings.jsx";

function Services() {
  const [items, setItems] = useState([]);
  const [form, setForm] = useState({ name: "", duration_minutes: 30, price: "" });
  const [error, setError] = useState("");

  const load = () => api("/services/").then(setItems);
  useEffect(() => { load(); }, []);

  async function add(e) {
    e.preventDefault();
    setError("");
    try { await api("/services/", { method: "POST", body: form }); setForm({ ...form, name: "", price: "" }); load(); }
    catch (err) { setError(err.message); }
  }
  async function toggle(s) { await api(`/services/${s.id}/`, { method: "PATCH", body: { active: !s.active } }); load(); }
  async function remove(s) {
    try { await api(`/services/${s.id}/`, { method: "DELETE" }); load(); }
    catch (err) { setError(err.message); }
  }

  return (
    <>
      <form className="row" onSubmit={add}>
        <input placeholder="Service name" value={form.name} required
          onChange={(e) => setForm({ ...form, name: e.target.value })} />
        <input type="number" min="5" step="5" title="Minutes" value={form.duration_minutes}
          onChange={(e) => setForm({ ...form, duration_minutes: e.target.value })} />
        <input type="number" min="0" placeholder="Price (₹)" value={form.price} required
          onChange={(e) => setForm({ ...form, price: e.target.value })} />
        <button>Add service</button>
      </form>
      {error && <p className="error">{error}</p>}
      <ul className="list">
        {items.map((s) => (
          <li key={s.id}>
            <div><strong>{s.name}</strong><div className="muted">{s.duration_minutes} min · ₹{s.price}</div></div>
            <span className={`pill ${s.active ? "open" : "cancelled"}`}>{s.active ? "active" : "hidden"}</span>
            <button className="ghost" onClick={() => toggle(s)}>{s.active ? "Hide" : "Show"}</button>
            <button className="danger" onClick={() => remove(s)}>Delete</button>
          </li>
        ))}
      </ul>
      <p className="muted">To add staff accounts, open the Django admin and set the user's role to Staff.</p>
    </>
  );
}

export default function Admin() {
  return <Tabs tabs={{ Services: <Services />, "All bookings": <Bookings canCancel showCustomer /> }} />;
}
