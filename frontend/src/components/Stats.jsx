import React from 'react';
import { DollarSign, Briefcase, Activity } from 'lucide-react';

const StatCard = ({ title, value, icon: Icon, colorClass }) => (
  <div className="relative overflow-hidden bg-dark-800 rounded-2xl p-6 border border-slate-700/50 hover:border-slate-600 transition-all group">
    <div className={`absolute -right-6 -top-6 w-24 h-24 rounded-full opacity-10 blur-xl ${colorClass}`}></div>
    <div className="flex items-center gap-4">
      <div className={`p-3 rounded-lg bg-dark-900 border border-slate-700 ${colorClass.replace('bg-', 'text-')}`}>
        <Icon size={24} />
      </div>
      <div>
        <p className="text-slate-400 text-sm font-medium uppercase tracking-wider">{title}</p>
        <p className="text-2xl font-bold text-white mt-1 group-hover:scale-105 transition-transform origin-left">
            {value}
        </p>
      </div>
    </div>
  </div>
);

const Stats = ({ stats }) => {
  if (!stats) return null;

  // Форматирование денег
  const formatMoney = (amount) => {
    return new Intl.NumberFormat('ru-KZ', {
      style: 'currency',
      currency: 'KZT',
      maximumSignificantDigits: 3
    }).format(amount);
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
      <StatCard
        title="Всего грантов"
        value={stats.total_grants}
        icon={Briefcase}
        colorClass="bg-primary-500"
      />
      <StatCard
        title="Активные сейчас"
        value={stats.active_grants}
        icon={Activity}
        colorClass="bg-secondary-500"
      />
      <StatCard
        title="Общий фонд"
        value={formatMoney(stats.total_max_amount)}
        icon={DollarSign}
        colorClass="bg-emerald-500"
      />
    </div>
  );
};

export default Stats;