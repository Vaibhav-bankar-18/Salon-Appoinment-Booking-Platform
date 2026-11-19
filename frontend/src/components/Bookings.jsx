import { useEffect, useState } from "react";
import { api, fmt } from "../api";

// Shared bookings list. canCancel shows a Cancel button on active bookings.
export default function Bookings({ canCancel = false, showCustomer = false }) {
  const [items, setItems] = useState([]);
  const [msg, setMsg] = useState("");

  const load = () => api("/bookings/").then(setItems).catch((e) => setMsg(e.message));
  useEffect(() => { load(); }, []);

  async function cancel(id) {
    setMsg("");
    try { await api(`/bookings/${id}/cancel/`, { method: "POST" }); load(); }
    catch (e) { setMsg(e.message); }
  }

  if (!items.length) return <p className="muted">No bookings yet.</p>;
  return (
    <>
      {msg && <p className="error">{msg}</p>}
      <ul className="list">
        {items.map((b) => (
          <li key={b.id}>
            <div>
              <strong>{b.service_name}</strong> with {b.staff_name}
              {showCustomer && <> for {b.customer_name}</>}
              <div className="muted">{fmt(b.start)}</div>
            </div>
            <span className={`pill ${b.status}`}>{b.status}</span>
            {canCancel && b.status === "booked" && (
              <button className="danger" onClick={() => cancel(b.id)}>Cancel booking</button>
            )}
          </li>
        ))}
      </ul>
    </>
  );
}
