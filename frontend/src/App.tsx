import { useState, useEffect } from 'react';
import { Sun, ArrowUpRight, ArrowDownLeft, Zap, Calendar, RefreshCw, BarChart2 } from 'lucide-react';

interface StatsItem {
  month?: number;
  day?: number;
  ePvDay: number;
  eExportDay: number;
  eImportDay: number;
  eConsumptionDay: number;
}

interface YearResponse {
  success: boolean;
  data: StatsItem[];
}

interface MonthResponse {
  success: boolean;
  dayMax: number;
  data: StatsItem[];
}

const UA_MONTHS = [
  'Січ', 'Лют', 'Бер', 'Кві', 'Тра', 'Чер',
  'Лип', 'Сер', 'Вер', 'Жов', 'Лис', 'Гру'
];

export default function App() {
  const [view, setView] = useState<'month' | 'year'>('year');
  const [yearData, setYearData] = useState<StatsItem[]>([]);
  const [monthData, setMonthData] = useState<StatsItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  // Selected data points for tooltips/interaction
  const [selectedSolar, setSelectedSolar] = useState<{ index: number; value: number } | null>(null);
  const [selectedExport, setSelectedExport] = useState<{ index: number; value: number } | null>(null);
  const [selectedImport, setSelectedImport] = useState<{ index: number; value: number } | null>(null);
  const [selectedConsumption, setSelectedConsumption] = useState<{ index: number; value: number } | null>(null);

  const getApiUrl = (path: string) => {
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
      return `http://localhost:8080${path}`;
    }
    return path;
  };

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [yearRes, monthRes] = await Promise.all([
        fetch(getApiUrl('/api/stats/year')).then(r => r.json()),
        fetch(getApiUrl('/api/stats/month')).then(r => r.json())
      ]);

      if (yearRes.success) {
        setYearData(yearRes.data);
      } else {
        throw new Error(yearRes.error || 'Failed to fetch year stats');
      }

      if (monthRes.success) {
        setMonthData(monthRes.data);
      } else {
        throw new Error(monthRes.error || 'Failed to fetch month stats');
      }
    } catch (err: any) {
      setError(err.message || 'Помилка підключення до сервера');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchData();
    // Initialize Telegram WebApp SDK if available
    if (window.Telegram?.WebApp) {
      const tg = window.Telegram.WebApp;
      tg.ready();
      tg.expand();
      // Set header color
      tg.setHeaderColor('#090b11');
      tg.setBackgroundColor('#090b11');
    }
  }, []);

  const handleRefresh = () => {
    setRefreshing(true);
    fetchData();
  };

  const currentData = view === 'year' ? yearData : monthData;

  // Helper to calculate totals
  const getTotals = () => {
    return currentData.reduce(
      (acc, item) => {
        acc.solar += item.ePvDay;
        acc.export += item.eExportDay;
        acc.import += item.eImportDay;
        acc.consumption += item.eConsumptionDay;
        return acc;
      },
      { solar: 0, export: 0, import: 0, consumption: 0 }
    );
  };

  const totals = getTotals();

  // Helper to format values
  const formatVal = (val: number) => {
    if (val >= 1000) {
      return `${(val / 1000).toFixed(2)} МВт·год`;
    }
    return `${val.toLocaleString()} кВт·год`;
  };

  if (loading && !refreshing) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-[#090b11] text-gray-400">
        <RefreshCw className="w-10 h-10 animate-spin text-purple-500 mb-4" />
        <p className="text-sm font-medium animate-pulse">Завантаження статистики...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-[#090b11] text-gray-400 p-6 text-center">
        <div className="bg-red-500/10 border border-red-500/20 rounded-2xl p-6 max-w-md">
          <p className="text-red-400 font-medium mb-4">⚠️ Помилка: {error}</p>
          <button
            onClick={fetchData}
            className="px-6 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-xl transition-all"
          >
            Спробувати знову
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#090b11] text-gray-100 p-4 pb-12 max-w-lg mx-auto font-sans">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
            <BarChart2 className="text-purple-500 w-6 h-6" />
            Статистика станції
          </h1>
          <p className="text-xs text-gray-500">Luxpower WManage API</p>
        </div>
        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className="p-2.5 rounded-xl glass-panel-light text-gray-400 hover:text-white transition-all active:scale-95"
        >
          <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin text-purple-500' : ''}`} />
        </button>
      </div>

      {/* View Switcher */}
      <div className="flex p-1 bg-[#121824] rounded-xl mb-6 border border-white/5">
        <button
          onClick={() => setView('month')}
          className={`flex-1 py-2 text-sm font-semibold rounded-lg transition-all flex items-center justify-center gap-2 ${
            view === 'month' ? 'bg-[#1e293b] text-white shadow-sm' : 'text-gray-400 hover:text-gray-200'
          }`}
        >
          <Calendar className="w-4 h-4" />
          Місяць
        </button>
        <button
          onClick={() => setView('year')}
          className={`flex-1 py-2 text-sm font-semibold rounded-lg transition-all flex items-center justify-center gap-2 ${
            view === 'year' ? 'bg-[#1e293b] text-white shadow-sm' : 'text-gray-400 hover:text-gray-200'
          }`}
        >
          <Zap className="w-4 h-4" />
          Рік
        </button>
      </div>

      {/* Widgets List */}
      <div className="space-y-6">
        
        {/* SOLAR WIDGET */}
        <WidgetCard
          title="Сонячна генерація"
          total={totals.solar}
          icon={<Sun className="w-5 h-5 text-amber-500" />}
          glowClass="bar-glow-solar"
          colorGradient="from-amber-500 to-yellow-400"
          data={currentData}
          dataKey="ePvDay"
          view={view}
          selectedState={selectedSolar}
          setSelectedState={setSelectedSolar}
        />

        {/* CONSUMPTION WIDGET */}
        <WidgetCard
          title="Власне споживання"
          total={totals.consumption}
          icon={<Zap className="w-5 h-5 text-red-500" />}
          glowClass="bar-glow-consumption"
          colorGradient="from-red-500 to-orange-400"
          data={currentData}
          dataKey="eConsumptionDay"
          view={view}
          selectedState={selectedConsumption}
          setSelectedState={setSelectedConsumption}
        />

        {/* EXPORT WIDGET */}
        <WidgetCard
          title="Експорт в мережу"
          total={totals.export}
          icon={<ArrowUpRight className="w-5 h-5 text-emerald-500" />}
          glowClass="bar-glow-export"
          colorGradient="from-emerald-500 to-green-400"
          data={currentData}
          dataKey="eExportDay"
          view={view}
          selectedState={selectedExport}
          setSelectedState={setSelectedExport}
        />

        {/* IMPORT WIDGET */}
        <WidgetCard
          title="Імпорт з мережі"
          total={totals.import}
          icon={<ArrowDownLeft className="w-5 h-5 text-violet-500" />}
          glowClass="bar-glow-import"
          colorGradient="from-violet-500 to-purple-400"
          data={currentData}
          dataKey="eImportDay"
          view={view}
          selectedState={selectedImport}
          setSelectedState={setSelectedImport}
        />

      </div>
    </div>
  );
}

interface WidgetCardProps {
  title: string;
  total: number;
  icon: React.ReactNode;
  glowClass: string;
  colorGradient: string;
  data: StatsItem[];
  dataKey: keyof StatsItem;
  view: 'month' | 'year';
  selectedState: { index: number; value: number } | null;
  setSelectedState: React.Dispatch<React.SetStateAction<{ index: number; value: number } | null>>;
}

function WidgetCard({
  title,
  total,
  icon,
  glowClass,
  colorGradient,
  data,
  dataKey,
  view,
  selectedState,
  setSelectedState
}: WidgetCardProps) {
  const maxVal = Math.max(...data.map(d => Number(d[dataKey] || 0)), 1);

  // Formatter for individual points
  const formatPointLabel = (item: StatsItem, idx: number) => {
    if (view === 'year') {
      return UA_MONTHS[idx];
    }
    return `${item.day} ${UA_MONTHS[new Date().getMonth()] || ''}`;
  };

  const totalLabel = () => {
    if (total >= 1000) {
      return `${(total / 1000).toFixed(2)} МВт·год`;
    }
    return `${total.toLocaleString()} кВт·год`;
  };

  return (
    <div className="glass-panel shadow-2xl rounded-2xl p-5 card-shadow transition-all duration-300 hover:scale-[1.01]">
      <div className="flex justify-between items-start mb-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-white/5 rounded-xl border border-white/5">
            {icon}
          </div>
          <div>
            <h3 className="text-sm font-semibold text-gray-300">{title}</h3>
            <p className="text-xs text-gray-500">{view === 'year' ? 'Сума за рік' : 'Сума за місяць'}</p>
          </div>
        </div>
        <div className="text-right">
          <div className="text-lg font-bold text-white tracking-tight">{totalLabel()}</div>
        </div>
      </div>

      {/* Micro Info Tooltip Display */}
      <div className="h-6 mb-3 flex items-center justify-between text-xs">
        {selectedState ? (
          <>
            <span className="text-gray-400 font-medium">
              {view === 'year' 
                ? `${UA_MONTHS[selectedState.index]} статистика:` 
                : `${selectedState.index + 1}-й день місяця:`}
            </span>
            <span className="text-white font-semibold bg-white/5 px-2 py-0.5 rounded-md">
              {selectedState.value.toLocaleString()} кВт·год
            </span>
          </>
        ) : (
          <span className="text-gray-500">Натисніть на стовпчик для деталей</span>
        )}
      </div>

      {/* Chart container */}
      <div className="flex items-end justify-between h-32 gap-1.5 px-1 py-2 bg-black/10 rounded-xl border border-white/5 overflow-x-auto">
        {data.map((item, idx) => {
          const val = Number(item[dataKey] || 0);
          const pct = (val / maxVal) * 100;
          const isSelected = selectedState?.index === idx;

          return (
            <div
              key={idx}
              onClick={() => setSelectedState({ index: idx, value: val })}
              className="flex-1 flex flex-col items-center cursor-pointer group h-full justify-end min-w-[14px]"
            >
              {/* Bar */}
              <div className="w-full flex justify-center h-full items-end">
                <div
                  style={{ height: `${Math.max(pct, 5)}%` }}
                  className={`w-full max-w-[12px] rounded-t-full bg-gradient-to-t ${colorGradient} transition-all duration-300 ${glowClass} ${
                    isSelected 
                      ? 'brightness-125 ring-2 ring-white/20' 
                      : 'opacity-70 group-hover:opacity-100 group-hover:scale-y-[1.03]'
                  }`}
                />
              </div>
              
              {/* Label */}
              <span className={`text-[9px] mt-1.5 font-medium transition-all ${
                isSelected ? 'text-white scale-110 font-bold' : 'text-gray-600 group-hover:text-gray-400'
              }`}>
                {view === 'year' ? UA_MONTHS[idx] : item.day}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
