import React from 'react';
import { Calendar, Building2, Wallet, ArrowUpRight } from 'lucide-react';

const GrantCard = ({ grant }) => {

  const formatDate = (dateStr) => {
    if (!dateStr) return 'Без даты';
    return new Date(dateStr).toLocaleDateString('ru-RU', {
      day: 'numeric',
      month: 'long',
      year: 'numeric'
    });
  };

  const deadlineDate = new Date(grant.deadline);
  const isUrgent =
    grant.deadline &&
    (deadlineDate - new Date()) < (7 * 24 * 60 * 60 * 1000);

  return (
    <div className="group relative flex flex-col bg-[#111827] rounded-2xl border border-slate-800 hover:border-blue-500/40 transition-all duration-300 h-full hover:-translate-y-1">

      {/* Метка срочности */}
      {isUrgent && grant.status === 'active' && (
        <div className="absolute top-4 right-4 px-3 py-1 bg-red-500/10 border border-red-500/30 text-red-400 text-xs font-medium rounded-full">
          Горит дедлайн
        </div>
      )}

      <div className="p-6 flex-1">

        {/* Организация */}
        <div className="flex items-center gap-2 mb-4 text-slate-400 text-sm">
          <Building2 className="w-4 h-4" />
          <span className="truncate">
            {grant.funder || "Неизвестный фонд"}
          </span>
        </div>

        {/* Заголовок */}
        <h3 className="text-lg font-semibold text-white mb-3 line-clamp-2 group-hover:text-blue-400 transition-colors">
          {grant.title}
        </h3>

        {/* Описание */}
        <p className="text-slate-400 text-sm line-clamp-3 mb-6">
          {grant.description || "Описание отсутствует..."}
        </p>

        {/* Детали */}
        <div className="space-y-3 border-t border-slate-800 pt-4">

          <div className="flex items-center gap-2 text-slate-300 text-sm">
            <Wallet className="w-4 h-4 text-slate-500" />
            <span>
              {grant.amount_max
                ? `${grant.amount_max.toLocaleString()} ${grant.currency}`
                : "Сумма не указана"}
            </span>
          </div>

          <div className="flex items-center gap-2 text-sm">
            <Calendar className="w-4 h-4 text-slate-500" />
            <span className={isUrgent ? "text-red-400" : "text-slate-300"}>
              {formatDate(grant.deadline)}
            </span>
          </div>

        </div>
      </div>

      {/* Кнопка */}
      <div className="p-6 pt-0 mt-auto">
        <a
          href={grant.source_url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center justify-center gap-2 w-full py-3 bg-blue-500 hover:bg-blue-600 text-white rounded-xl transition-all duration-300 font-medium"
        >
          Подробнее
          <ArrowUpRight className="w-4 h-4" />
        </a>
      </div>

    </div>
  );
};

export default GrantCard;