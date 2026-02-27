import React from 'react';
import { DollarSign, Briefcase, Activity } from 'lucide-react';

const StatCard = ({ title, value, icon: Icon }) => (
  <div className="bg-[#111827] rounded-2xl p-6 border border-slate-800 hover:border-blue-500/40 transition-all duration-300 hover:-translate-y-1">

    <div className="flex items-center gap-4">

      <div className="p-3 rounded-xl bg-slate-800 border border-slate-700 text-blue-400">
        <Icon size={22} />
      </div>

      <div>
        <p className="text-slate-400 text-xs font-medium uppercase tracking-wider">
          {title}
        </p>

        <p className="text-2xl font-semibold text-white mt-1">
          {value}
        </p>
      </div>

    </div>
  </div>
);

const Stats = ({ stats }) => {
  if (!stats) return null;

  const formatMoney = (amount) => {
    return new Intl.NumberFormat('ru-KZ', {
      style: 'currency',
      currency: 'KZT',
      maximumSignificantDigits: 3
    }).format(amount);
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-14">

      <StatCard
        title="Всего грантов"
        value={stats.total_grants}
        icon={Briefcase}
      />

      <StatCard
        title="Активные сейчас"
        value={stats.active_grants}
        icon={Activity}
      />

      <StatCard
        title="Общий фонд"
        value={formatMoney(stats.total_max_amount)}
        icon={DollarSign}
      />

    </div>
  );
};

export default Stats;