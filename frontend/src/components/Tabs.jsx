import { useState } from "react";

export default function Tabs({ tabs }) {
  const [active, setActive] = useState(Object.keys(tabs)[0]);
  return (
    <>
      <nav className="tabs">
        {Object.keys(tabs).map((name) => (
          <button key={name} className={name === active ? "on" : ""} onClick={() => setActive(name)}>
            {name}
          </button>
        ))}
      </nav>
      <main>{tabs[active]}</main>
    </>
  );
}
