import { useEffect, useState } from "react";
import { Routes, Route } from "react-router-dom";
import { initTelegram, getTelegramUser, type TelegramUser } from "./lib/telegram";
import Dashboard from "./pages/Dashboard";
import TrustScore from "./pages/TrustScore";
import Collection from "./pages/Collection";
import NavBar from "./components/NavBar";

export default function App() {
  const [user, setUser] = useState<TelegramUser | null>(null);

  useEffect(() => {
    initTelegram();
    const tgUser = getTelegramUser();
    setUser(tgUser);
  }, []);

  if (!user) {
    return (
      <div className="flex items-center justify-center h-screen bg-wase-bg text-wase-text">
        <div className="text-center">
          <p className="text-2xl font-bold mb-2">✦ ዋሴ</p>
          <p className="text-wase-hint">ይጫኑ...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-wase-bg text-wase-text pb-20">
      <Routes>
        <Route path="/" element={<Dashboard user={user} />} />
        <Route path="/score" element={<TrustScore user={user} />} />
        <Route path="/collection/:id" element={<Collection user={user} />} />
      </Routes>
      <NavBar />
    </div>
  );
}
