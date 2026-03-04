import { useState } from "react";
import { loginAdmin, collectFull } from "../api";
import { useNavigate } from "react-router-dom";
import { ArrowLeft } from "lucide-react";

export default function AdminPage({ isAuthed, setIsAuthed }) {
  const navigate = useNavigate();
  const [login, setLogin] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");

  const onLogin = async (e) => {
    e.preventDefault();
    setMessage("");
  
    try {
      const res = await loginAdmin(login, password);
      localStorage.setItem("token", res.access_token);
      setIsAuthed(true);
      setMessage("Админ-режим включён.");
    } catch (err) {
      setMessage(err?.message || "Ошибка входа");
    }
  };

  const onLogout = () => {
    localStorage.removeItem("token");
    setIsAuthed(false);
    setMessage("Админ-режим выключен.");
  };

  const onCollect = async () => {
    setMessage("Обновляю данные...");
    const res = await collectFull();
    setMessage(`Готово: ${res.status}`);
  };

  return (
    <div className="min-h-screen bg-[#070b14] text-white">
      <main className="max-w-3xl mx-auto px-6 pt-16 pb-24">
      <button
          onClick={() => navigate("/")}
          className="inline-flex items-center gap-2 text-slate-300 hover:text-white transition mb-8"
        >
          <ArrowLeft className="w-4 h-4" />
          На главную
        </button>
        <h1 className="text-3xl font-semibold mb-6">Админ-панель</h1>

        <div className="bg-slate-900 rounded-2xl border border-slate-800 p-6">
          {!isAuthed ? (
            <form onSubmit={onLogin} className="space-y-4">
              <div>
                <label className="block text-sm text-slate-400 mb-1">Логин</label>
                <input
                  value={login}
                  onChange={(e) => setLogin(e.target.value)}
                  className="w-full px-4 py-2 rounded-xl bg-[#0b0f19] border border-slate-700 outline-none"
                  placeholder="admin"
                />
              </div>

              <div>
                <label className="block text-sm text-slate-400 mb-1">Пароль</label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full px-4 py-2 rounded-xl bg-[#0b0f19] border border-slate-700 outline-none"
                  placeholder="••••••••"
                />
              </div>

              <button
                type="submit"
                className="px-5 py-2.5 rounded-xl bg-blue-500 hover:bg-blue-600 text-white font-medium transition"
              >
                Войти
              </button>
            </form>
          ) : (
            <div className="space-y-4">
              <p className="text-slate-400">Вы вошли в админ-режим.</p>

              <div className="flex flex-wrap gap-3">
                <button
                  onClick={onCollect}
                  className="px-5 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 font-medium transition"
                >
                  Обновить данные
                </button>

                <button
                  onClick={onLogout}
                  className="px-5 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 font-medium transition"
                >
                  Выйти
                </button>
              </div>
            </div>
          )}

          {message ? (
            <div className="mt-4 text-sm text-slate-300 bg-[#0b0f19] border border-slate-800 rounded-xl p-3">
              {message}
            </div>
          ) : null}
        </div>
      </main>
    </div>
  );
}