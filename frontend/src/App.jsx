import { useEffect, useState } from "react";
import { api, setTokens, getTokens } from "./api";
import Auth from "./components/Auth.jsx";
import Customer from "./components/Customer.jsx";
import Staff from "./components/Staff.jsx";
import Admin from "./components/Admin.jsx";

const DASHBOARDS = { customer: Customer, staff: Staff, admin: Admin };

export default function App() {
  const [user, setUser] = useState(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    if (!getTokens()) return setReady(true);
    api("/auth/me/").then(setUser).catch(() => setTokens(null)).finally(() => setReady(true));
  }, []);

  const logout = () => { setTokens(null); setUser(null); };
  if (!ready) return <p className="center">Loading…</p>;
  if (!user) return <Auth onLogin={setUser} />;

  const Dashboard = DASHBOARDS[user.role];
  return (
    <div className="app">
      <header>
        <h1>Salon Booking</h1>
        <div className="who">
          <span>{user.first_name || user.username} <em>({user.role})</em></span>
          <button className="ghost" onClick={logout}>Log out</button>
        </div>
      </header>
      <Dashboard user={user} />
    </div>
  );
}
