import { useEffect, useState } from "react";
import { api, fmt } from "../api";
import Tabs from "./Tabs.jsx";
import Bookings from "./Bookings.jsx";

function MySlots() {
  const [services, setServices] = useState([]);
  const [slots, setSlots] = useState([]);
  const [form, setForm] = useState({ service: "", start: "" });
  const [error, setError] = useState("");

  const load = () => api("/slots/").then(setSlots);
  useEffect(() => { api("/services/").then(setServices); load(); }, []);

  async function add(e) {
    e.preventDefault();
    setError("");
    try {
      await api("/slots/", { method: "POST",
        body: { service: form.service, start: new Date(form.start).toISOString() } });
      load();
    } catch (err) { setError(err.message); }
  }
  async function remove(id) {
    setError("");
    try { await api(`/slots/${id}/`, { method: "DELETE" }); load(); }
    catch (err) { setError(err.message); }
  }

  return (
    <>
      <form className="row" onSubmit={add}>
        <select value={form.service} required onChange={(e) => setForm({ ...form, service: e.target.value })}>
          <option value="">Choose service</option>
          {services.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
        </select>
        <input type="datetime-local" required value={form.start}
          onChange={(e) => setForm({ ...form, start: e.target.value })} />
        <button>Add slot</button>
      </form>
      {error && <p className="error">{error}</p>}
      <ul className="list">
        {slots.map((s) => (
          <li key={s.id}>
            <div><strong>{s.service_name}</strong><div className="muted">{fmt(s.start)}</div></div>
            <span className={`pill ${s.is_booked ? "booked" : "open"}`}>{s.is_booked ? "booked" : "open"}</span>
            <button className="danger" onClick={() => remove(s.id)}>Remove</button>
          </li>
        ))}
      </ul>
    </>
  );
}

export default function Staff() {
  return <Tabs tabs={{ "My slots": <MySlots />, "Appointments": <Bookings showCustomer /> }} />;
}
