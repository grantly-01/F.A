import React from 'react';
import { Calendar, Building2, Wallet, ArrowUpRight } from 'lucide-react';

const GrantCard = ({ grant }) => {
  const isKZT = grant.currency === 'KZT';

  // Красивое форматирование даты
  const formatDate = (dateStr) => {
    if (!dateStr) return 'Без даты';
    return new Date(dateStr).toLocaleDateString('ru-RU', {
      day: 'numeric', month: 'long', year: 'numeric'
    });
  };

  // Проверка статуса дедлайна
  const deadlineDate = new Date(grant.deadline);
  const isUrgent = grant.deadline && (deadlineDate - new Date()) < (7 * 24 * 60 * 60 * 1000); // Меньше 7 дней

  return (
    <div className="group relative flex flex-col bg-dark-800 rounded-2xl border border-slate-700 hover:border-primary-500/50 transition-all duration-300 hover:shadow-[0_0_20px_rgba(168,85,247,0.15)] h-full">

      {/* Метка срочности */}
      {isUrgent && grant.status === 'active' && (
        <div className="absolute top-4 right-4 px-3 py-1 bg-red-500/10 border border-red-500/30 text-red-400 text-xs font-bold rounded-full animate-pulse">
          Горит дедлайн
        </div>
      )}

      <div className="p-6 flex-1">
        {/* Организация */}
        <div className="flex items-center gap-2 mb-4">
          <Building2 className="w-4 h-4 text-secondary-400" />
          <span className="text-sm text-secondary-400 font-medium truncate">
            {grant.funder || "Неизвестный фонд"}
          </span>
        </div>

        {/* Заголовок */}
        <h3 className="text-xl font-bold text-white mb-3 line-clamp-2 group-hover:text-primary-400 transition-colors">
          {grant.title}
        </h3>

        {/* Описание */}
        <p className="text-slate-400 text-sm line-clamp-3 mb-6">
          {grant.description || "Описание отсутствует..."}
        </p>

        {/* Детали */}
        <div className="space-y-3 border-t border-slate-700/50 pt-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-slate-300 text-sm">
              <Wallet className="w-4 h-4 text-slate-500" />
              <span>
                {grant.amount_max
                  ? `${grant.amount_max.toLocaleString()} ${grant.currency}`
                  : "Сумма не указана"}
              </span>
            </div>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-slate-300 text-sm">
              <Calendar className="w-4 h-4 text-slate-500" />
              <span className={isUrgent ? "text-red-300" : ""}>
                {formatDate(grant.deadline)}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Футер карточки */}
      <div className="p-6 pt-0 mt-auto">
        <a
          href={grant.source_url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center justify-center gap-2 w-full py-3 bg-slate-700/50 hover:bg-primary-600 text-white rounded-xl transition-all duration-300 font-medium group-hover:translate-y-[-2px]"
        >
          Подробнее
          <ArrowUpRight className="w-4 h-4" />
        </a>
      </div>
    </div>
  );
};

export default GrantCard;