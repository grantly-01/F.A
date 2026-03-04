import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { getGrants } from "../api";
import { ArrowLeft } from "lucide-react";

export default function GrantDetailsPage() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [grants, setGrants] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        const data = await getGrants("");
        setGrants(data);
      } finally {
        setLoading(false);
      }
    };

    load();
  }, []);

  const grant = useMemo(() => {
    const numId = Number(id);
    return grants.find((g) => Number(g.id) === numId);
  }, [grants, id]);

  if (loading) {
    return (
      <div className="min-h-screen bg-[#070b14] text-white flex items-center justify-center">
        <div className="text-slate-400">Загрузка...</div>
      </div>
    );
  }

  if (!grant) {
    return (
      <div className="min-h-screen bg-[#070b14] text-white">
        <main className="max-w-4xl mx-auto px-6 pt-16 pb-24">
          <button
            onClick={() => navigate(-1)}
            className="inline-flex items-center gap-2 text-slate-300 hover:text-white transition mb-8"
          >
            <ArrowLeft className="w-4 h-4" />
            Назад
          </button>

          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8">
            <h1 className="text-2xl font-semibold mb-2">Грант не найден</h1>
            <p className="text-slate-400">
              Возможно, грант удалён или id неверный
            </p>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#070b14] text-white">
      <main className="max-w-4xl mx-auto px-6 pt-16 pb-24">
        <button
          onClick={() => navigate(-1)}
          className="inline-flex items-center gap-2 text-slate-300 hover:text-white transition mb-8"
        >
          <ArrowLeft className="w-4 h-4" />
          Назад
        </button>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8">
          <div className="text-slate-400 mb-2">{grant.funder || "Организатор не указан"}</div>

          <h1 className="text-3xl font-semibold mb-4">{grant.title}</h1>

          {grant.description ? (
            <p className="text-slate-300 leading-relaxed mb-6">{grant.description}</p>
          ) : (
            <p className="text-slate-400 mb-6">Описание отсутствует</p>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div className="bg-[#0b0f19] border border-slate-800 rounded-xl p-4">
              <div className="text-slate-400">Сумма</div>
              <div className="text-white mt-1">
                {grant.amount_min ?? 0} – {grant.amount_max ?? 0} {grant.currency || ""}
              </div>
            </div>

            <div className="bg-[#0b0f19] border border-slate-800 rounded-xl p-4">
              <div className="text-slate-400">Дедлайн</div>
              <div className="text-white mt-1">
                {grant.deadline ? new Date(grant.deadline).toLocaleDateString() : "Не указан"}
              </div>
            </div>

            <div className="bg-[#0b0f19] border border-slate-800 rounded-xl p-4 md:col-span-2">
              <div className="text-slate-400">Кому подходит</div>
              <div className="text-white mt-1">
                {grant.eligibility || "Не указано"}
              </div>
            </div>
          </div>

          {grant.source_url ? (
            <div className="mt-6">
              <a
                className="inline-flex items-center justify-center px-5 py-2.5 rounded-xl bg-blue-500 hover:bg-blue-600 text-white font-medium transition"
                href={grant.source_url}
                target="_blank"
                rel="noreferrer"
              >
                Перейти к источнику
              </a>
            </div>
          ) : null}
        </div>
      </main>
    </div>
  );
}