import { useEffect, useState } from "react";
import { api, fmt } from "../api";
import Tabs from "./Tabs.jsx";
import Bookings from "./Bookings.jsx";

const today = () => new Date().toLocaleDateString("en-CA"); // YYYY-MM-DD

function Book({ onBooked }) {
  const [services, setServices] = useState([]);
  const [service, setService] = useState("");
  const [date, setDate] = useState(today());
  const [slots, setSlots] = useState([]);
  const [msg, setMsg] = useState({ text: "", ok: false });

  useEffect(() => { api("/services/").then(setServices); }, []);
  const load = () =>
    api(`/slots/?date=${date}${service ? `&service=${service}` : ""}`).then(setSlots);
  useEffect(() => { load(); }, [date, service]);

  async function book(id) {
    try {
      await api("/bookings/", { method: "POST", body: { slot: id } });
      setMsg({ text: "Booked. See it under My bookings.", ok: true });
      onBooked?.();
    } catch (e) {
      setMsg({ text: e.message, ok: false });
    }
    load();
  }

  return (
    <>
      <div className="row">
        <select value={service} onChange={(e) => setService(e.target.value)}>
          <option value="">All services</option>
          {services.map((s) => <option key={s.id} value={s.id}>{s.name} ({s.duration_minutes} min, ₹{s.price})</option>)}
        </select>
        <input type="date" value={date} min={today()} onChange={(e) => setDate(e.target.value)} />
      </div>
      {msg.text && <p className={msg.ok ? "ok" : "error"}>{msg.text}</p>}
      {!slots.length ? <p className="muted">No open slots on this day. Try another date.</p> : (
        <ul className="list">
          {slots.map((s) => (
            <li key={s.id}>
              <div>
                <strong>{s.service_name}</strong> with {s.staff_name}
                <div className="muted">{fmt(s.start)}</div>
              </div>
              <button onClick={() => book(s.id)}>Book this slot</button>
            </li>
          ))}
        </ul>
      )}
    </>
  );
}

export default function Customer() {
  const [key, setKey] = useState(0);
  return <Tabs tabs={{
    "Book a slot": <Book onBooked={() => setKey(key + 1)} />,
    "My bookings": <Bookings key={key} canCancel />,
  }} />;
}
