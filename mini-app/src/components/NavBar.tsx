import { useLocation, useNavigate } from "react-router-dom";

const tabs = [
  { path: "/", label: "ዳሽቦርድ", icon: "📊" },
  { path: "/score", label: "ነጥብ", icon: "🛡" },
];

export default function NavBar() {
  const location = useLocation();
  const navigate = useNavigate();

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-wase-secondary-bg border-t border-gray-200 flex">
      {tabs.map((tab) => {
        const active = location.pathname === tab.path;
        return (
          <button
            key={tab.path}
            onClick={() => navigate(tab.path)}
            className={`flex-1 py-3 flex flex-col items-center gap-0.5 transition-colors ${
              active
                ? "text-wase-primary font-semibold"
                : "text-wase-hint"
            }`}
          >
            <span className="text-xl">{tab.icon}</span>
            <span className="text-xs">{tab.label}</span>
          </button>
        );
      })}
    </nav>
  );
}
